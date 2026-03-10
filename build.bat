@echo off
setlocal

chcp 65001 >nul
cd /d "%~dp0"

set "APP_NAME=IDailyx"
set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
set "ICON_FILE=assets\icon.ico"
set "TK_INFO_BAT=%TEMP%\idailyx_tk_paths.bat"

echo ==============================
echo   Сборка %APP_NAME%
echo ==============================
echo.

where py >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Не найден Python launcher ^(py^).
    echo Установи Python для Windows и включи py launcher.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [1/8] Создаю виртуальное окружение...
    py -3.14 -m venv .venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать .venv
        pause
        exit /b 1
    )
) else (
    echo [1/8] Виртуальное окружение уже есть.
)

echo [2/8] Обновляю pip...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 (
    echo [ОШИБКА] Не удалось обновить pip
    pause
    exit /b 1
)

echo [3/8] Ставлю зависимости проекта...
"%VENV_PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости из requirements.txt
    pause
    exit /b 1
)

echo [4/8] Ставлю PyInstaller...
"%VENV_PYTHON%" -m pip install pyinstaller
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить PyInstaller
    pause
    exit /b 1
)

echo [5/8] Проверяю tkinter в текущем интерпретаторе...
"%VENV_PYTHON%" -c "import tkinter, _tkinter; print('tkinter ok')" >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] В текущем Python нет tkinter или _tkinter.
    echo Сначала нужно починить сам интерпретатор / окружение.
    pause
    exit /b 1
)

echo [6/8] Ищу Tcl/Tk папки...
"%VENV_PYTHON%" -c "import sys; from pathlib import Path; root = Path(sys.base_prefix) / 'tcl'; tcl = next((p for p in root.iterdir() if p.is_dir() and p.name.startswith('tcl8')), None); tk = next((p for p in root.iterdir() if p.is_dir() and p.name.startswith('tk8')), None); print('set \"TCL_DIR=' + (str(tcl) if tcl else '') + '\"'); print('set \"TK_DIR=' + (str(tk) if tk else '') + '\"')" > "%TK_INFO_BAT%"
if errorlevel 1 (
    echo [ОШИБКА] Не удалось определить пути к Tcl/Tk.
    pause
    exit /b 1
)

call "%TK_INFO_BAT%"

if not defined TCL_DIR (
    echo [ОШИБКА] Не удалось найти папку Tcl.
    pause
    exit /b 1
)

if not defined TK_DIR (
    echo [ОШИБКА] Не удалось найти папку Tk.
    pause
    exit /b 1
)

if not exist "%TCL_DIR%" (
    echo [ОШИБКА] Папка Tcl не существует:
    echo %TCL_DIR%
    pause
    exit /b 1
)

if not exist "%TK_DIR%" (
    echo [ОШИБКА] Папка Tk не существует:
    echo %TK_DIR%
    pause
    exit /b 1
)

echo Найдено:
echo TCL_DIR=%TCL_DIR%
echo TK_DIR=%TK_DIR%
echo.

echo [7/8] Очищаю старую сборку...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "%APP_NAME%.spec" del /f /q "%APP_NAME%.spec"

echo [8/8] Собираю приложение...
"%VENV_PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --name "%APP_NAME%" ^
    --icon "%ICON_FILE%" ^
    --add-data "assets;assets" ^
    --add-data "data;data" ^
    --add-data "%TCL_DIR%;_tcl_data" ^
    --add-data "%TK_DIR%;_tk_data" ^
    --collect-all customtkinter ^
    --collect-submodules tkinter ^
    --hidden-import=tkinter ^
    --hidden-import=tkinter.ttk ^
    --hidden-import=tkinter.filedialog ^
    --hidden-import=tkinter.messagebox ^
    --hidden-import=tkinter.simpledialog ^
    --hidden-import=_tkinter ^
    --hidden-import=PIL._tkinter_finder ^
    main.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка завершилась с ошибкой.
    pause
    exit /b 1
)

if exist "%TK_INFO_BAT%" del /f /q "%TK_INFO_BAT%"

echo.
echo ==============================
echo   Сборка завершена успешно
echo ==============================
echo.
echo Готовый exe:
echo dist\%APP_NAME%\%APP_NAME%.exe
echo.

pause
exit /b 0