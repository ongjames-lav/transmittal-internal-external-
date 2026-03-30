# Django Email System - Architecture & Design Document

## 📚 Table of Contents
1. [System Architecture](#system-architecture)
2. [Component Description](#component-description)
3. [Data Flow](#data-flow)
4. [Models Structure](#models-structure)
5. [Views & Controllers](#views--controllers)
6. [Email System Design](#email-system-design)
7. [Security Architecture](#security-architecture)
8. [Admin Workflow](#admin-workflow)
9. [User Workflow](#user-workflow)
10. [Database Schema](#database-schema)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Django Application                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          URL Router (urls.py)                    │  │
│  │  /accounts/register/                            │  │
│  │  /accounts/admin/dashboard/                     │  │
│  │  /accounts/dashboard/                           │  │
│  └────────────┬─────────────────────────────────────┘  │
│               │                                        │
│  ┌────────────▼──────────────────────────────────────┐ │
│  │          Views Layer (views.py)                  │ │
│  │  ├─ register()                                  │ │
│  │  ├─ admin_dashboard()                           │ │
│  │  ├─ admin_approve_user()                        │ │
│  │  ├─ admin_reject_user()                         │ │
│  │  └─ user_dashboard()                            │ │
│  └────────────┬──────────────────────────────────────┘ │
│               │                                        │
│  ┌────────────▼──────────────────────────────────────┐ │
│  │    Forms Layer (forms.py)                        │ │
│  │  ├─ CustomUserCreationForm                       │ │
│  │  ├─ ProfileForm                                  │ │
│  │  └─ ProfileEditForm                              │ │
│  └────────────┬──────────────────────────────────────┘ │
│               │                                        │
│  ┌────────────▼──────────────────────────────────────┐ │
│  │   Models Layer (models.py)                       │ │
│  │  ├─ User (Django built-in)                       │ │
│  │  └─ Profile (Custom)                             │ │
│  └────────────┬──────────────────────────────────────┘ │
│               │                                        │
│  ┌────────────▼──────────────────────────────────────┐ │
│  │  Email System (email_utils.py)                   │ │
│  │  ├─ send_registration_notification_to_admin()   │ │
│  │  ├─ send_approval_email()                        │ │
│  │  └─ send_rejection_email()                       │ │
│  └────────────┬──────────────────────────────────────┘ │
│               │                                        │
│  ┌────────────▼──────────────────────────────────────┐ │
│  │  Database (SQLite/PostgreSQL)                    │ │
│  │  ├─ auth_user                                    │ │
│  │  └─ accounts_profile                             │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
        │                      │                    │
        ▼                      ▼                    ▼
    SMTP Server          Templates          Static Files
   (Gmail SMTP)        (Email & HTML)      (CSS & JS)
```

---

## Component Description

### 1. **URL Router** (emailsystem/urls.py)
**Purpose:** Route incoming requests to appropriate views

**URL Patterns:**
```
/                                  → Home page
/accounts/register/                → User registration form
/accounts/login/                   → Login form
/accounts/logout/                  → Logout
/accounts/dashboard/               → User dashboard
/accounts/admin/dashboard/         → Admin dashboard
/accounts/admin/user/<id>/         → View user details
/accounts/admin/user/<id>/edit/    → Edit user profile
/accounts/admin/user/<id>/approve/ → Approve user
/accounts/admin/user/<id>/reject/  → Reject user
/admin/                            → Django admin panel
```

### 2. **Views Layer** (accounts/views.py)
**Purpose:** Handle business logic and request processing

**Core Views:**
- `register()` - Handle user registration
- `registration_success()` - Show success message
- `user_dashboard()` - Display user profile
- `admin_dashboard()` - Show user list to admin
- `admin_edit_user()` - Allow admin to edit user
- `admin_approve_user()` - Approve user registration
- `admin_reject_user()` - Reject user registration
- `admin_view_user()` - View user details

### 3. **Forms Layer** (accounts/forms.py)
**Purpose:** Validate user input and handle form processing

**Forms:**
1. **CustomUserCreationForm**
   - Extends Django's UserCreationForm
   - Validates email uniqueness
   - Validates username uniqueness
   - Checks password requirements
   - Confirms passwords match

2. **ProfileForm**
   - Collects organization information
   - Validates contact number
   - Required: contact, company, department, location, address

3. **ProfileEditForm**
   - Allows admin to edit user profile
   - Update status (pending/approved/rejected)
   - Add internal notes

### 4. **Models Layer** (accounts/models.py)
**Purpose:** Define database structure

**Models:**
- **User** (Django Built-in)
  - username, email, password (hashed)
  - first_name, last_name
  - is_active, is_staff, is_superuser
  
- **Profile** (Custom)
  - OneToOneField → User
  - contact, company, department
  - location, address
  - status (pending/approved/rejected)
  - admin_notes, created_at, updated_at

### 5. **Email System** (accounts/email_utils.py)
**Purpose:** Send notifications to users and admins

**Functions:**
1. `send_registration_notification_to_admin()` - Alert admin
2. `send_registration_confirmation_to_user()` - Confirm receipt
3. `send_approval_email()` - Notify approval
4. `send_rejection_email()` - Notify rejection
5. `send_bulk_email()` - Generic bulk send

### 6. **Admin Interface** (accounts/admin.py)
**Purpose:** Provide admin management interface

**Features:**
- List all profiles with status
- Filter by status, company, department
- Search by username, email, name
- Inline editing
- Bulk approve/reject actions
- Custom display formatting

---

## Data Flow

### Registration Flow (User Perspective)

```
User Input
   │
   ▼
form validation (CustomUserCreationForm)
   ├─ Check username unique? YES
   ├─ Check email unique? YES
   ├─ Check password >= 8 chars? YES
   ├─ Passwords match? YES
   │
   ▼
Create User Object
   │
   ├─ user.username = "john_doe"
   ├─ user.email = "john@example.com"
   ├─ user.first_name = "John"
   ├─ user.last_name = "Doe"
   └─ user.password = hash("SecurePass123")
   │
   ▼
Signal: post_save (User)
   │
   ├─ Create Profile object
   ├─ profile.user = user (OneToOne)
   └─ profile.status = "pending"
   │
   ▼
form validation (ProfileForm)
   ├─ contact contains digit? YES
   └─ All fields present? YES
   │
   ▼
Create/Update Profile
   │
   ├─ profile.contact = "+1234567890"
   ├─ profile.company = "Acme Corp"
   ├─ profile.department = "IT"
   ├─ profile.location = "New York"
   ├─ profile.address = "123 Main St"
   └─ profile.status = "pending"
   │
   ▼
Send Notification Emails
   │
   ├─ Email 1: Admin notification
   │           (admin receives: new user details)
   │
   └─ Email 2: User confirmation
               (user receives: registration successful)
   │
   ▼
Redirect to Success Page
   │
   └─ Display message: "Check your email!"
```

### Admin Approval Flow

```
Admin Reviews Pending User
   │
   ▼
Admin Views User Details
   │
   ├─ Username
   ├─ Email
   ├─ Company
   ├─ Department
   ├─ Location
   └─ Address
   │
   ▼
Admin Decision
   │
   ├─ APPROVE or REJECT?
   │
   ├── APPROVE Path:
   │   │
   │   ▼
   │   Update Profile
   │   └─ profile.status = "approved"
   │   │
   │   ▼
   │   Send Approval Email
   │   ├─ Subject: "Registration Approved!"
   │   ├─ Content: Login instructions
   │   └─ Link: http://127.0.0.1:8000/accounts/login/
   │   │
   │   ▼
   │   User Can Now Login
   │   └─ Access dashboard
   │
   └── REJECT Path:
       │
       ▼
       Update Profile
       ├─ profile.status = "rejected"
       └─ profile.admin_notes = "Reason..."
       │
       ▼
       Send Rejection Email
       ├─ Subject: "Registration Status Update"
       ├─ Content: Rejection reason
       └─ Link: Contact support
       │
       ▼
       User Notified
       └─ Cannot login
```

---

## Models Structure

### User Model (Django Built-in)
```python
class User(AbstractUser):
    # Identification
    username: CharField          # Unique username
    email: EmailField           # Unique email
    
    # Name
    first_name: CharField       # User's first name
    last_name: CharField        # User's last name
    
    # Security
    password: CharField         # Hashed password
    
    # Permissions
    is_active: BooleanField     # Account active?
    is_staff: BooleanField      # Admin access?
    is_superuser: BooleanField  # Super admin?
    
    # Metadata
    last_login: DateTimeField
    date_joined: DateTimeField
```

### Profile Model (Custom)
```python
class Profile(Model):
    # Relationship
    user: OneToOneField(User)
        └─ Cascade on delete
        └─ Related name: 'profile'
    
    # Contact Information
    contact: CharField(max_length=20)
        └─ Phone number or contact
    
    # Organization
    company: CharField(max_length=100)
        └─ Company name
    
    department: CharField(max_length=100)
        └─ Department name
    
    # Location
    location: CharField(max_length=100)
        └─ City/Location
    
    address: TextField()
        └─ Full address
    
    # Status
    status: CharField(
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    
    # Admin Notes
    admin_notes: TextField(blank=True, null=True)
        └─ Internal admin notes
    
    # Timestamps
    created_at: DateTimeField(auto_now_add=True)
        └─ Registration date
    
    updated_at: DateTimeField(auto_now=True)
        └─ Last update date
```

### Relationship Diagram
```
┌─────────────────┐         ┌──────────────────┐
│     User        │         │     Profile      │
├─────────────────┤         ├──────────────────┤
│ id              │◄───────►│ id               │
│ username        │ 1:1     │ user_id (FK)     │
│ email           │         │ contact          │
│ first_name      │         │ company          │
│ last_name       │         │ department       │
│ password        │         │ location         │
│ is_active       │         │ address          │
│ is_staff        │         │ status           │
│ date_joined     │         │ admin_notes      │
│                 │         │ created_at       │
│                 │         │ updated_at       │
└─────────────────┘         └──────────────────┘
```

---

## Views & Controllers

### View Execution Flow

```
URL Request
    │
    ▼
URL Pattern Matching (urls.py)
    │
    ▼
View Function (views.py)
    │
    ├─ Check Authentication (if needed)
    ├─ Check Permissions (is_admin?)
    │
    ├─ GET Request: Display Form/Data
    │   │
    │   ▼
    │   Render Template
    │
    └─ POST Request: Process Data
        │
        ├─ Validate Form
        │
        ├─ Success:
        │   │
        │   ├─ Create/Update Database
        │   ├─ Send Emails (if needed)
        │   ├─ Show Success Message
        │   └─ Redirect
        │
        └─ Error:
            │
            ├─ Show Error Messages
            └─ Re-render Form
```

### Key Views

#### 1. register() - User Registration
```python
def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Create User
            user = user_form.save()
            
            # Create Profile (via signal)
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            
            # Send Emails
            send_registration_notification_to_admin(user, profile)
            send_registration_confirmation_to_user(user, profile)
            
            # Redirect
            return redirect('accounts:registration_success')
    
    return render(request, 'accounts/register.html', {...})
```

#### 2. admin_dashboard() - List Pending Users
```python
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get all profiles
    profiles = Profile.objects.all()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        profiles = profiles.filter(status=status_filter)
    
    # Search if provided
    search_query = request.GET.get('search')
    if search_query:
        profiles = profiles.filter(
            user__username__icontains=search_query
        )
    
    # Calculate stats
    stats = {
        'total': Profile.objects.count(),
        'pending': Profile.objects.filter(status='pending').count(),
        'approved': Profile.objects.filter(status='approved').count(),
        'rejected': Profile.objects.filter(status='rejected').count(),
    }
    
    return render(request, 'accounts/admin_dashboard.html', {
        'profiles': profiles,
        'stats': stats,
    })
```

#### 3. admin_approve_user() - Approve User
```python
@login_required
@user_passes_test(is_admin)
def admin_approve_user(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    
    if request.method == 'POST':
        # Update status
        profile.status = 'approved'
        profile.save()
        
        # Send email
        send_approval_email(profile)
        
        # Redirect
        return redirect('accounts:admin_dashboard')
    
    return render(request, 'accounts/admin_confirm_action.html', {
        'profile': profile,
    })
```

---

## Email System Design

### Email Architecture

```
┌─────────────────────────────────────────┐
│      Email Trigger Events               │
├─────────────────────────────────────────┤
│ • User registers                        │
│ • Admin approves user                   │
│ • Admin rejects user                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ Email Utils   │
         │ (email_utils) │
         └────────┬──────┘
                  │
         ┌────────┴──────────────────┐
         │                           │
         ▼                           ▼
    ┌─────────────┐          ┌─────────────┐
    │ HTML Templ. │          │ Plain Text  │
    │ Rendering   │          │ (fallback)  │
    └────────┬────┘          └─────┬───────┘
             │                     │
             └────────────┬────────┘
                          │
                          ▼
                    ┌──────────────┐
                    │ EmailMulti   │
                    │ Alternative  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ SMTP Server  │
                    │ (Gmail SMTP) │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ User/Admin   │
                    │ Inbox        │
                    └──────────────┘
```

### Email Templates

**1. Admin Notification Email**
```
To: admin@example.com
Subject: New User Registration - john_doe

Headers:
  From: system@example.com
  Content-Type: text/html; charset=utf-8

Body:
  - User details (name, email, company, etc.)
  - Action link to admin dashboard
  - Registration date/time
```

**2. User Confirmation Email**
```
To: user@example.com
Subject: Registration Confirmation - Welcome!

Body:
  - Thank you message
  - What happens next
  - Timeline (24-48 hours)
  - Support contact
```

**3. Approval Email**
```
To: user@example.com
Subject: Registration Approved!

Body:
  - Approval notification
  - Login instructions
  - Login link
  - Available features
```

**4. Rejection Email**
```
To: user@example.com
Subject: Registration Status Update

Body:
  - Rejection notification
  - Reason for rejection
  - Support contact
  - Reapplication option
```

---

## Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────┐
│         Request from Browser            │
└────────────────┬────────────────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ Check Authentication       │
    │ (@login_required)          │
    │ ├─ Session cookie exists?  │
    │ └─ Valid user ID?          │
    └────────┬───────────────────┘
             │ YES
             ▼
    ┌────────────────────────────┐
    │ Check Authorization        │
    │ (@user_passes_test)        │
    │ ├─ is_staff?               │
    │ └─ is_superuser?           │
    └────────┬───────────────────┘
             │ YES
             ▼
    ┌────────────────────────────┐
    │ Execute View Logic         │
    │ (Access to data)           │
    └────────────────────────────┘

    If NO at any step → Redirect to login
```

### Password Security

```
User Input: "MyPassword123"
    │
    ▼
PBKDF2 Hash Function
├─ Algorithm: PBKDF2-SHA256
├─ Iterations: 600,000
├─ Salt: Randomly generated
└─ Output: 64-byte hash
    │
    ▼
Stored: "pbkdf2_sha256$600000$..."
    │
    ▼
User Login: "MyPassword123"
    │
    ├─ Hash with same salt
    ├─ Compare with stored hash
    └─ Match? → Allow login
```

### CSRF Protection

```
Form Request:
    │
    ├─ Generate: CSRF Token
    ├─ Store: Session
    └─ Embed: Form HTML
        │
        ▼
    Form Submission:
        │
        ├─ Extract token from POST
        ├─ Compare with session token
        ├─ Match? → Process request
        └─ Mismatch? → Reject (403)
```

### Input Validation

```
User Form Input
    │
    ├─ Email validation
    │  ├─ Format check (email@domain.com)
    │  ├─ Uniqueness check
    │  └─ Length limits
    │
    ├─ Username validation
    │  ├─ Uniqueness check
    │  └─ Character validation
    │
    ├─ Password validation
    │  ├─ Length >= 8 chars
    │  ├─ Confirmation match
    │  └─ Not similar to username
    │
    └─ Profile validation
       ├─ Contact has digits
       ├─ Required fields present
       └─ Length limits
```

---

## Admin Workflow

### Complete Admin Workflow

```
STEP 1: Admin Login
    │
    ├─ URL: /admin/
    ├─ Enter username/password
    └─ Django admin authenticates
        │
        ▼
STEP 2: Admin Dashboard
    │
    ├─ URL: /accounts/admin/dashboard/
    ├─ View:
    │  ├─ Total users: 50
    │  ├─ Pending: 15
    │  ├─ Approved: 30
    │  └─ Rejected: 5
    │
    └─ Display: List of all users
        │
        ▼
STEP 3: Filter/Search
    │
    ├─ Filter by status: [pending]
    ├─ Search: [company name]
    └─ Result: Filtered list
        │
        ▼
STEP 4: Review User
    │
    ├─ Click "View" on user
    ├─ See: All registration details
    │  ├─ Personal info
    │  ├─ Organization info
    │  ├─ Contact info
    │  └─ Registration date
    │
    └─ Click "Edit" to manage
        │
        ▼
STEP 5: Decision
    │
    ├── APPROVE ──→ Click "Approve"
    │                │
    │                ├─ Update: status = "approved"
    │                ├─ Send: Approval email
    │                ├─ Display: Success message
    │                └─ User can now login
    │
    └── REJECT ───→ Click "Reject"
                    │
                    ├─ Enter: Reason
                    ├─ Update: status = "rejected"
                    ├─ Update: admin_notes = reason
                    ├─ Send: Rejection email
                    ├─ Display: Success message
                    └─ User cannot login
```

---

## User Workflow

### Complete User Journey

```
STEP 1: Arrive at Home Page
    │
    ├─ URL: http://127.0.0.1:8000/
    ├─ See: System description + features
    └─ Click: "Register" button
        │
        ▼
STEP 2: Registration Form
    │
    ├─ URL: /accounts/register/
    ├─ Form sections:
    │  ├─ Account Information
    │  │  ├─ Username
    │  │  ├─ Email
    │  │  ├─ Password
    │  │  └─ Confirm Password
    │  │
    │  ├─ Personal Information
    │  │  ├─ First Name
    │  │  └─ Last Name
    │  │
    │  └─ Organization & Contact
    │     ├─ Contact Number
    │     ├─ Company
    │     ├─ Department
    │     ├─ Location
    │     └─ Address
    │
    └─ Click: "Create Account"
        │
        ▼
STEP 3: Validation
    │
    ├─ System validates:
    │  ├─ All fields present?
    │  ├─ Passwords match?
    │  ├─ Email format valid?
    │  ├─ Username not taken?
    │  └─ Email not taken?
    │
    └─ If valid: Continue
        │
        ▼
STEP 4: Registration Success
    │
    ├─ User created in database
    ├─ Profile created (auto)
    ├─ Status: PENDING
    ├─ Emails sent:
    │  ├─ To user: Confirmation
    │  └─ To admin: Notification
    │
    └─ Display: Success page
        │
        ▼
STEP 5: Waiting for Approval
    │
    ├─ User checks email
    ├─ Sees: Confirmation message
    ├─ Sees: "Wait 24-48 hours"
    │
    └─ Admin reviews (during this time)
        │
        ▼
STEP 6: Approval/Rejection (By Admin)
    │
    ├─ If APPROVED:
    │  │
    │  ├─ User receives: Approval email
    │  ├─ User status: APPROVED
    │  │
    │  └─ User can now:
    │     ├─ Go to login
    │     ├─ Enter credentials
    │     └─ Access dashboard
    │
    └─ If REJECTED:
        │
        ├─ User receives: Rejection email
        ├─ User status: REJECTED
        ├─ Reason: In email
        │
        └─ User cannot login
            │
            └─ Can contact support
```

---

## Database Schema

### Complete Database Diagram

```sql
-- Django Built-in Table
CREATE TABLE auth_user (
    id              INTEGER PRIMARY KEY,
    username        VARCHAR(150) UNIQUE NOT NULL,
    password        VARCHAR(128) NOT NULL,        -- Hashed
    first_name      VARCHAR(150),
    last_name       VARCHAR(150),
    email           VARCHAR(254),
    is_staff        BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    is_superuser    BOOLEAN DEFAULT FALSE,
    last_login      DATETIME,
    date_joined     DATETIME NOT NULL
);

-- Custom Profile Table
CREATE TABLE accounts_profile (
    id              INTEGER PRIMARY KEY,
    user_id         INTEGER UNIQUE NOT NULL,      -- Foreign Key
    contact         VARCHAR(20) NOT NULL,
    company         VARCHAR(100) NOT NULL,
    department      VARCHAR(100) NOT NULL,
    location        VARCHAR(100) NOT NULL,
    address         TEXT NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending', -- pending/approved/rejected
    admin_notes     TEXT,
    created_at      DATETIME DEFAULT NOW(),
    updated_at      DATETIME DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
        ON DELETE CASCADE
);

-- Django Session Table (auto-created)
CREATE TABLE django_session (
    session_key     VARCHAR(40) PRIMARY KEY,
    session_data    LONGTEXT,
    expire_date     DATETIME
);
```

### Indexes for Performance
```sql
-- Username lookup (login)
CREATE INDEX idx_user_username ON auth_user(username);

-- Email lookup (registration check)
CREATE INDEX idx_user_email ON auth_user(email);

-- Status filtering (admin dashboard)
CREATE INDEX idx_profile_status ON accounts_profile(status);

-- User lookups
CREATE INDEX idx_profile_user ON accounts_profile(user_id);

-- Created date (sorting)
CREATE INDEX idx_profile_created ON accounts_profile(created_at);
```

---

## Summary

This architecture provides:

✅ **Separation of Concerns:** Models, Views, Forms, Email
✅ **Security:** Password hashing, CSRF, input validation
✅ **Scalability:** Proper indexing, efficient queries
✅ **Maintainability:** Clear structure, documented code
✅ **Flexibility:** Easy to extend with new features
✅ **Free Services:** Uses Gmail SMTP (no paid APIs)

---

**Document Version:** 1.0
**Last Updated:** January 23, 2026
**Framework:** Django 6.0.1
**Database:** SQLite (dev) / PostgreSQL (production)
