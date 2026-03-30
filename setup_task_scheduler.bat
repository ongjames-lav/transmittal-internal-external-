@echo off
REM
REM Task Scheduler Setup Script
REM Automatically creates the scheduled task for email system notifications
REM
REM REQUIRES: Administrator privileges
REM

echo.
echo ================================================================================
echo EMAIL SYSTEM - TASK SCHEDULER SETUP
echo ================================================================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script requires Administrator privileges!
    echo.
    echo Please run Command Prompt as Administrator and try again.
    echo.
    echo To run as Administrator:
    echo   1. Press Win + R
    echo   2. Type: cmd
    echo   3. Press Ctrl + Shift + Enter
    echo   4. Run this script again
    echo.
    pause
    exit /b 1
)

REM Configuration
set TASK_NAME=Email System Notifications
set TASK_DESCRIPTION=Automated notifications: auto-receive, status reminders, external transmittals
set BATCH_FILE=C:\Users\CDC.MIS.OJT\Desktop\emailsystem\run_notifications.bat
set WORKING_DIR=C:\Users\CDC.MIS.OJT\Desktop\emailsystem

echo [STEP 1] Verifying configuration...
echo   Task Name: %TASK_NAME%
echo   Batch File: %BATCH_FILE%
echo   Working Directory: %WORKING_DIR%
echo.

REM Check if batch file exists
if not exist "%BATCH_FILE%" (
    echo ERROR: Batch file not found at:
    echo   %BATCH_FILE%
    echo.
    echo Please verify the path and try again.
    echo.
    pause
    exit /b 1
)

echo   ✓ Batch file found
echo.

REM Check if task already exists
echo [STEP 2] Checking if task already exists...
schtasks /query /tn "%TASK_NAME%" >nul 2>&1

if %errorLevel% equ 0 (
    echo   Found existing task: %TASK_NAME%
    echo.
    echo   Do you want to replace it? (Y/N)
    set /p REPLACE=
    if /i not "%REPLACE%"=="Y" (
        echo   Task setup cancelled.
        echo.
        pause
        exit /b 0
    )
    echo   Deleting existing task...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
    echo   ✓ Existing task deleted
    echo.
)

echo [STEP 3] Creating scheduled task...
echo.
echo   Scheduling: Daily at 9:00 AM
echo   Repetition: Every 1 hour
echo   Privileges: Administrator
echo   Action: Run notifications batch file
echo.

REM Create the task
schtasks /create ^
    /tn "%TASK_NAME%" ^
    /tr "\"%BATCH_FILE%\"" ^
    /sc daily ^
    /st 09:00:00 ^
    /rl highest ^
    /f

if %errorLevel% equ 0 (
    echo   ✓ Task created successfully!
    echo.
) else (
    echo   ERROR: Failed to create task
    echo.
    pause
    exit /b 1
)

echo [STEP 4] Configuring task settings...
echo.

REM Set task to repeat every hour
schtasks /change ^
    /tn "%TASK_NAME%" ^
    /ru SYSTEM

if %errorLevel% equ 0 (
    echo   ✓ Task configured to run as SYSTEM
    echo.
)

echo ================================================================================
echo SETUP COMPLETE
echo ================================================================================
echo.
echo The scheduled task has been created successfully!
echo.
echo Task Details:
echo   Name: %TASK_NAME%
echo   Schedule: Daily at 9:00 AM, repeated every 1 hour
echo   Privileges: Administrator (SYSTEM account)
echo   Batch File: %BATCH_FILE%
echo.
echo Next Steps:
echo   1. Test the task: schtasks /run /tn "%TASK_NAME%"
echo   2. Check logs: type logs\notification_scheduler.log
echo   3. View task details in Task Scheduler GUI (taskschd.msc)
echo.
echo To view the task in Task Scheduler GUI:
echo   1. Press Win + R
echo   2. Type: taskschd.msc
echo   3. Find "Email System Notifications" in Task Scheduler Library
echo.
echo To view detailed task properties:
echo   1. Open Task Scheduler
echo   2. Right-click "Email System Notifications"
echo   3. Select "Properties"
echo.
pause
