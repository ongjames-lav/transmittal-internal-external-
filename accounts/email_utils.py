"""
Email Utility Functions

This module handles all email operations for the system.
Uses Django's built-in email backend (Gmail SMTP or other free services).
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from .models import Profile


def send_registration_notification_to_admin(user, profile):
    """
    Send email notification to admin when a new user registers.
    
    Args:
        user: Django User object
        profile: Profile object with additional user details
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Prepare email context
        context = {
            'user': user,
            'profile': profile,
            'full_name': profile.get_full_name(),
            'registration_date': profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'approval_url': f"{settings.SITE_URL}/admin/accounts/profile/{profile.id}/change/"
        }
        
        # Render HTML email template
        html_message = render_to_string(
            'accounts/emails/admin_notification.html',
            context
        )
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        # Send email to admin
        email = EmailMultiAlternatives(
            subject=f'New User Registration - {user.username}',
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        return True
    
    except Exception as e:
        print(f"Error sending admin notification email: {str(e)}")
        return False


def send_registration_confirmation_to_user(user, profile):
    """
    Send welcome/confirmation email to the newly registered user.
    
    Args:
        user: Django User object
        profile: Profile object with additional user details
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        context = {
            'user': user,
            'profile': profile,
            'full_name': profile.get_full_name(),
            'username': user.username,
            'support_email': settings.SUPPORT_EMAIL
        }
        
        html_message = render_to_string(
            'accounts/emails/user_confirmation.html',
            context
        )
        plain_message = strip_tags(html_message)
        
        email = EmailMultiAlternatives(
            subject='Registration Confirmation - Welcome!',
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        return True
    
    except Exception as e:
        print(f"Error sending user confirmation email: {str(e)}")
        return False


def send_approval_email(profile):
    """
    Send approval notification email when admin approves a user.
    
    Args:
        profile: Profile object of approved user
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        context = {
            'user': profile.user,
            'full_name': profile.get_full_name(),
            'login_url': f"{settings.SITE_URL}/login/",
            'support_email': settings.SUPPORT_EMAIL
        }
        
        html_message = render_to_string(
            'accounts/emails/approval_notification.html',
            context
        )
        plain_message = strip_tags(html_message)
        
        email = EmailMultiAlternatives(
            subject='Registration Approved!',
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[profile.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        return True
    
    except Exception as e:
        print(f"Error sending approval email: {str(e)}")
        return False


def send_rejection_email(profile, reason=''):
    """
    Send rejection notification email when admin rejects a user.
    
    Args:
        profile: Profile object of rejected user
        reason: Optional reason for rejection
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        context = {
            'user': profile.user,
            'full_name': profile.get_full_name(),
            'reason': reason or 'Your registration could not be approved at this time.',
            'support_email': settings.SUPPORT_EMAIL
        }
        
        html_message = render_to_string(
            'accounts/emails/rejection_notification.html',
            context
        )
        plain_message = strip_tags(html_message)
        
        email = EmailMultiAlternatives(
            subject='Registration Status Update',
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[profile.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        return True
    
    except Exception as e:
        print(f"Error sending rejection email: {str(e)}")
        return False


def send_bulk_email(recipient_list, subject, html_content, plain_content=None):
    """
    Generic function to send bulk emails to multiple recipients.
    
    Args:
        recipient_list: List of email addresses
        subject: Email subject
        html_content: HTML formatted email content
        plain_content: Plain text email content (auto-generated if not provided)
    
    Returns:
        bool: True if all emails sent successfully
    """
    try:
        if plain_content is None:
            plain_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
    
    except Exception as e:
        print(f"Error sending bulk email: {str(e)}")
        return False
