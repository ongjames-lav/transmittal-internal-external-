# Digital Signature Feature - Visual Flow Diagram

## User Flow Diagrams

### 1. UPLOAD SIGNATURE TO PROFILE

```
┌─────────────────────────────────────────────────────────────┐
│                     USER LOGS IN                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  CLICKS EDIT PROFILE                        │
│  (accounts:dashboard → Edit Profile link)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            SEES EDIT PROFILE FORM WITH:                    │
│  ✓ Avatar upload field                                     │
│  ✓ Digital Signature upload field (NEW)                    │
│  ✓ Contact, Department, Company fields                     │
│  ✓ Address field                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  USER SELECTS SIGNATURE   │
         │  IMAGE FILE (JPG/PNG)     │
         └──────────┬────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│          CLICKS SAVE CHANGES                                │
│  ▼ Validation (format, size < 5MB)                         │
│  ▼ File saved to /media/signatures/                        │
│  ▼ Path stored in Profile.digital_signature                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│        SIGNATURE SUCCESSFULLY STORED                        │
│  ✓ Shows in profile edit page next time                    │
│  ✓ Will be used when marking transmittals as received     │
│  ✓ Can be replaced anytime                                │
└─────────────────────────────────────────────────────────────┘
```

---

### 2. MARK TRANSMITTAL AS RECEIVED (WITH STORED SIGNATURE)

```
┌─────────────────────────────────────────────────────────────┐
│         RECEIVER VIEWS TRANSMITTAL DETAIL                   │
│  ✓ Shows: From, To, Description, Status                   │
│  ✓ Button: "Mark as Received"                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│        CLICKS "MARK AS RECEIVED" BUTTON                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│      SEES CONFIRMATION FORM WITH:                          │
│  ✓ Transmittal Details Review                              │
│  ✓ Digital Signature field (OPTIONAL) (NEW)                │
│  ✓ Confirmation checkbox                                    │
│  ✓ Cancel and Submit buttons                               │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼ UPLOADS NEW         ▼ SKIPS UPLOAD
      ┌────────────┐       ┌──────────────────┐
      │ NEW FILE   │       │ AUTO USE STORED  │
      │SELECTED    │       │ SIGNATURE        │
      └──────┬─────┘       └────────┬─────────┘
             │                      │
             └──────────┬───────────┘
                        │
                        ▼
        ┌─────────────────────────────────┐
        │ CHECKS CONFIRMATION CHECKBOX    │
        │ CLICKS "CONFIRM RECEIVED"       │
        └────────────────┬────────────────┘
                         │
                    ▼ VALIDATION
        ┌─────────────────────────────────┐
        │ ✓ File format checked           │
        │ ✓ File size checked (< 5MB)     │
        │ ✓ Confirmation checkbox checked │
        └─────────────┬───────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         TRANSMITTAL MARKED AS RECEIVED                      │
│  ▼ Status changed: in_transit → received                   │
│  ▼ received_at = current timestamp                         │
│  ▼ received_by = current user                              │
│  ▼ receiver_signature = uploaded OR stored signature        │
│  ▼ is_resolved = True                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│       NOTIFICATIONS SENT:                                   │
│  ✓ Sender receives email notification                      │
│  ✓ Custodian receives notification (if exists)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│   REDIRECTED TO TRANSMITTAL DETAIL VIEW                    │
│  ✓ Status now shows: "RECEIVED"                            │
│  ✓ Signature image displays in "Received by" section       │
│  ✓ Date and time of receipt visible                        │
└─────────────────────────────────────────────────────────────┘
```

---

### 3. VIEW & PRINT TRANSMITTAL WITH SIGNATURE

```
┌─────────────────────────────────────────────────────────────┐
│      USER VIEWS RECEIVED TRANSMITTAL                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         DETAIL PAGE SHOWS:                                  │
│  ✓ From, To, Description, Status: RECEIVED                │
│  ✓ Attachment section (if any)                             │
│  ▼ SIGNATURE SECTION (NEW):                                │
│    │                                                         │
│    ├─ Received by: [SIGNATURE IMAGE]                       │
│    ├─ Date: February 6, 2026                               │
│    └─ Time: 2:30 PM                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
    JUST VIEW             CLICK PRINT
          │                     │
          ▼                     ▼
┌──────────────────┐  ┌──────────────────────┐
│ DETAIL PAGE      │  │ PRINT PREVIEW OPENS  │
│ WITH SIGNATURE   │  │                      │
│ DISPLAYED        │  │ Shows full report    │
│                  │  │ with signature       │
│                  │  │ embedded             │
└──────────────────┘  └────────┬─────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
            PRINT TO PAPER        SAVE AS PDF
                    │                     │
                    ▼                     ▼
          ┌──────────────────┐  ┌──────────────────┐
          │ PHYSICAL COPY    │  │ DIGITAL COPY     │
          │ WITH SIGNATURE   │  │ WITH SIGNATURE   │
          └──────────────────┘  └──────────────────┘
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER ACTION                               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│ UPLOAD SIGNATURE     │              │ MARK AS RECEIVED     │
│ IN PROFILE           │              │ WITH SIGNATURE       │
└──────┬───────────────┘              └──────┬───────────────┘
       │                                      │
       ▼                                      ▼
┌──────────────────────┐              ┌──────────────────────┐
│ UserProfileUpdateForm│              │ ReceiveTransmittalForm
│                      │              │                      │
│ - signature field    │              │ - signature field    │
│ - validation         │              │ - confirm field      │
└──────┬───────────────┘              │ - validation         │
       │                              └──────┬───────────────┘
       ▼                                     │
┌──────────────────────┐                     ▼
│ mark_received view   │              ┌──────────────────────┐
│ (in edit profile)    │              │ mark_received view   │
│                      │              │                      │
│ - Save profile       │              │ - Process form       │
│ - Update signal      │              │ - Save transmittal   │
└──────┬───────────────┘              │ - Send notification  │
       │                              └──────┬───────────────┘
       ▼                                     │
┌──────────────────────┐                     ▼
│ /media/signatures/   │              ┌──────────────────────┐
│ [user_sig.jpg]       │              │ /media/transmittal_  │
│                      │              │ signatures/          │
│ (FILE STORAGE)       │              │ [receiver_sig.jpg]   │
└──────┬───────────────┘              │                      │
       │                              │ (FILE STORAGE)       │
       ▼                              └──────┬───────────────┘
┌──────────────────────┐                     │
│ DATABASE:            │                     ▼
│ Profile              │              ┌──────────────────────┐
│ digital_signature    │              │ DATABASE:            │
│ field = path         │              │ Transmittal          │
│                      │              │ receiver_signature   │
│ (PATH STORED)        │              │ field = path         │
└──────┬───────────────┘              │                      │
       │                              │ (PATH STORED)        │
       │                              └──────┬───────────────┘
       │                                     │
       └────────────────────┬────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                       TEMPLATES RENDER                           │
│                                                                  │
│  ├─ edit_profile.html                                           │
│  │  └─ Displays Profile.digital_signature image                │
│  │                                                              │
│  ├─ detail.html                                                │
│  │  └─ Displays Transmittal.receiver_signature image           │
│  │                                                              │
│  ├─ print.html                                                 │
│  │  └─ Embeds Transmittal.receiver_signature for printing      │
│  │                                                              │
│  └─ confirm_status.html                                        │
│     └─ Shows signature upload form                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Database Diagram

```
┌─────────────────────────────────────┐
│         accounts_profile            │
├─────────────────────────────────────┤
│ id (PK)                             │
│ user_id (FK)                        │
│ contact                             │
│ department                          │
│ company                             │
│ location                            │
│ address                             │
│ status                              │
│ avatar                              │
│ digital_signature ◄─────────────┐   │
│ created_at                      │   │
│ updated_at                      │   │
└─────────────────────────────────────┘
                                      │
                                      │
    ┌─────────────────────────────────┘
    │
    │ ONE-TO-MANY
    │
    ▼
┌─────────────────────────────────────┐
│      transmittals_transmittal        │
├─────────────────────────────────────┤
│ id (PK)                             │
│ sender_id (FK → User)               │
│ received_by_id (FK → User)          │
│ reference_number                    │
│ recipient_name                      │
│ recipient_email                     │
│ status                              │
│ sent_at                             │
│ received_at                         │
│ receiver_signature ◄────────────┐   │
│ is_resolved                     │   │
│ driver_remarks                  │   │
│ ... (other fields)              │   │
└─────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┘
        │
        │ STORED IN
        │
        ▼
    ┌──────────────────────┐
    │  /media/ directory   │
    ├──────────────────────┤
    │ /signatures/         │ ◄─ Profile images
    │   user_123_sig.jpg   │
    │   user_456_sig.png   │
    │                      │
    │ /transmittal_        │
    │ signatures/          │
    │   trans_001_sig.jpg  │ ◄─ Transmittal images
    │   trans_002_sig.jpg  │
    └──────────────────────┘
```

---

## Feature Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────┐        ┌──────────────────┐        │
│  │ Edit Profile     │        │ Confirm Status   │        │
│  │ Template         │        │ (Receive) Form   │        │
│  │                  │        │                  │        │
│  │ - Show current   │        │ - Accept upload  │        │
│  │   signature      │        │ - Show checkbox  │        │
│  │ - File input     │        │ - Display help   │        │
│  └────────┬─────────┘        └────────┬─────────┘        │
│           │                           │                   │
└───────────┼───────────────────────────┼───────────────────┘
            │                           │
            ▼                           ▼
┌────────────────────────────────────────────────────────────┐
│                   FORM LAYER                               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────┐        ┌──────────────────┐        │
│  │ UserProfile      │        │ Receive          │        │
│  │ UpdateForm       │        │ TransmittalForm  │        │
│  │                  │        │                  │        │
│  │ - signature      │        │ - signature      │        │
│  │ - validation     │        │ - confirm        │        │
│  └────────┬─────────┘        │ - validation     │        │
│           │                  └────────┬─────────┘        │
└───────────┼──────────────────────────┼───────────────────┘
            │                          │
            ▼                          ▼
┌────────────────────────────────────────────────────────────┐
│                    VIEW LAYER                              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Edit Profile View    │    Mark Received View             │
│  - Process form       │    - Process form                 │
│  - Save profile       │    - Handle signature logic       │
│  - Attach to user     │    - Save transmittal             │
│  - Redirect           │    - Send notifications           │
│                       │    - Redirect                      │
│                                                            │
└───────────────┬───────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│                  MODEL LAYER (ORM)                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Profile.digital_signature         Transmittal.receiver_  │
│  ImageField                        signature ImageField   │
│  - upload_to='signatures/'         - upload_to='transmittal
│  - blank=True                        _signatures/'       │
│  - null=True                       - blank=True          │
│                                    - null=True           │
│                                                            │
└───────────────┬───────────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────┐
│              DATABASE & FILE STORAGE LAYER                 │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Database Entries:         File System:                   │
│  - Profile rows with       - /media/signatures/           │
│    signature paths         - /media/transmittal_          │
│  - Transmittal rows with     signatures/                  │
│    signature paths                                        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## State Diagram - Transmittal Signature States

```
                    ┌─────────────────────┐
                    │  TRANSMITTAL        │
                    │  CREATED            │
                    │ receiver_signature  │
                    │      = NULL         │
                    └──────────┬──────────┘
                               │
                               ▼ (User marks as received)
                    ┌─────────────────────┐
                    │ SIGNATURE UPLOAD    │
                    │   DECISION          │
                    └──────┬──┬──┬────────┘
          ┌─────────────────┘  │  └─────────────────┐
          │                    │                    │
    OPTION 1              OPTION 2            OPTION 3
    (Upload)              (Auto-use)          (Skip)
          │                    │                    │
          ▼                    ▼                    ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ NEW FILE │        │ STORED   │        │ EMPTY    │
    │ RECEIVED │        │ PROFILE  │        │ SIGNAL   │
    └────┬─────┘        │ SIG USED │        └────┬─────┘
         │              └────┬─────┘             │
         │                   │                   │
         └─────────┬─────────┴───────────────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ TRANSMITTAL MARKED  │
        │ AS RECEIVED         │
        │                     │
        │ receiver_signature  │
        │ field updated with: │
        │ - Image path (if    │
        │   sig provided)     │
        │ - NULL (if no sig)  │
        └──────────┬──────────┘
                   │
                   ▼
        ┌─────────────────────┐
        │ TRANSMITTAL SAVED   │
        │ TO DATABASE         │
        │                     │
        │ Ready for display   │
        │ in reports/views    │
        └─────────────────────┘
```

---

## Summary

This visual guide shows:
1. **User flows** for uploading and using signatures
2. **Data flow** through the application layers
3. **Database structure** for storing signature references
4. **System architecture** from UI to storage
5. **State transitions** for transmittal signature handling

All components work together to provide a seamless digital signature feature for transmittal reports.

---

*Created: February 6, 2026*
*Status: Complete and Ready for Implementation*
