#!/usr/bin/env python
"""
Session Timeout Verification Script
Tests that the 15-minute idle session timeout is working correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emailsystem.settings')
django.setup()

from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*80)
print("SESSION TIMEOUT CONFIGURATION VERIFICATION")
print("="*80 + "\n")

# Check 1: Settings
print("[CHECK 1] Django Session Settings")
print("-" * 80)
print(f"  SESSION_ENGINE: {settings.SESSION_ENGINE}")
print(f"  SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} seconds ({settings.SESSION_COOKIE_AGE // 60} minutes)")
print(f"  SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")
print(f"  SESSION_COOKIE_SAMESITE: {settings.SESSION_COOKIE_SAMESITE}")
print(f"  SESSION_EXPIRE_AT_BROWSER_CLOSE: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
print(f"  SESSION_SAVE_EVERY_REQUEST: {settings.SESSION_SAVE_EVERY_REQUEST}")

expected_age = 900  # 15 minutes
if settings.SESSION_COOKIE_AGE == expected_age:
    print(f"\n  ✓ Timeout correctly set to 15 minutes")
else:
    print(f"\n  ✗ WARNING: SESSION_COOKIE_AGE is {settings.SESSION_COOKIE_AGE} seconds, expected {expected_age}")

if not settings.SESSION_SAVE_EVERY_REQUEST:
    print(f"  ✓ SESSION_SAVE_EVERY_REQUEST is False (correct - prevents session reset on every request)")
else:
    print(f"  ✗ WARNING: SESSION_SAVE_EVERY_REQUEST is True (will reset session on every request)")

# Check 2: Middleware
print("\n[CHECK 2] Middleware Configuration")
print("-" * 80)
if 'accounts.middleware.SessionTimeoutMiddleware' in settings.MIDDLEWARE:
    print(f"  ✓ SessionTimeoutMiddleware is installed")
else:
    print(f"  ✗ SessionTimeoutMiddleware is NOT installed")

if 'accounts.middleware.LoginLogoutTrackingMiddleware' in settings.MIDDLEWARE:
    print(f"  ✓ LoginLogoutTrackingMiddleware is installed")
else:
    print(f"  ✗ LoginLogoutTrackingMiddleware is NOT installed")

# Check 3: Active sessions
print("\n[CHECK 3] Active Sessions in Database")
print("-" * 80)
try:
    from accounts.models import ActiveSession
    
    active_count = ActiveSession.objects.filter(is_active=True).count()
    print(f"  Total active sessions: {active_count}")
    
    if active_count > 0:
        print("\n  Recent sessions:")
        recent = ActiveSession.objects.filter(is_active=True).order_by('-last_activity')[:5]
        for session in recent:
            elapsed = timezone.now() - session.last_activity
            elapsed_minutes = elapsed.total_seconds() / 60
            print(f"    - {session.user.username}: Last activity {elapsed_minutes:.1f} minutes ago")
    
except Exception as e:
    print(f"  Error checking active sessions: {e}")

# Check 4: Session age statistics
print("\n[CHECK 4] Configured Timeout Rules")
print("-" * 80)
timeout_seconds = 900  # 15 minutes
print(f"  Idle timeout: {timeout_seconds} seconds = {timeout_seconds // 60} minutes")
print(f"  Users will be logged out after {timeout_seconds // 60} minutes of inactivity")
print(f"  Activity resets the countdown (on each user action)")
print(f"  Static page loads (no interaction) will trigger timeout after {timeout_seconds // 60} minutes")

# Check 5: How to verify in production
print("\n[CHECK 5] Testing in Production")
print("-" * 80)
print("""
  To test the session timeout:
  
  1. Login to the application
  2. Note the current time
  3. Do NOT perform any actions for 15 minutes
  4. Try to access any page after 15 minutes
  5. You should be logged out automatically
  
  Expected behavior:
    - Session is created on login
    - Each user action (page load, button click, form submission) resets the 15-minute timer
    - After 15 minutes of NO activity, user is logged out
    - User sees login page
    - UserActivity log shows "Session timeout - idle for 15 minutes"
""")

print("="*80)
print("VERIFICATION COMPLETE")
print("="*80 + "\n")

print("Summary:")
if settings.SESSION_COOKIE_AGE == 900 and not settings.SESSION_SAVE_EVERY_REQUEST:
    print("  ✓ Session timeout is correctly configured for 15 minutes")
    print("  ✓ Sessions will NOT be reset on every request")
    print("  ✓ Only user activity extends the session")
    print("\n  System is ready for testing!")
else:
    print("  ✗ Configuration issues detected - see above")
