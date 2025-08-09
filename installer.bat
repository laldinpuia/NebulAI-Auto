@echo off
REM NebulAI Mining Suite Installer for Windows
REM Quick setup script for Windows systems

echo ================================================
echo     NebulAI Mining Suite Installer v1.0
echo ================================================
echo.
echo WARNING: This software violates NebulAI ToS!
echo Use at your own risk!
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause > nul

REM Check Python version
echo.
echo Checking Python version...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)
python --version
echo Python found!

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
python -m pip install --upgrade pip > nul 2>&1
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully

REM Create necessary files
echo.
echo Setting up configuration files...

REM Create .env from template if it doesn't exist
if not exist .env (
    if exist .env.template (
        copy .env.template .env > nul
        echo Created .env file from template
    ) else (
        (
            echo # NebulAI Mining Script Environment Variables
            echo SOLANA_PRIVATE_KEY=your_solana_private_key_here
            echo LOG_LEVEL=INFO
            echo TOKEN_REFRESH_HOURS=23
        ) > .env
        echo Created .env file
    )
    echo Please edit .env and add your SOLANA_PRIVATE_KEY
) else (
    echo .env file already exists
)

REM Create tokens.txt if it doesn't exist
if not exist tokens.txt (
    type nul > tokens.txt
    echo Created empty tokens.txt
    echo Please add your JWT tokens to tokens.txt ^(one per line^)
) else (
    echo tokens.txt already exists
)

REM Create convenience scripts
echo.
echo Creating launcher scripts...

REM Create run_miner.bat
(
    echo @echo off
    echo call venv\Scripts\activate.bat
    echo python nebulai_miner.py
    echo pause
) > run_miner.bat

REM Create run_monitor.bat
(
    echo @echo off
    echo call venv\Scripts\activate.bat
    echo python monitor.py
    echo pause
) > run_monitor.bat

REM Create run_health_check.bat
(
    echo @echo off
    echo call venv\Scripts\activate.bat
    echo python health_check.py
    echo pause
) > run_health_check.bat

REM Create run_token_utility.bat
(
    echo @echo off
    echo call venv\Scripts\activate.bat
    echo python token_utility.py %*
    echo pause
) > run_token_utility.bat

echo Launcher scripts created

REM Run health check
echo.
echo Running health check...
python health_check.py

REM Final instructions
echo.
echo ================================================
echo             Installation Complete!
echo ================================================
echo.
echo Next steps:
echo.
echo 1. Edit .env file and add your Solana private key:
echo    notepad .env
echo.
echo 2. Add your JWT tokens to tokens.txt:
echo    notepad tokens.txt
echo.
echo 3. Run the health check:
echo    run_health_check.bat
echo.
echo 4. Start mining:
echo    run_miner.bat
echo.
echo 5. Monitor performance (in another window):
echo    run_monitor.bat
echo.
echo 6. Manage tokens:
echo    run_token_utility.bat check
echo.
echo ================================================
echo.
echo Remember: This violates NebulAI's ToS!
echo Your account may be suspended!
echo.
pause