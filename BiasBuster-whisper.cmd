@echo OFF
pushd %~sdp0

::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: this script requires a compiled faster-whisper from https://github.com/guillaumekln/faster-whisper
:: or more simply, the binaries provided by https://github.com/Purfview/whisper-standalone-win
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: Models are downloaded automatically or can be downloaded manually from: https://huggingface.co/guillaumekln
:: Models go under %WhisperFasterPath%\_models\
:: available models as of November 2023:
::   tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2
:: for English radio broadcasts, small gives the best results so far
::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:custom
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: update the path where you installed Whisper-Faster ::
::         DO NOT add double quotes there             ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
set WhisperFasterPath=E:\GPT\Whisper-Faster
:: Python path. I recommend using miniconda3 or similar
set PythonVenv=E:\GPT\stable-diffusion-webui\venv\Scripts
:: model small gives the best results for radio broadcasts
set model=small
:: delete mp3 processed
set deleteMp3=y
:: delete logs
set deleteLogs=y
:: do not reprocess same mp3
set reprocess=n
:: import text files created
set import=y
:: build the html schedule page at the end
set html=y
::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:init
set PATH=%WhisperFasterPath%;%PythonVenv%;%PATH%
set existingModels=tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2

:defaults
set LOG="%~dpn0.log"
set htmlGen=
set busybox=

:prechecks
IF NOT EXIST "%WhisperFasterPath%"  echo ERROR: update WhisperFasterPath in this script & pause & exit 1
IF NOT EXIST "%PythonVenv%"         echo ERROR: update PythonVenv in this script & pause & exit 1
where busybox.exe >NUL 2>&1 && set busybox=busybox.exe

IF "%~1"=="" (
  call %PythonVenv%\activate
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
  echo   python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --graph pie --show
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
  
  cmd /k
  exit
)

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
if /I "%import%"=="y" set importTexts=--import --folder "%~1"
if /I "%html%"=="y"   set htmlGen=--html %~n1 --autoGenerate --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt

IF EXIST "%~1\*" (
  REM :: first, address reprocess by deleting processed files, in case the batch was interrupted for instance
  IF /I "%reprocess%"=="n" (
    for %%a in ("%~1\*.mp3") DO (
      IF EXIST "%%~dpna.text" (
        IF /I "%deleteMp3%"=="y" (
          echo deleting "%%~a" 1>&2
          del /f /q "%%~a"
        ) ELSE (
          echo ERROR: conflict: you don't want to reprocess %%a but also don't want to delete processed files.
          echo make up your mind.
          echo:
          pause
          exit /b 1
        )
      )
    )
  )

  REM :: process files in folder one by one (overhead induced as whisper will reload the model each time):
  REM for %%a in ("%~1\*.mp3") DO (
    REM echo busybox time whisper-faster "%%~a" --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa | busybox tee -a %LOG%
    REM busybox time whisper-faster "%%~a" --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%deleteMp3%"=="y" del /q "%%~a"
  REM )

  REM :: process folder recursively (faster):
  IF DEFINED busybox (
    echo busybox time whisper-faster "%~1" --batch_recursive --language=en --model=%model% --output_format=all --device=cuda --output_dir="%~1" | busybox tee -a %LOG%
    busybox time whisper-faster "%~1" --batch_recursive --language=en --model=%model% --output_format=all --device=cuda --output_dir="%~1"
  ) ELSE (
    echo whisper-faster "%~1" --batch_recursive --language=en --model=%model% --output_format=all --device=cuda --output_dir="%~1" >>%LOG%
    echo whisper-faster "%~1" --batch_recursive --language=en --model=%model% --output_format=all --device=cuda --output_dir="%~1"
    whisper-faster "%~1" --batch_recursive --language=en --model=%model% --output_format=all --device=cuda --output_dir="%~1"
  )

  IF /I %deleteMp3%==y (
    for %%a in ("%~1\*.mp3") DO (
      IF EXIST "%%~dpna.text" (
        echo deleting "%%~a" 1>&2
        del /f /q "%%~a"
      )
    )
  )

  
) ELSE (
  REM :: list:
  for %%a in (%*) DO (
    IF DEFINED busybox (
      echo busybox time whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa | busybox tee -a %LOG%
      busybox time whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%deleteMp3%"=="y" del /q "%%~a"
    ) ELSE (
      echo whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa >>%LOG%
      echo whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa
      whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%deleteMp3%"=="y" del /q "%%~a"
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
  echo to import + generate html: python KJZZ-db.py --import --folder "%~1" --html %~n1 --autoGenerate --inputStopWordsFiles data\stopWords.ranks.nl.uniq.txt --inputStopWordsFiles data\stopWords.Wordlist-Adjectives-All.txt
  goto :end
)

IF NOT "%~1"=="" (
  IF EXIST "%~1\*.text" (
    IF /I "%deleteLogs%=="y" (
      echo deleting %~1\*.log" 1>&2
      del /f /q "%~1\*.log"
    )
    call %PythonVenv%\activate
    echo python KJZZ-db.py %importTexts% %htmlGen%
    python KJZZ-db.py %importTexts% %htmlGen%
  )
)


:end
timeout /t 10
REM pause
