@echo OFF
pushd %~dp0

:init

set miniconda3=E:\GPT\miniconda3;E:\GPT\miniconda3\Library\mingw-w64\bin;E:\GPT\miniconda3\Library\usr\bin;E:\GPT\miniconda3\Library\bin;E:\GPT\miniconda3\Scripts;E:\GPT\miniconda3\bin;E:\GPT\miniconda3\condabin
REM set MinGW=E:\GPT\MinGW\bin
set VisualStudio2022=E:\GPT\VisualStudio\2022\BuildTools\VC\Tools\MSVC\14.36.32532\bin\HostX86\x86;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\VC\VCPackages;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\TestWindow;E:\GPT\VisualStudio\2022\BuildTools\MSBuild\Current\bin\Roslyn;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja;E:\GPT\VisualStudio\2022\BuildTools\Common7\IDE\VC\Linux\bin\ConnectionManagerExe

set GITHUB_ACTIONS=true
set pip_cache_dir=E:\GPT\miniconda3\envs\h2ogpt\cache-pip
set CMAKEPATH=E:\GPT\BiasBuster\cmake-3.27.6-windows-x86_64\bin
set PYTHONPATH=E:\GPT\miniconda3\envs\BiasBuster
set CUDA_HOME=E:\GPT\miniconda3\envs\BiasBuster
set NLTK_DATA=e:\gpt\miniconda3\envs\BiasBuster\nltk_data
set HF_HOME=e:\gpt\miniconda3\envs\BiasBuster\cache-huggingface

set PATH=%miniconda3%;%MinGW%;%PATH%
set PATH=%PATH%;%CMAKEPATH%
set PATH=E:\GPT\Whisper-Faster\;E:\GPT\miniconda3\envs\h2ogpt\Lib\site-packages\torch\lib\;%PATH%
set PATH=C:\Program Files\NVIDIA Corporation\Installer2\Display.PhysX.{6876BF95-ECDB-4BF4-88CF-F6A58BF50A6F}\files\Common\;%PATH%


:defaults
title whispering BiasBuster broadcasts
set ROOT=E:\GPT\stable-diffusion-webui
set LOG="%~dpn0.log"
set model=small


:main
REM call %ROOT%\venv\Scripts\activate
pushd %~sdp0

IF NOT "%~1"=="" (
  pushd "%~sdp1"
  echo         small small.en medium
  set /P model=model? [%model%] 
)

IF EXIST "%~1\*" (
  REM :: folder:
  for %%a in ("%~1\*.mp3") DO (
    echo busybox time whisper-faster "%%~a" --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa | busybox tee -a %LOG%
    busybox time whisper-faster "%%~a" --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log"
  )
) ELSE (
  REM :: list:
  for %%a in (%*) DO (
    echo busybox time whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa | busybox tee -a %LOG%
    busybox time whisper-faster %%a --language en --model %model% --output_format all --device cuda --output_dir %%~sdpa 2>"%%~a.%model%.log"
  )
)

REM no arguments? open a command prompt
IF     "%~1"=="" cmd /k

:end
timeout /t 10
