import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("Starting email test...")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Default From: {settings.DEFAULT_FROM_EMAIL}")

try:
    result = send_mail(
        subject='Test Email',
        message='Test message',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['ongjamesdaryl@gmail.com'],
        fail_silently=False,
    )
    print(f"Email sent successfully! Result: {result}")
except Exception as e:
    print(f"Error sending email: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
