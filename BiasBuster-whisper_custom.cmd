::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: update the path where you installed Whisper-Faster ::
::         DO NOT add double quotes there             ::
::::::::::::::::::::::::::::::::::::::::::::::::::::::::
REM set WhisperFasterPath=E:\GPT\Whisper-Faster
REM set WhisperBin=whisper-faster.exe
REM set existingModels=tiny tiny.en base base.en small small.en medium medium.en large-v1 large-v2

set WhisperFasterPath=E:\GPT\Faster-Whisper-XXL
set WhisperBin=faster-whisper-xxl.exe

:: Python path. I recommend using miniconda3 or similar
set PythonVenv=E:\GPT\stable-diffusion-webui\venv\Scripts
set PythonVenv=E:\GPT\sd.webui
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

::::::::::::::::::::::::::::::::::::::::::::::::::::::::
