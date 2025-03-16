@echo OFF
pushd %~sdp0

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: This script will trancribe mp3 chunks of 30mn. It accepts:
:: 1. no arguments = opens a prompt
:: 2. a folder = trancribes *.mp3 in that folder
:: 3. 1 or more files.mp3 = trancribes those files
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: This script requires a file named BiasBuster-whisper_custom.cmd
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: this script requires a compiled faster-whisper from https://github.com/guillaumekln/faster-whisper -> https://github.com/SYSTRAN/faster-whisper
:: but actually on windows we use the binaries provided by https://github.com/Purfview/whisper-standalone-win
:: we started with  faster-whisper 0.9.0      small
:: we curently use  Faster-Whisper-XXL r245.2 distil-large-v3
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::  Models go under %WhisperFasterPath%\_models\
::  available models for faster-whisper 0.9.0:
::  https://huggingface.co/guillaumekln
::    tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2
::    for English radio broadcasts, small gives the best results so far; 12 real seconds/s
::  available models for Faster-Whisper-XXL r245.2:
::  https://huggingface.co/Systran  https://huggingface.co/Purfview
::    tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2 large-v3 large large-v3-turbo turbo distil-large-v2 distil-medium.en distil-small.en distil-large-v3
::    distil-large-v3 currently give best results and is 3x faster then faster-whisper 0.9.0 + small: 46 real seconds/s
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: to compare performance and quality: see :compareSpeed at the bottom of this script
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: what is diarize? supposedly seperate speakers by voice in files that accept it: json
:: what is distile? https://github.com/huggingface/distil-whisper Distil-Whisper is a distilled version of Whisper for English speech recognition that is 6 times faster, 49% smaller
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:init
set author=AudioscavengeR

:defaults
set LOG="%~dpn0.log"
set busybox=
set importTexts=--import --folder "%~1"
set htmlGen=--html %~n1 --autoGenerate
set misInfoGen=--gettext week=%~n1 --misInformation --noMerge

set WhisperFasterPath=E:\GPT\Faster-Whisper-XXL
set WhisperBin=faster-whisper-xxl.exe
set existingModels=tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2 large-v3 large large-v3-turbo turbo distil-large-v2 distil-medium.en distil-small.en distil-large-v3

:: Python path. I recommend using miniconda3 or similar
set PythonVenv=E:\GPT\stable-diffusion-webui\venv\Scripts
:: model small gives the best results for radio broadcasts, but medium is recommended
:: latest distil-large-v3 seems the best as of early 2025
REM set model=small
set model=distil-large-v3
:: delete mp3 processed
set deleteMp3=n
:: delete logs
set deleteLogs=y
:: do not reprocess same mp3
set reprocess=n
:: import text files created
set import=y
:: build the html schedule page at the end, and calculate misInformation values
set html=y
set misInfo=y
set language=en

set WhisperOptions=


:prechecks
call :loadCustomValues
IF NOT EXIST "%WhisperFasterPath%\"  echo ERROR: update WhisperFasterPath in %~n0_custom.cmd & pause & exit 1
IF NOT EXIST "%PythonVenv%\"         echo ERROR: update PythonVenv in %~n0_custom.cmd & pause & exit 1

where busybox.exe >NUL 2>&1 && set busybox=busybox.exe

set models=
for /f %%a in ('dir /b /od "%WhisperFasterPath%\_models\faster-whisper-*"') DO (
  for /f "tokens=3 delims=-" %%A in ("%%a") DO call set "models=%%models%% %%A"
)

IF NOT DEFINED models (
  echo WARNING: no models found under %WhisperFasterPath%\_models
  echo If it's the first time you run this batch, that's normal. If not, that's an error.
  echo:
  set models=%existingModels%
)

:main
title BiasBuster: transcribe sounds to text with Whisper-Faster
set PATH=%WhisperFasterPath%;%PythonVenv%;%PATH%

IF "%~1"=="" call :USAGE
echo WhisperBin:          %WhisperBin%
echo existingModels:      %existingModels%

IF NOT "%~1"=="" (
  echo availableModels:    %models%
  set /P     model=model?              [%model%] 
  set /P deleteMp3=deleteMp3 after?    [%deleteMp3%] 
  set /P reprocess=reprocess existing? [%reprocess%] 
  set /P      html=generate html?      [%html%] 
)
if /I NOT "%html%"=="y" (
  set /P    import=import texts?       [%import%] 
)
if /I "%html%"=="y" set misInfo=y

REM :: folder was passed
IF EXIST "%~1\*.mp3" (
  echo mkdir "%~1\done"
  mkdir "%~1\done"
  REM :: first, address reprocess by deleting processed files, in case the batch was interrupted for instance
  IF /I "%reprocess%"=="n" (
    for %%a in ("%~1\*.mp3") DO (
      IF EXIST "%%~dpna.text" (
        IF /I "%deleteMp3%"=="y" (
          echo deleting "%%~a" 1>&2
          del /f /q "%%~a"
        REM ) ELSE (
          REM move processed files so we don't reprocess them
          REM echo ERROR: conflict: you don't want to reprocess %%a but also don't want to delete processed files.
          REM echo make up your mind.
          REM echo:
          REM pause
          REM exit /b 1
        )
      )
    )
  )

  REM :: process files in folder one by one (overhead induced as whisper will reload the model each time):
  REM for %%a in ("%~1\*.mp3") DO (
    REM echo busybox time %WhisperBin% "%%~a" -pp --language=%language% --model %model% --output_format=all --device=cuda --output_dir %%~sdpa | busybox tee -a %LOG%
    REM busybox time %WhisperBin% "%%~a" -pp --language=%language% --model %model% --output_format=all --device=cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%deleteMp3%"=="y" del /q "%%~a"
  REM )

  REM :: process folder recursively (faster):
  IF DEFINED busybox (
    echo busybox time %WhisperBin% "%~1" --batch_recursive -pp --language=%language% --model=%model% --output_format=all --device=cuda --output_dir="%~1" | busybox tee -a %LOG%
    busybox time %WhisperBin% "%~1" --batch_recursive -pp --language=%language% --model=%model% --output_format=all --device=cuda --output_dir="%~1"
  ) ELSE (
    echo %WhisperBin% "%~1" --batch_recursive -pp --language=%language% --model=%model% --output_format=all --device=cuda --output_dir="%~1" >>%LOG%
    echo %WhisperBin% "%~1" --batch_recursive -pp --language=%language% --model=%model% --output_format=all --device=cuda --output_dir="%~1"
    %WhisperBin% "%~1" --batch_recursive -pp --language=%language% --model=%model% --output_format=all --device=cuda --output_dir="%~1"
  )

  for %%a in ("%~1\*.mp3") DO (
    IF EXIST "%%~dpna.text" (
      IF /I "%deleteMp3%"=="y" (
        echo deleting "%%~a" 1>&2
        del /f /q "%%~a"
      ) ELSE (
        echo move /y "%%~a" "%%~dpa\done\%%~nxa" 1>&2
        move /y "%%~a" "%%~dpa\done\%%~nxa" 1>&2
      )
    )
  )

REM :: list of files.text was passed
) ELSE (
  REM :: list:
  for %%a in (%*) DO (
    IF /I "%%~xa"==".mp3" (
      IF DEFINED busybox (
        echo busybox time %WhisperBin% %%a -pp --language=%language% --model %model% --output_format=all --device=cuda --output_dir %%~sdpa | busybox tee -a %LOG%
        busybox time %WhisperBin% %%a --language en --model %model% --output_format=all --device=cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%deleteMp3%"=="y" del /q "%%~a"
      ) ELSE (
        echo %WhisperBin% %%a -pp --language=%language% --model %model% --output_format=all --device=cuda --output_dir %%~sdpa >>%LOG%
        echo %WhisperBin% %%a -pp --language=%language% --model %model% --output_format=all --device=cuda --output_dir %%~sdpa
        %WhisperBin% %%a -pp --language=%language% --model %model% --output_format=all --device=cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%deleteMp3%"=="y" del /q "%%~a"
      )
    )
  )
)

REM no arguments? open a command prompt
IF     "%~1"=="" cmd /k


:import
if /I NOT "%import%"=="y" (
  echo:
  echo IMPORT DISABLED!
  echo to import:                 python KJZZ-db.py --import --folder "%~1"
  echo to import + generate html: python KJZZ-db.py --import --folder "%~1" --html %~n1 --autoGenerate
  echo to       generate misInfo: python KJZZ-db.py --gettext week=%~n1 --misInformation --noMerge
  goto :end
)

IF NOT "%~1"=="" (
  IF EXIST "%~1\*.text" (
    IF /I "%deleteLogs%"=="y" (
      echo deleting %~1\*.log" 1>&2
      del /f /q "%~1\*.log"
    )

    call %PythonVenv%\activate || call %PythonVenv%\environment
    IF /I "%import%"=="y" (
      echo python KJZZ-db.py %importTexts%
      python KJZZ-db.py %importTexts%
    )
    IF /I "%misInfo%"=="y" (
      echo python KJZZ-db.py %misInfoGen%
      python KJZZ-db.py %misInfoGen%
    )
    IF /I "%html%"=="y" (
      echo python KJZZ-db.py %htmlGen%
      python KJZZ-db.py %htmlGen%
    )
  )
)


:end
timeout /t 10
pause
exit




:::::::::::::::::::::::::::::::::::::::::::::: functions
:USAGE
call %PythonVenv%\activate || call %PythonVenv%\environment
nvidia-smi

echo   python KJZZ-db.py --import --folder kjzz\43
echo   python KJZZ-db.py --query title
echo   python KJZZ-db.py --query chunkLast10 -p
echo   python KJZZ-db.py --gettext chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v --wordCloud
echo   python KJZZ-db.py --gettext title="All Things Considered" -v --wordCloud
echo   python KJZZ-db.py --gettext title="All Things Considered" -v --wordCloud
echo   python KJZZ-db.py --gettext title="BBC Newshour" -v --wordCloud
echo   python KJZZ-db.py --gettext title="BBC World Business Report" -v --wordCloud
echo   python KJZZ-db.py --gettext title="BBC World Service" -v --wordCloud
echo   python KJZZ-db.py --gettext title="Fresh Air" -v --wordCloud
echo   python KJZZ-db.py --gettext title="Here and Now" -v --wordCloud
echo   python KJZZ-db.py --gettext title="Marketplace" -v --wordCloud
echo   python KJZZ-db.py --gettext title="Morning Edition" -v --wordCloud
echo   python KJZZ-db.py --gettext title="The Show" -v --wordCloud
echo   python KJZZ-db.py --gettext week=42+Day=Mon+title="The Show" -v --wordCloud --stopLevel 3
echo   python KJZZ-db.py --gettext week=42+Day=Mon+title="All Things Considered" --wordCloud --stopLevel 3 --show
echo   python KJZZ-db.py --gettext week=42 --wordCloud --stopLevel 3 --show --max_words=10000
echo   python KJZZ-db.py --gettext week=44 --wordCloud --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
echo   python KJZZ-db.py --gettext week=43+title="TED Radio Hour" --wordCloud --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
echo   python KJZZ-db.py --gettext week=42+title="Freakonomics" --misInformation --show
echo   python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --graphs pie,bar --show
echo   python KJZZ-db.py --gettext week=46+title="Morning Edition"+Day=Mon --misInformation --show
echo   python KJZZ-db.py --gettext week=48+title="The Pulse" --wordCloud
echo   python KJZZ-db.py --html 42 --byChunk
echo   python KJZZ-db.py --rebuildThumbnails 41
REM    for /l %a in (42,1,48) DO @python KJZZ-db.py --rebuildThumbnails %a
echo   python KJZZ-db.py --gettext week=43+title="TED Radio Hour"+Day=Sun --wordCloud  --useJpeg --jpegQuality 50 --stopLevel 3 --show --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt

REM (re)generate all thumbnails for week 42 manually:
REM for /f "tokens=*" %t in ('python KJZZ-db.py -q title -p') DO (for %d in (Mon Tue Wed Thu Fri Sat Sun) DO @python KJZZ-db.py -g week=42+title=%t+Day=%d --wordCloud --stopLevel 3 --max_words=1000 --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt --output kjzz)
REM (re)generate all thumbnails for week 42 automatically along with an html page:
echo python KJZZ-db.py --html 42 --autoGenerate --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
REM (re)generate all wordClouds and html for some weeks:
REM for /l %a in (40,1,48) DO @python KJZZ-db.py --html %a --autoGenerate --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt

REM REimport + REgenerate all misInfo values + regenerate html:
echo for /l %a in (40,1,48) DO @python KJZZ-db.py --import --folder kjzz\%a --force --gettext week=%a --misInformation --noMerge --noPics
echo for /l %a in (40,1,48) DO @python KJZZ-db.py --html %a

cmd /k
exit 99
goto :EOF


:loadCustomValues
IF EXIST %~n0_custom.cmd (
  call %~n0_custom.cmd
) ELSE (
  echo ::::::::::::::::::::::::::::::::::::::::::::::::::::::::>>%~n0_custom.cmd
  echo :: update the path where you installed Whisper-Faster ::>>%~n0_custom.cmd
  echo ::         DO NOT add double quotes anywhere          ::>>%~n0_custom.cmd
  echo ::::::::::::::::::::::::::::::::::::::::::::::::::::::::>>%~n0_custom.cmd
  echo set WhisperFasterPath=%WhisperFasterPath%>>%~n0_custom.cmd
  echo set WhisperBin=%WhisperBin%>>%~n0_custom.cmd
  echo :: Python path. I recommend using miniconda3 or similar>>%~n0_custom.cmd
  echo set PythonVenv=%PythonVenv%>>%~n0_custom.cmd
  echo :: model small gives the best results for radio broadcasts, but medium is recommended>>%~n0_custom.cmd
  echo :: latest distil-large-v3 seems the best as of early 2025>>%~n0_custom.cmd
  echo set model=%model%>>%~n0_custom.cmd
  echo :: delete mp3 processed>>%~n0_custom.cmd
  echo set deleteMp3=%deleteMp3%>>%~n0_custom.cmd
  echo :: delete logs>>%~n0_custom.cmd
  echo set deleteLogs=%deleteLogs%>>%~n0_custom.cmd
  echo :: do not reprocess same mp3>>%~n0_custom.cmd
  echo set reprocess=%reprocess%>>%~n0_custom.cmd
  echo :: import text files created>>%~n0_custom.cmd
  echo set import=%import%>>%~n0_custom.cmd
  echo :: build the html schedule page at the end, and calculate misInformation values>>%~n0_custom.cmd
  echo set html=%html%>>%~n0_custom.cmd
  echo set misInfo=%misInfo%>>%~n0_custom.cmd
  echo set language=%language%>>%~n0_custom.cmd
  echo ::::::::::::::::::::::::::::::::::::::::::::::::::::::::>>%~n0_custom.cmd
  
  echo Now edit this file: %~n0_custom.cmd
  echo And set the correct values for WhisperFasterPath and PythonVenv
  echo:
  type %~n0_custom.cmd
  notepad %~n0_custom.cmd
  pause
  exit
)
goto :EOF


:::::::::::::::::::::::::::::::::::::::::::::::::::: THE END ::::::::::::::::::::::::::::::::::::::::::::::::::::
::                                the below is just debug commands to play with









:compareSpeed
set compareFolder=E:\GPT\BiasBuster\assets\compare
set compareFile=KJZZ_2023-10-08_Sun_2300-2330_BBC World Service
pushd %compareFolder%

 :: 2024 - E:\GPT\Whisper-Faster\_models\
:: set existingModels=tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2
set WhisperFasterPath=E:\GPT\Whisper-Faster
set WhisperBin=whisper-faster.exe
REM 97 seconds  small
busybox time whisper-faster.exe     "%compareFile%.mp3" --language en --model small --output_format all --device cuda --output_dir small-wf-0.9.0
REM 86 seconds  small.en
busybox time whisper-faster.exe     "%compareFile%.mp3" --language en --model small.en --output_format all --device cuda --output_dir small.en-wf-0.9.0
REM 169 seconds medium
busybox time whisper-faster.exe     "%compareFile%.mp3" --language en --model medium --output_format all --device cuda --output_dir medium-wf-0.9.0
REM 145 seconds medium.en
busybox time whisper-faster.exe     "%compareFile%.mp3" --language en --model medium.en --output_format all --device cuda --output_dir medium.en-wf-0.9.0

:: 2025 - E:\GPT\Faster-Whisper-XXL\_models\
:: set existingModels=tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2 large-v3 large large-v3-turbo turbo distil-large-v2 distil-medium.en distil-small.en distil-large-v3
set WhisperFasterPath=E:\GPT\Faster-Whisper-XXL
set WhisperBin=faster-whisper-xxl.exe
REM 96 seconds small
busybox time faster-whisper-xxl.exe "%compareFile%.mp3" -pp --language en --model small --output_format all --device cuda --check_files --output_dir small-fw-xxl-1.1.0
REM 168 seconds medium
busybox time faster-whisper-xxl.exe "%compareFile%.mp3" -pp --language en --model medium --output_format all --device cuda --check_files --output_dir medium-fw-xxl-1.1.0
REM 65 seconds turbo = large-v3-turbo Note: 'large-v3' model may produce worse results than 'large-v2'!
busybox time faster-whisper-xxl.exe "%compareFile%.mp3" -pp --language en --model turbo --output_format all --device cuda --check_files --output_dir turbo-fw-xxl-1.1.0
REM 48 seconds 
busybox time faster-whisper-xxl.exe "%compareFile%.mp3" -pp --language en --model distil-large-v3 --output_format all --device cuda --check_files --output_dir distil-large-v3-fw-xxl-1.1.0


:: 1. join all lines and split by sentence
for %a in (small-wf-0.9.0 small-fw-xxl-1.1.0 medium-fw-xxl-1.1.0 turbo-fw-xxl-1.1.0 distil-large-v3-fw-xxl-1.1.0) DO (
  type "%a\%compareFile%.text" | busybox tr "\r\n" " " | busybox sed -r -e "s/\s+/ /g" -e "s/\. /\.\r\n/g" -e "s/(U\.N\.|U\.S\.A\.|U\.S\.|U\.K\.|Mr\.)\r\n/\1 /g" >%a.text
)

1. small-wf-0.9.0 vs small-fw-xxl-1.1.0
xxl: much better punctuation with much more commas, and correct spelling of acronyms: UN vs U.N. etc
xxl: very few sentences missing
0.9.0 miss many starting sentence words such as So, Do, etc
This is a no-brainer, switch to small-fw-xxl-1.1.0

2. small-fw-xxl-1.1.0 vs medium-fw-xxl-1.1.0
missing acronyms improvements from small, I do not trust it. Plus it's 2x slower.
Can be discarded

3. small-fw-xxl-1.1.0 vs turbo-fw-xxl-1.1.0
they are very similar, but:
- turbo hallucinates and added all these sentences at the end of the program, while only speechless music was playing:
  We'll be right back in the story.
  I'll see you.
  Thanks.
  And this is the first sentence.
- turbo misses long sentences replaced by ...

4. small-fw-xxl-1.1.0 vs  distil-large-v3-fw-xxl-1.1.0
- distil also lost the acronyms correct spelling
- aside from being 2x faster then small, it makes similar mistakes
- especially with forgein speakers with thick accent
- distil looks better overall but I am biased by the 2x speed improvement.



faster-whisper-xxl.exe
usage: faster-whisper-xxl.exe [-h] [--model MODEL] [--model_dir MODEL_DIR] [--device DEVICE] [--output_dir OUTPUT_DIR]
  [--output_format [{json,lrc,txt,text,vtt,srt,tsv,all} ...]]
  [--compute_type {default,auto,int8,int8_float16,int8_float32,int8_bfloat16,int16,float16,float32,bfloat16}]
  [--verbose VERBOSE] [--task {transcribe,translate}]
  [--language {af,am,ar,as,az,ba,be,bg,bn,bo,br,bs,ca,cs,cy,da,de,el,en,es,et,eu,fa,fi,fo,fr,gl,gu,ha,haw,he,hi,hr,ht,hu,hy,id,is,it,ja,jw,ka,kk,km,kn,ko,la,lb,ln,lo,lt,lv,mg,mi,mk,ml,mn,mr,ms,mt,my,ne,nl,nn,no,oc,pa,pl,ps,pt,ro,ru,sa,sd,si,sk,sl,sn,so,sq,sr,su,sv,sw,ta,te,tg,th,tk,tl,tr,tt,uk,ur,uz,vi,yi,yo,yue,zh,Afrikaans,Albanian,Amharic,Arabic,Armenian,Assamese,Azerbaijani,Bashkir,Basque,Belarusian,Bengali,Bosnian,Breton,Bulgarian,Burmese,Cantonese,Castilian,Catalan,Chinese,Croatian,Czech,Danish,Dutch,English,Estonian,Faroese,Finnish,Flemish,French,Galician,Georgian,German,Greek,Gujarati,Haitian,Haitian Creole,Hausa,Hawaiian,Hebrew,Hindi,Hungarian,Icelandic,Indonesian,Italian,Japanese,Javanese,Kannada,Kazakh,Khmer,Korean,Lao,Latin,Latvian,Letzeburgesch,Lingala,Lithuanian,Luxembourgish,Macedonian,Malagasy,Malay,Malayalam,Maltese,Mandarin,Maori,Marathi,Moldavian,Moldovan,Mongolian,Myanmar,Nepali,Norwegian,Nynorsk,Occitan,Panjabi,Pashto,Persian,Polish,Portuguese,Punjabi,Pushto,Romanian,Russian,Sanskrit,Serbian,Shona,Sindhi,Sinhala,Sinhalese,Slovak,Slovenian,Somali,Spanish,Sundanese,Swahili,Swedish,Tagalog,Tajik,Tamil,Tatar,Telugu,Thai,Tibetan,Turkish,Turkmen,Ukrainian,Urdu,Uzbek,Valencian,Vietnamese,Welsh,Yiddish,Yoruba}]
  [--language_detection_threshold LANGUAGE_DETECTION_THRESHOLD]
  [--language_detection_segments LANGUAGE_DETECTION_SEGMENTS] [--temperature TEMPERATURE] [0.0 ,,, 1.0]
  [--best_of BEST_OF] [--beam_size BEAM_SIZE] [--patience PATIENCE]
  [--length_penalty LENGTH_PENALTY] [--repetition_penalty REPETITION_PENALTY]
  [--no_repeat_ngram_size NO_REPEAT_NGRAM_SIZE] [--suppress_blank SUPPRESS_BLANK]
  [--suppress_tokens SUPPRESS_TOKENS] [--initial_prompt INITIAL_PROMPT] [--prefix PREFIX]
  [--condition_on_previous_text CONDITION_ON_PREVIOUS_TEXT]
  [--prompt_reset_on_temperature PROMPT_RESET_ON_TEMPERATURE]
  [--without_timestamps WITHOUT_TIMESTAMPS]
  [--max_initial_timestamp MAX_INITIAL_TIMESTAMP]
  [--temperature_increment_on_fallback TEMPERATURE_INCREMENT_ON_FALLBACK]
  [--compression_ratio_threshold COMPRESSION_RATIO_THRESHOLD]
  [--logprob_threshold LOGPROB_THRESHOLD] [--no_speech_threshold NO_SPEECH_THRESHOLD]
  [--word_timestamps WORD_TIMESTAMPS] [--highlight_words HIGHLIGHT_WORDS]
  [--prepend_punctuations PREPEND_PUNCTUATIONS]
  [--append_punctuations APPEND_PUNCTUATIONS] [--threads THREADS] [--version]
  [--vad_filter VAD_FILTER] [--vad_threshold VAD_THRESHOLD]
  [--vad_min_speech_duration_ms VAD_MIN_SPEECH_DURATION_MS]
  [--vad_max_speech_duration_s VAD_MAX_SPEECH_DURATION_S]
  [--vad_min_silence_duration_ms VAD_MIN_SILENCE_DURATION_MS]
  [--vad_speech_pad_ms VAD_SPEECH_PAD_MS]
  [--vad_window_size_samples VAD_WINDOW_SIZE_SAMPLES]
  [--vad_method {silero_v4_fw,silero_v5_fw,silero_v3,silero_v4,silero_v5,pyannote_v3,pyannote_onnx_v3,auditok,webrtc}]
  [--vad_dump] [--vad_dump_aud] [--vad_device VAD_DEVICE]
  [--hallucination_silence_threshold HALLUCINATION_SILENCE_THRESHOLD]
  [--hallucination_silence_th_temp {0.0,0.2,0.5,0.8,1.0}]
  [--clip_timestamps CLIP_TIMESTAMPS] [--max_new_tokens MAX_NEW_TOKENS]
  [--chunk_length CHUNK_LENGTH] [--hotwords HOTWORDS] [--batched]
  [--batch_size BATCH_SIZE] [--multilingual MULTILINGUAL] [--model_preload MODEL_PRELOAD]
  [--batch_recursive] [--beep_off] [--skip] [--checkcuda] [--print_progress] [--postfix]
  [--check_files] [--alt_writer_off] [--ignore_dupe_prompt IGNORE_DUPE_PROMPT]
  [--hallucinations_list_off] [--v3_offsets_off] [--reprompt REPROMPT]
  [--prompt_reset_on_no_end {0,1,2}] [--rehot] [--unmerged]
  [--japanese {blend,kanji,hiragana,katakana}] [--one_word {0,1,2}] [--sentence]
  [--standard] [--standard_asia] [--max_comma MAX_COMMA]
  [--max_comma_cent {20,30,40,50,60,70,80,90,100}] [--max_gap MAX_GAP]
  [--max_line_width MAX_LINE_WIDTH] [--max_line_count MAX_LINE_COUNT]
  [--min_dist_to_end {0,4,5,6,7,8,9,10,11,12}] [--ff_dump] [--ff_track {1,2,3,4,5,6}]
  [--ff_fc] [--ff_lc] [--ff_invert] [--ff_mp3] [--ff_sync] [--ff_rnndn_sh]
  [--ff_rnndn_xiph] [--ff_fftdn [0 - 97]] [--ff_tempo [0.5 - 2.0]] [--ff_gate]
  [--ff_speechnorm] [--ff_loudnorm] [--ff_silence_suppress noise duration]
  [--ff_lowhighpass] [--ff_mdx_kim2] [--mdx_chunk MDX_CHUNK] [--mdx_device MDX_DEVICE]
  [--diarize {pyannote_v3.0,pyannote_v3.1,reverb_v1,reverb_v2}]
  [--diarize_device DIARIZE_DEVICE] [--diarize_threads DIARIZE_THREADS] [--diarize_dump]
  [--speaker SPEAKER] [--num_speakers NUM_SPEAKERS] [--min_speakers MIN_SPEAKERS]
  [--max_speakers MAX_SPEAKERS] [--diarize_ff DIARIZE_FF] [--return_embeddings]
  [--diarize_only]
  audio [audio ...]

[2025-02-28 17:11:01.395] [ctranslate2] [thread 31016] [info] CPU: GenuineIntel (SSE4.1=true, AVX=true, AVX2=true, AVX512=false)
[2025-02-28 17:11:01.396] [ctranslate2] [thread 31016] [info]  - Selected ISA: AVX2
[2025-02-28 17:11:01.397] [ctranslate2] [thread 31016] [info]  - Use Intel MKL: true
[2025-02-28 17:11:01.398] [ctranslate2] [thread 31016] [info]  - SGEMM backend: MKL (packed: false)
[2025-02-28 17:11:01.398] [ctranslate2] [thread 31016] [info]  - GEMM_S16 backend: MKL (packed: false)
[2025-02-28 17:11:01.398] [ctranslate2] [thread 31016] [info]  - GEMM_S8 backend: MKL (packed: false, u8s8 preferred: true)
[2025-02-28 17:11:01.401] [ctranslate2] [thread 31016] [info] GPU #0: NVIDIA GeForce RTX 3090 (CC=8.6)
[2025-02-28 17:11:01.401] [ctranslate2] [thread 31016] [info]  - Allow INT8: true
[2025-02-28 17:11:01.401] [ctranslate2] [thread 31016] [info]  - Allow FP16: true (with Tensor Cores: true)
[2025-02-28 17:11:01.401] [ctranslate2] [thread 31016] [info]  - Allow BF16: true
[2025-02-28 17:11:03.951] [ctranslate2] [thread 31016] [info] Using CUDA allocator: cuda_malloc_async
[2025-02-28 17:11:04.169] [ctranslate2] [thread 31016] [info] Loaded model E:\GPT\Faster-Whisper-XXL\_models\faster-distil-whisper-large-v3 on device cuda:0
[2025-02-28 17:11:04.169] [ctranslate2] [thread 31016] [info]  - Binary version: 6
[2025-02-28 17:11:04.170] [ctranslate2] [thread 31016] [info]  - Model specification revision: 3
[2025-02-28 17:11:04.171] [ctranslate2] [thread 31016] [info]  - Selected compute type: int8_float16

