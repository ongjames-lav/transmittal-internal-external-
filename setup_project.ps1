Write-Host "Starting PDD Tracking System Initialization..." -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path "pdd_tracking_system" | Out-Null
Set-Location -Path "pdd_tracking_system"

Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

Write-Host "Activating virtual environment and installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install django djangorestframework djangorestframework-simplejwt channels daphne pillow django-filter mysqlclient django-cors-headers

Write-Host "Creating Django project and applications..." -ForegroundColor Yellow
django-admin startproject pdd_system .
python manage.py startapp accounts
python manage.py startapp job_orders
python manage.py startapp workflow
python manage.py startapp chat
python manage.py startapp notifications
python manage.py startapp core
python manage.py startapp reports

Write-Host "Saving requirements..." -ForegroundColor Yellow
pip freeze > requirements.txt

Write-Host "Setup Complete! The new project is ready." -ForegroundColor Green
