# Transmittal System V2 - Implementation Guide

## Quick Start

The Transmittal System V2 is now **fully implemented and ready to use**. All models, views, templates, and migrations are in place.

---

## 1. Setup Checklist

### Database Setup

```bash
cd emailsystem
python manage.py migrate
```

**Status:** ✅ All migrations applied
- Locations seeded: 5 core locations (Pantoc, Meycauayan, Bpm, Main, Araneta)
- Models created: Location, Transmittal with complete fields
- Profile model updated: Added `role` and `assigned_location` fields

### Email Configuration

Edit `emailsystem/settings.py`:

```python
# Gmail SMTP (Recommended for testing)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use Google App Password, not regular password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Or use your organization's SMTP server
# EMAIL_HOST = 'mail.company.com'
# etc.
```

### Admin Setup

```bash
python manage.py createsuperuser
python manage.py runserver
```

Visit: `http://localhost:8000/admin/`

1. Log in with superuser credentials
2. Go to **Transmittals → Locations**
3. For each of the 5 core locations, assign a **Custodian** (a user with `role='custodian'`)
4. Optionally add address information

---

## 2. User Roles Setup

### Create Test Users

In Django admin or using manage.py:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import Profile

# Create Sender (regular user)
sender = User.objects.create_user('sender@company.com', 'sender@company.com', 'password')
sender.first_name = 'John'
sender.last_name = 'Doe'
sender.save()
sender.profile.department = 'Engineering'
sender.profile.location = 'Pantoc'
sender.profile.role = 'user'
sender.profile.status = 'approved'
sender.profile.save()

# Create Custodian
custodian = User.objects.create_user('custodian@company.com', 'custodian@company.com', 'password')
custodian.first_name = 'Jane'
custodian.last_name = 'Smith'
custodian.save()
custodian.profile.department = 'Operations'
custodian.profile.location = 'Meycauayan'
custodian.profile.role = 'custodian'
custodian.profile.assigned_location = 'Meycauayan'
custodian.profile.status = 'approved'
custodian.profile.save()

# Create Receiver
receiver = User.objects.create_user('receiver@company.com', 'receiver@company.com', 'password')
receiver.first_name = 'Bob'
receiver.last_name = 'Johnson'
receiver.save()
receiver.profile.department = 'Sales'
receiver.profile.location = 'Pantoc'
receiver.profile.role = 'receiver'
receiver.profile.status = 'approved'
receiver.profile.save()

exit()
```

---

## 3. Core Features Overview

### A. Creating a Transmittal

**User:** Sender (role='user' with status='approved')

**URL:** `http://localhost:8000/transmittals/create/`

**Steps:**
1. Navigate to "Create Transmittal" (in navbar if configured)
2. See auto-filled fields:
   - Transmittal Number (e.g., PAN-20260127-0001)
   - From: Current user's name
   - Department: From user's profile
   - Current date/time
3. Fill in:
   - Recipient Name
   - Recipient Email
   - Recipient Department
   - Destination Location (dropdown)
   - Description (required)
   - Remarks (optional)
4. Click "Submit"
5. Confirmation popup
6. Success page with print button

**Email Notifications Sent To:**
- Recipient (Gmail + System)
- Custodian at destination (Gmail)

### B. Custodian Marks as Arrived

**User:** Custodian (role='custodian' assigned to a location)

**URL:** `http://localhost:8000/transmittals/inbox/` → Select transmittal

**Steps:**
1. View transmittal detail
2. Click "Mark as Arrived" button
3. Confirm on confirmation page
4. Status changes to "Arrived"
5. Timestamps recorded

**Notifications Sent To:**
- Sender (System)
- Receiver (System)

### C. Receiver Marks as Received

**User:** Receiver (recipient email matches)

**URL:** `http://localhost:8000/transmittals/inbox/` → Select transmittal

**Available From:**
- **In Transit status** (Direct receipt - receiver gets item directly without custodian)
- **Arrived status** (Standard receipt - after custodian marks as arrived)

**Steps:**
1. View transmittal detail
2. Click "Mark as Received" button
3. Confirm on confirmation page
4. Status changes to "Received"
5. Timestamps recorded (received_at, received_by)

**Notifications Sent To:**
- Sender (Gmail + System)
- Custodian (System) - if custodian exists for the destination location

**Note:** The receiver can bypass the custodian step and mark the transmittal as received directly if they receive the item physically without custodian involvement. This is useful in real-world scenarios where items are picked up directly.

### D. Cancel Transmittal

**User:** Sender (only)

**URL:** `http://localhost:8000/transmittals/sent/` → Select transmittal → "Cancel"

**Conditions:**
- Only available if status is "In Transit"
- Cannot cancel after custodian marks as arrived

**Steps:**
1. Click "Cancel Transmittal"
2. View transmittal details and warnings
3. Optionally enter reason
4. Confirm cancellation
5. Status changes to "Cancelled"

**Notifications Sent To:**
- Receiver (System)
- Custodian (System)

### E. Print Transmittal

**URL:** `http://localhost:8000/transmittals/print/<id>/`

**Access:**
- Sender (own transmittals)
- Recipient (received transmittals)
- Staff (all)

**Features:**
- Professional CDC MFG CORP branding
- All transmittal details
- Signature lines for physical acceptance
- Print-friendly styling
- Browser print dialog (Ctrl+P)

### F. Dashboard & Navigation

**URL:** `http://localhost:8000/transmittals/dashboard/`

**Shows:**
- Recent sent (5 items)
- Recent received (5 items)
- Counts
- Quick navigation links

### G. Inbox (Received)

**URL:** `http://localhost:8000/transmittals/inbox/`

**Features:**
- List of all received transmittals
- Status badges
- Search/filter
- Bulk delete to trash
- Click to view detail

### H. Sent

**URL:** `http://localhost:8000/transmittals/sent/`

**Features:**
- List of all sent transmittals
- Status badges
- Cancel option (if In Transit)
- Search/filter
- Bulk delete to trash

### I. Trash & Restore

**URL:** `http://localhost:8000/transmittals/trash/`

**Features:**
- Soft-deleted items
- Restore to inbox/sent
- Permanent delete/purge
- Separate for sent/received items

---

## 4. Admin Interface

### Location Management

**URL:** `http://localhost:8000/admin/transmittals/location/`

**Actions:**
- ✅ Add new locations
- ✅ Edit existing locations
- ✅ Delete locations
- ✅ Assign custodians
- ✅ Toggle active status
- ✅ View email addresses

**Required Fields When Creating:**
- Name (e.g., "Pantoc")
- Prefix (e.g., "PAN") - must be unique
- Custodian (ForeignKey to User)

### Transmittal Management

**URL:** `http://localhost:8000/admin/transmittals/transmittal/`

**Features:**
- Filter by status, location, date
- Search by reference number, sender, recipient
- View all transmittal details
- Readonly timestamps
- View status history

---

## 5. Reference Number Generation

### Format

```
[LOCATION_PREFIX]-[YYYYMMDD]-[SEQUENCE]
```

### Examples

**Same location, same day:**
- PAN-20260127-0001
- PAN-20260127-0002
- PAN-20260127-0003

**Different location, same day:**
- MY-20260127-0001
- BP-20260127-0001

**Different day:**
- PAN-20260128-0001
- MY-20260128-0001

### How It Works

1. User selects destination location during transmittal creation
2. Origin location is automatically set from user's profile
3. System generates reference number using origin location's prefix
4. Example: User at Pantoc location creates transmittal
   - Prefix: PAN
   - Date: Today
   - Sequence: Auto-incremented based on transmittals created today from Pantoc
   - Result: PAN-20260127-0005

---

## 6. Status Lifecycle Diagram

```
CREATE TRANSMITTAL
       ↓
   [IN_TRANSIT]
   ╱ | \
  ╱  |  \
 /   |   \
CANCEL   CUSTODIAN MARKS ARRIVED    RECEIVER MARKS RECEIVED (Direct)
 ↓       ↓                           ↓
[CANCELLED]  [ARRIVED]          [RECEIVED]
 ↓           ↓                    ↓
(END)   RECEIVER MARKS RECEIVED  (END)
         ↓
      [RECEIVED]
         ↓
       (END)
```

### Workflow Scenarios

**Scenario 1: Standard Workflow (Custodian involved)**
```
Sender creates → In Transit → Custodian marks Arrived → Receiver marks Received → End
```

**Scenario 2: Direct Receipt (Receiver bypasses custodian)**
```
Sender creates → In Transit → Receiver marks Received directly → End
(Useful when receiver picks up item directly without custodian handling)
```

**Scenario 3: Cancellation**
```
Sender creates → In Transit → Sender cancels → Cancelled → End
(Can only cancel while In Transit)
```

### Valid Transitions

- `in_transit` → `arrived` (Custodian only)
- `in_transit` → `received` (Receiver only - direct receipt, bypasses custodian)
- `arrived` → `received` (Receiver only - standard receipt after custodian marks arrived)
- `in_transit` → `cancelled` (Sender only)

### Invalid Transitions

- Cannot go back to previous status
- Cannot skip steps except receiver can skip "arrived" and go directly to "received"
- Cancelled transmittals are final

---

## 7. Database Schema Quick Reference

### Location Table

```
id          | Integer (PK)
name        | CharField(100)
prefix      | CharField(10) - UNIQUE
custodian_id| ForeignKey(User)
custodian_email | EmailField
address     | TextField
is_active   | Boolean (True)
created_at  | DateTimeField
updated_at  | DateTimeField
```

### Transmittal Table

```
id                      | Integer (PK)
reference_number        | CharField(30) - UNIQUE
sender_id              | ForeignKey(User)
sender_department      | CharField(255)
origin_location_id     | ForeignKey(Location)
recipient_name         | CharField(255)
recipient_email        | EmailField
recipient_department   | CharField(255)
destination_location_id| ForeignKey(Location)
description            | TextField
remarks                | TextField (nullable)
status                 | CharField(20) [in_transit|arrived|received|cancelled]
sent_at                | DateTimeField (auto_now_add)
arrived_at             | DateTimeField (nullable)
received_at            | DateTimeField (nullable)
cancelled_at           | DateTimeField (nullable)
arrived_by_id          | ForeignKey(User, nullable)
received_by_id         | ForeignKey(User, nullable)
sender_deleted         | Boolean (False)
recipient_deleted      | Boolean (False)
sender_deleted_at      | DateTimeField (nullable)
recipient_deleted_at   | DateTimeField (nullable)
sender_purged          | Boolean (False)
recipient_purged       | Boolean (False)
is_resolved            | Boolean (False)
date_created           | DateField (auto_now_add)
time_created           | TimeField (auto_now_add)
```

---

## 8. Testing the System

### Test Scenario 1: Full Workflow

1. **Create Transmittal**
   - Login as Sender
   - Go to `/transmittals/create/`
   - Fill in details
   - Submit

2. **Receiver Gets Notification**
   - Check receiver's email
   - Check inbox list at `/transmittals/inbox/`

3. **Custodian Marks Arrived**
   - Login as Custodian
   - Go to inbox
   - Find transmittal
   - Click "Mark as Arrived"
   - Confirm

4. **Receiver Marks Received**
   - Login as Receiver
   - Go to inbox
   - Find transmittal (now shows "Arrived")
   - Click "Mark as Received"
   - Confirm

5. **Sender Gets Confirmation**
   - Login as Sender
   - Go to sent page
   - View transmittal
   - Status should be "Received"

### Test Scenario 2: Cancellation

1. **Create Transmittal** (as Sender)
2. **Cancel Before Arrival** (as Sender)
   - Go to sent page
   - Click cancel button
   - Confirm
   - Status → "Cancelled"
3. **Verify Notifications** (Receiver/Custodian get notified)

### Test Scenario 3: Print & Signature

1. **View Transmittal Detail**
2. **Click Print Button**
3. **Verify Content:**
   - CDC MFG CORP header
   - Reference number
   - Origin/Destination info
   - Description/Remarks
   - Signature lines
4. **Print to PDF** (Ctrl+P)

### Test Scenario 4: Trash & Restore

1. **Create Transmittal** (as Sender)
2. **Soft Delete:**
   - Go to sent page
   - Select transmittal
   - Delete (moves to trash)
3. **View Trash:**
   - Go to `/transmittals/trash/`
   - Verify transmittal appears
4. **Restore:**
   - Click restore
   - Verify reappears in sent
5. **Permanent Delete:**
   - Go to trash again
   - Permanently delete
   - Cannot restore

---

## 9. Common Tasks

### Assign a User as Custodian for a Location

```
1. Go to /admin/transmittals/location/
2. Click on the location (e.g., "Pantoc")
3. Under "Custodian Assignment":
   - Select the user from "Custodian" dropdown
   - Optionally enter custodian email
4. Click Save
```

### Create a New Location

```
1. Go to /admin/transmittals/location/
2. Click "Add Location"
3. Fill in:
   - Name: e.g., "Antipolo"
   - Prefix: e.g., "ATP" (must be unique)
   - Custodian: Select from dropdown
   - Address: Optional
   - Active: Check to enable
4. Click Save
```

### Approve a User's Registration

```
1. Go to /admin/accounts/profile/
2. Find the user
3. Change status from "pending" to "approved"
4. Click Save
5. User receives approval email
6. User can now create transmittals
```

### Set User Role

```
In Django shell or admin:
user.profile.role = 'custodian'  # or 'user', 'receiver'
user.profile.assigned_location = 'Meycauayan'  # if custodian
user.profile.save()
```

### View All Transmittals for a Custodian's Location

```
1. Go to /admin/transmittals/transmittal/
2. Filter by "Destination Location"
3. Select the location
4. View all incoming transmittals
```

---

## 10. Email Configuration Examples

### Gmail (Recommended for Testing)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # NOT your regular password!
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Note: Generate app password at https://myaccount.google.com/apppasswords
```

### Corporate SMTP Server

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.company.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'emailsystem@company.com'
EMAIL_HOST_PASSWORD = 'password'
DEFAULT_FROM_EMAIL = 'emailsystem@company.com'
```

### Console Backend (Development/Testing Only)

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Emails will print to console instead of being sent
```

### File Backend (Development/Testing Only)

```python
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
# Emails saved to files for inspection
```

---

## 11. Troubleshooting

### Issue: "Location not found" when creating transmittal

**Solution:**
- Ensure locations are seeded: `python manage.py migrate`
- Check admin panel: `http://localhost:8000/admin/transmittals/location/`
- Verify location has `is_active = True`

### Issue: Emails not sending

**Solution:**
- Check email configuration in settings.py
- Test with console backend first
- Verify credentials
- Check spam folder
- Enable "less secure apps" if using Gmail (old accounts)

### Issue: Can't mark as arrived (button not showing)

**Solution:**
- Verify you're logged in as the custodian for that location
- Verify transmittal status is "In Transit"
- Check that custodian is properly assigned in admin

### Issue: Can't mark as received

**Solution:**
- Verify transmittal status is "Arrived" (not "In Transit")
- Verify your email matches recipient email
- Try logging out and back in

### Issue: Reference number not generating

**Solution:**
- Verify origin location is set on transmittal
- Check location has a prefix
- Restart Django server
- Clear browser cache

---

## 12. Template Files Location

```
emailsystem/
├── transmittals/
│   └── templates/
│       └── transmittals/
│           ├── create_transmittal.html     ← Create form
│           ├── transmittal_success.html    ← Success page
│           ├── detail.html                 ← Detail/read view
│           ├── inbox.html                  ← List (sent/received)
│           ├── trash.html                  ← Trash/deleted
│           ├── print.html                  ← Print format ✨ NEW
│           ├── cancel_transmittal.html     ← Cancel confirmation ✨ NEW
│           └── confirm_status.html         ← Status update confirmation ✨ NEW
└── accounts/
    └── templates/
        └── accounts/
            └── gmail_base.html             ← Base template
```

---

## 13. URL Map

```
Dashboard:       /transmittals/dashboard/
Create:          /transmittals/create/
Success:         /transmittals/success/
Inbox:           /transmittals/inbox/
Sent:            /transmittals/sent/
Detail:          /transmittals/detail/<id>/
Print:           /transmittals/print/<id>/
Mark Arrived:    /transmittals/mark-arrived/<id>/
Mark Received:   /transmittals/mark-received/<id>/
Cancel:          /transmittals/cancel/<id>/
Trash:           /transmittals/trash/
Delete (soft):   /transmittals/delete/
Restore:         /transmittals/restore/
Permanent Delete:/transmittals/permanent-delete/
Admin Locations: /admin/transmittals/location/
Admin Transmit:  /admin/transmittals/transmittal/
```

---

## 14. Best Practices

1. **Email Configuration**
   - Always use environment variables for sensitive data
   - Test with console backend first
   - Monitor mail logs

2. **User Management**
   - Approve users before they can send transmittals
   - Assign custodians to all locations
   - Keep user roles consistent

3. **Location Management**
   - Create locations before assigning custodians
   - Deactivate locations instead of deleting (preserves data)
   - Use clear, consistent naming

4. **Monitoring**
   - Log all transmittal actions
   - Review admin dashboard regularly
   - Monitor failed email deliveries
   - Check trash regularly for orphaned items

5. **Security**
   - Use HTTPS in production
   - Require strong passwords
   - Implement 2FA for admin accounts
   - Regular backups of database

---

## 15. Getting Help

For issues or questions:

1. Check the **TRANSMITTAL_SYSTEM_V2.md** for detailed documentation
2. Review this Implementation Guide
3. Check Django logs: `python manage.py shell` and query models
4. Test with different scenarios (see Testing section)
5. Check admin panel for data consistency

---

**Version:** 2.0.0
**Last Updated:** January 27, 2026
**Status:** ✅ Ready for Production

---

## Next Steps

1. ✅ Run migrations
2. ✅ Configure email settings
3. ✅ Create test users with different roles
4. ✅ Test complete workflow
5. ✅ Configure production email server
6. ✅ Set up logging and monitoring
7. ✅ Deploy to production
8. ✅ Train users on new system
