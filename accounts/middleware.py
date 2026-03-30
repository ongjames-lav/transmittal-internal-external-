from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from datetime import timedelta
from .models import UserActivity, ActiveSession


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to handle 15 minute idle session timeout.
    Logs out users who have been inactive for more than 15 minutes.
    
    How it works:
    1. On first request (login), sets 'last_activity' timestamp
    2. On each subsequent request, checks if 15 minutes have passed since last_activity
    3. If timeout is exceeded, user is logged out automatically
    4. If user is still active, 'last_activity' is updated to current time
    5. Only updates session if there's actual user activity (not on every request)
    """
    
    # 15 minute idle timeout in seconds
    SESSION_TIMEOUT = 900  # 15 * 60
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def process_request(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            last_activity = request.session.get('last_activity')
            
            # If this is the first request or no last_activity set, initialize it
            if not last_activity:
                request.session['last_activity'] = now.isoformat()
                return None
            
            # Parse the last activity timestamp
            try:
                last_activity_dt = timezone.datetime.fromisoformat(last_activity)
            except (ValueError, TypeError):
                # If we can't parse the timestamp, reset it
                request.session['last_activity'] = now.isoformat()
                return None
            
            # Check if session has expired due to inactivity
            time_diff = now - last_activity_dt
            timeout_seconds = self.SESSION_TIMEOUT
            
            if time_diff.total_seconds() > timeout_seconds:
                # Session has expired - log the user out
                from django.contrib.auth import logout
                
                # Log timeout logout
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='logout',
                    page_url=request.path,
                    description=f'Session timeout - idle for {timeout_seconds//60} minutes',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                logout(request)
                request.user = AnonymousUser()
                return None
            
            # User is still within timeout window - update last activity timestamp
            request.session['last_activity'] = now.isoformat()
            request.session.modified = True  # Ensure session is saved
            
            # Update active session record in database
            try:
                active_session = ActiveSession.objects.get(user=request.user)
                active_session.last_activity = now
                active_session.save(update_fields=['last_activity'])
            except ActiveSession.DoesNotExist:
                pass
        
        return None


class LoginLogoutTrackingMiddleware(MiddlewareMixin):
    """Track login and logout events"""
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def process_response(self, request, response):
        # Track successful login (after redirect)
        if request.path == '/accounts/login/' and request.method == 'POST' and response.status_code == 302:
            # This is a successful login
            from django.contrib.auth import get_user
            user = get_user(request)
            if user.is_authenticated:
                UserActivity.objects.create(
                    user=user,
                    activity_type='login',
                    page_url='/accounts/login/',
                    description='User logged in',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                
                # Create or update active session
                ActiveSession.objects.update_or_create(
                    user=user,
                    defaults={
                        'ip_address': self.get_client_ip(request),
                        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                        'session_key': request.session.session_key or '',
                        'is_active': True,
                    }
                )
        
        # Track logout
        if request.path == '/accounts/logout/' and response.status_code == 302:
            # Log the logout activity before session is cleared
            if request.user.is_authenticated:
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='logout',
                    page_url='/accounts/logout/',
                    description='User logged out',
                    ip_address=self.get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
            
            # Mark session as inactive
            try:
                ActiveSession.objects.filter(session_key=request.session.session_key).update(is_active=False)
            except:
                pass
        
        return response

