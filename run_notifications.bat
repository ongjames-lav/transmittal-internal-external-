@echo off
REM External Transmittal Deadline Notifications Script
REM Runs daily at 9:00 AM (weekdays only) via Windows Task Scheduler
REM
REM SETUP INSTRUCTIONS:
REM 1. Edit the paths below to match your installation
REM 2. Save this file as run_notifications.bat in your project root
REM 3. Create a scheduled task in Windows Task Scheduler pointing to this file
REM 4. See EXTERNAL_TRANSMITTAL_SCHEDULER_SETUP.md for detailed instructions

REM ============================================================================
REM CONFIGURATION - EDIT THESE PATHS
REM ============================================================================

REM Path to Python executable in virtual environment
SET PYTHON_PATH=C:\Users\CDC.MIS.OJT\Desktop\emailsystem\venv\Scripts\python.exe

REM Path to Django project root
SET PROJECT_ROOT=C:\Users\CDC.MIS.OJT\Desktop\emailsystem

REM Path to logs directory (will be created if doesn't exist)
SET LOGS_DIR=%PROJECT_ROOT%\logs

REM ============================================================================
REM SCRIPT EXECUTION
REM ============================================================================

REM Change to project directory
cd /d %PROJECT_ROOT%

REM Create logs directory if it doesn't exist
if not exist "%LOGS_DIR%" mkdir "%LOGS_DIR%"

REM Run the auto-receive transmittals command
REM Auto-receives transmittals that have been in 'picked' status for 3+ days
echo. >> "%LOGS_DIR%\notification_scheduler.log"
echo [%date% %time%] Starting Auto-Receive Transmittals Job... >> "%LOGS_DIR%\notification_scheduler.log"

%PYTHON_PATH% manage.py auto_receive_transmittals >> "%LOGS_DIR%\notification_scheduler.log" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Auto-receive job completed successfully. >> "%LOGS_DIR%\notification_scheduler.log"
) else (
    echo [%date% %time%] ERROR: Auto-receive job failed with exit code %ERRORLEVEL%. >> "%LOGS_DIR%\notification_scheduler.log"
)

REM Run the status reminders command
REM Sends reminders for transmittals stuck 5+ days in same status
echo. >> "%LOGS_DIR%\notification_scheduler.log"
echo [%date% %time%] Starting Status Reminders Job... >> "%LOGS_DIR%\notification_scheduler.log"

%PYTHON_PATH% manage.py send_status_reminders >> "%LOGS_DIR%\notification_scheduler.log" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Status reminders job completed successfully. >> "%LOGS_DIR%\notification_scheduler.log"
) else (
    echo [%date% %time%] ERROR: Status reminders job failed with exit code %ERRORLEVEL%. >> "%LOGS_DIR%\notification_scheduler.log"
)

REM Run the external transmittal notification command
echo. >> "%LOGS_DIR%\notification_scheduler.log"
echo [%date% %time%] Starting External Transmittal Notification Job... >> "%LOGS_DIR%\notification_scheduler.log"

%PYTHON_PATH% manage.py send_external_transmittal_notifications >> "%LOGS_DIR%\notification_scheduler.log" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Notification job completed successfully. >> "%LOGS_DIR%\notification_scheduler.log"
) else (
    echo [%date% %time%] ERROR: Notification job failed with exit code %ERRORLEVEL%. >> "%LOGS_DIR%\notification_scheduler.log"
)

REM ============================================================================
REM END OF SCRIPT
REM ============================================================================
