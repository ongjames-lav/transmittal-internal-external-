#!/usr/bin/env python
"""
Test SMTP connection and send a test email.
"""
import os
import django
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

def test_smtp_connection():
    """Test raw SMTP connection"""
    print("=" * 70)
    print("SMTP CONNECTION TEST")
    print("=" * 70)
    
    print(f"\n📧 Email Configuration:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"   Use SSL: {settings.EMAIL_USE_SSL}")
    print(f"   Host User: {settings.EMAIL_HOST_USER}")
    print(f"   Default From: {settings.DEFAULT_FROM_EMAIL}")
    
    print(f"\n🔗 Testing SMTP connection...")
    try:
        if settings.EMAIL_USE_SSL:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        
        if settings.EMAIL_USE_TLS:
            server.starttls()
        
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("✅ SMTP connection successful!")
        
        # Send test email
        print(f"\n📤 Sending test email to ongjamesdaryl@gmail.com...")
        
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = 'ongjamesdaryl@gmail.com'
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Test Email - Transmittal Reminder System'
        msg['From'] = from_email
        msg['To'] = to_email
        
        text = """\
Hi,

This is a test email from the Transmittal Reminder System.

If you received this email, the SMTP configuration is working correctly.

Best regards,
Transmittal System
"""
        
        html = """\
<html>
  <body>
    <p>Hi,</p>
    <p>This is a test email from the Transmittal Reminder System.</p>
    <p>If you received this email, the SMTP configuration is working correctly.</p>
    <p>Best regards,<br>Transmittal System</p>
  </body>
</html>
"""
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        server.sendmail(from_email, [to_email], msg.as_string())
        print("✅ Test email sent successfully!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print("   - Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_django_send_mail():
    """Test Django send_mail function"""
    print("\n" + "=" * 70)
    print("DJANGO SEND_MAIL TEST")
    print("=" * 70)
    
    print(f"\n📤 Sending test email via Django...")
    
    try:
        result = send_mail(
            subject='Test Email - Django send_mail()',
            message='This is a test email from the Transmittal Reminder System using Django send_mail().',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['ongjamesdaryl@gmail.com'],
            html_message='<p>This is a test email from the Transmittal Reminder System using Django send_mail().</p>',
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ Django send_mail() successful!")
            return True
        else:
            print(f"⚠️  send_mail returned {result} (expected 1)")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n")
    smtp_ok = test_smtp_connection()
    django_ok = test_django_send_mail()
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"SMTP Connection: {'✅ PASS' if smtp_ok else '❌ FAIL'}")
    print(f"Django send_mail: {'✅ PASS' if django_ok else '❌ FAIL'}")
    print("=" * 70)
    
    if smtp_ok and django_ok:
        print("\n✅ All tests passed! Email should be sent successfully.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
