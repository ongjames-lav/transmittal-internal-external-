from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class Location(models.Model):
    """
    Dynamic location model for transmittal routing.
    Admin can add/edit/delete locations via the Admin Panel.
    Each location has a unique code/prefix used for reference numbers.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Location Name",
        help_text="e.g., Pantoc, Meycauayan, Main"
    )
    
    prefix = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Code/Prefix",
        help_text="Unique prefix for reference numbers (e.g., PAN, MY, HO)"
    )
    
    custodian = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custodian_locations',
        verbose_name="Assigned Custodian",
        help_text="User responsible for receiving items at this location"
    )
    
    custodian_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Custodian Email",
        help_text="Email for notifications (uses custodian user email if blank)"
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Location Address",
        help_text="Full address of this location"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Inactive locations won't appear in dropdowns"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.prefix})"
    
    def get_custodian_email(self):
        """Return custodian email, falling back to user email if not set."""
        if self.custodian_email:
            return self.custodian_email
        if self.custodian:
            return self.custodian.email
        return None


class Transmittal(models.Model):
    """
    Transmittal Report model with location-based routing and status tracking.
    Follows a lifecycle: In Transit -> Arrived -> Received (or Cancelled).
    """
    
    STATUS_CHOICES = (
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived'),
        ('picked', 'Picked'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    )
    
    # Reference number with location prefix
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Reference No."
    )
    
    # Sender information (auto-filled)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_transmittals',
        verbose_name="From (Sender)"
    )
    sender_department = models.CharField(
        max_length=255,
        verbose_name="Sender Department",
        blank=True,
        null=True
    )
    origin_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='outgoing_transmittals',
        verbose_name="Origin Location",
        help_text="Where the transmittal originates from",
        null=True,
        blank=True
    )
    
    # Recipient information (user input)
    recipient_name = models.CharField(
        max_length=255,
        verbose_name="To (Recipient)"
    )
    recipient_email = models.EmailField(
        verbose_name="Recipient Email"
    )
    recipient_id = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='received_transmittals',
        verbose_name="Recipient User",
        help_text="Internal user receiving this transmittal",
        null=False,
        blank=False
    )
    recipient_company = models.CharField(
        max_length=255,
        verbose_name="Recipient Company",
        blank=True,
        null=True
    )
    recipient_department = models.CharField(
        max_length=255,
        verbose_name="Recipient Department"
    )
    destination_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name='incoming_transmittals',
        verbose_name="Destination Location",
        help_text="Where the transmittal is being sent to",
        null=True,
        blank=True
    )
    
    assigned_location_text = models.CharField(
        max_length=255,
        verbose_name="Assigned Location (Manual Entry)",
        help_text="Manually entered assigned location when not selected from dropdown",
        blank=True,
        null=True
    )
    
    # Content
    description = models.TextField(
        verbose_name="Description"
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarks"
    )
    pick_remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="Pick Remarks",
        help_text="Optional remarks from custodian when picking the transmittal"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_transit',
        verbose_name="Status"
    )
    
    # Status timestamps
    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Sent At"
    )
    arrived_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Arrived At"
    )
    picked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Picked At"
    )
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Received At"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelled At"
    )
    cancellation_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Cancellation Reason",
        help_text="Reason provided by sender for cancelling the transmittal"
    )
    
    # Who changed the status
    arrived_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_arrived_transmittals',
        verbose_name="Marked Arrived By"
    )
    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='marked_received_transmittals',
        verbose_name="Marked Received By"
    )
    
    # Auto-receive tracking
    auto_received = models.BooleanField(
        default=False,
        verbose_name="Auto Received",
        help_text="Whether this transmittal was automatically received by the system after 3 days in 'picked' status"
    )
    
    # Soft delete flags (kept from original)
    sender_deleted = models.BooleanField(default=False, verbose_name="Deleted by Sender")
    recipient_deleted = models.BooleanField(default=False, verbose_name="Deleted by Recipient")
    sender_deleted_at = models.DateTimeField(null=True, blank=True)
    recipient_deleted_at = models.DateTimeField(null=True, blank=True)
    sender_purged = models.BooleanField(default=False, verbose_name="Purged by Sender")
    recipient_purged = models.BooleanField(default=False, verbose_name="Purged by Recipient")
    
    # Legacy fields (kept for compatibility)
    date_created = models.DateField(auto_now_add=True)
    time_created = models.TimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, verbose_name="Resolved")
    
    # Sender environment details (captured at transmission)
    device_information = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Device Information",
        help_text="Device type (Desktop/Mobile/Tablet) and operating system"
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="IP Address",
        help_text="IPv4 or IPv6 address from which the transmittal was sent"
    )
    browser_of_sender = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Browser of Sender",
        help_text="Browser name and version used to send the transmittal"
    )
    
    # File attachment
    file = models.FileField(
        upload_to='transmittals/',
        blank=True,
        null=True,
        verbose_name="Attachment",
        help_text="Optional file attachment (PDF, Image, Document, etc.)"
    )
    
    # Driver information
    driver_remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="Driver Information",
        help_text="Driver name and vehicle plate number"
    )
    
    # Receiver's digital signature
    receiver_signature = models.ImageField(
        upload_to='transmittal_signatures/',
        blank=True,
        null=True,
        verbose_name="Receiver Signature",
        help_text="Digital signature of the person who received the transmittal"
    )
    
    # Status reminder tracking
    status_changed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Status Changed At",
        help_text="When the status was last changed"
    )
    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Reminder Sent At",
        help_text="When the 5-day reminder email was sent for the current status"
    )
    
    class Meta:
        verbose_name = "Transmittal"
        verbose_name_plural = "Transmittals"
        ordering = ['-sent_at']
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        
        # Initialize or update status_changed_at
        from django.utils import timezone
        if not self.pk:
            # New instance - initialize status_changed_at
            if not self.status_changed_at:
                self.status_changed_at = timezone.now()
        else:
            # Existing instance - check if status changed
            try:
                old_instance = Transmittal.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    self.status_changed_at = timezone.now()
                    self.reminder_sent_at = None  # Reset reminder when status changes
            except Transmittal.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        """
        Generate reference number based on destination location prefix (if available),
        otherwise fallback to origin location.
        Format: [PREFIX]-[YYYYMMDD]-[XXXX]
        Example: HO-20260127-0001 (if going to Main Office)
        Sequences are based on DATE only, not time
        """
        if self.destination_location:
            prefix = self.destination_location.prefix
        elif self.origin_location:
            prefix = self.origin_location.prefix
        else:
            prefix = "REF"
        
        date_str = datetime.now().strftime('%Y%m%d')
        full_prefix = f"{prefix}-{date_str}"
        
        # Find last transmittal with this date prefix (sequence resets by date, not time)
        last_transmittal = Transmittal.objects.filter(
            reference_number__startswith=full_prefix
        ).order_by('reference_number').last()
        
        if last_transmittal and last_transmittal.reference_number:
            try:
                last_number = int(last_transmittal.reference_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}-{date_str}-{new_number:04d}"
    
    def get_custodian(self):
        """Get custodian assigned to destination location."""
        if self.destination_location:
            return self.destination_location.custodian
        return None
    
    def get_custodian_email(self):
        """Get custodian email for destination location."""
        if self.destination_location:
            return self.destination_location.get_custodian_email()
        return None
    
    def can_cancel(self):
        """Check if transmittal can be cancelled (only In Transit status)."""
        return self.status == 'in_transit'
    
    def __str__(self):
        return f"[{self.reference_number}] {self.recipient_name}"


class Attachment(models.Model):
    """
    File attachment model for transmittal reports.
    Allows multiple file uploads per transmittal with total 5MB limit.
    Only used for transmittal attachments, NOT for digital signatures.
    """
    transmittal = models.ForeignKey(
        Transmittal,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="Transmittal",
        help_text="The transmittal this attachment belongs to"
    )
    
    file = models.FileField(
        upload_to='transmittals/',
        verbose_name="Attachment File",
        help_text="Attached image file (JPG, PNG, GIF, BMP, WebP)"
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Uploaded At"
    )
    
    class Meta:
        verbose_name = "Transmittal Attachment"
        verbose_name_plural = "Transmittal Attachments"
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"{self.transmittal.reference_number} - {self.file.name}"


# ============================================================================
# EXTERNAL TRANSMITTAL SYSTEM - NEW SUBSYSTEM
# ============================================================================

class ExternalLocation(models.Model):
    """
    External location model for true external recipients (companies/individuals).
    No custodian FK - purely for external transmittal destinations.
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Location/Recipient Name",
        help_text="Name of external location or recipient organization"
    )
    
    email = models.EmailField(
        verbose_name="Email Address",
        help_text="Contact email for this external location"
    )
    
    company_name = models.CharField(
        max_length=255,
        verbose_name="Company Name"
    )
    
    company_address = models.TextField(
        verbose_name="Company Address"
    )
    
    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Contact Person",
        help_text="Name of primary contact person at this location"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Inactive locations won't appear in dropdowns"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "External Location"
        verbose_name_plural = "External Locations"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.company_name})"


class ExternalTransmittal(models.Model):
    """
    External Transmittal model for sending items to external recipients.
    
    Main Types:
    - For Keep: Permanent transfer, no return expected
    - For Return: Temporary transfer with deadline monitoring and return tracking
    
    Sub Types (only for For Return):
    - Full: All items returned
    - Partial: Some items returned, case remains open
    - For Sample: Receiver keeps items as paid sample
    - For Keep: All items converted to permanent transfer
    """
    
    MAIN_TYPE_CHOICES = (
        ('for_keep', 'For Keep'),
        ('for_return', 'For Return'),
    )
    
    SUB_TYPE_CHOICES = (
        ('full', 'Full Return'),
        ('partial', 'Partial Return'),
        ('for_sample', 'Paid Sample'),
        ('for_keep', 'For Keep (SubType)'),
    )
    
    # For Keep uses: IN_TRANSIT, RECEIVED
    # For Return uses: OPEN, CLOSED
    # Cancelled: CANCELLED (terminal status)
    STATUS_CHOICES = (
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Reference number with unique identifier
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Reference No."
    )
    
    # Sender information (can be external email, no account required)
    sender_email = models.EmailField(
        verbose_name="Sender Email",
        help_text="Email of the person sending the transmittal (can be external)"
    )
    sender_name = models.CharField(
        max_length=255,
        verbose_name="Sender Name"
    )
    sender_company = models.CharField(
        max_length=255,
        verbose_name="Sender Company",
        blank=True,
        null=True
    )
    
    # Sender user ID (tracks which authenticated user sent this transmittal)
    sender_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='external_sent_transmittals',
        verbose_name="Sender User",
        help_text="System user who sent this transmittal (if sent by authenticated user)"
    )
    
    # Recipient information
    recipient_email = models.CharField(
        max_length=255,
        verbose_name="Recipient Email",
        help_text="Email of the person receiving the transmittal (can be multiple separated by commas)"
    )
    recipient_name = models.CharField(
        max_length=255,
        verbose_name="Recipient Name",
        help_text="Full name of the recipient"
    )
    recipient_company_name = models.CharField(
        max_length=255,
        verbose_name="Recipient Company Name",
        help_text="Company or organization name"
    )
    recipient_company_address = models.TextField(
        verbose_name="Recipient Company Address",
        help_text="Full address of the recipient's company"
    )
    # Plain text location input from sender (no FK table needed)
    external_location_text = models.CharField(
        max_length=255,
        verbose_name="External Location",
        help_text="Location/address as entered by the sender",
        null=True,
        blank=True
    )
    recipient_location = models.ForeignKey(
        ExternalLocation,
        on_delete=models.SET_NULL,
        related_name='incoming_external_transmittals',
        verbose_name="Recipient Location (Legacy)",
        null=True,
        blank=True
    )
    
    # Transmittal classification
    main_type = models.CharField(
        max_length=20,
        choices=MAIN_TYPE_CHOICES,
        default='for_return',
        verbose_name="Transmittal Type"
    )
    
    sub_type = models.CharField(
        max_length=20,
        choices=SUB_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sub Type",
        help_text="For Return cases only: set when resolved"
    )
    
    # Content description
    description = models.TextField(
        verbose_name="Description",
        help_text="Description of items being transmitted"
    )
    
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name="Remarks"
    )
    
    # Image attachment stored directly on model (no separate table)
    attachment = models.FileField(
        upload_to='external_transmittals/attachments/',
        blank=True,
        null=True,
        verbose_name="Image Attachment",
        help_text="Optional image or document attached by the sender"
    )
    
    # For Return: date the item should be returned
    date_return = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date of Return",
        help_text="The date the item is to be returned (For Return type)"
    )

    # For Return: hard deadline for monitoring
    date_deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name="Return Deadline Date",
        help_text="Hard deadline for return monitoring; reminders sent when today >= this date"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_transit',
        verbose_name="Status"
    )
    
    # For Return specific: Open/Closed tracking
    # Also includes Cancelled for transmittals that have been cancelled
    RECEIVED_STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    received_status = models.CharField(
        max_length=20,
        choices=RECEIVED_STATUS_CHOICES,
        blank=True,
        null=True,
        verbose_name="Received Status",
        help_text="Open or Closed status for For Return transmittals"
    )
    
    # Status timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    in_transit_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="In Transit At"
    )
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Received At"
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Closed At"
    )
    
    # Cancellation tracking
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Cancelled At"
    )
    
    cancellation_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Cancellation Reason"
    )
    
    # Deadline monitoring
    last_notification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Last Notification Date",
        help_text="Tracks when last deadline reminder was sent (prevents duplicate emails)"
    )
    
    class Meta:
        verbose_name = "External Transmittal"
        verbose_name_plural = "External Transmittals"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)
    
    def generate_reference_number(self):
        """
        Generate reference number for external transmittals.
        Format: EXT-[YYYYMMDD]-[XXXX]
        Example: EXT-20260127-0001
        """
        date_str = datetime.now().strftime('%Y%m%d')
        full_prefix = f"EXT-{date_str}"
        
        # Find last external transmittal with this date prefix
        last_transmittal = ExternalTransmittal.objects.filter(
            reference_number__startswith=full_prefix
        ).order_by('reference_number').last()
        
        if last_transmittal and last_transmittal.reference_number:
            try:
                last_number = int(last_transmittal.reference_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"EXT-{date_str}-{new_number:04d}"
    
    def is_for_keep(self):
        """Check if this is a For Keep type transmittal."""
        return self.main_type == 'for_keep'
    
    def is_for_return(self):
        """Check if this is a For Return type transmittal."""
        return self.main_type == 'for_return'
    
    def can_mark_received(self):
        """Check if transmittal can be marked as received (from In Transit)."""
        return self.status == 'in_transit'

    def can_transition_to_full_return(self):
        """Check if transmittal can transition to Full Return."""
        return self.is_for_return() and self.status == 'received' and self.received_status == 'open'

    def can_transition_to_partial(self):
        """Check if transmittal can transition to Partial Return."""
        return self.is_for_return() and self.status == 'received' and self.received_status == 'open'
    
    def can_transition_to_paid_sample(self):
        """Check if transmittal can transition to Paid Sample."""
        return self.is_for_return() and self.status == 'received' and self.received_status == 'open'
    
    def can_transition_to_for_keep_subtype(self):
        """Check if transmittal can transition to For Keep SubType."""
        return self.is_for_return() and self.status == 'received' and self.received_status == 'open'
    
    def can_cancel(self):
        """Check if transmittal can be cancelled (must be in In Transit status)."""
        return self.status == 'in_transit'
    
    def __str__(self):
        return f"[{self.reference_number}] {self.main_type.upper()} - {self.recipient_email}"


class ExternalTransmittalAttachment(models.Model):
    """
    Attachment model for external transmittals.
    Supports proof of delivery, RGA documents, and other required attachments.
    """
    transmittal = models.ForeignKey(
        ExternalTransmittal,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="External Transmittal",
        help_text="The external transmittal this attachment belongs to"
    )
    
    file = models.FileField(
        upload_to='external_transmittals/',
        verbose_name="Attachment File",
        help_text="Proof of delivery, RGA, or other supporting document"
    )
    
    attachment_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Attachment Type",
        help_text="e.g., Proof of Delivery, RGA, Signature"
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Uploaded At"
    )
    
    uploaded_by_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Uploaded By (Email)",
        help_text="Email of person who uploaded this attachment"
    )
    
    class Meta:
        verbose_name = "External Transmittal Attachment"
        verbose_name_plural = "External Transmittal Attachments"
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"{self.transmittal.reference_number} - {self.file.name}"


class ExternalTransmittalAuditTrail(models.Model):
    """
    Audit trail for external transmittal status changes and resolution workflows.
    Tracks all actions, who performed them, when, and what proof was attached.
    """
    
    ACTION_CHOICES = (
        ('created', 'Created'),
        ('mark_received', 'Marked Received'),
        ('full_return', 'Full Return Initiated'),
        ('partial_return', 'Partial Return Initiated'),
        ('paid_sample', 'Paid Sample Resolved'),
        ('convert_to_keep', 'Converted to For Keep'),
        ('closed', 'Closed'),
        ('admin_override', 'Admin Override'),
    )
    
    transmittal = models.ForeignKey(
        ExternalTransmittal,
        on_delete=models.CASCADE,
        related_name='audit_trail',
        verbose_name="External Transmittal"
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        verbose_name="Action"
    )
    
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='external_transmittal_actions',
        verbose_name="Performed By",
        help_text="User who performed this action (null if system action)"
    )
    
    performed_by_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Performed By Email",
        help_text="Email if performed by external sender"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Additional notes about this action"
    )
    
    required_attachment_proof = models.ForeignKey(
        ExternalTransmittalAttachment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_trail_entry',
        verbose_name="Proof Attachment",
        help_text="Attachment required for this action (RGA, signature, etc.)"
    )
    
    class Meta:
        verbose_name = "External Transmittal Audit Trail"
        verbose_name_plural = "External Transmittal Audit Trails"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.transmittal.reference_number} - {self.action} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
