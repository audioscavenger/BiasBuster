@echo OFF
pushd %~sdp0

::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: this script requires a compiled faster-whisper from https://github.com/guillaumekln/faster-whisper
:: or more simply, the binaries provided by https://github.com/Purfview/whisper-standalone-win
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: models will be automatically downloaded from https://huggingface.co/guillaumekln
:: available models:
::   tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2
:: for English radio broadcasts, small gives me the best results so far
::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:custom
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: update the path where you installed Whisper-Faster ::
::         DO NOT add double quotes there             ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
set WhisperFasterPath=E:\GPT\Whisper-Faster
:: optional: use this batch to also load Python command line
set stableROOT=E:\GPT\stable-diffusion-webui\venv\Scripts
::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:init
set PATH=%WhisperFasterPath%;%stableROOT%;%PATH%
set existingModels=tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2

:defaults
set LOG="%~dpn0.log"
set model=small
set delete=y
set reprocess=n

:prechecks
IF "%~1"=="" (
  call %stableROOT%\activate
  echo   python KJZZ-db.py -i -f kjzz\43
  echo   python KJZZ-db.py -q title
  echo   python KJZZ-db.py -q chunkLast10 -p
  echo   python KJZZ-db.py -g chunk="KJZZ_2023-10-13_Fri_1700-1730_All Things Considered" -v --wordCloud
  echo   python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
  echo   python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
  echo   python KJZZ-db.py -g title="All Things Considered" -v --wordCloud
  echo   python KJZZ-db.py -g title="BBC Newshour" -v --wordCloud
  echo   python KJZZ-db.py -g title="BBC World Business Report" -v --wordCloud
  echo   python KJZZ-db.py -g title="BBC World Service" -v --wordCloud
  echo   python KJZZ-db.py -g title="Fresh Air" -v --wordCloud
  echo   python KJZZ-db.py -g title="Here and Now" -v --wordCloud
  echo   python KJZZ-db.py -g title="Marketplace" -v --wordCloud
  echo   python KJZZ-db.py -g title="Morning Edition" -v --wordCloud
  echo   python KJZZ-db.py -g title="The Show" -v --wordCloud
  echo   python KJZZ-db.py -g week=42+Day=Mon+title="The Show" -v --wordCloud --stopLevel 2
  echo   python KJZZ-db.py -g week=42+Day=Mon+title="All Things Considered" --wordCloud --stopLevel 3 --show
  echo   python KJZZ-db.py -g week=42 --wordCloud --stopLevel 3 --show --max_words=10000
  echo   python KJZZ-db.py -g week=44 --wordCloud --stopLevel 5 --show --max_words=1000 --inputStopWordsFiles stopWords.ranks.nl.txt --inputStopWordsFiles  stopWords.Wordlist-Adjectives-All.txt
  echo   python KJZZ-db.py -g week=43+title="TED Radio Hour" --wordCloud --stopLevel 5 --show --max_words=1000 --inputStopWordsFiles stopWords.ranks.nl.txt --inputStopWordsFiles  stopWords.Wordlist-Adjectives-All.txt
  echo   python KJZZ-db.py -g week=42+title="Freakonomics" --misInformation --stopLevel 5 --show --max_words=1000 --inputStopWordsFiles stopWords.ranks.nl.txt --inputStopWordsFiles stopWords.Wordlist-Adjectives-All.txt
  echo   python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --graph pie --show
  echo   python KJZZ-db.py --gettext week=42+title="Morning Edition"+Day=Mon --misInformation --noMerge   --show
  echo   python KJZZ-db.py --html 42 --byChunk

  REM generate all thumbnails for week 42:
  REM for /f "tokens=*" %t in ('python KJZZ-db.py -q title -p') DO (for %d in (Mon Tue Wed Thu Fri Sat Sun) DO python KJZZ-db.py -g week=42+title=%t+Day=%d --wordCloud --stopLevel 4 --max_words=1000 --inputStopWordsFiles stopWords.ranks.nl.txt --inputStopWordsFiles stopWords.Wordlist-Adjectives-All.txt --output kjzz)

  cmd /k
  exit
)

set models=
for /f %%a in ('dir /b /od "%WhisperFasterPath%\_models\faster-whisper-*"') DO (
  for /f "tokens=3 delims=-" %%A in ("%%a") DO call set "models=%%models%% %%A"
)

IF NOT DEFINED models (
  echo WARNING: no models found under %WhisperFasterPath%\_models
  echo If it's the first time you start it, that's normal. If not, that's an error.
  echo:
  set models=%existingModels%
)

:main
title BiasBuster: transcribe sounds to text with Whisper-Faster

echo existingModels:      %existingModels%

IF NOT "%~1"=="" (
  echo availableModels:    %models%
  set /P     model=model?              [%model%] 
  set /P    delete=delete after?       [%delete%] 
  set /P reprocess=reprocess existing? [%reprocess%] 
)

IF EXIST "%~1\*" (
  REM :: first, address reprocess by deleting processed files
  IF /I %reprocess%==n (
    for %%a in ("%~1\*.mp3") DO (
      IF EXIST "%%~dpna.text" (
        IF /I %delete%==y (
          IF %%~za GTR 0 del /f /q "%%~a"
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
    REM busybox time whisper-faster "%%~a" --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%delete%"=="y" del /q "%%~a"
  REM )

  REM :: process folder recursively (faster):
  whisper-faster "%~1" --batch_recursive --language=en --model=%model% --output_format=all --device=cuda --output_dir="%~1"

  IF /I %delete%==y (
    for %%a in ("%~1\*.mp3") DO (
      IF EXIST "%%~dpna.text" del /f /q "%%~a"
    )
  )

  
) ELSE (
  REM :: list:
  for %%a in (%*) DO (
    echo busybox time whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa | busybox tee -a %LOG%
    busybox time whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%delete%"=="y" del /q "%%~a"
  )
)

REM no arguments? open a command prompt
IF     "%~1"=="" cmd /k


:import

IF NOT "%~1"=="" (
  IF EXIST "%~1\*.text" (
    del /f /q "%~1\*.log"
    call %stableROOT%\activate
    echo python KJZZ-db.py -i -f "%~1"
    python KJZZ-db.py -i -f "%~1"
  )
)


:end
timeout /t 10
