@echo off
echo Starting PDD Tracking System Initialization...

mkdir pdd_tracking_system
cd pdd_tracking_system

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install django djangorestframework djangorestframework-simplejwt channels daphne pillow django-filter mysqlclient django-cors-headers

echo Creating Django project and applications...
django-admin startproject pdd_system .
python manage.py startapp accounts
python manage.py startapp job_orders
python manage.py startapp workflow
python manage.py startapp chat
python manage.py startapp notifications
python manage.py startapp core
python manage.py startapp reports

echo Saving requirements...
pip freeze > requirements.txt

echo Setup Complete!
pause
