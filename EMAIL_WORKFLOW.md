# Email Workflow Documentation

## Complete User Registration & Approval Workflow

### **Step 1: User Registration**
**Action:** User fills out registration form and submits

**Automatic Emails Sent:**
1. **Email to ADMIN** ✉️
   - Subject: "New User Registration"
   - Content: All user details in a professional table format
   - Includes: Approval/Reject buttons in admin dashboard

2. **Email to USER** ✉️
   - Subject: "Registration Confirmation"
   - Content: Welcome message, next steps
   - Status: "Your registration is pending approval"

**Database State:** 
- User created: `is_active = True`
- Profile created: `status = 'pending'`

---

### **Step 2: Admin Review in Admin Panel**
**Location:** `/admin/accounts/profile/`

**Admin sees:**
- Username
- Full Name
- Email
- Company/Department
- Status Badge (Yellow = Pending)
- Quick Action Buttons (Approve | Reject)

**Status Options Displayed:**
- 🟡 **Pending** - Awaiting admin approval
- 🟢 **Approved** - Account activated
- 🔴 **Rejected** - Registration declined

---

### **Step 3: Admin Approves User**
**Action:** Admin clicks "Approve" button OR uses bulk approve action

**What Happens:**
1. Profile status changes to `'approved'`
2. Profile is saved to database
3. Approval email is automatically sent to user

**Email Sent to USER** ✉️
- Subject: "Registration Approved!"
- Content: 
  - Congratulations message
  - Login link: `/accounts/login/`
  - List of features available
  - Support contact info
- Status: Account is now ACTIVATED ✓

---

### **Step 4: Admin Rejects User (Optional)**
**Action:** Admin clicks "Reject" button

**What Happens:**
1. Admin enters rejection reason
2. Profile status changes to `'rejected'`
3. Reason stored in `admin_notes`
4. Rejection email is automatically sent to user

**Email Sent to USER** ✉️
- Subject: "Registration Status Update"
- Content:
  - Rejection notification
  - Reason for rejection
  - Support contact for questions
- Status: Account DENIED ✗

---

## Email Timeline Example

```
TIME    EVENT                                  EMAIL SENT TO
────────────────────────────────────────────────────────────────
11:00   User submits registration form        ✉️ ADMIN (notification)
        ↓                                      ✉️ USER (confirmation)
        
11:05   Admin reviews pending users in        (no email)
        /admin/accounts/profile/
        
11:10   Admin clicks "APPROVE"                ✉️ USER (approval)
        Profile status → 'approved'
        
11:12   User receives approval email          
        Can now login at /accounts/login/
```

---

## Email Templates Used

| Event | Template File | Subject |
|-------|---------------|---------|
| User Registration (Admin Notification) | `admin_notification.html` | New User Registration |
| User Registration (User Confirmation) | `user_confirmation.html` | Registration Confirmation |
| Admin Approval | `approval_notification.html` | Registration Approved! |
| Admin Rejection | `rejection_notification.html` | Registration Status Update |

---

## Database Fields Involved

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `Profile.status` | CharField | pending, approved, rejected | Track registration stage |
| `Profile.admin_notes` | TextField | (any text) | Store rejection reason or admin comments |
| `User.is_active` | BooleanField | True/False | Control login access |
| `Profile.created_at` | DateTime | (auto) | Registration timestamp |

---

## How to Test

### 1. **Test Registration Email**
```bash
1. Go to http://127.0.0.1:8000/accounts/register/
2. Fill out form and submit
3. Check:
   - Admin receives notification email
   - User receives confirmation email
   - Profile status is 'pending' in admin
```

### 2. **Test Approval Email**
```bash
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser account
3. Click "Profiles" under Accounts
4. Select a pending user
5. Click "APPROVE" button
6. Check:
   - User receives approval email
   - Status changes to 'approved' in admin
   - User can now login
```

### 3. **Test Rejection Email**
```bash
1. Go to /admin/accounts/profile/
2. Select a pending user
3. Click "REJECT" button
4. Enter reason: "Email domain not verified"
5. Check:
   - User receives rejection email with reason
   - Status changes to 'rejected' in admin
   - User cannot login
```

---

## Gmail Configuration Required

In `emailsystem/settings.py`:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use Gmail App Password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
ADMIN_EMAIL = 'admin@yourdomain.com'
SUPPORT_EMAIL = 'support@yourdomain.com'
```

---

## Admin Panel Status Display

The admin panel shows:
- **Registration Status** dropdown with three choices:
  - Pending (Yellow badge 🟡)
  - Approved (Green badge 🟢)
  - Rejected (Red badge 🔴)

- **Quick Actions** (for pending users):
  - Approve button (sends approval email)
  - Reject button (prompts for reason, sends rejection email)

---

## Summary

✅ User Registration → 2 emails sent (Admin + User)  
✅ Admin Reviews in Panel → Status visible (pending/approved/rejected)  
✅ Admin Approves → Approval email sent to user automatically  
✅ Admin Rejects → Rejection email sent with reason  
✅ All emails are HTML formatted with professional styling  
✅ All emails use Gmail SMTP (free service)  
