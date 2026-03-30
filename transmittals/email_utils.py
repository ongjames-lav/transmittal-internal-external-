"""
Email utilities for transmittal notifications V2.

Sends email notifications to:
- Receiver and Custodian when transmittal is created (In Transit)
- Sender and Receiver when status changes to Arrived
- Sender when status changes to Received
"""
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
import mimetypes
import os


def send_transmittal_email(transmittal):
    """
    Send transmittal notifications when created.
    - Receiver: Internal email (green)
    - Origin Custodian (Sender's Custodian): External email (red) - can view in Outgoing
    - Destination Custodian (Receiver's Custodian): External email (red)
    - Sender: Does NOT receive any email
    """
    from accounts.models import Profile
    from django.utils import timezone
    
    sender_name = transmittal.sender.get_full_name() or transmittal.sender.username
    origin = transmittal.origin_location.name if transmittal.origin_location else 'Unknown'
    destination = transmittal.destination_location.name if transmittal.destination_location else 'Unknown'
    
    # Convert timestamps to local timezone (USE_TZ=False, so no conversion needed)
    sent_at_local = transmittal.sent_at if transmittal.sent_at else None
    
    # Get emails
    sender_email = transmittal.sender.email
    receiver_email = transmittal.recipient_email
    
    # Get custodian emails
    origin_custodian_email = None
    destination_custodian_email = None
    
    if transmittal.origin_location:
        origin_custodian = Profile.objects.filter(
            role='custodian',
            assigned_location=transmittal.origin_location
        ).first()
        if origin_custodian:
            origin_custodian_email = origin_custodian.user.email
    
    if transmittal.destination_location:
        dest_custodian = Profile.objects.filter(
            role='custodian',
            assigned_location=transmittal.destination_location
        ).first()
        if dest_custodian:
            destination_custodian_email = dest_custodian.user.email
    
    # Prepare email list - ONLY receiver and custodians (excluding sender)
    # Sender does NOT receive any email, regardless of whether they are a custodian
    email_list = [
        (receiver_email, 'receiver', 'INTERNAL'),
    ]
    
    # Add origin custodian (sender's custodian) ONLY if they are not the sender or receiver
    # Sender's custodian will see this in their Outgoing page
    if origin_custodian_email and origin_custodian_email != sender_email and origin_custodian_email != receiver_email:
        email_list.append((origin_custodian_email, 'custodian', 'EXTERNAL'))
    
    # Add destination custodian (receiver's custodian) ONLY if they are not the sender or receiver
    if destination_custodian_email and destination_custodian_email != sender_email and destination_custodian_email != receiver_email:
        email_list.append((destination_custodian_email, 'custodian', 'EXTERNAL'))
    
    # Send emails
    all_sent = True
    for recipient_email, recipient_type, email_category in email_list:
        # Determine status text based on transmittal status
        if transmittal.status == 'arrived':
            status_text = 'Arrived'
            status_badge = '📍 ARRIVED'
        elif transmittal.status == 'received':
            status_text = 'Received'
            status_badge = '✅ RECEIVED'
        else:
            status_text = 'In Transit'
            status_badge = '🚚 IN TRANSIT'
        
        subject = f"[{transmittal.reference_number}] Transmittal Report - {status_text}"
        
        if email_category == 'EXTERNAL':
            # External email for custodians
            header_bg = '#dc3545'  # Red
            header_title = 'TRANSMITTAL NOTIFICATION'
            alert_text = 'CUSTODIAN NOTIFICATION: A new transmittal report has been sent in the system that requires your attention.'
        else:
            # Internal email for sender/receiver
            header_bg = '#00703c'  # Green
            header_title = '📧 TRANSMITTAL REPORT'
            alert_text = None
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 650px; margin: 20px auto; background-color: #fff; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: {header_bg}; color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .badge {{ display: inline-block; padding: 6px 16px; background-color: #FFC107; color: #000; border-radius: 15px; font-weight: 600; font-size: 12px; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-size: 14px; font-weight: 700; color: {header_bg}; margin-bottom: 8px; border-bottom: 2px solid {header_bg}; padding-bottom: 5px; }}
        .info-table {{ width: 100%; border-collapse: collapse; }}
        .info-table td {{ padding: 8px 0; vertical-align: top; }}
        .info-table td:first-child {{ font-weight: 600; color: #555; width: 140px; }}
        .description-box {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #667eea; border-radius: 3px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #777; border-top: 1px solid #e0e0e0; }}
        .alert {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
        .cta-button {{ display: inline-block; padding: 14px 32px; background-color: {header_bg}; color: white; text-decoration: none; border-radius: 5px; font-weight: 600; font-size: 14px; margin: 20px 0; text-align: center; }}
        .cta-button:hover {{ opacity: 0.9; }}
        .button-container {{ text-align: center; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{header_title}</h1>
            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Ref: {transmittal.reference_number}</p>
            <p style="margin: 10px 0 0 0;"><span class="badge">{status_badge}</span></p>
        </div>
        
        <div class="content">
            {f'<div class="alert">{alert_text}</div>' if alert_text else ''}
            
            <!-- Two-Column Layout for Origin and Destination -->
            <div style="border: 1px solid #333; border-radius: 4px; margin-bottom: 15px; display: flex; overflow: hidden;">
                <!-- Left Column: Origin Location -->
                <div style="flex: 1; padding: 12px; border-right: 1px solid #333;">
                    <div class="section-title" style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid {header_bg};">ORIGIN</div>
                    <table class="info-table">
                        <tr><td>Location:</td><td><strong>{origin}</strong></td></tr>
                        <tr><td>From:</td><td>{sender_name}</td></tr>
                        <tr><td>Department:</td><td>{transmittal.sender_department or '-'}</td></tr>
                    </table>
                </div>
                <!-- Right Column: Destination Location -->
                <div style="flex: 1; padding: 12px;">
                    <div class="section-title" style="margin-bottom: 12px; padding-bottom: 8px; border-bottom: 2px solid {header_bg};">DESTINATION</div>
                    <table class="info-table">
                        <tr><td>Location:</td><td><strong>{destination}</strong></td></tr>
                        <tr><td>To:</td><td>{transmittal.recipient_name}</td></tr>
                        <tr><td>Department:</td><td>{transmittal.recipient_department}</td></tr>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">DESCRIPTION</div>
                <div class="description-box">{transmittal.description}</div>
            </div>
            
            {f'<div class="section"><div class="section-title">REMARKS</div><div class="description-box">{transmittal.remarks}</div></div>' if transmittal.remarks else ''}
            
            {f'<div class="section"><div class="section-title">ATTACHMENTS</div><table class="info-table"><tr><td>Files:</td><td>' + ', '.join([att.file.name.split("/")[-1] for att in transmittal.attachments.all()]) + '</td></tr></table></div>' if transmittal.attachments.exists() else ''}
            
            <div class="section">
                <table class="info-table">
                    <tr><td>Date/Time:</td><td>{sent_at_local.strftime('%B %d, %Y  %I:%M %p') if sent_at_local else '-'}</td></tr>
                </table>
            </div>
            
            <div class="button-container">
                <a href="{settings.SITE_URL}/transmittals/detail/{transmittal.id}/" class="cta-button">📋 View Transmittal Report</a>
            </div>
        </div>
        
        <div class="footer">
            <p>This is an automated notification from the CDC MFG CORP Transmittal System.</p>
            <p>Reference: <strong>{transmittal.reference_number}</strong></p>
        </div>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
TRANSMITTAL REPORT
Reference: {transmittal.reference_number}
Status: IN TRANSIT

From: {sender_name}
Origin: {origin}
To: {transmittal.recipient_name}
Destination: {destination}

Message: {transmittal.description}

{f'Remarks: {transmittal.remarks}' if transmittal.remarks else ''}

View full report: {settings.SITE_URL}/transmittals/detail/{transmittal.id}/
"""
        
        try:
            msg = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
            )
            msg.attach_alternative(html_content, "text/html")
            
            # Attach all files from Attachment model
            for attachment in transmittal.attachments.all():
                try:
                    file_path = attachment.file.path
                    file_name = os.path.basename(file_path)
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'
                    with open(file_path, 'rb') as f:
                        msg.attach(file_name, f.read(), mime_type)
                except Exception as e:
                    print(f"Error attaching file {file_name}: {e}")
            
            msg.send()
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {e}")
            all_sent = False
    
    return all_sent


def send_cancellation_email_to_receiver(transmittal, cancellation_reason):
    """
    Send external cancellation notification to receiver.
    Notifies the receiver that the transmittal from the sender has been cancelled.
    """
    recipients = [transmittal.recipient_email]
    
    subject = f"Transmittal Notification: {transmittal.reference_number} - Cancelled"
    
    sender_name = transmittal.sender.get_full_name() or transmittal.sender.username
    origin = transmittal.origin_location.name if transmittal.origin_location else 'Unknown'
    destination = transmittal.destination_location.name if transmittal.destination_location else 'Unknown'
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 650px; margin: 20px auto; background-color: #fff; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-size: 14px; font-weight: 700; color: #dc3545; margin-bottom: 10px; border-bottom: 2px solid #dc3545; padding-bottom: 5px; }}
        .info-table {{ width: 100%; border-collapse: collapse; }}
        .info-table td {{ padding: 10px 0; vertical-align: top; }}
        .info-table td:first-child {{ font-weight: 600; color: #555; width: 140px; }}
        .info-table td:last-child {{ color: #333; }}
        .notification-box {{ background: #fff3cd; border: 1px solid #ffc107; border-left: 4px solid #dc3545; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #333; }}
        .notification-box strong {{ color: #dc3545; }}
        .reason-box {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; border-radius: 3px; margin-top: 10px; line-height: 1.6; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #777; border-top: 1px solid #e0e0e0; }}
        .footer p {{ margin: 5px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Transmittal Cancellation Notice</h1>
            <p>Reference: {transmittal.reference_number}</p>
        </div>
        
        <div class="content">
            <div class="notification-box">
                <p><strong>Dear {transmittal.recipient_name},</strong></p>
                <p>We are writing to inform you that the transmittal scheduled to be sent to you has been <strong>cancelled</strong> by the sender.</p>
            </div>
            
            <div class="section">
                <div class="section-title">TRANSMITTAL DETAILS</div>
                <table class="info-table">
                    <tr>
                        <td>Reference Number:</td>
                        <td><strong>{transmittal.reference_number}</strong></td>
                    </tr>
                    <tr>
                        <td>From:</td>
                        <td>{sender_name}</td>
                    </tr>
                    <tr>
                        <td>From Location:</td>
                        <td>{origin}</td>
                    </tr>
                    <tr>
                        <td>To Location:</td>
                        <td>{destination}</td>
                    </tr>
                    <tr>
                        <td>Department:</td>
                        <td>{transmittal.recipient_department or '-'}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">CANCELLATION REASON</div>
                <div class="reason-box">
                    {cancellation_reason}
                </div>
            </div>
            
            <div class="section">
                <p style="color: #666; font-size: 13px;">
                    If you have any questions regarding this cancellation, please contact {sender_name} directly.
                </p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>CDC Manufacturing Corporation</strong></p>
            <p>Transmittal Management System</p>
            <p style="margin-top: 10px; color: #999;">Reference: {transmittal.reference_number}</p>
        </div>
    </div>
</body>
</html>
"""
    
    plain_message = f"""
TRANSMITTAL CANCELLATION NOTICE

Dear {transmittal.recipient_name},

We are writing to inform you that the transmittal scheduled to be sent to you has been cancelled by the sender.

TRANSMITTAL DETAILS:
  Reference Number: {transmittal.reference_number}
  From: {sender_name}
  From Location: {origin}
  To Location: {destination}
  Department: {transmittal.recipient_department or '-'}

CANCELLATION REASON:
{cancellation_reason}

If you have any questions regarding this cancellation, please contact {sender_name} directly.

---
CDC Manufacturing Corporation
Transmittal Management System
Reference: {transmittal.reference_number}
"""
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending receiver cancellation email: {e}")
        return False


def send_cancellation_email(transmittal, cancellation_reason):
    """
    Send cancellation notification when transmittal is cancelled.
    To: Sender, Receiver
    BCC: Origin Custodian (Sender's Custodian), Destination Custodian (Receiver's Custodian)
    """
    from accounts.models import Profile
    
    recipients = [transmittal.sender.email, transmittal.recipient_email]
    bcc_recipients = []
    
    # Add origin custodian (sender's custodian) to BCC if available
    if transmittal.origin_location:
        origin_custodian = Profile.objects.filter(
            role='custodian',
            assigned_location=transmittal.origin_location
        ).first()
        if origin_custodian and origin_custodian.user.email not in recipients and origin_custodian.user.email not in bcc_recipients:
            bcc_recipients.append(origin_custodian.user.email)
    
    # Add destination custodian (receiver's custodian) to BCC if available
    if transmittal.destination_location:
        destination_custodian = Profile.objects.filter(
            role='custodian',
            assigned_location=transmittal.destination_location
        ).first()
        if destination_custodian and destination_custodian.user.email not in recipients and destination_custodian.user.email not in bcc_recipients:
            bcc_recipients.append(destination_custodian.user.email)
    
    subject = f"[{transmittal.reference_number}] Transmittal Cancelled"
    
    sender_name = transmittal.sender.get_full_name() or transmittal.sender.username
    origin = transmittal.origin_location.name if transmittal.origin_location else 'Unknown'
    destination = transmittal.destination_location.name if transmittal.destination_location else 'Unknown'
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 650px; margin: 20px auto; background-color: #fff; border: 1px solid #e0e0e0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: #dc3545; color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .content {{ padding: 30px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-size: 14px; font-weight: 700; color: #dc3545; margin-bottom: 8px; border-bottom: 2px solid #dc3545; padding-bottom: 5px; }}
        .info-table {{ width: 100%; border-collapse: collapse; }}
        .info-table td {{ padding: 8px 0; vertical-align: top; }}
        .info-table td:first-child {{ font-weight: 600; color: #555; width: 140px; }}
        .status-badge {{ display: inline-block; padding: 6px 16px; background-color: #dc3545; color: white; border-radius: 15px; font-weight: 600; font-size: 12px; }}
        .warning-box {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 3px; margin-bottom: 15px; color: #856404; }}
        .reason-box {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; border-radius: 3px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #777; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ TRANSMITTAL CANCELLED</h1>
            <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Ref: {transmittal.reference_number}</p>
            <p style="margin: 10px 0 0 0;"><span class="status-badge">❌ CANCELLED</span></p>
        </div>
        
        <div class="content">
            <div class="warning-box">
                <strong>⚠️ Important Notice</strong>
                <p style="margin: 8px 0 0 0;">This transmittal has been cancelled by {sender_name}. The transmittal is no longer in transit.</p>
            </div>
            
            <div class="section">
                <div class="section-title">TRANSMITTAL INFORMATION</div>
                <table class="info-table">
                    <tr><td>Reference:</td><td><strong>{transmittal.reference_number}</strong></td></tr>
                    <tr><td>From:</td><td>{sender_name}</td></tr>
                    <tr><td>To:</td><td>{transmittal.recipient_name}</td></tr>
                    <tr><td>Origin:</td><td>{origin}</td></tr>
                    <tr><td>Destination:</td><td>{destination}</td></tr>
                </table>
            </div>
            
            <div class="section">
                <div class="section-title">CANCELLATION REASON</div>
                <div class="reason-box">{cancellation_reason}</div>
            </div>
            
            <div class="section">
                <div class="section-title">ORIGINAL DESCRIPTION</div>
                <div class="reason-box">{transmittal.description}</div>
            </div>
            
            <p style="margin-top: 20px; font-size: 13px; color: #666;">
                <strong>Cancelled on:</strong> {transmittal.updated_at.strftime('%B %d, %Y at %I:%M %p') if hasattr(transmittal, 'updated_at') else 'N/A'}
            </p>
        </div>
        
        <div class="footer">
            <p>This is an automated notification from the CDC MFG CORP Transmittal System.</p>
            <p>Reference: <strong>{transmittal.reference_number}</strong></p>
        </div>
    </div>
</body>
</html>
"""
    
    plain_message = f"""
TRANSMITTAL CANCELLED NOTIFICATION
Reference: {transmittal.reference_number}
Status: CANCELLED

IMPORTANT: This transmittal has been cancelled by {sender_name}. The transmittal is no longer in transit.

TRANSMITTAL INFORMATION:
  Reference: {transmittal.reference_number}
  From: {sender_name}
  To: {transmittal.recipient_name}
  Origin: {origin}
  Destination: {destination}

CANCELLATION REASON:
{cancellation_reason}

ORIGINAL DESCRIPTION:
{transmittal.description}

Cancelled on: {transmittal.updated_at.strftime('%B %d, %Y at %I:%M %p') if hasattr(transmittal, 'updated_at') else 'N/A'}

---
CDC MFG CORP Transmittal System
"""
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            bcc=bcc_recipients
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending cancellation email: {e}")
        return False


def send_status_notification(transmittal, new_status, auto_received=False):
    """
    Send notification when status changes.
    
    - arrived: Notify sender and receiver
    - received: Notify sender and custodian
    - auto_received: Flag indicating system auto-received (for audit purposes)
    """
    recipients = []
    
    if new_status == 'arrived':
        # Notify sender and receiver
        recipients = [transmittal.sender.email, transmittal.recipient_email]
        status_display = '📍 ARRIVED'
        status_color = '#17A2B8'
        message = f"The transmittal has arrived at {transmittal.destination_location.name if transmittal.destination_location else 'destination'}."
    elif new_status == 'picked':
        # Notify sender and receiver
        recipients = [transmittal.sender.email, transmittal.recipient_email]
        status_display = '📦 PICKED'
        status_color = '#6f42c1'
        pick_remarks_text = f"\n\nPick Remarks: {transmittal.pick_remarks}" if transmittal.pick_remarks else ""
        message = f"The transmittal has been picked up at the custodian facility.{pick_remarks_text}"
    elif new_status == 'received':
        # Notify sender
        recipients = [transmittal.sender.email]
        # Also notify custodian (for audit purposes)
        if transmittal.destination_location and transmittal.destination_location.custodian:
            recipients.append(transmittal.destination_location.custodian.email)
        status_display = '✅ RECEIVED'
        status_color = '#28A745'
        # Add note if auto-received by system
        auto_receive_note = " (Automatically received by system after 3 days in picked status)" if auto_received else ""
        message = f"The transmittal has been received by {transmittal.recipient_name}.{auto_receive_note}"
    else:
        return False
    
    # Remove duplicates
    recipients = list(set(recipients))
    
    subject = f"[{transmittal.reference_number}] Status Update: {new_status.title()}"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #fff; border: 1px solid #e0e0e0; }}
        .header {{ background: {status_color}; color: white; padding: 25px; text-align: center; }}
        .content {{ padding: 25px; }}
        .status-badge {{ display: inline-block; padding: 8px 20px; background: white; color: {status_color}; border-radius: 20px; font-weight: 700; font-size: 14px; }}
        .info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .cta-button {{ display: inline-block; padding: 14px 32px; background-color: {status_color}; color: white; text-decoration: none; border-radius: 5px; font-weight: 600; font-size: 14px; margin: 20px 0; text-align: center; }}
        .cta-button:hover {{ opacity: 0.9; }}
        .button-container {{ text-align: center; margin: 20px 0; }}
        .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #777; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">TRANSMITTAL STATUS UPDATE</h2>
            <p style="margin: 10px 0 0 0;"><span class="status-badge">{status_display}</span></p>
        </div>
        
        <div class="content">
            <p><strong>Reference:</strong> {transmittal.reference_number}</p>
            <p>{message}</p>
            
            <div class="info">
                <p><strong>From:</strong> {transmittal.sender.get_full_name() or transmittal.sender.username}</p>
                <p><strong>To:</strong> {transmittal.recipient_name}</p>
                <p><strong>Description:</strong> {transmittal.description[:100]}...</p>
            </div>
            
            <div class="button-container">
                <a href="{settings.SITE_URL}/transmittals/detail/{transmittal.id}/" class="cta-button">📋 View Transmittal Report</a>
            </div>
        </div>
        
        <div class="footer">
            <p>CDC MFG CORP Transmittal System</p>
        </div>
    </div>
</body>
</html>
"""
    
    plain_message = f"""
TRANSMITTAL STATUS UPDATE

Reference: {transmittal.reference_number}
Status: {new_status.upper()}

{message}

From: {transmittal.sender.get_full_name() or transmittal.sender.username}
To: {transmittal.recipient_name}
Description: {transmittal.description[:100]}...

---
CDC MFG CORP Transmittal System
"""
    
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending status notification: {e}")
        return False

def send_driver_update_email(transmittal, driver_remarks, updated_by):
    """
    Send notification when driver information is updated.
    Sends email to:
    - Receiver
    - Destination custodian
    """
    from accounts.models import Profile
    
    recipients = []
    
    # Add receiver
    if transmittal.recipient_email:
        recipients.append(transmittal.recipient_email)
        print(f"[DEBUG] Added receiver: {transmittal.recipient_email}")
    
    # Add destination custodian
    if transmittal.destination_location:
        dest_custodian = Profile.objects.filter(
            role='custodian',
            assigned_location=transmittal.destination_location
        ).first()
        if dest_custodian and dest_custodian.user.email not in recipients:
            recipients.append(dest_custodian.user.email)
            print(f"[DEBUG] Added destination custodian: {dest_custodian.user.email}")
        else:
            print(f"[DEBUG] No destination custodian found for location: {transmittal.destination_location}")
    else:
        print(f"[DEBUG] No destination location set for transmittal {transmittal.pk}")
    
    # Remove duplicates
    recipients = list(set(recipients))
    
    print(f"[DEBUG] Final recipients list: {recipients}")
    
    if not recipients:
        print(f"[WARNING] No recipients found for driver update email for transmittal {transmittal.pk}")
        return False
    
    subject = f"[{transmittal.reference_number}] Driver Information Update"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #fff; border: 1px solid #e0e0e0; }}
        .header {{ background: #0066cc; color: white; padding: 25px; text-align: center; }}
        .content {{ padding: 25px; }}
        .status-badge {{ display: inline-block; padding: 8px 20px; background: white; color: #0066cc; border-radius: 20px; font-weight: 700; font-size: 14px; }}
        .info {{ background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #0066cc; }}
        .driver-box {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #FFC107; }}
        .footer {{ padding: 15px; text-align: center; font-size: 12px; color: #777; border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2 style="margin: 0;">🚚 DRIVER INFORMATION UPDATE</h2>
            <p style="margin: 10px 0 0 0;"><span class="status-badge">DRIVER UPDATED</span></p>
        </div>
        
        <div class="content">
            <p><strong>Reference:</strong> {transmittal.reference_number}</p>
            <p>Driver information has been updated for this transmittal.</p>
            
            <div class="driver-box">
                <strong>🚛 Driver Information:</strong>
                <p style="margin: 8px 0 0 0; white-space: pre-wrap;">{driver_remarks}</p>
            </div>
            
            <div class="info">
                <p><strong>From:</strong> {transmittal.sender.get_full_name() or transmittal.sender.username}</p>
                <p><strong>To:</strong> {transmittal.recipient_name}</p>
                <p><strong>Destination:</strong> {transmittal.destination_location.name if transmittal.destination_location else 'Unknown'}</p>
            </div>
            
            <p><em>Updated by: {updated_by.get_full_name() or updated_by.username}</em></p>
        </div>
        
        <div class="footer">
            <p>CDC MFG CORP Transmittal System</p>
        </div>
    </div>
</body>
</html>
"""
    
    plain_message = f"""
🚚 DRIVER INFORMATION UPDATE

Reference: {transmittal.reference_number}

Driver information has been updated for this transmittal.

DRIVER INFORMATION:
{driver_remarks}

From: {transmittal.sender.get_full_name() or transmittal.sender.username}
To: {transmittal.recipient_name}
Destination: {transmittal.destination_location.name if transmittal.destination_location else 'Unknown'}

Updated by: {updated_by.get_full_name() or updated_by.username}

---
CDC MFG CORP Transmittal System
"""
    
    try:
        print(f"[DEBUG] Attempting to send driver update email to {recipients}")
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_content, "text/html")
        result = email.send(fail_silently=False)
        print(f"[DEBUG] Email sent successfully. Result: {result}")
        return True
    except Exception as e:
        print(f"[ERROR] Error sending driver update email: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# EXTERNAL TRANSMITTAL EMAIL FUNCTIONS
# ============================================================================

def send_external_transmittal_created_email(transmittal):
    """
    Send notification email when external transmittal is created.
    Sent to: sender_email and recipient_email
    
    For Keep: Status = IN_TRANSIT
    For Return: Status = IN_TRANSIT (will transition to OPEN after proof upload)
    """
    try:
        sender_email = transmittal.sender_email
        recipient_email = transmittal.recipient_email
        ref_number = transmittal.reference_number
        main_type = transmittal.get_main_type_display()
        created_at = transmittal.created_at.strftime('%Y-%m-%d %H:%M')
        
        subject = f"[{ref_number}] External Transmittal Created - {main_type}"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .info-section {{ margin: 15px 0; border-left: 4px solid #667eea; padding-left: 10px; }}
        .label {{ font-weight: bold; color: #667eea; }}
        .footer {{ text-align: center; padding: 10px; color: #999; font-size: 12px; border-top: 1px solid #ddd; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>External Transmittal Notification</h2>
    </div>
    <div class="content">
        <p>Dear {transmittal.recipient_name},</p>
        
        <p>A new external transmittal has been created in the system.</p>
        
        <div class="info-section">
            <p><span class="label">Reference Number:</span> {ref_number}</p>
            <p><span class="label">Type:</span> {main_type}</p>
            <p><span class="label">Status:</span> In Transit</p>
            <p><span class="label">Created:</span> {created_at}</p>
            <p><span class="label">Description:</span> {transmittal.description}</p>
        </div>
        
        <div class="info-section">
            <p><span class="label">From:</span> {transmittal.sender_name} ({transmittal.sender_email})</p>
            <p><span class="label">Company:</span> {transmittal.sender_company or 'N/A'}</p>
        </div>
        
        <div class="info-section">
            <p><span class="label">Destination:</span> {transmittal.recipient_company_name or '—'}</p>
            <p><span class="label">To:</span> {transmittal.recipient_name}</p>
            <p><span class="label">Email:</span> {transmittal.recipient_email}</p>
            <p><span class="label">Company Address:</span> {transmittal.recipient_company_address if transmittal.recipient_company_address else '—'}</p>
        </div>
        
        {f'<div class="info-section"><p><span class="label">Expected Return:</span> {transmittal.date_return.strftime("%Y-%m-%d") if transmittal.date_return else "N/A"}</p></div>' if transmittal.is_for_return() else ''}
        
        <p>Please retain this reference number for your records.</p>
        
        <p>Best regards,<br>Transmittal System</p>
    </div>
    <div class="footer">
        <p>This is an automated notification. Please do not reply to this email.</p>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
External Transmittal Created

Reference: {ref_number}
Type: {main_type}
Status: In Transit
Created: {created_at}
Description: {transmittal.description}

From: {transmittal.sender_name} ({transmittal.sender_email})
Company: {transmittal.sender_company or 'N/A'}

Destination: {transmittal.recipient_company_name or '—'}
To: {transmittal.recipient_name}
Email: {transmittal.recipient_email}
Company Address: {transmittal.recipient_company_address if transmittal.recipient_company_address else '—'}

{f'Expected Return: {transmittal.date_return.strftime("%Y-%m-%d") if transmittal.date_return else "N/A"}' if transmittal.is_for_return() else ''}

Please retain this reference number for your records.
"""
        
        # Handle multiple recipients
        recipients = [e.strip() for e in recipient_email.split(',') if e.strip()]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_content, "text/html")
        
        # Attach the main single attachment field if present
        if transmittal.attachment:
            try:
                file_name = os.path.basename(transmittal.attachment.name)
                file_content = transmittal.attachment.read()
                mime_type, _ = mimetypes.guess_type(file_name)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                email.attach(file_name, file_content, mime_type)
                print(f"[DEBUG] Attached file: {file_name}")
            except Exception as e:
                print(f"[ERROR] Error attaching main file: {e}")
        
        # Attach all additional files from ExternalTransmittalAttachment model
        for attachment in transmittal.attachments.all():
            try:
                if attachment.file:
                    file_name = os.path.basename(attachment.file.name)
                    # Read file directly from storage
                    file_content = attachment.file.read()
                    mime_type, _ = mimetypes.guess_type(file_name)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'
                    email.attach(file_name, file_content, mime_type)
                    print(f"[DEBUG] Attached file: {file_name}")
            except Exception as e:
                print(f"[ERROR] Error attaching related file: {e}")
        
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"[ERROR] Error sending external transmittal created email: {e}")
        return False


def send_external_transmittal_deadline_reminder(transmittal, days_overdue):
    """
    Send deadline reminder email for For Return transmittals.
    
    Called on:
    - Day 0 (deadline day)
    - Day +1 overdue
    - Day +3 overdue
    - Day +7 overdue (final reminder)
    
    Escalation notifications help track time-sensitive returns.
    """
    try:
        sender_email = transmittal.sender_email
        recipient_email = transmittal.recipient_email
        ref_number = transmittal.reference_number
        
        # Determine escalation level message
        if days_overdue == 0:
            level_msg = "DEADLINE TODAY"
            level_color = "#FFA500"  # Orange
        elif days_overdue > 0:
            level_msg = f"{days_overdue} DAY{'S' if days_overdue > 1 else ''} OVERDUE"
            if days_overdue >= 7:
                level_msg += " - FINAL REMINDER"
                level_color = "#8B0000"  # Dark red
            elif days_overdue >= 3:
                level_color = "#CC0000"  # Dark red
            else:
                level_color = "#FF6347"  # Red
        else:
            # If triggered before deadline (e.g. on Expected Return Date if that's before deadline)
            level_msg = "RETURN REMINDER"
            level_color = "#FFA500" # Orange
        
        subject = f"[{ref_number}] {level_msg} - Transmittal Return Deadline"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, {level_color} 0%, #8B0000 100%); color: white; padding: 20px; text-align: center; }}
        .alert {{ background: {level_color}; color: white; padding: 15px; margin: 15px 0; border-radius: 4px; }}
        .content {{ padding: 20px; }}
        .info-section {{ margin: 15px 0; border-left: 4px solid {level_color}; padding-left: 10px; }}
        .label {{ font-weight: bold; color: {level_color}; }}
        .footer {{ text-align: center; padding: 10px; color: #999; font-size: 12px; border-top: 1px solid #ddd; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>⚠️  Transmittal Return Deadline Reminder</h2>
    </div>
    <div class="content">
        <div class="alert">
            <strong>{level_msg}</strong>
        </div>
        
        <p>Dear Recipient,</p>
        
        <p>This is an automatic reminder regarding the return deadline for the following transmittal:</p>
        
        <div class="info-section">
            <p><span class="label">Reference Number:</span> {ref_number}</p>
            <p><span class="label">Type:</span> For Return</p>
            <p><span class="label">Status:</span> {transmittal.received_status.upper() if transmittal.received_status else 'OPEN'}</p>
            <p><span class="label">Expected Return:</span> {transmittal.date_return.strftime("%Y-%m-%d") if transmittal.date_return else 'N/A'}</p>
            <p><span class="label">Description:</span> {transmittal.description}</p>
        </div>
        
        <p><strong>Action Required:</strong></p>
        <p>Please arrange for the return of items or update the transmittal status (Full Return, Partial Return, Paid Sample, or Convert to For Keep) as soon as possible.</p>
        
        <p>Best regards,<br>Transmittal System</p>
    </div>
    <div class="footer">
        <p>This is an automated notification. Please do not reply to this email.</p>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
Transmittal Return Deadline Reminder

{level_msg}

Reference: {ref_number}
Type: For Return
Status: {transmittal.received_status.upper() if transmittal.received_status else 'OPEN'}
Expected Return: {transmittal.date_return.strftime("%Y-%m-%d") if transmittal.date_return else 'N/A'}
Description: {transmittal.description}

Action Required:
Please arrange for the return of items or update the transmittal status as soon as possible.
"""
        
        # Handle multiple recipients
        recipient_list = [e.strip() for e in recipient_email.split(',') if e.strip()]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sender_email] + recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # Attach the main single attachment field if present
        if transmittal.attachment:
            try:
                file_name = os.path.basename(transmittal.attachment.name)
                file_content = transmittal.attachment.read()
                mime_type, _ = mimetypes.guess_type(file_name)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                email.attach(file_name, file_content, mime_type)
                print(f"[DEBUG] Attached file: {file_name}")
            except Exception as e:
                print(f"[ERROR] Error attaching main file: {e}")
        
        # Attach all additional files from ExternalTransmittalAttachment model
        for attachment in transmittal.attachments.all():
            try:
                if attachment.file:
                    file_name = os.path.basename(attachment.file.name)
                    # Read file directly from storage
                    file_content = attachment.file.read()
                    mime_type, _ = mimetypes.guess_type(file_name)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'
                    email.attach(file_name, file_content, mime_type)
                    print(f"[DEBUG] Attached file: {file_name}")
            except Exception as e:
                print(f"[ERROR] Error attaching related file: {e}")
        
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"[ERROR] Error sending deadline reminder email: {e}")
        return False


def send_external_transmittal_resolution_email(transmittal, action_type, notes=''):
    """
    Send notification when external transmittal is resolved (status transition).
    
    FEATURE: Automatically sends SMTP email on EVERY status change in external transmittals.
    ENHANCED: Includes actual file attachments (downloadable) + image previews (inline).
    
    Called for:
    - mark_received (For Keep type marked as received)
    - full_return (Full Return initiated)
    - partial_return (Partial Return initiated)
    - paid_sample (Paid Sample resolved)
    - convert_to_keep (Converted to For Keep SubType)
    - closed (Transmittal closed)
    - admin_override (Admin status change)
    """
    try:
        from django.utils import timezone
        import os
        import base64
        
        sender_email = transmittal.sender_email
        recipient_email = transmittal.recipient_email
        ref_number = transmittal.reference_number
        
        # Determine action display and color
        action_display = {
            'mark_received': ('Marked as Received', '#28A745'),
            'full_return': ('Full Return', '#17A2B8'),
            'partial_return': ('Partial Return', '#FFC107'),
            'paid_sample': ('Paid Sample - Resolved', '#6F42C1'),
            'convert_to_keep': ('Converted to For Keep', '#28A745'),
            'closed': ('Closed', '#6C757D'),
            'admin_override': ('Status Changed (Admin Override)', '#FF6B6B'),
        }
        
        action_msg, color = action_display.get(action_type, ('Updated', '#007BFF'))
        
        subject = f"[{ref_number}] Transmittal {action_msg}"
        
        # Get attachment details and prepare for email attachment
        attachments_html = ""
        attachments_text = ""
        image_previews_html = ""
        email_attachments = []  # Store attachments to add to email
        
        try:
            attachments = transmittal.attachments.all().order_by('-uploaded_at')
            if attachments.exists():
                attachments_html = '<div class="info-section"><p><span class="label">📎 Attachments Uploaded (Downloadable):</span></p><ul>'
                attachments_text += "\n📎 ATTACHMENTS UPLOADED (DOWNLOADABLE):\n"
                image_previews_html = '<div class="info-section"><p><span class="label">🖼️ Image Previews:</span></p><div class="image-gallery">'
                
                for att in attachments:
                    att_type = att.attachment_type or "Document"
                    file_name = att.file.name.split('/')[-1] if att.file.name else "File"
                    uploaded_time = att.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if att.uploaded_at else "N/A"
                    file_size = att.file.size if att.file else 0
                    file_size_kb = file_size / 1024
                    
                    attachments_html += f'<li>{att_type}: <strong>{file_name}</strong> ({file_size_kb:.1f}KB) - Uploaded: {uploaded_time}</li>'
                    attachments_text += f"  • {att_type}: {file_name} ({file_size_kb:.1f}KB) - Uploaded: {uploaded_time}\n"
                    
                    # Try to attach file and prepare for email
                    try:
                        # Check if file exists
                        if att.file and os.path.exists(att.file.path):
                            file_path = att.file.path
                            
                            # Read file content
                            with open(file_path, 'rb') as f:
                                file_content = f.read()
                            
                            # Get MIME type
                            mime_type, _ = mimetypes.guess_type(file_path)
                            if mime_type is None:
                                mime_type = 'application/octet-stream'
                            
                            # Store attachment for email
                            email_attachments.append({
                                'filename': file_name,
                                'content': file_content,
                                'mimetype': mime_type,
                                'file_obj': att,
                                'is_image': mime_type.startswith('image/')
                            })
                            
                            # For images, add preview to HTML
                            if mime_type.startswith('image/'):
                                encoded_image = base64.b64encode(file_content).decode('utf-8')
                                image_previews_html += f'''
                                <div class="image-item" style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                                    <p style="margin: 0 0 5px 0;"><strong>{file_name}</strong></p>
                                    <img src="data:{mime_type};base64,{encoded_image}" style="max-width: 400px; max-height: 300px; border-radius: 3px;" alt="{file_name}"/>
                                    <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">Uploaded: {uploaded_time}</p>
                                </div>
                                '''
                        else:
                            print(f"[WARNING] Attachment file not found: {att.file.path if att.file else 'N/A'}")
                    except Exception as e:
                        print(f"[WARNING] Error processing attachment {file_name}: {e}")
                
                attachments_html += '</ul></div>'
                image_previews_html += '</div></div>'
                
                # Only add image preview section if images exist
                if not any(att['is_image'] for att in email_attachments):
                    image_previews_html = ""
        except Exception as e:
            print(f"[WARNING] Error fetching attachments: {e}")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, {color} 0%, #666 100%); color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .info-section {{ margin: 15px 0; border-left: 4px solid {color}; padding-left: 10px; }}
        .label {{ font-weight: bold; color: {color}; }}
        .attachment-list {{ margin: 10px 0; padding-left: 20px; }}
        .attachment-list li {{ margin: 8px 0; }}
        .image-gallery {{ margin: 10px 0; display: flex; flex-wrap: wrap; gap: 10px; }}
        .image-item {{ flex: 1; min-width: 300px; }}
        .footer {{ text-align: center; padding: 10px; color: #999; font-size: 12px; border-top: 1px solid #ddd; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>✅ Transmittal {action_msg}</h2>
    </div>
    <div class="content">
        <p>Dear Recipient,</p>
        
        <p>The transmittal has been updated with the following action:</p>
        
        <div class="info-section">
            <p><span class="label">Reference Number:</span> {ref_number}</p>
            <p><span class="label">Action:</span> {action_msg}</p>
            <p><span class="label">Type:</span> {transmittal.get_main_type_display()}</p>
            <p><span class="label">Current Status:</span> {transmittal.get_status_display()}</p>
            <p><span class="label">Description:</span> {transmittal.description}</p>
            <p><span class="label">Updated At:</span> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        {f'<div class="info-section"><p><span class="label">Sub Type:</span> {transmittal.get_sub_type_display()}</p></div>' if transmittal.sub_type else ''}
        
        {attachments_html}
        
        {image_previews_html}
        
        {f'<div class="info-section"><p><span class="label">Notes:</span> {notes}</p></div>' if notes else ''}
        
        <p>For more details, please contact the sender or check the transmittal system.</p>
        
        <p>Best regards,<br>Transmittal System</p>
    </div>
    <div class="footer">
        <p>This is an automated notification. Please do not reply to this email.</p>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
Transmittal {action_msg}

Reference: {ref_number}
Action: {action_msg}
Type: {transmittal.get_main_type_display()}
Current Status: {transmittal.get_status_display()}
Description: {transmittal.description}
Updated At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

{f'Sub Type: {transmittal.get_sub_type_display()}' if transmittal.sub_type else ''}

{attachments_text}

{f'Notes: {notes}' if notes else ''}

For more details, please contact the sender or check the transmittal system.
"""
        
        # Handle multiple recipients
        recipient_list = [e.strip() for e in recipient_email.split(',') if e.strip()]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sender_email] + recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # Attach actual files to email for download
        for att_info in email_attachments:
            try:
                email.attach(
                    filename=att_info['filename'],
                    content=att_info['content'],
                    mimetype=att_info['mimetype']
                )
                print(f"[INFO] Attached file to email: {att_info['filename']}")
            except Exception as e:
                print(f"[WARNING] Failed to attach file {att_info['filename']}: {e}")
        
        email.send(fail_silently=False)
        
        print(f"[SUCCESS] Email sent for {action_type} on transmittal {ref_number} with {len(email_attachments)} attachment(s)")
        return True
    except Exception as e:
        print(f"[ERROR] Error sending resolution email: {e}")
        return False


def send_external_transmittal_cancelled_email(transmittal, cancellation_reason):
    """
    Send notification email when external transmittal is cancelled.
    Sent to: recipient_email
    """
    try:
        recipient_email = transmittal.recipient_email
        ref_number = transmittal.reference_number
        main_type = transmittal.get_main_type_display()
        cancelled_at = timezone.now().strftime('%Y-%m-%d %H:%M')
        
        subject = f"[{ref_number}] External Transmittal Cancelled - {main_type}"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%); color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .info-section {{ margin: 15px 0; border-left: 4px solid #d32f2f; padding-left: 10px; }}
        .label {{ font-weight: bold; color: #d32f2f; }}
        .warning-box {{ background-color: #ffebee; border: 1px solid #ef5350; border-radius: 4px; padding: 12px; margin: 15px 0; }}
        .footer {{ text-align: center; padding: 10px; color: #999; font-size: 12px; border-top: 1px solid #ddd; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>External Transmittal Cancelled</h2>
    </div>
    <div class="content">
        <p>Dear {transmittal.recipient_name},</p>
        
        <div class="warning-box">
            <p><strong>⚠️ The following external transmittal has been cancelled:</strong></p>
        </div>
        
        <div class="info-section">
            <p><span class="label">Reference Number:</span> {ref_number}</p>
            <p><span class="label">Type:</span> {main_type}</p>
            <p><span class="label">Created:</span> {transmittal.created_at.strftime('%Y-%m-%d %H:%M')}</p>
            <p><span class="label">Cancelled:</span> {cancelled_at}</p>
            <p><span class="label">Description:</span> {transmittal.description}</p>
        </div>
        
        <div class="info-section">
            <p><span class="label">From:</span> {transmittal.sender_name} ({transmittal.sender_email})</p>
            <p><span class="label">Company:</span> {transmittal.sender_company or 'N/A'}</p>
        </div>
        
        <div class="info-section">
            <p><span class="label">Destination:</span> {transmittal.recipient_company_name or '—'}</p>
            <p><span class="label">To:</span> {transmittal.recipient_name}</p>
            <p><span class="label">Email:</span> {transmittal.recipient_email}</p>
            <p><span class="label">Company Address:</span> {transmittal.recipient_company_address if transmittal.recipient_company_address else '—'}</p>
        </div>
        
        <div class="info-section">
            <p><span class="label">Cancellation Reason:</span></p>
            <p style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 8px;">{cancellation_reason}</p>
        </div>
        
        <p style="margin-top: 20px; color: #d32f2f;"><strong>This transmittal is no longer active. Please disregard any previous instructions regarding this transmittal.</strong></p>
        
        <p>Best regards,<br>Transmittal System</p>
    </div>
    <div class="footer">
        <p>This is an automated notification. Please do not reply to this email.</p>
    </div>
</body>
</html>
"""
        
        plain_message = f"""
External Transmittal Cancelled

⚠️ The following external transmittal has been cancelled:

Reference: {ref_number}
Type: {main_type}
Created: {transmittal.created_at.strftime('%Y-%m-%d %H:%M')}
Cancelled: {cancelled_at}
Description: {transmittal.description}

From: {transmittal.sender_name} ({transmittal.sender_email})
Company: {transmittal.sender_company or 'N/A'}

Destination: {transmittal.recipient_company_name or '—'}
To: {transmittal.recipient_name}
Email: {transmittal.recipient_email}
Company Address: {transmittal.recipient_company_address if transmittal.recipient_company_address else '—'}

Cancellation Reason:
{cancellation_reason}

This transmittal is no longer active. Please disregard any previous instructions regarding this transmittal.

Best regards,
Transmittal System
"""
        
        # Handle multiple recipients
        recipients = [e.strip() for e in recipient_email.split(',') if e.strip()]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"[ERROR] Error sending external transmittal cancellation email: {e}")
        return False
