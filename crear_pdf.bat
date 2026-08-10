@echo off
setlocal

set "ROOT=%~dp0"
set "PANDOC=pandoc"
set "TYPST=typst"
set "TEMPLATE=%ROOT%templates\apuntes.typ"
set "OUTDIR="
set "KEEP_TYP=0"

if exist "%ROOT%bin\pandoc\pandoc.exe" (
  set "PANDOC=%ROOT%bin\pandoc\pandoc.exe"
) else if exist "%LOCALAPPDATA%\Pandoc\pandoc.exe" (
  set "PANDOC=%LOCALAPPDATA%\Pandoc\pandoc.exe"
)

if exist "%ROOT%bin\typst\typst.exe" (
  set "TYPST=%ROOT%bin\typst\typst.exe"
)

if "%~1"=="" (
  echo Uso: crear_pdf.bat archivo.md [carpeta_salida]
  echo.
  echo Ejemplo:
  echo   crear_pdf.bat ejemplos\prueba_apuntes.md
  exit /b 1
)

if not exist "%~1" (
  echo Error: no existe el archivo de entrada: %~1
  exit /b 1
)

if not "%~2"=="" (
  set "OUTDIR=%~2"
) else (
  set "OUTDIR=%~dp1"
)

if "%OUTDIR%"=="" set "OUTDIR=%CD%\"
if not exist "%OUTDIR%" mkdir "%OUTDIR%"

set "BASENAME=%~n1"
set "TYPFILE=%OUTDIR%%BASENAME%.typ"
set "PDFFILE=%OUTDIR%%BASENAME%.pdf"

"%PANDOC%" --version >nul 2>nul
if errorlevel 1 (
  echo Error: pandoc no esta disponible.
  echo Coloca pandoc.exe en "%ROOT%bin\pandoc\" o instalalo en PATH.
  exit /b 1
)

"%TYPST%" --version >nul 2>nul
if errorlevel 1 (
  echo Error: typst no esta disponible.
  echo Se generara solo el archivo Typst intermedio para comprobar Pandoc.
  "%PANDOC%" "%~1" -f markdown -t typst -s --template="%TEMPLATE%" -o "%TYPFILE%"
  if errorlevel 1 exit /b 1
  echo Archivo generado: "%TYPFILE%"
  echo Coloca typst.exe en "%ROOT%bin\typst\" o instalalo en PATH y vuelve a ejecutar este comando.
  exit /b 2
)

"%PANDOC%" "%~1" -f markdown -t typst -s --template="%TEMPLATE%" -o "%TYPFILE%"
if errorlevel 1 (
  echo Error al convertir Markdown a Typst.
  exit /b 1
)

"%TYPST%" compile "%TYPFILE%" "%PDFFILE%"
if errorlevel 1 (
  echo Error al compilar Typst a PDF.
  exit /b 1
)

if "%KEEP_TYP%"=="0" del "%TYPFILE%" >nul 2>nul

echo PDF generado: "%PDFFILE%"
endlocal
