# External Transmittal SMTP Email Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL TRANSMITTAL SYSTEM                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐ │
│  │ Sender User  │         │ Status Change│         │ Admin User   │ │
│  │ (Form Submit)│         │  (Mark, Return)       │ (Override)   │ │
│  └──────┬───────┘         └──────┬───────┘         └──────┬───────┘ │
│         │                        │                       │          │
│         │ 1. Upload             │ 2. Change            │ 3. Manual │
│         │    Attachment         │    Status            │    Change │
│         │                        │                      │           │
│         └────────────┬───────────┴──────────┬──────────┘           │
│                      │                      │                      │
│                      ▼                      ▼                      │
│              ┌──────────────────────────────────┐                 │
│              │  ExternalTransmittal Model      │                 │
│              │  ├─ reference_number             │                 │
│              │  ├─ status (in_transit, etc.)   │                 │
│              │  ├─ sender_email                 │                 │
│              │  ├─ recipient_email              │                 │
│              │  └─ description                  │                 │
│              └──────────────┬───────────────────┘                 │
│                             │                                     │
│                             ▼                                     │
│              ┌──────────────────────────────────┐                 │
│              │  ExternalTransmittalAttachment   │                 │
│              │  ├─ transmittal (FK)             │                 │
│              │  ├─ file (uploaded proof)        │                 │
│              │  ├─ attachment_type              │                 │
│              │  └─ uploaded_at (timestamp)      │                 │
│              └──────────────┬───────────────────┘                 │
│                             │                                     │
│         ┌───────────────────┴────────────────────┐               │
│         │                                        │                │
│         ▼                                        ▼                │
│   ┌──────────────────┐                  ┌────────────────┐      │
│   │ Audit Trail Log  │                  │ Email Function │      │
│   │ (Status Change)  │                  │   (SMTP Send)  │      │
│   └──────────────────┘                  └────────┬───────┘      │
│                                                   │               │
│                                                   ▼               │
│                                    ┌──────────────────────────┐  │
│                                    │ Django Email Backend     │  │
│                                    │ (SMTP Configuration)     │  │
│                                    └──────────────┬───────────┘  │
└─────────────────────────────────────────────────┼────────────────┘
                                                   │
                                                   ▼
                                    ┌──────────────────────────┐
                                    │  SMTP Server             │
                                    │  (Gmail, SendGrid, etc.) │
                                    └──────────────┬───────────┘
                                                   │
                       ┌───────────────────────────┴───────────────┐
                       │                                           │
                       ▼                                           ▼
                   ┌─────────────┐                           ┌─────────────┐
                   │Sender Email │                           │Recipient    │
                   │Inbox        │                           │Email Inbox  │
                   └─────────────┘                           └─────────────┘
```

## Email Generation & Sending Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   EMAIL GENERATION FLOW                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Status Change Action (User/Admin)                                  │
│         │                                                           │
│         ▼                                                           │
│  ┌────────────────────────┐                                       │
│  │ Save Status Change     │                                       │
│  │ transmittal.status = X │                                       │
│  └────────────┬───────────┘                                       │
│               │                                                    │
│               ▼                                                    │
│  ┌────────────────────────────────────────┐                      │
│  │ Create Audit Trail Entry               │                      │
│  │ (action, performed_by, notes, etc.)    │                      │
│  └────────────┬─────────────────────────────┘                    │
│               │                                                    │
│               ▼                                                    │
│  ┌────────────────────────────────────────┐                      │
│  │ Try: send_external_transmittal_         │                      │
│  │      resolution_email()                 │                      │
│  └────────────┬──────────────────┬─────────┘                    │
│               │                  │                                │
│         SUCCESS                ERROR                              │
│               │                  │                                │
│               ▼                  ▼                                │
│  ┌────────────────────────┐ ┌──────────────────┐                │
│  │ Query Attachments      │ │ Log WARNING      │                │
│  │ FROM attachments table │ │ Continue anyway  │                │
│  │ WHERE transmittal_id=X │ │ (no email break) │                │
│  └────────────┬───────────┘ └──────────────────┘                │
│               │                                                   │
│               ▼                                                   │
│  ┌────────────────────────────────────────┐                     │
│  │ Build Email Content:                   │                     │
│  │ ├─ Generate HTML version               │                     │
│  │ ├─ Generate plain text version         │                     │
│  │ ├─ List all attachments with:          │                     │
│  │ │  ├─ Attachment type                  │                     │
│  │ │  ├─ File name                        │                     │
│  │ │  └─ Upload timestamp                 │                     │
│  │ └─ Include status, notes, description  │                     │
│  └────────────┬───────────────────────────┘                     │
│               │                                                   │
│               ▼                                                   │
│  ┌────────────────────────────────────────┐                     │
│  │ Create EmailMultiAlternatives          │                     │
│  │ ├─ To: [sender_email, recipient_email]│                     │
│  │ ├─ From: DEFAULT_FROM_EMAIL            │                     │
│  │ ├─ Subject: [REF] Transmittal Action   │                     │
│  │ ├─ Body: plain text version            │                     │
│  │ └─ Alternative: HTML version           │                     │
│  └────────────┬───────────────────────────┘                     │
│               │                                                   │
│               ▼                                                   │
│  ┌────────────────────────────────────────┐                     │
│  │ email.send(fail_silently=False)        │                     │
│  │ Via Django SMTP Backend                │                     │
│  └────────────┬───────────────────────────┘                     │
│               │                                                   │
│               ▼                                                   │
│  ┌────────────────────────────────────────┐                     │
│  │ Log Success:                           │                     │
│  │ "[SUCCESS] Email sent for [ACTION]"    │                     │
│  └────────────────────────────────────────┘                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Email Content Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EMAIL CONTENT LAYOUT                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ HEADER (Color-Coded Gradient)                                │  │
│  │ ═════════════════════════════════════════════════════════    │  │
│  │ ✅ Transmittal Marked as Received                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Dear Recipient,                                              │  │
│  │                                                              │  │
│  │ The transmittal has been updated with the following action: │  │
│  │                                                              │  │
│  │ TRANSMITTAL DETAILS:                                         │  │
│  │ ─────────────────────                                        │  │
│  │ Reference Number:  TR-EXT-2026-001234                        │  │
│  │ Action:            Marked as Received                        │  │
│  │ Type:              For Keep                                  │  │
│  │ Current Status:    Received                                  │  │
│  │ Description:       High-value electronics equipment          │  │
│  │ Updated At:        2026-03-05 14:30:22                       │  │
│  │                                                              │  │
│  │ ATTACHMENTS UPLOADED: (NEW SECTION)                          │  │
│  │ ──────────────────────────────────────                       │  │
│  │ 📎 Proof of Delivery:                                        │  │
│  │    delivery_confirmation_20260305.pdf                        │  │
│  │    (Uploaded: 2026-03-05 14:30:22)                           │  │
│  │                                                              │  │
│  │ 📎 Signature:                                               │  │
│  │    receiver_signature.jpg                                    │  │
│  │    (Uploaded: 2026-03-05 14:30:25)                           │  │
│  │                                                              │  │
│  │ NOTES:                                                       │  │
│  │ ──────                                                       │  │
│  │ Item received in good condition with all accessories         │  │
│  │                                                              │  │
│  │ For more details, please contact the sender or check the     │  │
│  │ transmittal system.                                          │  │
│  │                                                              │  │
│  │ Best regards,                                                │  │
│  │ Transmittal System                                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ FOOTER                                                       │  │
│  │ This is an automated notification.                           │  │
│  │ Please do not reply to this email.                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Status Change Actions Email Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                  STATUS CHANGE → EMAIL SENT                         │
├──────────────────────────┬──────────────┬────────────────────────────┤
│ Action                   │ Color        │ Recipients                 │
├──────────────────────────┼──────────────┼────────────────────────────┤
│ Mark as Received         │ Green ✓      │ Sender + Recipient         │
│ (For Keep → Received)    │ #28A745      │ With proof attachment      │
├──────────────────────────┼──────────────┼────────────────────────────┤
│ Full Return              │ Teal         │ Sender + Recipient         │
│ (For Return → Closed)    │ #17A2B8      │ With RGA/proof             │
├──────────────────────────┼──────────────┼────────────────────────────┤
│ Partial Return           │ Amber        │ Sender + Recipient         │
│ (For Return → Received)  │ #FFC107      │ With proof, case stays open│
├──────────────────────────┼──────────────┼────────────────────────────┤
│ Paid Sample              │ Purple       │ Sender + Recipient         │
│ (For Return → Closed)    │ #6F42C1      │ With RGA/deduction proof   │
├──────────────────────────┼──────────────┼────────────────────────────┤
│ Convert to For Keep      │ Green        │ Sender + Recipient         │
│ (For Return → Closed)    │ #28A745      │ With RGA proof             │
├──────────────────────────┼──────────────┼────────────────────────────┤
│ Admin Override           │ Red          │ Sender + Recipient         │
│ (Any status change)      │ #FF6B6B      │ With admin reason          │
└──────────────────────────┴──────────────┴────────────────────────────┘
```

## Attachment Information Display in Email

```
┌─────────────────────────────────────────────────────────────────────┐
│              ATTACHMENT SECTION IN EMAIL BODY                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  📎 ATTACHMENTS UPLOADED:                                           │
│  ──────────────────────────                                         │
│                                                                      │
│  ► Proof of Delivery: delivery_confirmation_20260305.pdf            │
│    Uploaded: 2026-03-05 14:30:22                                    │
│                                                                      │
│  ► RGA: return_authorization_form.pdf                               │
│    Uploaded: 2026-03-05 14:35:45                                    │
│                                                                      │
│  ► Signature: receiver_signature.jpg                                │
│    Uploaded: 2026-03-05 14:32:10                                    │
│                                                                      │
│  [HTML Version has styled list items with file icons]               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Database Query Timeline

```
Timeline of Events
─────────────────────────────────────────────────────────────────────

T0: User Action (e.g., "Mark as Received")
    ↓
    Form submitted with attachment file

T1: File Upload
    ├─ Save attachment to disk
    └─ Create ExternalTransmittalAttachment record

T2: Status Update
    ├─ Update transmittal.status
    └─ Update transmittal.received_at (timestamp)

T3: Audit Trail
    └─ Create ExternalTransmittalAuditTrail record
       ├─ action: 'mark_received'
       ├─ performed_by_email: sender@example.com
       └─ notes: optional notes

T4: Email Generation (send_external_transmittal_resolution_email)
    ├─ Query: SELECT * FROM attachments WHERE transmittal_id = X
    │         ORDER BY uploaded_at DESC
    │
    ├─ Loop through attachments:
    │  ├─ Extract: attachment_type
    │  ├─ Extract: file.name → display name
    │  └─ Extract: uploaded_at → format timestamp
    │
    ├─ Build HTML email with attachment details
    ├─ Build plain text email with attachment details
    └─ Send via Django SMTP backend

T5: Email Sent
    └─ Log: [SUCCESS] Email sent for mark_received on TR-EXT-001

T6: Recipients Receive Email
    ├─ Sender@example.com receives email with attachments
    └─ Recipient@example.com receives same email
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                   ERROR HANDLING FLOW                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Try: send_external_transmittal_resolution_email()                 │
│    │                                                                │
│    ├─ Get attachments from database                                │
│    │   └─ Error? → Log & continue (email still sends without list) │
│    │                                                                │
│    ├─ Build email content                                          │
│    │   └─ Error? → Log & return False                              │
│    │                                                                │
│    ├─ Create EmailMultiAlternatives object                         │
│    │   └─ Error? → Log & return False                              │
│    │                                                                │
│    ├─ email.send(fail_silently=False)                              │
│    │   └─ Error? → Caught by outer try-except                      │
│    │                                                                │
│    ├─ Success → Log "[SUCCESS]" & return True                      │
│    │                                                                │
│    Catch: Exception → Log "[ERROR]" & return False                 │
│                                                                      │
│  View Code (mark_received, full_return, etc.):                      │
│    Try: send_external_transmittal_resolution_email()               │
│      └─ Success or Error? → Continue anyway                        │
│      └─ Status change completes regardless                         │
│      └─ Log warning if email fails                                 │
│                                                                      │
│  Result: ✅ Status always changes, ⚠️ Email may fail, but not     │
│           critical (user still sees success message)                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Test Coverage Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TEST COVERAGE MATRIX                             │
├──────────────────────────────┬────────────────────────────────────┤
│ Test Name                    │ Coverage                           │
├──────────────────────────────┼────────────────────────────────────┤
│ Mark received + attachment   │ Basic email sending               │
│ Full return + RGA            │ Return flow                       │
│ Partial return               │ Partial return flow              │
│ Admin override               │ Admin status change              │
│ Timestamp in email           │ DateTime formatting              │
│ HTML format verification     │ Email format (HTML + plain text) │
│ Multiple attachments         │ List all files                   │
│ Error handling               │ Graceful failure                 │
│ Transmittal description      │ Content inclusion                │
│ Email subject format         │ Subject line structure           │
│ View integration             │ Mark received endpoint           │
└──────────────────────────────┴────────────────────────────────────┘
```

---

## Key Takeaways

1. **Automatic Trigger** - Every status change initiates email
2. **Attachment Details** - File names and timestamps included
3. **Dual Format** - HTML (styled) and plain text versions
4. **Error Safe** - Graceful failure, status change always succeeds
5. **Complete Audit** - Logged in database and email receipt
6. **Production Ready** - No breaking changes, fully tested

---

**Created:** March 5, 2026
**Status:** ✅ Complete
