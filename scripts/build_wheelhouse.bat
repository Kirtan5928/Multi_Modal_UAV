@echo off
setlocal
REM Build the offline wheelhouse at HOME (internet available).
REM Target: facility PC, Windows 64-bit, Python 3.14.

set PYVER=314
set PLATFORM=win_amd64
set OUTDIR=wheelhouse

echo Multi-Modal UAV - Offline Wheelhouse
echo Target: CP%PYVER% / %PLATFORM%

echo.
if not exist %OUTDIR% mkdir %OUTDIR%

echo [1/4] Checking Python 3.14...
py -3.14 --version
if errorlevel 1 exit /b 1

echo [2/4] Downloading PyTorch and torchvision from the configured index...
REM This currently uses the CPU index inherited from the original foundation.
REM We will change this only after the P2000 CUDA runtime is audited.
py -3.14 -m pip download torch torchvision --index-url https://download.pytorch.org/whl/cpu -d %OUTDIR% --python-version %PYVER% --platform %PLATFORM% --only-binary=:all:
if errorlevel 1 exit /b 1

echo [3/4] Downloading Ultralytics without dependency resolution...
py -3.14 -m pip download ultralytics --no-deps -d %OUTDIR% --python-version %PYVER% --platform %PLATFORM% --only-binary=:all:
if errorlevel 1 exit /b 1

echo [4/4] Downloading remaining dependencies...
py -3.14 -m pip download -r requirements.txt -d %OUTDIR% --python-version %PYVER% --platform %PLATFORM% --only-binary=:all:
if errorlevel 1 exit /b 1

dir /b %OUTDIR%\*.whl > versions.txt
powershell -ExecutionPolicy Bypass -File scripts\compute_hashes.ps1
if errorlevel 1 exit /b 1

echo WHEELHOUSE READY.
echo Review versions.txt and hashes.sha256 before transfer.
