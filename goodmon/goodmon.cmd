@echo off
setlocal
set "GM_PY="
if defined VIRTUAL_ENV if exist "%VIRTUAL_ENV%\Scripts\python.exe" set "GM_PY=%VIRTUAL_ENV%\Scripts\python.exe"
if not defined GM_PY if exist "%~dp0.venv\Scripts\python.exe" set "GM_PY=%~dp0.venv\Scripts\python.exe"
if defined GM_PY goto run
python -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>nul
if errorlevel 1 goto launcher
python "%~dp0goodmon" %*
exit /b %errorlevel%
:launcher
where py >nul 2>nul
if errorlevel 1 goto missing
py -3 "%~dp0goodmon" %*
exit /b %errorlevel%
:missing
echo goodmon: instale Python 3.10+ e siga goodmon/README.md. 1>&2
exit /b 2
:run
"%GM_PY%" "%~dp0goodmon" %*
exit /b %errorlevel%
