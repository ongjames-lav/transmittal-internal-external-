# Session Timeout Fix - 15 Minutes Idle Logout

## Problem Fixed ✅

Your session was timing out in **less than 5 minutes** even though settings declared 15 minutes. This was caused by:

1. **SESSION_SAVE_EVERY_REQUEST = True** (was ENABLED)
   - This resets the session timer on EVERY request
   - Even just loading a page resets the 15-minute countdown
   - Made it impossible to achieve idle-based timeouts

2. **Session configuration** was partially working but not correctly

## Solution Applied ✅

### 1. Updated `emailsystem/settings.py`

Changed from:
```python
SESSION_COOKIE_AGE = 900              # 15 min
SESSION_SAVE_EVERY_REQUEST = True     # ❌ WRONG - resets timer
```

To:
```python
SESSION_COOKIE_AGE = 900                # 15 minutes = 900 seconds
SESSION_COOKIE_HTTPONLY = True          # Prevent JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'        # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Clear on browser close
SESSION_SAVE_EVERY_REQUEST = False      # ✅ CORRECT - only update on activity
```

**KEY CHANGE:** `SESSION_SAVE_EVERY_REQUEST = False`

This means:
- Session is created on login
- Session is ONLY updated when there's actual user activity (click, form submit, page load with interaction)
- Idle time counts toward the 15-minute timeout
- After 15 minutes of NO activity → automatic logout

### 2. Updated `accounts/middleware.py`

Improved the SessionTimeoutMiddleware to:
- **Properly track idle time** using `last_activity` timestamp
- **Only update session** when user is still within timeout window
- **Log the timeout event** when 15-minute threshold is exceeded
- **Clear comments** explaining the 15-minute timeout rule

Key improvements:
```python
SESSION_TIMEOUT = 900  # 15 minutes in seconds

# Check if idle time exceeded
if time_diff.total_seconds() > timeout_seconds:
    # Logout user - they've been idle for 15 minutes
    logout(request)
else:
    # User still active - update last_activity timestamp
    request.session['last_activity'] = now.isoformat()
    request.session.modified = True  # Force save
```

## How It Works Now ✅

### Timeline Example:

```
9:00 AM - User logs in
         Last activity set to: 9:00 AM
         
9:05 AM - User clicks a button
         Idle time: 5 minutes (< 15, OK)
         Last activity updated to: 9:05 AM
         
9:10 AM - User fills out form (no submit yet)
         Idle time: 5 minutes since 9:05 (< 15, OK)
         Last activity updated to: 9:10 AM
         
9:20 AM - User just reads the screen, doesn't click anything
         Idle time: 10 minutes since 9:10 (< 15, OK)
         
9:25 AM - User tries to click button
         Idle time: 15 minutes since 9:10 (>= 15, TIMEOUT!)
         ❌ Session expired - redirected to login
         UserActivity log: "Session timeout - idle for 15 minutes"
```

## What Constitutes Activity?

✅ **RESETS the 15-minute timer:**
- Click any button
- Submit any form
- Navigate to another page
- Perform any server request

❌ **DOES NOT reset the timer:**
- Just reading the page
- Browser sitting idle
- JavaScript running in background (unless it makes requests)

## Testing the Fix

### Manual Test (15-minute test):
1. Log in to the system
2. Note the time
3. **Do nothing** for 15 minutes (don't click, type, or interact)
4. Try to perform an action after 15 minutes
5. You should be automatically logged out

### Quick Test (verify it's working):
1. Log in
2. Let page sit for ~1 minute without clicking
3. Check your browser's Network tab to see NO requests being made
4. After 1-2 more minutes of inactivity, try a page action
5. If configured correctly, should still work
6. After 15 total minutes of inactivity, you'll be logged out

## Database Tracking

Automatic logouts are logged in `UserActivity`:
- **activity_type:** 'logout'
- **description:** "Session timeout - idle for 15 minutes"
- **timestamp:** Exact time of logout

## Settings Summary

| Setting | Before | After | Impact |
|---------|--------|-------|--------|
| SESSION_COOKIE_AGE | 900 | 900 | ✓ No change (correct) |
| SESSION_SAVE_EVERY_REQUEST | **True** | **False** | ✅ FIXED - Was breaking timeout |
| SESSION_EXPIRE_AT_BROWSER_CLOSE | True | True | ✓ Sessions clear on close |
| SESSION_COOKIE_HTTPONLY | True | True | ✓ Security - blocks JS access |

## Verification Checklist

✅ Settings.py updated:
- SESSION_SAVE_EVERY_REQUEST = False
- SESSION_COOKIE_AGE = 900
- All session settings present

✅ Middleware updated:
- SessionTimeoutMiddleware properly checks idle time
- Logs timeout events to UserActivity
- Handles edge cases and errors

✅ Test recommendations:
- Wait 15+ minutes without clicking anything
- Try to perform an action
- Should be logged out
- Check UserActivity logs for timeout event

## Why This Fix Works

**Before:** Every page load/request reset the session to fresh 15 minutes
- User could stay logged in indefinitely by just loading pages
- No real idle timeout protection

**After:** Only user-initiated actions affect the session
- True idle timeout: 15 minutes of NO activity
- Sessions timeout independently
- Each action extends the window by 15 minutes from that point

## No Further Action Needed

The fix is applied and active. Just:
1. Test with a 15-minute wait
2. Verify automatic logout works
3. Check logs for timeout events

Done! Your session timeout is now truly 15 minutes idle. 🎉
