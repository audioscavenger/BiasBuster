@echo OFF
pushd %~sdp0

:custom
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: update the path where you installed Whisper-Faster ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
set WhisperFasterPath=E:\GPT\Whisper-Faster
::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:init
set PATH=%WhisperFasterPath%;%PATH%


:defaults
set LOG="%~dpn0.log"
set model=small
set delete=y


:main
title whispering BiasBuster broadcasts

IF NOT "%~1"=="" (
  pushd "%~sdp1"
  echo         small small.en medium
  set /P model=model?         [%model%] 
  set /P delete=delete after? [%delete%] 
)

IF EXIST "%~1\*" (
  REM :: folder:
  whisper-faster "%~1" --batch_recursive --language=en --model=%model% --output_format=all --device=cuda --output_dir="%~1"
  
  REM for %%a in ("%~1\*.mp3") DO (
    REM echo busybox time whisper-faster "%%~a" --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa | busybox tee -a %LOG%
    REM busybox time whisper-faster "%%~a" --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log" && IF /I "%delete%"=="y" del /q "%%~a"
  REM )
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
