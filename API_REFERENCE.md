# Django Email System - Complete API Reference & System Guide

## 📖 Complete System Reference

### I. Project Structure Summary

```
emailsystem/
├── accounts/                          # Main application
│   ├── models.py                      # Database models
│   ├── views.py                       # Business logic
│   ├── forms.py                       # Form validation
│   ├── email_utils.py                 # Email functions
│   ├── admin.py                       # Admin interface
│   ├── urls.py                        # URL routing
│   ├── apps.py                        # App config
│   ├── tests.py                       # Unit tests
│   ├── migrations/                    # Database changes
│   └── templates/                     # HTML files
│       └── accounts/
│           ├── base.html              # Base template
│           ├── register.html          # Registration form
│           ├── login.html             # Login form
│           ├── user_dashboard.html    # User profile
│           ├── admin_dashboard.html   # Admin panel
│           ├── admin_edit_user.html   # Edit user
│           ├── admin_view_user.html   # View user
│           ├── registration_success.html
│           └── emails/                # Email templates
│               ├── admin_notification.html
│               ├── user_confirmation.html
│               ├── approval_notification.html
│               └── rejection_notification.html
│
├── emailsystem/                       # Project settings
│   ├── settings.py                    # Configuration
│   ├── urls.py                        # Main routing
│   ├── asgi.py                        # ASGI server
│   └── wsgi.py                        # WSGI server
│
├── templates/                         # Global templates
│   └── home.html                      # Homepage
│
├── manage.py                          # Django CLI
├── db.sqlite3                         # Database
├── requirements.txt                   # Dependencies
├── QUICK_START.md                     # Getting started
├── SYSTEM_DOCUMENTATION.md            # Full documentation
└── ARCHITECTURE.md                    # System design
```

---

## 📋 Models API Reference

### User Model

**Location:** Django built-in (django.contrib.auth.models)

**Fields:**
```python
User
├── id (AutoField)
├── username (CharField, unique)
├── email (EmailField)
├── first_name (CharField)
├── last_name (CharField)
├── password (CharField, hashed)
├── is_active (BooleanField)
├── is_staff (BooleanField)
├── is_superuser (BooleanField)
├── last_login (DateTimeField)
└── date_joined (DateTimeField)
```

**Methods:**
```python
User.objects.create_user(username, email, password)
User.objects.create_superuser(username, email, password)
user.set_password(raw_password)
user.check_password(raw_password)
user.is_authenticated
user.get_full_name()
```

---

### Profile Model

**Location:** accounts/models.py

**Fields:**
```python
Profile
├── id (AutoField, PK)
├── user (OneToOneField → User)
│   └── Related name: 'profile'
├── contact (CharField, max_length=20)
├── company (CharField, max_length=100)
├── department (CharField, max_length=100)
├── location (CharField, max_length=100)
├── address (TextField)
├── status (CharField, choices)
│   ├── 'pending' (default)
│   ├── 'approved'
│   └── 'rejected'
├── admin_notes (TextField, blank, null)
├── created_at (DateTimeField, auto_now_add)
└── updated_at (DateTimeField, auto_now)
```

**Methods:**
```python
profile.get_full_name()              # Returns "First Last"
profile.get_status_display()         # Returns "Pending"
profile.get_status_display_color()   # Returns color code
```

**Query Examples:**
```python
# Get all profiles
Profile.objects.all()

# Get pending approvals
Profile.objects.filter(status='pending')

# Get by user
Profile.objects.get(user=request.user)

# Get by username
Profile.objects.get(user__username='john')

# Filter by company
Profile.objects.filter(company='Acme Corp')

# Count by status
Profile.objects.filter(status='approved').count()
```

---

## 📝 Forms API Reference

### CustomUserCreationForm

**Location:** accounts/forms.py

**Purpose:** Register new users

**Fields:**
```
- username (CharField) → Validates unique
- email (EmailField) → Validates unique, format
- first_name (CharField, required)
- last_name (CharField, required)
- password1 (PasswordInput) → Validates min 8 chars
- password2 (PasswordInput) → Must match password1
```

**Usage:**
```python
if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
        user = form.save()
        # user.password is hashed automatically
```

**Validation Methods:**
```python
clean_email()       # Check uniqueness
clean_username()    # Check uniqueness
clean_password1()   # Check min length
clean()             # Check password match
```

---

### ProfileForm

**Location:** accounts/forms.py

**Purpose:** Collect organization information

**Fields:**
```
- contact (CharField, required)
- company (CharField, required)
- department (CharField, required)
- location (CharField, required)
- address (Textarea, required)
```

**Usage:**
```python
form = ProfileForm(request.POST)
if form.is_valid():
    profile = form.save(commit=False)
    profile.user = user
    profile.save()
```

---

### ProfileEditForm

**Location:** accounts/forms.py

**Purpose:** Admin editing of profiles

**Fields:**
```
- first_name (CharField) → Sync with User
- last_name (CharField) → Sync with User
- email (EmailField) → Sync with User
- status (ChoiceField)
  ├── 'pending'
  ├── 'approved'
  └── 'rejected'
- admin_notes (Textarea)
```

**Usage:**
```python
form = ProfileEditForm(request.POST, instance=profile)
if form.is_valid():
    form.save()  # Updates both Profile and User
```

---

## 🔧 Views API Reference

### Authentication Views

**Location:** accounts/urls.py (using Django built-in)

```python
# Login
URL: /accounts/login/
Method: GET, POST
Template: accounts/login.html
Redirects: dashboard (on success)

# Logout
URL: /accounts/logout/
Method: POST
Redirects: home page

# Password Reset
URL: /accounts/password-reset/
Method: GET, POST
Template: accounts/password_reset.html

# Password Reset Confirm
URL: /accounts/password-reset/<uidb64>/<token>/
Method: GET, POST
Template: accounts/password_reset_confirm.html
```

---

### Registration Views

**register(request)**
```
URL: /accounts/register/
Method: GET, POST
Requires Auth: No

GET Response:
  - Display registration form
  - Template: accounts/register.html
  - Context: user_form, profile_form

POST Response (Valid):
  - Create User and Profile
  - Send admin notification email
  - Send user confirmation email
  - Redirect: registration_success
  - Message: Success notification

POST Response (Invalid):
  - Re-render form
  - Display error messages
  - HTTP Status: 200
```

**registration_success(request)**
```
URL: /accounts/registration-success/
Method: GET
Requires Auth: No

Response:
  - Display success message
  - Template: accounts/registration_success.html
  - Message: "Check your email"
```

---

### User Views

**user_dashboard(request)**
```
URL: /accounts/dashboard/
Method: GET
Requires Auth: Yes (login_required)

Response:
  - Display user profile
  - Show all user details
  - Display current status
  - Show admin notes if rejected
  - Template: accounts/user_dashboard.html
  - Context: profile, user

Access:
  - Only authenticated users
  - Self data (can view own profile only)
```

---

### Admin Views

**admin_dashboard(request)**
```
URL: /accounts/admin/dashboard/
Method: GET
Requires Auth: Yes (is_staff)

Parameters:
  - status (optional): Filter by status
  - search (optional): Search by username/email

Response:
  - Display all users
  - Show statistics (total, pending, approved, rejected)
  - Filter options
  - Search results
  - Template: accounts/admin_dashboard.html
  - Context: profiles, stats, status_filter, search_query

Example:
  GET /accounts/admin/dashboard/?status=pending&search=john
```

**admin_view_user(request, profile_id)**
```
URL: /accounts/admin/user/<id>/
Method: GET
Requires Auth: Yes (is_staff)

Parameters:
  - profile_id (int): Profile ID

Response:
  - Display detailed user information
  - All registration details
  - Admin notes
  - Status
  - Template: accounts/admin_view_user.html
  - Context: profile, user
```

**admin_edit_user(request, profile_id)**
```
URL: /accounts/admin/user/<id>/edit/
Method: GET, POST
Requires Auth: Yes (is_staff)

GET Response:
  - Display edit form
  - Pre-populate user info
  - Template: accounts/admin_edit_user.html

POST Response (Valid):
  - Update Profile
  - Update User (if email/name changed)
  - If status changed:
    ├─ If approved: Send approval email
    └─ If rejected: Send rejection email
  - Redirect: admin_dashboard
  - Message: Success notification

POST Response (Invalid):
  - Re-render form with errors
```

**admin_approve_user(request, profile_id)**
```
URL: /accounts/admin/user/<id>/approve/
Method: GET, POST
Requires Auth: Yes (is_staff)

GET Response:
  - Display confirmation page
  - Template: accounts/admin_confirm_action.html

POST Response:
  - Update: status = 'approved'
  - Send: Approval email to user
  - Redirect: admin_dashboard
  - Message: "User approved!"
```

**admin_reject_user(request, profile_id)**
```
URL: /accounts/admin/user/<id>/reject/
Method: GET, POST
Requires Auth: Yes (is_staff)

GET Response:
  - Display rejection form
  - Text area for rejection reason
  - Template: accounts/admin_reject_user.html

POST Response:
  - Update: status = 'rejected'
  - Update: admin_notes = reason
  - Send: Rejection email to user
  - Redirect: admin_dashboard
  - Message: "User rejected!"
```

---

## 📧 Email Functions API Reference

**Location:** accounts/email_utils.py

### send_registration_notification_to_admin()

```python
send_registration_notification_to_admin(user, profile)

Parameters:
  - user (User): User object
  - profile (Profile): Profile object

Returns: bool (True if sent, False if error)

Email Details:
  - To: settings.ADMIN_EMAIL
  - Subject: "New User Registration - [username]"
  - Template: admin_notification.html
  - Contains: All registration details + approval link
```

**Usage:**
```python
from accounts.email_utils import send_registration_notification_to_admin

send_registration_notification_to_admin(user, profile)
```

---

### send_registration_confirmation_to_user()

```python
send_registration_confirmation_to_user(user, profile)

Parameters:
  - user (User): User object
  - profile (Profile): Profile object

Returns: bool (True if sent, False if error)

Email Details:
  - To: user.email
  - Subject: "Registration Confirmation - Welcome!"
  - Template: user_confirmation.html
  - Contains: Thank you message, next steps, timeline
```

---

### send_approval_email()

```python
send_approval_email(profile)

Parameters:
  - profile (Profile): Profile object

Returns: bool

Email Details:
  - To: profile.user.email
  - Subject: "Registration Approved!"
  - Template: approval_notification.html
  - Contains: Approval notification, login link, instructions
```

---

### send_rejection_email()

```python
send_rejection_email(profile, reason='')

Parameters:
  - profile (Profile): Profile object
  - reason (str, optional): Rejection reason

Returns: bool

Email Details:
  - To: profile.user.email
  - Subject: "Registration Status Update"
  - Template: rejection_notification.html
  - Contains: Rejection notification, reason, support contact
```

---

### send_bulk_email()

```python
send_bulk_email(recipient_list, subject, html_content, plain_content=None)

Parameters:
  - recipient_list (list): Email addresses
  - subject (str): Email subject
  - html_content (str): HTML formatted content
  - plain_content (str, optional): Plain text content

Returns: bool

Usage:
  from accounts.email_utils import send_bulk_email
  
  recipients = ['user1@example.com', 'user2@example.com']
  send_bulk_email(recipients, 'Subject', '<h1>Hello</h1>')
```

---

## ⚙️ Settings Configuration Reference

**Location:** emailsystem/settings.py

### Email Configuration

```python
# Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail SMTP Settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Email Addresses
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
ADMIN_EMAIL = 'admin@example.com'
SUPPORT_EMAIL = 'support@example.com'

# Site Configuration
SITE_URL = 'http://localhost:8000'
```

### Alternative Email Backends

```python
# Console Backend (Testing - prints to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# File Backend (Testing - saves to files)
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

# Memory Backend (Testing - stores in memory)
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

### Authentication Settings

```python
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'
```

---

## 🌐 URL Patterns Reference

**Location:** accounts/urls.py

### Complete URL Mapping

```
Pattern                                    View Function
────────────────────────────────────────  ──────────────────────────
/accounts/register/                       register()
/accounts/registration-success/           registration_success()
/accounts/login/                          LoginView (Django built-in)
/accounts/logout/                         LogoutView (Django built-in)
/accounts/password-reset/                 PasswordResetView
/accounts/password-reset/done/            PasswordResetDoneView
/accounts/password-reset/<uidb>/<token>/  PasswordResetConfirmView
/accounts/password-reset/complete/        PasswordResetCompleteView
/accounts/dashboard/                      user_dashboard()
/accounts/admin/dashboard/                admin_dashboard()
/accounts/admin/user/<id>/                admin_view_user()
/accounts/admin/user/<id>/edit/           admin_edit_user()
/accounts/admin/user/<id>/approve/        admin_approve_user()
/accounts/admin/user/<id>/reject/         admin_reject_user()
```

---

## 🔐 Permissions & Access Control

### User Access Matrix

```
Page/Feature              Anonymous  User  Admin
─────────────────────────────────────────────────
Home Page                   ✓        ✓     ✓
Register                    ✓        ✗     ✗
Login                       ✓        ✗     ✗
User Dashboard              ✗        ✓     ✓
Admin Dashboard             ✗        ✗     ✓
Admin Edit User             ✗        ✗     ✓
Admin Approve/Reject        ✗        ✗     ✓
Django Admin Panel          ✗        ✗     ✓
```

### Decorators Used

```python
# User must be logged in
@login_required(login_url='accounts:login')
def user_dashboard(request):
    pass

# User must be staff/admin
@user_passes_test(is_admin, login_url='accounts:dashboard')
def admin_dashboard(request):
    pass

# Only allow specific HTTP method
@require_http_methods(["GET", "POST"])
def register(request):
    pass
```

---

## 📊 Database Query Examples

### User Queries

```python
# Get all users
from django.contrib.auth.models import User
User.objects.all()

# Get user by username
User.objects.get(username='john')

# Get user by email
User.objects.get(email='john@example.com')

# Create new user
user = User.objects.create_user(
    username='john',
    email='john@example.com',
    password='SecurePass123',
    first_name='John',
    last_name='Doe'
)

# Update user
user.first_name = 'Jane'
user.save()

# Delete user (cascades to profile)
user.delete()
```

### Profile Queries

```python
from accounts.models import Profile

# Get all profiles
Profile.objects.all()

# Get pending approvals
pending = Profile.objects.filter(status='pending')

# Get approved users
approved = Profile.objects.filter(status='approved')

# Get user's profile
profile = request.user.profile

# Filter by company
profiles = Profile.objects.filter(company='Acme Corp')

# Count by status
pending_count = Profile.objects.filter(status='pending').count()

# Get profile with user info
profile = Profile.objects.select_related('user').get(id=1)

# Search
from django.db.models import Q
search = Profile.objects.filter(
    Q(user__username__icontains='john') |
    Q(company__icontains='acme')
)

# Order by date
latest = Profile.objects.order_by('-created_at')

# Pagination
from django.core.paginator import Paginator
paginator = Paginator(profiles, 25)
page = paginator.get_page(1)
```

---

## 🧪 Testing Examples

### Test Registration

```python
from django.test import Client
from django.contrib.auth.models import User

client = Client()

# Test registration form
response = client.post('/accounts/register/', {
    'username': 'testuser',
    'email': 'test@example.com',
    'first_name': 'Test',
    'last_name': 'User',
    'password1': 'TestPassword123',
    'password2': 'TestPassword123',
    'contact': '+1234567890',
    'company': 'Test Corp',
    'department': 'IT',
    'location': 'New York',
    'address': '123 Main St'
})

assert response.status_code == 302  # Redirect after success

# Check user created
user = User.objects.get(username='testuser')
assert user.email == 'test@example.com'

# Check profile created
assert hasattr(user, 'profile')
assert user.profile.status == 'pending'
```

### Test Admin Approval

```python
from accounts.models import Profile

# Get pending profile
profile = Profile.objects.get(status='pending')

# Approve
profile.status = 'approved'
profile.save()

# Verify
profile.refresh_from_db()
assert profile.status == 'approved'
```

---

## 🔍 Debugging Tips

### Enable Console Email

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Emails will print to console instead of sending
```

### Django Shell

```bash
python manage.py shell

# Example queries
from accounts.models import Profile
from django.contrib.auth.models import User

# Check user
user = User.objects.get(username='john')
print(user.profile.status)

# Check profile
profile = Profile.objects.get(id=1)
print(profile.get_full_name())

# List all pending
pendings = Profile.objects.filter(status='pending')
for p in pendings:
    print(f"{p.user.username} - {p.company}")
```

### View Logs

```bash
# Check for errors in terminal where runserver is running
python manage.py runserver

# Search for email errors
grep -r "Error sending" .
```

---

## 📈 Performance Optimization

### Database Indexes

Automatically created on:
- User.username
- User.email
- Profile.status
- Profile.created_at

### Query Optimization

```python
# Bad: N+1 queries
for profile in Profile.objects.all():
    print(profile.user.username)  # SQL query for each

# Good: Use select_related
profiles = Profile.objects.select_related('user').all()
for profile in profiles:
    print(profile.user.username)  # No extra queries
```

### Caching (Future Enhancement)

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def admin_dashboard(request):
    ...
```

---

## 🚀 Deployment Checklist

- [ ] Update SECRET_KEY in settings.py
- [ ] Set DEBUG = False
- [ ] Update ALLOWED_HOSTS
- [ ] Configure production database
- [ ] Set email backend to SMTP
- [ ] Update email credentials
- [ ] Enable HTTPS
- [ ] Set SECURE_SSL_REDIRECT = True
- [ ] Configure logging
- [ ] Run migrations
- [ ] Collect static files
- [ ] Test email sending
- [ ] Create backup strategy

---

**Last Updated:** January 23, 2026
**Framework:** Django 6.0.1
**Document Version:** 1.0
