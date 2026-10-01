@echo off
setlocal
set LOG=install_log.txt
echo Install started: %date% %time% > %LOG%

echo [1/8] Verifying wheelhouse integrity...
powershell -ExecutionPolicy Bypass -File scripts\verify_hashes.ps1 >> %LOG% 2>&1
if errorlevel 1 goto :fail

echo [2/8] Checking Python 3.14 and 64-bit...
py -3.14 --version >> %LOG% 2>&1
if errorlevel 1 goto :fail
py -3.14 -c "import struct; assert struct.calcsize('P')*8==64; print('64-bit Python OK')" >> %LOG% 2>&1
if errorlevel 1 goto :fail

echo [3/8] Creating virtual environment...
py -3.14 -m venv venv >> %LOG% 2>&1
if errorlevel 1 goto :fail

echo [4/8] Installing entirely offline from wheelhouse...
venv\Scripts\python -m pip install --no-index --find-links=wheelhouse -r requirements.txt >> %LOG% 2>&1
if errorlevel 1 goto :fail
venv\Scripts\python -m pip install --no-index --find-links=wheelhouse torch torchvision >> %LOG% 2>&1
if errorlevel 1 goto :fail
venv\Scripts\python -m pip install --no-index --find-links=wheelhouse ultralytics --no-deps >> %LOG% 2>&1
if errorlevel 1 goto :fail

echo [5/8] Verifying core imports...
venv\Scripts\python -c "import yaml, dotenv, click, torch, torchvision, ultralytics, cv2, numpy, streamlit, reportlab" >> %LOG% 2>&1
if errorlevel 1 goto :fail

echo [6/8] Checking bundled FFmpeg and FFprobe...
if not exist tools\ffmpeg\bin\ffmpeg.exe goto :ffmpegfail
if not exist tools\ffmpeg\bin\ffprobe.exe goto :ffmpegfail
tools\ffmpeg\bin\ffprobe.exe -version >> %LOG% 2>&1

echo [7/8] Running media-inspection smoke test...
venv\Scripts\python -m src.media.inspect --help >> %LOG% 2>&1
if errorlevel 1 goto :fail

echo [8/8] INSTALL OK
echo INSTALL OK - %date% %time% >> %LOG%
goto :eof

:ffmpegfail
echo FFmpeg or FFprobe missing under tools\ffmpeg\bin
goto :fail

:fail
echo INSTALL FAILED - see %LOG%
exit /b 1
