@echo off
setlocal

REM Переходим в папку, где лежит этот bat-файл
cd /d "%~dp0"

REM Проверяем наличие виртуального окружения
if exist ".venv\Scripts\python.exe" (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

REM Запускаем программу и передаем ей все аргументы (например, -i и -o)
%PYTHON_CMD% -m src.main %*

endlocal