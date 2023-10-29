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
::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:init
set PATH=%WhisperFasterPath%;%PATH%
set existingModels=tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2

:defaults
set LOG="%~dpn0.log"
set model=small
set delete=y
set reprocess=n

:prechecks
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
  pushd "%~sdp1"
  echo availableModels:    %models%
  set /P     model=model?              [%model%] 
  set /P    delete=delete after?       [%delete%] 
  set /P reprocess=reprocess existing? [%reprocess%] 
)

IF EXIST "%~1\*" (
  REM :: first, address reprocess by deleting processed files
  IF /I %reprocess%==n (
    for %%a in ("%~1\*.mp3") DO (
      IF EXIST "%%~dpna.text" IF %%~za GTR 0 del /f /q "%%~a"
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

:end
timeout /t 10
