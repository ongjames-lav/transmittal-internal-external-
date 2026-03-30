from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


class Department(models.Model):
    """
    Department Model for standardized department selection
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Department name"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this department is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return self.name


class Profile(models.Model):
    """
    Extended User Profile Model
    
    This model extends Django's User model with additional fields required for
    the registration system. Uses OneToOneField to maintain a 1:1 relationship
    with the User model.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    ROLE_CHOICES = (
        ('user', 'Regular User'),
        ('custodian', 'Custodian'),
        ('admin', 'Administrator'),
    )
    
    # User relationship
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Link to Django User model"
    )
    
    # Contact information
    contact = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text="Phone number or contact number"
    )
    
    # Organization details
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='profiles',
        verbose_name="Department",
        help_text="Department"
    )
    
    company = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Company or organization name"
    )
    
    # Location information
    location = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="City or location"
    )
    
    address = models.TextField(
        blank=True,
        default='',
        help_text="Full address"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Registration status: pending, approved, or rejected"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="User registration date"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last profile update date"
    )
    
    # Admin notes (only visible to admin)
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal notes from admin"
    )
    
    # Role assignment
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        blank=True,
        verbose_name="User Role",
        help_text="User role: Regular User, Custodian, or Administrator"
    )
    
    # Assigned location for custodians
    assigned_location = models.ForeignKey(
        'transmittals.Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_staff',
        verbose_name="Assigned Location",
        help_text="Location assigned to this custodian (only for custodian role)"
    )

    # User Avatar
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="User profile image"
    )
    
    # Digital Signature
    digital_signature = models.ImageField(
        upload_to='signatures/',
        null=True,
        blank=True,
        help_text="User's digital signature for transmittal reports"
    )
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.user.username
    
    def get_full_name(self):
        """Return user's full name"""
        return f"{self.user.first_name} {self.user.last_name}".strip()
    
    def get_status_display_color(self):
        """Return color code for status (for UI purposes)"""
        colors = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger'
        }
        return colors.get(self.status, 'secondary')


@receiver(pre_save, sender=Profile)
def store_previous_status(sender, instance, **kwargs):
    """
    Store the previous status before saving to detect changes.
    """
    if instance.pk:  # Only for existing profiles
        try:
            old_profile = Profile.objects.get(pk=instance.pk)
            instance._original_status = old_profile.status
        except Profile.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create a Profile when a new User is created.
    This ensures every User has an associated Profile.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def handle_profile_status_change(sender, instance, created, **kwargs):
    """
    Signal receiver to handle Profile status changes and send notifications.
    
    When a user's registration status changes:
    - Send approval email when status changes to 'approved'
    - Send rejection email when status changes to 'rejected'
    - Update User.is_active based on approval status
    """
    # Import here to avoid circular imports
    from .email_utils import send_approval_email, send_rejection_email
    
    # Skip if this is a new profile being created
    if created:
        return
    
    # Get the previous state from database
    try:
        old_profile = Profile.objects.get(pk=instance.pk)
        old_status = old_profile.status
    except Profile.DoesNotExist:
        # Profile doesn't exist yet in database
        return
    
    # Re-fetch from database to get old values before this save
    # We need to check if status actually changed
    if hasattr(instance, '_original_status'):
        old_status = instance._original_status
        current_status = instance.status
        
        # Only send emails if status changed FROM pending
        if old_status != current_status and old_status == 'pending':
            user = instance.user
            
            # Status changed to APPROVED
            if current_status == 'approved':
                # Activate user account
                user.is_active = True
                user.save()
                
                # Send approval email
                send_approval_email(instance)
                print(f"[SUCCESS] Approval email sent to {user.email}")
            
            # Status changed to REJECTED
            elif current_status == 'rejected':
                # Deactivate user account
                user.is_active = False
                user.save()
                
                # Send rejection email
                send_rejection_email(instance)
                print(f"[INFO] Rejection email sent to {user.email}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal receiver to save Profile when User is saved.
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # Profile doesn't exist yet, will be created by create_user_profile signal
        pass

# =====================
# User Activity Tracking
# =====================

class UserActivity(models.Model):
    """Track user login/logout and page visits"""
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('page_view', 'Page View'),
        ('form_submit', 'Form Submit'),
        ('download', 'Download'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    page_url = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"


class ActiveSession(models.Model):
    """Track currently active user sessions"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_session')
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True)
    session_key = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - Active"
    
    def is_truly_online(self):
        """Check if user is truly online based on last activity timestamp"""
        from datetime import timedelta
        from django.conf import settings
        
        if not self.is_active:
            return False
        
        # Get session timeout from settings (SESSION_COOKIE_AGE in seconds)
        timeout_seconds = getattr(settings, 'SESSION_COOKIE_AGE', 300)
        timeout = timedelta(seconds=timeout_seconds)
        
        # Check if last activity is within the timeout window
        now = timezone.now()
        return (now - self.last_activity) <= timeout
    
    def get_session_duration(self):
        """Calculate how long user has been logged in"""
        from datetime import timedelta
        duration = timezone.now() - self.login_time
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"