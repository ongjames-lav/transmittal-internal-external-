# Quick Start Guide - Django Email System

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Create Superuser
```bash
python manage.py createsuperuser
```
Follow prompts and create an admin account.

### Step 4: Configure Email (Gmail)

**A. Setup Gmail:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Go to https://myaccount.google.com/apppasswords
4. Select Mail → Windows Computer
5. Copy the 16-character password

**B. Update settings.py:**
```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # App password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
ADMIN_EMAIL = 'admin@example.com'
```

### Step 5: Run Server
```bash
python manage.py runserver
```

### Step 6: Access System
- **Home:** http://127.0.0.1:8000/
- **Register:** http://127.0.0.1:8000/accounts/register/
- **Admin:** http://127.0.0.1:8000/admin/

---

## 📋 Registration Workflow (Step-by-Step)

### For New Users:
1. Click "Register" on home page
2. Fill out registration form:
   ```
   Username: john_doe
   Email: john@example.com
   Password: SecurePass123
   First Name: John
   Last Name: Doe
   Contact: +1234567890
   Company: Acme Corp
   Department: IT
   Location: New York
   Address: 123 Main St, NY 10001
   ```
3. Submit form
4. See success message
5. Check email for confirmation
6. **Status: PENDING** (waiting for admin review)

### For Admins:
1. Login to Admin: http://127.0.0.1:8000/admin/
2. Or use Dashboard: http://127.0.0.1:8000/accounts/admin/dashboard/
3. View pending users
4. Click on a user to review
5. Click "Approve" or "Reject"
6. User receives notification email
7. **Status Updated: APPROVED or REJECTED**

---

## 📧 Email Templates (What Users Receive)

### 1. Registration Confirmation (Sent to User)
```
Subject: Registration Confirmation - Welcome!

Hello [User Name],

Thank you for registering! Your registration has been received.
An administrator will review your details within 24-48 hours.

Keep this email for your records.
```

### 2. Admin Notification (Sent to Admin)
```
Subject: New User Registration - [username]

A new user has registered:
- Username: [username]
- Name: [full name]
- Email: [email]
- Company: [company]
- Department: [department]
- Location: [location]

[Admin Dashboard Link]
```

### 3. Approval Email (Sent to User)
```
Subject: Registration Approved!

Hello [User Name],

Great news! Your registration has been approved.
You can now log in at: http://127.0.0.1:8000/accounts/login/

Use your username and password to access the system.
```

### 4. Rejection Email (Sent to User)
```
Subject: Registration Status Update

Hello [User Name],

Unfortunately, your registration could not be approved at this time.

Reason: [admin notes]

Contact support for more information.
```

---

## 🔐 Test Credentials

**Admin Account (Create this):**
```
Username: admin
Password: (you set this)
Email: admin@example.com
```

**Test User (Create via registration):**
```
Username: testuser
Email: test@example.com
Password: TestPassword123
Status: PENDING (until admin approves)
```

---

## 🛠️ Common Commands

### Database
```bash
# Reset database (WARNING: Deletes all data)
python manage.py flush

# Recreate migrations
python manage.py makemigrations
python manage.py migrate

# View database records
python manage.py dbshell
```

### Testing
```bash
# Run tests
python manage.py test

# Test email (console backend)
# Change EMAIL_BACKEND in settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Admin
```bash
# Create superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword username
```

---

## ✅ Verification Checklist

- [ ] Database created (db.sqlite3)
- [ ] Migrations applied
- [ ] Superuser created
- [ ] Email settings configured
- [ ] Server running without errors
- [ ] Can access home page
- [ ] Can access registration form
- [ ] Can create test user
- [ ] Can log in as admin
- [ ] Can approve/reject users
- [ ] Email sent to admin inbox

---

## 🐛 Quick Troubleshooting

### "Email not sending"
→ Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py
→ Verify Gmail App Password is correct

### "Migration errors"
→ Run: `python manage.py migrate --fake-initial`
→ Then: `python manage.py migrate`

### "Superuser login failed"
→ Run: `python manage.py changepassword admin`

### "Port 8000 in use"
→ Run: `python manage.py runserver 8001`

---

## 📊 File Structure Reference

```
emailsystem/
├── accounts/
│   ├── models.py           ← User & Profile models
│   ├── views.py            ← Registration & approval logic
│   ├── forms.py            ← Form definitions
│   ├── admin.py            ← Admin configuration
│   ├── email_utils.py      ← Email sending functions
│   ├── urls.py             ← URL routing
│   ├── templates/
│   │   └── accounts/
│   │       ├── register.html
│   │       ├── login.html
│   │       ├── user_dashboard.html
│   │       ├── admin_dashboard.html
│   │       └── emails/
│   │           ├── admin_notification.html
│   │           ├── user_confirmation.html
│   │           ├── approval_notification.html
│   │           └── rejection_notification.html
│   └── migrations/         ← Auto-generated
├── emailsystem/
│   └── settings.py         ← Configuration (EDIT THIS for email)
├── templates/
│   └── home.html           ← Home page
├── manage.py               ← Django CLI
├── requirements.txt        ← Dependencies
├── db.sqlite3              ← Database
└── SYSTEM_DOCUMENTATION.md ← Full documentation
```

---

## 🎯 Next Steps

1. **Complete Setup:** Follow the 5-minute setup above
2. **Test Registration:** Create a test user account
3. **Review Admin Panel:** Explore the admin interface
4. **Approve Test User:** Practice the approval workflow
5. **Check Emails:** Verify all notification emails work
6. **Customize:** Update email templates as needed
7. **Deploy:** Follow deployment checklist in full documentation

---

## 📞 Support Resources

- **Full Documentation:** See SYSTEM_DOCUMENTATION.md
- **Django Docs:** https://docs.djangoproject.com/
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Email Issues:** Check console output and email settings

---

**Last Updated:** January 23, 2026
**Difficulty Level:** Beginner-Friendly
**Estimated Setup Time:** 5-10 minutes
