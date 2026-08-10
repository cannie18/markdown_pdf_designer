@echo off
setlocal

set "ROOT=%~dp0"
set "PYTHON=%ROOT%.venv\Scripts\pythonw.exe"

if not exist "%PYTHON%" (
  echo Error: no existe el entorno Python en "%ROOT%.venv".
  echo Crea el entorno e instala dependencias con:
  echo   python -m venv .venv
  echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

start "" /D "%ROOT%" "%PYTHON%" -m app.main %*

endlocal
