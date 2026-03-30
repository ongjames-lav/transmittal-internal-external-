# 📋 CDC Transmittal System — User Manual

> **Version 2.1** | Last Updated: February 2026

---

## Table of Contents

- [Introduction](#introduction)
- [Part 1: Regular User Guide](#part-1-regular-user-guide)
- [Part 2: Custodian Guide](#part-2-custodian-guide)
- [Part 3: Administrator Guide](#part-3-administrator-guide)
- [Appendix: Transmittal Status Flow](#appendix-transmittal-status-flow)

---

## Introduction

### What is the Transmittal System?

The CDC Transmittal System is a web-based application for **tracking documents and packages** sent between offices and locations. Think of it like a registered mail system — every item you send gets a unique tracking number, and everyone involved can see the real-time status of the delivery.

### Who Uses This System?

| Role | What They Do |
|------|-------------|
| **Regular User** | Sends and receives transmittals (documents/packages) |
| **Custodian** | Manages incoming/outgoing transmittals at a specific location (like a front desk officer) |
| **Administrator** | Manages user accounts, approves registrations, and oversees the entire system |

### How Does a Transmittal Work?

Every transmittal follows this simple flow:

```
Sender creates transmittal
        ↓
   📦 IN TRANSIT (on the way)
        ↓
   📍 ARRIVED (custodian confirms it reached the location)
        ↓
   ✅ RECEIVED (recipient confirms they got it)
```

A transmittal can also be **❌ CANCELLED** by the sender — but only while it is still "In Transit."

---

# Part 1: Regular User Guide

This section is for **all users** who send and receive transmittals.

---

## 1.1 Getting Started

### Creating Your Account

1. Open the system in your web browser
2. Click **"Register"** on the login page
3. Fill in the registration form:
   - **Username** — Choose a unique username
   - **First Name** and **Last Name**
   - **Email Address** — Must be unique (you'll receive notifications here)
   - **Password** — At least 8 characters
   - **Confirm Password** — Type your password again
4. Fill in your profile details:
   - **Contact Number** — Your phone number
   - **Department** — Select from the dropdown list
   - **Company/Organization**
   - **Location/City** — Select your office location
   - **Address** — Your full office address
5. Click **"Register"**

> ⏳ **Note:** After registering, your account needs to be **approved by an Administrator** before you can use the system. You'll receive an email when your account is approved.

### Logging In

1. Go to the login page
2. Enter your **Username** and **Password**
3. Click **"Login"**
4. You'll be taken to your **Dashboard**

### Forgot Your Password?

1. On the login page, click **"Forgot Password?"**
2. Enter your registered email address
3. Check your email for a password reset link
4. Click the link and set a new password

---

## 1.2 Your Dashboard

When you log in, you'll see your **Dashboard** — your home page in the system.

### What You'll See:

- **Your profile info** — Name, department, company, and profile picture
- **Stat Cards** showing counts for:
  - 📦 **Incoming** — Transmittals on the way to you
  - 📍 **Arrived** — Transmittals that have reached your location
  - ✅ **Received** — Transmittals you've confirmed receiving
- **Recent Incoming Items** — A quick list of your latest transmittals
- **Recent Arrived Items** — Items waiting for you to pick up

### Quick Actions from Dashboard:

- Click **"Edit Profile"** to update your information
- Click **"Change Password"** to set a new password
- Click **"View All →"** on any stat card to see the full list

---

## 1.3 Editing Your Profile

1. From the Dashboard, click the **"Edit Profile"** button (under your avatar)
2. You can update:
   - **First Name** and **Last Name**
   - **Email Address**
   - **Profile Picture** — Upload a photo of yourself
   - **Digital Signature** — Upload an image of your signature (PNG or JPG). This will be used automatically when you receive transmittals
   - **Contact Number**
   - **Company**
   - **Full Address**
   - **Address**
3. Click **"Save Changes"**

> 🔒 **Note:** Your **Department** and **Assigned Location** are managed by your Administrator and cannot be changed by you. If they are incorrect, contact your admin.

### Changing Your Password

1. From the Dashboard, click **"Change Password"**
2. A popup will appear. Enter:
   - **Current Password**
   - **New Password** (at least 4 characters)
   - **Confirm New Password**
3. Click **"Change Password"**

---

## 1.4 Sending a Transmittal

This is the main action of the system — sending a document or package to someone.

### Step-by-Step:

1. From the sidebar menu, click **"✏️ Compose"** (or navigate to Create Transmittal)
2. The form will **automatically fill in** your information:
   - Your name (sender)
   - Your department
   - Your origin location
   - A preview reference number
3. **Select a Recipient:**
   - Start typing a name in the recipient field
   - A dropdown will show matching registered users
   - Select the person you're sending to
   - Their details (email, company, department, location) will auto-fill
4. **Fill in the details:**
   - **Description** — Describe what you're sending (e.g., "Invoice for January 2026" or "Contract documents — 3 copies")
   - **Remarks** (optional) — Any additional notes
   - **Attachment** (optional) — Upload a file (PDF, image, document, etc.)
5. Click **"Send Transmittal"**
6. You'll see a **success page** with the reference number
7. Both you and the recipient will receive **email notifications**

> 💡 **Tip:** Save the **Reference Number** (e.g., HO-20260210-0001) — you can use it to track your transmittal later.

---

## 1.5 Your Inbox — Transmittals Received

Your Inbox shows all transmittals **sent to you**.

### Navigating the Inbox:

1. Click **"📥 Inbox"** in the sidebar
2. By default, you'll see items with status **"In Transit"** (on the way to you)
3. Use the **status filter tabs** to switch between:
   - **In Transit** — On the way
   - **Arrived** — At your location, waiting for pickup
   - **Received** — Items you've already confirmed receiving
   - **Cancelled** — Items the sender cancelled

### Sorting:

Click on column headers to sort by:
- Sender name
- Description
- Reference number
- Date sent

### Viewing Details:

Click on any transmittal row to see its full details.

---

## 1.6 Sent Items — Transmittals You Sent

This page shows all transmittals **you have sent**.

1. Click **"📤 Sent"** in the sidebar
2. View the status of each transmittal you've sent
3. Use the **status filter** to see:
   - **In Transit** — Still on the way
   - **Arrived** — Reached the destination
   - **Received** — Confirmed received by the recipient
   - **Cancelled** — Items you cancelled

---

## 1.7 Transmittal Detail Page

When you click on a transmittal (from Inbox or Sent), you'll see the full details:

### Information Shown:

- **Reference Number**
- **Sender** — Name, department, company
- **Recipient** — Name, department, company
- **Origin & Destination Locations**
- **Description** and **Remarks**
- **Current Status** with color-coded badge
- **Timeline** — When it was sent, arrived, and received
- **Attachment** — Download any attached file
- **Driver Information** — If added by the custodian
- **Sender Environment** — Device and browser info (for security)

### Actions You Can Take:

| Action | Who Can Do It | When |
|--------|--------------|------|
| **Mark as Received** | You (as recipient) | When status is "In Transit" or "Arrived" |
| **Cancel Transmittal** | You (as sender) | Only when status is "In Transit" |
| **Print** | Sender, recipient, or custodian | Any time |

### Marking a Transmittal as Received:

1. Open the transmittal detail page
2. Click **"Mark as Received"**
3. Optionally upload a **signature** (or your saved digital signature will be used automatically)
4. Confirm the action
5. The sender will be notified by email

### Cancelling a Transmittal:

1. Open the transmittal from your **Sent** list
2. Click **"Cancel"**
3. Enter a **reason for cancellation**
4. Confirm — the recipient and custodian will be notified

---

## 1.8 Printing a Transmittal Report

1. Open the transmittal detail page
2. Click the **"🖨️ Print"** button
3. A printer-friendly version will open
4. Use your browser's print function (Ctrl+P or Cmd+P)

The printed report includes:
- Reference number
- Sender and recipient details
- Description and remarks
- Status and timestamps
- Digital signature (if received)

---

## 1.9 Search

You can search for transmittals using the **search bar** at the top of Inbox or Sent pages. Search works across:

- **Reference Number** (most precise — e.g., "HO-20260210")
- **Recipient or Sender Name**
- **Description**

As you type, **suggestions will appear** — click one to go directly to that transmittal.

---

# Part 2: Custodian Guide

A **Custodian** is a user assigned to manage transmittals at a specific location (e.g., a front desk officer, warehouse clerk, or receiving staff).

> 📌 Everything in Part 1 (Regular User Guide) also applies to you. This section covers **additional features** available only to Custodians.

---

## 2.1 Your Custodian Dashboard

When you log in, you'll see your **Custodian Dashboard** instead of the regular dashboard.

### What You'll See:

- **Your Location** — The location you're assigned to manage
- **Three stat cards:**
  - 📦 **In Transit** — Items heading to your location
  - 📍 **Arrived** — Items you've confirmed as arrived
  - ✅ **Received** — Items confirmed received by the final recipient

### Navigation Tabs:

Your sidebar has special custodian sections:

| Tab | What It Shows |
|-----|--------------|
| **In Transit** | Transmittals coming to your location |
| **Arrived** | Transmittals you've marked as arrived |
| **Received** | Transmittals confirmed received |
| **Outgoing** | Transmittals sent FROM your location |
| **Export Report** | Export received transmittals to Excel |

---

## 2.2 Managing In Transit Items

These are transmittals **heading toward your location** that haven't arrived yet.

1. Click **"In Transit"** in the sidebar
2. You'll see all items currently on the way
3. For each item, you can:
   - Click **"Mark Arrived"** (quick action) to confirm it has reached your location
   - Click on the item to view full details

### Marking an Item as Arrived:

- **Quick Action:** Click the **"Mark Arrived"** button directly from the list — instant confirmation
- **From Detail Page:** Open the transmittal → Click **"Mark as Arrived"** → Confirm

> When you mark something as "Arrived," the sender and recipient will receive an **email notification**.

---

## 2.3 Managing Arrived Items

These are items that have arrived at your location but **haven't been picked up yet** by the recipient.

1. Click **"Arrived"** in the sidebar
2. You'll see items waiting to be received
3. You can:
   - **Mark as Received** — If the recipient picks it up and you confirm receipt on their behalf
   - **Add Driver Remarks** — Enter driver name and vehicle plate number

### Adding Driver Information:

1. Click on the transmittal from the Arrived list
2. In the detail page, look for the **Driver Information** section
3. Enter the driver's name and vehicle plate number
4. Click **"Save"**

> 💡 **Batch Update:** You can update driver information for **multiple transmittals at once** using the batch update feature.

---

## 2.4 Managing Received Items

1. Click **"Received"** in the sidebar
2. View all completed transmittals at your location
3. Use the **date range filter** to narrow results:
   - Set a **"From"** date
   - Set a **"To"** date
   - Click **"Filter"**

---

## 2.5 Viewing Outgoing Items

See all transmittals that were **sent from your location** (by you or other users at your location).

1. Click **"Outgoing"** in the sidebar
2. Use filters to narrow down:
   - **Destination filter** — Select a specific destination location
   - **Status filter** — Choose In Transit, Arrived, or Received

---

## 2.6 Exporting Reports to Excel

You can **download an Excel report** of transmittals for record-keeping or reporting.

### Step-by-Step:

1. Click **"Export Report"** in the sidebar
2. Select options:
   - **Status** — Choose which status to export (Received, Arrived, In Transit, or All)
   - **Date From** — Start date
   - **Date To** — End date
3. Preview the transmittals in the table below
4. Click **"📥 Download Excel"**
5. An `.xlsx` file will download to your computer

### What's Included in the Excel Report:

- Reference Number
- Sender Name & Department
- Recipient Name & Department
- Description
- Date & Time Sent
- Date & Time Received
- Status
- Driver Information

---

## 2.7 Sending Transmittals as Custodian

When you (as a Custodian) send a transmittal, it works slightly differently:

- The transmittal is automatically set to **"Arrived"** status (instead of "In Transit")
- This is because you're sending from the location itself — it's already there

Everything else works the same as regular sending (see Section 1.4).

---

# Part 3: Administrator Guide

**Administrators** manage the entire system — user accounts, departments, locations, and system settings.

> 📌 Everything in Part 1 (Regular User Guide) also applies to you. This section covers **additional admin features**.

---

## 3.1 Admin Dashboard

When you log in as an admin, you'll see the **Admin Dashboard**.

### What You'll See:

- **Stats Overview:**
  - Total registered users
  - Pending approvals
  - Approved users
  - Rejected users
  - Currently active sessions (users online)

- **User List** — A table of all registered users showing:
  - Username
  - Full name
  - Email
  - Company
  - Department
  - Location
  - Status (Pending / Approved / Rejected)
  - Registration date

### Filtering Users:

Use the filter options at the top to narrow the list:
- **By Status** — Pending, Approved, or Rejected
- **By Department** — Select a specific department
- **By Location** — Select a specific location
- **Search** — Type a name, email, username, company, or department

---

## 3.2 Approving User Registrations

When a new user registers, their account starts as **"Pending"** and they cannot send transmittals until approved.

### Approving a Single User:

1. On the Admin Dashboard, find the user in the list
2. Click **"Approve"** next to their name
3. Confirm the approval
4. The user will receive an **approval email** and can now log in

### Rejecting a User:

1. Find the user in the list
2. Click **"Reject"**
3. Optionally enter a **reason for rejection**
4. Confirm — the user will receive a rejection email

### Batch Approving (Multiple Users):

1. Check the boxes next to multiple **Pending** users
2. Click the **"Batch Approve"** button
3. All selected users will be approved at once and receive notification emails

---

## 3.3 Viewing and Editing User Profiles

### Viewing a User:

1. Click on a user's name in the admin dashboard
2. You'll see their complete profile:
   - Personal information
   - Contact details
   - Department and company
   - Registration date
   - Current status
   - Admin notes

### Editing a User:

1. Click **"Edit"** next to the user's name
2. You can update:
   - **First Name** and **Last Name**
   - **Email Address**
   - **Status** — Change from Pending to Approved or Rejected
   - **Admin Notes** — Internal notes visible only to admins
3. Click **"Save Changes"**

### Deleting a User:

1. Click **"Delete"** next to the user's name
2. Confirm the deletion
3. The user account and all associated data will be **permanently removed**

> ⚠️ **Warning:** Deleting a user cannot be undone. Their transmittal history will remain but their account will be removed.

---

## 3.4 Managing Departments

Departments are managed through the **Django Admin Panel**.

1. Go to `/admin/` in your browser
2. Log in with your admin credentials
3. Under **Accounts**, click **"Departments"**
4. Here you can:
   - **Add a new department** — Click "Add Department," enter the name, and save
   - **Edit a department** — Click on the department name to modify it
   - **Deactivate a department** — Uncheck "Is Active" to hide it from registration forms (without deleting it)

---

## 3.5 Managing Locations

Locations determine where transmittals are routed. They're also managed through the Django Admin Panel.

1. Go to `/admin/`
2. Under **Transmittals**, click **"Locations"**
3. For each location, you can set:
   - **Location Name** — e.g., "Main Office," "Pantoc Branch"
   - **Code/Prefix** — Used in reference numbers (e.g., "HO" → HO-20260210-0001)
   - **Assigned Custodian** — The user who manages items at this location
   - **Custodian Email** — Email for notifications (optional, falls back to custodian's user email)
   - **Address** — Physical address of the location
   - **Active** — Uncheck to disable the location

> 💡 **Tip:** Each location should have a custodian assigned. Without a custodian, no one can mark incoming items as "Arrived" at that location.

---

## 3.6 Assigning User Roles

Users can have one of three roles:

| Role | Description |
|------|-------------|
| **Regular User** | Default role — can send and receive transmittals |
| **Custodian** | Manages transmittals at a specific location |
| **Administrator** | Full access to user management and system settings |

### Assigning a Custodian Role:

1. Go to the **Django Admin Panel** (`/admin/`)
2. Under **Accounts**, click **"User Profiles"**
3. Find the user and click their name
4. Change **Role** to **"Custodian"**
5. Set their **Assigned Location** to the location they'll manage
6. Click **"Save"**

### Making an Admin:

1. Go to **Django Admin Panel** → **Users**
2. Find the user and click their name
3. Check **"Staff status"** (and/or **"Superuser status"**)
4. Click **"Save"**

---

## 3.7 User Activity Logs

Monitor who is logged in and track user activity.

1. From the Admin Dashboard, click **"Activity Logs"** (or navigate to the activity logs page)
2. You'll see:
   - **Online Users** — Currently active users with their login time and duration
   - **Offline Users** — Users not currently logged in
   - **Statistics:**
     - Total users
     - Online count
     - Offline count
     - Today's logins
   - **Recent Activity** — Login/logout history with timestamps

### Filtering Activity:

- **By Activity Type** — Login, Logout, or All
- **By User** — Select a specific user

---

## 3.8 Email Notifications (Automatic)

The system automatically sends email notifications for the following events:

| Event | Who Gets Notified |
|-------|------------------|
| New user registration | Admin |
| Registration confirmation | New user |
| Account approved | User |
| Account rejected | User |
| Transmittal sent | Recipient + Destination custodian |
| Transmittal arrived | Sender + Recipient |
| Transmittal received | Sender + Custodian |
| Transmittal cancelled | Recipient + Custodian |

> No action needed — these emails are sent automatically by the system.

---

# Appendix: Transmittal Status Flow

## Status Definitions

| Status | Icon | Meaning |
|--------|------|---------|
| **In Transit** | 📦 | The transmittal has been sent and is on its way to the destination |
| **Arrived** | 📍 | The custodian at the destination has confirmed it arrived at the location |
| **Received** | ✅ | The recipient (or custodian on their behalf) has confirmed they received the item |
| **Cancelled** | ❌ | The sender cancelled the transmittal before it arrived |

## Who Can Change Status?

```
IN TRANSIT ──→ ARRIVED      (Destination Custodian only)
IN TRANSIT ──→ RECEIVED     (Recipient only - bypasses Arrived)
IN TRANSIT ──→ CANCELLED    (Sender only)
ARRIVED    ──→ RECEIVED     (Recipient, Sender, or Destination Custodian)
```

## Reference Number Format

Each transmittal gets a unique reference number:

```
HO-20260210-0001
│   │         │
│   │         └─ Sequence number (resets daily)
│   └─────────── Date (YYYYMMDD)
└─────────────── Location prefix (destination)
```

**Examples:**
- `HO-20260210-0001` → First transmittal to Head Office on Feb 10, 2026
- `PAN-20260210-0003` → Third transmittal to Pantoc on Feb 10, 2026

---

## Quick Reference: Common Tasks

| I want to... | Go to... | Steps |
|--------------|----------|-------|
| Send a document | ✏️ Compose | Fill form → Select recipient → Send |
| Check my incoming items | 📥 Inbox | View list → Click for details |
| Confirm I received something | 📥 Inbox → Click item | Click "Mark as Received" |
| Track something I sent | 📤 Sent | View list → Check status |
| Cancel a transmittal I sent | 📤 Sent → Click item | Click "Cancel" (only if In Transit) |
| Print a transmittal | Any detail page | Click "🖨️ Print" |
| Update my profile | Dashboard → Edit Profile | Update fields → Save |
| Change my password | Dashboard → Change Password | Enter old & new password → Save |

---

> **Need Help?** Contact your system administrator for assistance with account issues, department changes, or technical problems.
