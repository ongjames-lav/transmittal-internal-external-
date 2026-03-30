"""
Views for User Registration and Profile Management

This module contains all views for:
- User registration
- Profile creation
- User dashboard
- Email notifications
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Profile, Department
from .forms import CustomUserCreationForm, ProfileForm, ProfileEditForm, UserProfileUpdateForm
from .email_utils import (
    send_registration_notification_to_admin,
    send_registration_confirmation_to_user,
    send_approval_email,
    send_rejection_email
)


def is_admin(user):
    """Check if user is an admin"""
    return user.is_staff or user.is_superuser


def index_redirect(request):
    """
    Redirects users based on authentication status.
    - Admins -> Admin Dashboard
    - Custodians -> Custodian Dashboard
    - Users -> User Dashboard
    - Guests -> Home Page
    """
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('accounts:admin_dashboard')
        # Check if user is custodian
        try:
            if request.user.profile.role == 'custodian':
                return redirect('transmittals:custodian_dashboard')
        except Profile.DoesNotExist:
            pass
        return redirect('accounts:dashboard')
    return redirect('accounts:login')


# =====================
# Registration Views
# =====================

@require_http_methods(["GET", "POST"])
def register(request):
    """
    User registration view.
    
    GET: Display registration form
    POST: Process registration form submission
    
    Flow:
    1. User fills out CustomUserCreationForm and ProfileForm
    2. System creates User and Profile objects
    3. Admin receives email notification
    4. User receives confirmation email
    5. User is redirected to confirmation page
    """
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Create user
            user = user_form.save(commit=False)
            user.is_active = True  # User account is active immediately
            user.save()
            
            # Retrieve the auto-created profile (created by signal)
            profile = user.profile
            profile.save()
            
            # Send emails
            admin_email_sent = send_registration_notification_to_admin(user, profile)
            user_email_sent = send_registration_confirmation_to_user(user, profile)
            
            messages.success(
                request,
                'Registration successful! Please check your email for confirmation. '
                'Your account will be activated once approved by the administrator.'
            )
            
            return redirect('accounts:registration_success')
        
        else:
            # Form validation failed
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    else:
        user_form = CustomUserCreationForm()
        profile_form = ProfileForm()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/register.html', context)


def registration_success(request):
    """
    Display registration success message.
    """
    return render(request, 'accounts/registration_success.html')


# =====================
# User Dashboard Views
# =====================

@never_cache
@login_required(login_url='accounts:login')
def user_dashboard(request):
    """
    User dashboard showing their registration status and transmittals.
    
    Shows:
    - User information
    - Profile details
    - Current approval status
    - Inbox items (transmittals sent to user)
    - Sent items (transmittals sent by user)
    - Received items (transmittals confirmed received by user)
    """
    from transmittals.models import Transmittal
    from accounts.models import Profile
    
    # Get or create profile for the user
    profile, created = Profile.objects.select_related('department', 'assigned_location').get_or_create(user=request.user)
    
    if created:
        # New profile was just created, populate default values
        profile.contact = ''
        profile.company = ''
        profile.location = ''
        profile.address = ''
        profile.save()
    
    current_department = profile.department if profile.department else None
    current_department_name = profile.department.name if profile.department else 'No department assigned'
    
    # Get inbox items (transmittals where user is recipient, in transit)
    inbox_items = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='in_transit'
    ).order_by('-sent_at')[:5]
    
    # Get arrived items (transmittals that have arrived to recipient)
    arrived_items = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='arrived'
    ).order_by('-sent_at')[:5]
    
    # Get received items (transmittals confirmed received by user)
    received_items = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='received'
    ).order_by('-received_at')[:5]
    
    # Get picked items (transmittals that have been picked by custodian)
    picked_items = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='picked'
    ).order_by('-sent_at')[:5]
    
    # Get counts
    inbox_count = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='in_transit'
    ).count()
    
    arrived_count = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='arrived'
    ).count()
    
    picked_count = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='picked'
    ).count()
    
    received_count = Transmittal.objects.filter(
        recipient_id=request.user.id,
        status='received'
    ).count()
    
    context = {
        'profile': profile,
        'user': request.user,
        'current_department': current_department,
        'current_department_name': current_department_name,
        'inbox_items': inbox_items,
        'arrived_items': arrived_items,
        'picked_items': picked_items,
        'received_items': received_items,
        'inbox_count': inbox_count,
        'arrived_count': arrived_count,
        'picked_count': picked_count,
        'received_count': received_count,
    }
    return render(request, 'accounts/user_dashboard.html', context)


@login_required(login_url='accounts:login')
def edit_profile(request):
    """
    View for users to edit their own profile information.
    Assigned location and department are locked and cannot be changed by the user.
    """
    # Get or create profile for the user
    from accounts.models import Profile
    profile, created = Profile.objects.select_related('department', 'assigned_location').get_or_create(user=request.user)
    
    if created:
        # New profile was just created, populate default values
        profile.contact = ''
        profile.company = ''
        profile.location = ''
        profile.address = ''
        profile.save()
    
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Preserve assigned_location (it's disabled in form, so won't be in cleaned_data)
            original_assigned_location = profile.assigned_location
            
            form.save()
            
            # Restore assigned_location if it was changed somehow
            profile.refresh_from_db()
            if profile.assigned_location != original_assigned_location:
                profile.assigned_location = original_assigned_location
                profile.save()
            
            messages.success(request, 'Your profile has been updated successfully!')
            
            # Redirect based on role
            user = request.user
            if is_admin(user):
                return redirect('accounts:admin_dashboard')
            try:
                if user.profile.role == 'custodian':
                    return redirect('transmittals:custodian_dashboard')
            except Profile.DoesNotExist:
                pass
            
            return redirect('accounts:dashboard')
    else:
        form = UserProfileUpdateForm(instance=profile)
        
    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'current_department': profile.department.name if profile.department else 'No department assigned'
    })


# =====================
# Admin Views
# =====================

@never_cache
@login_required(login_url='accounts:login')
def admin_dashboard(request):
    """
    Admin dashboard showing all registered users and their statuses.
    
    Features:
    - List all users
    - Filter by status (pending, approved, rejected)
    - Quick approval/rejection actions
    - View active user sessions
    - View user activity logs
    """
    # Check admin access
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('accounts:dashboard')
    
    from .models import ActiveSession, UserActivity
    
    profiles = Profile.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'None':
        profiles = profiles.filter(status=status_filter)
    elif status_filter == 'None':
        status_filter = None
    
    # Filter by department
    department_filter = request.GET.get('department')
    if department_filter and department_filter != 'None':
        profiles = profiles.filter(department_id=department_filter)
    
    # Filter by location
    location_filter = request.GET.get('location')
    if location_filter and location_filter != 'None':
        profiles = profiles.filter(assigned_location__name=location_filter)
        
    # Get unique values for filters
    departments = Department.objects.filter(is_active=True).values_list('id', 'name').order_by('name')
    locations = Profile.objects.filter(assigned_location__isnull=False).values_list('assigned_location__name', flat=True).distinct().order_by('assigned_location__name')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        profiles = profiles.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(department__name__icontains=search_query) |
            Q(location__icontains=search_query)
        ).distinct()
    
    stats = {
        'total': Profile.objects.count(),
        'pending': Profile.objects.filter(status='pending').count(),
        'approved': Profile.objects.filter(status='approved').count(),
        'rejected': Profile.objects.filter(status='rejected').count(),
        'active_sessions': ActiveSession.objects.filter(is_active=True).count(),
    }
    
    context = {
        'profiles': profiles,
        'stats': stats,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'location_filter': location_filter,
        'departments': departments,
        'locations': locations,
        'search_query': search_query,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@never_cache
@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:dashboard')
@require_http_methods(["GET", "POST"])
def admin_edit_user(request, profile_id):
    """
    Admin view to edit user profile and update approval status.
    
    GET: Display edit form
    POST: Process approval/rejection decision
    
    Features:
    - Edit user information
    - Approve/Reject registration
    - Add admin notes
    - Send corresponding notification emails
    """
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        
        if form.is_valid():
            old_status = profile.status
            profile = form.save(commit=False)
            profile.save()
            
            # Send appropriate email based on new status
            if old_status != profile.status:
                if profile.status == 'approved':
                    send_approval_email(profile)
                    messages.success(request, f'User {profile.user.username} approved! Notification email sent.')
                
                elif profile.status == 'rejected':
                    reason = request.POST.get('rejection_reason', '')
                    send_rejection_email(profile, reason)
                    messages.success(request, f'User {profile.user.username} rejected! Notification email sent.')
            
            else:
                messages.success(request, 'Profile updated successfully!')
            
            return redirect('accounts:admin_dashboard')
    
    else:
        form = ProfileEditForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'user': profile.user,
    }
    return render(request, 'accounts/admin_edit_user.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:dashboard')
def admin_approve_user(request, profile_id):
    """
    Quick approve action for admin.
    
    Updates status to 'approved' and sends notification email.
    """
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        profile.status = 'approved'
        profile.save()
        send_approval_email(profile)
        
        messages.success(request, f'User {profile.user.username} has been approved!')
        return redirect('accounts:admin_dashboard')
    
    context = {'profile': profile}
    return render(request, 'accounts/admin_confirm_action.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:dashboard')
def admin_reject_user(request, profile_id):
    """
    Quick reject action for admin.
    
    Updates status to 'rejected' and sends notification email with reason.
    """
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        profile.status = 'rejected'
        profile.admin_notes = reason
        profile.save()
        send_rejection_email(profile, reason)
        
        messages.success(request, f'User {profile.user.username} has been rejected!')
        return redirect('accounts:admin_dashboard')
    
    context = {'profile': profile}
    return render(request, 'accounts/admin_reject_user.html', context)


@never_cache
@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:dashboard')
def admin_view_user(request, profile_id):
    """
    Admin view to see detailed user information.
    """
    profile = get_object_or_404(Profile, id=profile_id)
    
    context = {
        'profile': profile,
        'user': profile.user,
    }
    return render(request, 'accounts/admin_view_user.html', context)


# =====================
# Login Views
# =====================

class AdminLoginView(LoginView):
    """
    Custom Login View for Admins.
    Redirects to admin dashboard on success.
    """
    template_name = 'accounts/admin_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return '/accounts/admin/dashboard/'
    
    def form_valid(self, form):
        """
        Security check: Ensure user is actually an admin
        """
        user = form.get_user()
        if not is_admin(user):
            messages.error(self.request, "Access Denied: You do not have administrator privileges.")
            return self.form_invalid(form)
        return super().form_valid(form)


class UserLoginView(LoginView):
    """
    Custom Login View for Users.
    Redirects based on user role:
    - Admin -> Admin Dashboard
    - Custodian -> Custodian Dashboard
    - User -> User Dashboard
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if is_admin(user):
            return '/accounts/admin/dashboard/'
        # Check if user is custodian
        try:
            if user.profile.role == 'custodian':
                return '/transmittals/custodian/dashboard/'
        except Profile.DoesNotExist:
            pass
        return '/accounts/dashboard/'

@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:dashboard')
@require_http_methods(["POST"])
def admin_delete_user(request, profile_id):
    """
    Admin action to delete a user.
    """
    profile = get_object_or_404(Profile, id=profile_id)
    user = profile.user
    username = user.username
    
    # Delete the user (this cascades to profile)
    user.delete()
    
    messages.success(request, f'User {username} has been deleted.')
    return redirect('accounts:admin_dashboard')


class SecureLogoutView(View):
    """
    Custom Logout View that allows GET (for link compatibility)
    and ensures session is completely cleared.
    """
    def get(self, request):
        from django.contrib.auth import logout
        from .models import ActiveSession, UserActivity
        
        try:
            # Log logout activity BEFORE logout is called
            if request.user.is_authenticated:
                user = request.user
                ip_address = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
                
                UserActivity.objects.create(
                    user=user,
                    activity_type='logout',
                    page_url='/accounts/logout/',
                    description='User logged out',
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                # Mark user as offline
                try:
                    active_session = ActiveSession.objects.get(user=user)
                    active_session.is_active = False
                    active_session.save()
                except (ActiveSession.DoesNotExist, Exception):
                    pass
            
            logout(request)
            messages.info(request, "You have been logged out securely.")
        except Exception:
            # If any error occurs, just ensure we redirect
            pass
            
        return redirect('accounts:login')

    def post(self, request):
        from django.contrib.auth import logout
        from .models import ActiveSession, UserActivity
        
        try:
            # Log logout activity BEFORE logout is called
            if request.user.is_authenticated:
                user = request.user
                ip_address = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
                
                UserActivity.objects.create(
                    user=user,
                    activity_type='logout',
                    page_url='/accounts/logout/',
                    description='User logged out',
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                # Mark user as offline
                try:
                    active_session = ActiveSession.objects.get(user=user)
                    active_session.is_active = False
                    active_session.save()
                except (ActiveSession.DoesNotExist, Exception):
                    pass
            
            logout(request)
            messages.info(request, "You have been logged out securely.")
        except Exception:
            # If any error occurs, just ensure we redirect
            pass
            
        return redirect('accounts:login')
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:dashboard')
def admin_batch_approve(request):
    """
    Batch approve multiple users at once.
    
    Expects POST request with list of profile IDs.
    """
    if request.method == 'POST':
        profile_ids = request.POST.getlist('profile_ids')
        
        if not profile_ids:
            messages.warning(request, 'No users selected for approval.')
            return redirect('accounts:admin_dashboard')
        
        # Get all profiles to approve
        profiles_to_approve = list(Profile.objects.filter(id__in=profile_ids, status='pending'))
        count = len(profiles_to_approve)
        
        if count == 0:
            messages.warning(request, 'No pending users found in your selection.')
            return redirect('accounts:admin_dashboard')
        
        # Approve all selected profiles in bulk
        Profile.objects.filter(id__in=[p.id for p in profiles_to_approve]).update(status='approved')
        
        # Send approval emails
        for profile in profiles_to_approve:
            # Update local instance status for email context if needed
            profile.status = 'approved'
            send_approval_email(profile)
        
        messages.success(request, f'Successfully approved {count} user{"s" if count != 1 else ""}!')
        # Redirect with query parameter
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(reverse('accounts:admin_dashboard') + '?status=pending')
    
    messages.error(request, 'Invalid request method.')
    return redirect('accounts:admin_dashboard')


@login_required(login_url='accounts:login')
def change_password(request):
    """
    Handle password change for logged-in users.
    
    POST request with:
    - current_password: User's current password
    - new_password: User's new password
    """
    import json
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.hashers import check_password
    from django.http import JsonResponse
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        
        # Verify current password
        if not check_password(current_password, request.user.password):
            return JsonResponse({
                'success': False,
                'current_password_error': 'Current password is incorrect.'
            })
        
        # Update password
        request.user.set_password(new_password)
        request.user.save()
        
        # Keep user logged in after password change
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Password changed successfully!'
        })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })


@never_cache
@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:dashboard')
@require_http_methods(["GET"])
def user_activity_logs(request):
    """
    Dedicated page showing active user sessions and user activity logs.
    Shows online/offline users and login/logout activities.
    """
    from .models import ActiveSession, UserActivity
    from django.contrib.auth.models import User
    from datetime import timedelta
    from django.conf import settings
    
    # Get timeout setting (default 5 minutes = 300 seconds)
    timeout_seconds = getattr(settings, 'SESSION_COOKIE_AGE', 300)
    timeout_threshold = timezone.now() - timedelta(seconds=timeout_seconds)
    
    # Get truly online sessions (is_active=True AND last_activity within timeout)
    active_sessions = ActiveSession.objects.filter(
        is_active=True,
        last_activity__gte=timeout_threshold
    ).select_related('user', 'user__profile').order_by('-login_time')
    
    # Get sessions that are marked active but have gone stale (offline)
    stale_sessions = ActiveSession.objects.filter(
        is_active=True,
        last_activity__lt=timeout_threshold
    ).select_related('user', 'user__profile').order_by('-last_activity')
    
    # Get IDs of truly online users
    online_user_ids = active_sessions.values_list('user_id', flat=True)
    
    # Get all users who are offline (not in truly active sessions)
    offline_users = User.objects.filter(
        is_active=True
    ).exclude(
        id__in=online_user_ids
    ).select_related('profile').order_by('-last_login')
    
    # Calculate statistics
    total_users = User.objects.filter(is_active=True).count()
    online_count = active_sessions.count()
    offline_count = total_users - online_count
    
    # Today's logins
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_logins = UserActivity.objects.filter(
        activity_type='login',
        timestamp__gte=today_start
    ).count()
    
    # Get recent login/logout activities
    login_logout_activities = UserActivity.objects.filter(
        activity_type__in=['login', 'logout']
    ).select_related('user', 'user__profile').order_by('-timestamp')[:20]
    
    # Activity filter
    activity_filter = request.GET.get('activity_type')
    if activity_filter and activity_filter != 'all':
        login_logout_activities = login_logout_activities.filter(activity_type=activity_filter)
    
    # User filter
    user_filter = request.GET.get('user')
    if user_filter:
        login_logout_activities = login_logout_activities.filter(user__id=user_filter)
    
    context = {
        'active_sessions': active_sessions,
        'offline_users': offline_users,
        'recent_activities': login_logout_activities,
        'activity_filter': activity_filter,
        'user_filter': user_filter,
        # Statistics
        'total_users': total_users,
        'online_count': online_count,
        'offline_count': offline_count,
        'todays_logins': todays_logins,
    }
    return render(request, 'accounts/user_activity_logs.html', context)


# ============================================================================
# PROTECTED MEDIA FILE SERVING
# ============================================================================

@login_required(login_url='accounts:login')
def serve_protected_media(request, filepath):
    """
    Serve protected media files that require authentication.
    
    Handles both external transmittal and internal transmittal media files.
    Unauthenticated users will be redirected to login.
    
    Files are served inline for preview:
    - PDFs preview in browser PDF viewer
    - Images (PNG, JPG, GIF, etc.) preview inline
    - Documents (DOCX, XLSX) preview inline
    - Other files can be downloaded
    """
    import os
    import mimetypes
    from django.conf import settings
    from django.http import FileResponse
    
    # Validate file path - prevent directory traversal
    if '..' in filepath or filepath.startswith('/'):
        return HttpResponse('Access Denied', status=403)
    
    # Determine which directory the file is in based on the request path
    if 'external_transmittals' in request.path:
        directory = 'external_transmittals'
    elif 'transmittals' in request.path:
        directory = 'transmittals'
    else:
        return HttpResponse('Access Denied', status=403)
    
    # Construct full path
    full_path = os.path.join(settings.MEDIA_ROOT, directory, filepath)
    
    # Verify file exists and is within MEDIA_ROOT
    try:
        full_path = os.path.abspath(full_path)
        media_root = os.path.abspath(settings.MEDIA_ROOT)
        
        if not full_path.startswith(media_root):
            return HttpResponse('Access Denied', status=403)
        
        if not os.path.exists(full_path):
            return HttpResponse('File Not Found', status=404)
        
        # Get filename and content type
        filename = os.path.basename(full_path)
        content_type, _ = mimetypes.guess_type(full_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # List of file types that should be previewed inline
        previewable_types = {
            'application/pdf',  # PDF
            'image/jpeg',  # JPG
            'image/png',  # PNG
            'image/gif',  # GIF
            'image/webp',  # WebP
            'image/tiff',  # TIFF
            'text/plain',  # TXT
            'text/html',  # HTML
            'application/msword',  # DOC
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # DOCX
            'application/vnd.ms-excel',  # XLS
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # XLSX
            'application/vnd.ms-powerpoint',  # PPT
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # PPTX
            'video/mp4',  # MP4
            'audio/mpeg',  # MP3
        }
        
        # Determine if file should be previewed inline or downloaded
        disposition = 'inline' if content_type in previewable_types else 'attachment'
        
        # Serve the file
        response = FileResponse(open(full_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Cache-Control'] = 'private, max-age=3600'
        return response
    
    except Exception as e:
        print(f"Error serving protected media: {e}")
        return HttpResponse('Access Denied', status=403)


