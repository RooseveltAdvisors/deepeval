@echo off
setlocal enabledelayedexpansion

:: Parse command line arguments
set PORT=8501
set MAX_RETRIES=3

:parse_args
if "%~1"=="" goto :done_parsing
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--max-retries" (
    set MAX_RETRIES=%~2
    shift
    shift
    goto :parse_args
)
echo Unknown option: %~1
exit /b 1

:done_parsing

:: Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

:: Check Python version
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Error: Python 3.8 or higher is required
    exit /b 1
)

:: Navigate to project root
cd %~dp0..\..

:: Create results directory if it doesn't exist
if not exist .deepeval_results mkdir .deepeval_results

:: Check and activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Creating one...
    where uv >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        uv venv
        call .venv\Scripts\activate.bat
        uv pip install -e .
    ) else (
        python -m venv .venv
        call .venv\Scripts\activate.bat
        pip install -e .
    )
)

:: Install required packages if not already installed
python -c "import psutil" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installing required packages...
    where uv >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        uv pip install psutil
    ) else (
        pip install psutil
    )
)

:: Run the server with arguments
echo Starting DeepEval Dashboard...
python examples\dashboard\server.py --port %PORT% --max-retries %MAX_RETRIES% 