# Django Email System - Complete Documentation

## 📋 System Overview

This is a production-ready Django-based email system with user registration and admin management features. The system uses Django's built-in authentication combined with email notifications via free SMTP services (like Gmail).

### Key Features
- ✅ User registration with validation
- ✅ Email notifications (free SMTP)
- ✅ Admin approval workflow
- ✅ Role-based access control
- ✅ Secure password hashing
- ✅ CSRF protection
- ✅ Status tracking (pending/approved/rejected)
- ✅ Admin dashboard
- ✅ User dashboard
- ✅ Responsive UI

---

## 📁 Project Structure

```
emailsystem/
├── manage.py                          # Django CLI
├── requirements.txt                   # Dependencies
├── db.sqlite3                         # Database
├── emailsystem/                       # Project settings
│   ├── settings.py                   # Main configuration
│   ├── urls.py                       # Main URL routing
│   ├── asgi.py                       # ASGI config
│   ├── wsgi.py                       # WSGI config
│   └── __init__.py
└── accounts/                          # Main application
    ├── models.py                     # Database models
    ├── views.py                      # Views logic
    ├── forms.py                      # Form definitions
    ├── admin.py                      # Admin configuration
    ├── urls.py                       # App URL patterns
    ├── email_utils.py                # Email functions
    ├── apps.py                       # App configuration
    ├── tests.py                      # Tests
    ├── migrations/                   # Database migrations
    ├── templates/                    # HTML templates
    │   └── accounts/
    │       ├── base.html
    │       ├── register.html
    │       ├── login.html
    │       ├── user_dashboard.html
    │       ├── admin_dashboard.html
    │       ├── admin_edit_user.html
    │       ├── admin_view_user.html
    │       └── emails/               # Email templates
    │           ├── admin_notification.html
    │           ├── user_confirmation.html
    │           ├── approval_notification.html
    │           └── rejection_notification.html
    └── __init__.py
```

---

## 🗄️ Database Models

### User Model (Django Built-in)
Extends Django's authentication system:
- `username` - Unique username
- `first_name` - User's first name
- `last_name` - User's last name
- `email` - Email address
- `password` - Hashed password (PBKDF2)
- `is_active` - Account status
- `is_staff` - Admin flag

### Profile Model (Custom Extension)

```python
class Profile(models.Model):
    # Relationships
    user = OneToOneField(User)  # One user = one profile
    
    # Contact Information
    contact = CharField()       # Phone number
    
    # Organization
    company = CharField()       # Company/Organization name
    department = CharField()    # Department name
    
    # Location
    location = CharField()      # City/Location
    address = TextField()       # Full address
    
    # Status Management
    status = CharField(         # pending/approved/rejected
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ]
    )
    
    # Admin Notes
    admin_notes = TextField()   # Internal notes (admin only)
    
    # Timestamps
    created_at = DateTimeField()  # Registration date
    updated_at = DateTimeField()  # Last update date
```

**Key Features:**
- Automatic creation via Django signals when User is created
- Status tracking throughout approval workflow
- Admin notes for internal documentation
- Timestamped for audit trail

---

## 📝 Forms

### CustomUserCreationForm
**Purpose:** User account creation
**Fields:**
- Username (validated for uniqueness)
- Email (validated for uniqueness and format)
- First Name
- Last Name
- Password (8+ chars)
- Password Confirmation (must match)

**Validations:**
- Email uniqueness
- Username uniqueness
- Minimum password length (8)
- Password confirmation match

### ProfileForm
**Purpose:** Additional profile information
**Fields:**
- Contact Number
- Company Name
- Department
- Location
- Address

### ProfileEditForm
**Purpose:** Admin editing of user profiles
**Fields:**
- Status (dropdown)
- Admin Notes
- User details (synced with User model)

---

## 🔧 Views & URL Patterns

### Registration Views
```
POST /accounts/register/
- Process user registration
- Create User and Profile
- Send admin notification email
- Send user confirmation email
- Redirect to success page

GET /accounts/registration-success/
- Display success message
```

### Authentication Views
```
GET/POST /accounts/login/
POST /accounts/logout/
GET/POST /accounts/password-reset/
GET /accounts/password-reset/done/
GET/POST /accounts/password-reset/<uidb64>/<token>/
GET /accounts/password-reset/complete/
```

### User Dashboard
```
GET /accounts/dashboard/
- Display user profile
- Show registration status
- Display admin notes (if rejected)
```

### Admin Views
```
GET /accounts/admin/dashboard/
- List all users with filtering
- Search functionality
- Status statistics

GET/POST /accounts/admin/user/<id>/
- View detailed user information

GET/POST /accounts/admin/user/<id>/edit/
- Edit user profile and status
- Update admin notes

POST /accounts/admin/user/<id>/approve/
- Quick approve action
- Send approval email

POST /accounts/admin/user/<id>/reject/
- Quick reject action
- Send rejection email with reason
```

---

## 📧 Email System

### Email Functions (email_utils.py)

#### 1. send_registration_notification_to_admin()
**Trigger:** New user registration
**Recipient:** Admin email
**Content:** Complete user registration details
**Purpose:** Alert admin to review and approve user

#### 2. send_registration_confirmation_to_user()
**Trigger:** User completes registration
**Recipient:** User email
**Content:** Confirmation message + next steps
**Purpose:** Confirm receipt of registration

#### 3. send_approval_email()
**Trigger:** Admin approves user
**Recipient:** User email
**Content:** Approval notification + login instructions
**Purpose:** Notify user of approval

#### 4. send_rejection_email()
**Trigger:** Admin rejects user
**Recipient:** User email
**Content:** Rejection notification + reason
**Purpose:** Inform user of rejection

#### 5. send_bulk_email()
**Purpose:** Generic function for sending bulk emails
**Usage:** Admin communications to multiple users

### Email Templates
All templates use HTML formatting with fallback plain text versions.

**Email Templates Location:**
```
accounts/templates/accounts/emails/
├── admin_notification.html       # To admin
├── user_confirmation.html        # To new user
├── approval_notification.html    # To approved user
└── rejection_notification.html   # To rejected user
```

---

## ⚙️ Email Configuration

### Settings (emailsystem/settings.py)

```python
# Email Backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail SMTP (Free Service)
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Admin & Support Emails
ADMIN_EMAIL = 'admin@example.com'
SUPPORT_EMAIL = 'support@example.com'
SITE_URL = 'http://localhost:8000'
```

### Setting Up Gmail SMTP

#### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification

#### Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer"
3. Google generates a 16-character password
4. Use this password in settings (NOT your Gmail password)

#### Step 3: Update settings.py
```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # The app password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

### Alternative Email Services (Free)

**Option 1: SendGrid (Free Tier)**
- 100 emails/day
- https://sendgrid.com
- No SMTP setup needed

**Option 2: Mailgun (Free Tier)**
- 5,000 emails/month
- https://www.mailgun.com
- Supports SMTP

**Option 3: Console Backend (Testing)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Prints emails to console instead of sending
```

**Option 4: File Backend (Testing)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```

---

## 🔐 Security Implementation

### Password Security
- ✅ PBKDF2 hashing (Django default)
- ✅ Argon2 support enabled
- ✅ BCrypt support enabled
- ✅ Minimum 8 characters required
- ✅ Password confirmation validation

### CSRF Protection
- ✅ CSRF tokens in all forms
- ✅ Middleware enabled
- ✅ Cookie-based protection

### User Input Validation
- ✅ Email format validation
- ✅ Uniqueness checks (email, username)
- ✅ Required field validation
- ✅ Contact number validation

### Authentication
- ✅ Django's built-in auth system
- ✅ Session-based authentication
- ✅ Login required decorators
- ✅ Role-based access control

### Data Protection
- ✅ User signals for automatic profile creation
- ✅ Cascading deletion (user → profile)
- ✅ Timestamp auditing
- ✅ Admin notes for decisions

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Database & Apply Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 6. Update Email Settings
Edit `emailsystem/settings.py`:
```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
ADMIN_EMAIL = 'your-admin-email@gmail.com'
```

### 7. Run Development Server
```bash
python manage.py runserver
```

### 8. Access the System
- **Home:** http://127.0.0.1:8000/
- **Register:** http://127.0.0.1:8000/accounts/register/
- **Login:** http://127.0.0.1:8000/accounts/login/
- **Admin:** http://127.0.0.1:8000/admin/

---

## 📊 Registration Workflow

### User Registration Flow
```
1. User visits /accounts/register/
   ↓
2. Fills registration form with:
   - Account info (username, password, email)
   - Personal info (first name, last name)
   - Organization info (company, department, location)
   ↓
3. System validates all fields
   ↓
4. User and Profile created in database
   ↓
5. Email sent to Admin (admin_notification.html)
   ↓
6. Confirmation email sent to User (user_confirmation.html)
   ↓
7. User redirected to success page
   ↓
8. Status: PENDING (awaiting admin review)
```

### Admin Approval Workflow
```
1. Admin views /accounts/admin/dashboard/
   ↓
2. Sees pending users list
   ↓
3. Clicks "View" or "Edit" on a user
   ↓
4. Reviews user details:
   - Personal information
   - Company/Organization
   - Contact details
   - Registration date
   ↓
5. Admin decides: APPROVE or REJECT
   ↓
6. If APPROVED:
   - Status changed to "approved"
   - Approval email sent to user
   - User can now log in
   ↓
7. If REJECTED:
   - Status changed to "rejected"
   - Reason provided by admin
   - Rejection email sent to user
   - Admin notes added
```

### User Status Tracking
```
Registration Submitted
        ↓
    PENDING (yellow)
    ↙       ↘
APPROVED    REJECTED
(green)     (red)
  ↓           ↓
Login      Contact Support
Available
```

---

## 👨‍💼 Admin Panel Features

### Django Admin (/admin/)
- View and manage User accounts
- View and manage Profile information
- Filter by status
- Search by username, email, name
- Inline editing
- Bulk actions (approve/reject)

### Custom Admin Dashboard (/accounts/admin/dashboard/)
- User list with status badges
- Filter by status
- Search functionality
- Quick approve/reject buttons
- Statistics (total, pending, approved, rejected)
- Detailed view of each user
- Edit and manage profiles

### Admin Capabilities
- ✅ View all registered users
- ✅ Filter by registration status
- ✅ Search users
- ✅ View complete user details
- ✅ Edit user information
- ✅ Approve registrations
- ✅ Reject registrations with reasons
- ✅ Add internal notes
- ✅ Send email notifications

---

## 👥 User Features

### User Dashboard (/accounts/dashboard/)
- View profile information
- See registration status
- Check admin notes (if rejected)
- View all submitted details
- Change password
- Logout

### User Capabilities
- ✅ Create account
- ✅ View profile
- ✅ Check approval status
- ✅ Receive email notifications
- ✅ Reset password

---

## 📝 Admin Notes & Tracking

### Decision Documentation
- **Approval:** Include any approval notes
- **Rejection:** Document reason for rejection
- **Follow-up:** Track reason for future reference

### Audit Trail
- Registration date
- Last update date
- All status changes
- Admin modifications

---

## 🔍 Testing the System

### Test User Registration
```
1. Visit http://127.0.0.1:8000/accounts/register/
2. Fill all fields:
   - Username: testuser
   - Email: test@example.com
   - Password: TestPassword123
   - First Name: John
   - Last Name: Doe
   - Contact: +1234567890
   - Company: Test Corp
   - Department: IT
   - Location: New York
   - Address: 123 Main St
3. Click "Create Account"
4. Check email for confirmation
5. Admin receives notification email
```

### Test Admin Approval
```
1. Login as admin: http://127.0.0.1:8000/admin/
2. Go to Profiles
3. Click on pending user
4. Click "Approve Selected" or "Reject Selected"
5. User receives approval/rejection email
```

### Test User Login
```
1. Visit http://127.0.0.1:8000/accounts/login/
2. Enter approved user credentials
3. Access user dashboard
4. View profile and status
```

---

## 🐛 Troubleshooting

### Email Not Sending
**Problem:** Emails not sent to users/admin
**Solutions:**
1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
2. Verify 2FA and App Password on Gmail
3. Check email address format
4. Enable "Less secure app access" (if not using App Password)
5. Check Django console for error messages

### Gmail Authentication Failed
**Solution:**
- Gmail now requires App Passwords
- Create at: https://myaccount.google.com/apppasswords
- Use the 16-character password generated

### Database Issues
**Solution:**
```bash
# Reset database
python manage.py flush
python manage.py migrate

# Create new superuser
python manage.py createsuperuser
```

### Migration Errors
**Solution:**
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Static Files Not Loading
**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput
```

---

## 📦 Deployment Checklist

### Before Production
- [ ] Set DEBUG = False
- [ ] Update ALLOWED_HOSTS with your domain
- [ ] Use environment variables for secrets
- [ ] Set CSRF_COOKIE_SECURE = True
- [ ] Set SESSION_COOKIE_SECURE = True
- [ ] Configure proper database (PostgreSQL)
- [ ] Set up HTTPS/SSL
- [ ] Configure email service
- [ ] Set up logging
- [ ] Enable database backups
- [ ] Configure static files serving

### Production Settings Template
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Use environment variables
import os
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')
```

---

## 📚 Additional Resources

- Django Docs: https://docs.djangoproject.com/
- Django Signals: https://docs.djangoproject.com/en/stable/topics/signals/
- Gmail App Passwords: https://myaccount.google.com/apppasswords
- Django Security: https://docs.djangoproject.com/en/stable/topics/security/

---

## 🎯 System Architecture Summary

```
┌─────────────────────────────────────┐
│         User Registration           │
│  (Registration Form + Profile)      │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│    Django Models & Database         │
│  (User + Profile OneToOne)          │
└──────────────┬──────────────────────┘
               │
               ├─→ Send Confirmation Email (User)
               │
               └─→ Send Notification Email (Admin)
                        │
                        ↓
                ┌───────────────────┐
                │  Admin Review     │
                │  (Admin Dashboard)│
                └────────┬──────────┘
                         │
                ┌────────┴────────┐
                ↓                 ↓
            APPROVE           REJECT
                │                 │
                ├─→ Approval Email
                │
                └─→ Rejection Email
                        │
                        ↓
                User Status Updated
                (APPROVED/REJECTED)
```

---

## ✅ Features Checklist

- ✅ User registration with complete validation
- ✅ Email notifications to admin and users
- ✅ Admin approval/rejection workflow
- ✅ User status tracking
- ✅ Secure password hashing
- ✅ CSRF protection
- ✅ Role-based access control
- ✅ Admin dashboard
- ✅ User dashboard
- ✅ Email templates
- ✅ Form validation
- ✅ Database models
- ✅ Signal handling
- ✅ Responsive UI
- ✅ Error handling
- ✅ Free services only (Gmail SMTP)

---

## 📞 Support & Maintenance

For issues or questions:
1. Check error logs in Django console
2. Review email configuration in settings.py
3. Verify database migrations are applied
4. Test with Django's console email backend
5. Check SMTP credentials

---

**Last Updated:** January 23, 2026
**Django Version:** 6.0.1
**Python Version:** 3.8+
