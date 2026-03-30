@echo off
REM ======================================================================
REM Transmittal Email Reminder Task
REM ======================================================================
REM This batch file runs the Django management command to send email reminders
REM for transmittals stuck in the same status for 5 days
REM
REM Usage: Schedule this file in Windows Task Scheduler to run daily at 9:00 AM
REM ======================================================================

setlocal enabledelayedexpansion

cd /d "c:\Users\CDC.MIS.OJT\Desktop\emailsystem"

REM Check if directory exists
if not exist "%cd%\logs" mkdir logs

REM Get current date and time
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)

REM Run the management command
echo [%mydate% %mytime%] Starting status reminder check... >> logs\reminder_task.log
python manage.py send_status_reminders >> logs\reminder_task.log 2>&1
echo [%mydate% %mytime%] Status reminder check completed >> logs\reminder_task.log
echo. >> logs\reminder_task.log

REM Exit without pause (remove 'pause' for unattended execution)
REM pause
