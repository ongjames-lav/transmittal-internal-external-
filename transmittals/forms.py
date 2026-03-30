"""
Forms for Transmittal system V2.
"""
from django import forms
from django.utils import timezone
from datetime import date
from .models import Transmittal, Location, ExternalTransmittal, ExternalLocation, ExternalTransmittalAttachment
from accounts.models import Profile


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class TransmittalForm(forms.ModelForm):
    """
    Form for creating a new transmittal.
    
    Auto-fills: reference_number, sender, sender_department, origin_location
    User inputs: recipient info, destination_location, description, remarks
    """
    
    # Select from existing users
    selected_user = forms.ModelChoiceField(
        queryset=Profile.objects.filter(status='approved').select_related('user'),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'selected-user'
        }),
        label='Select Recipient',
        required=False,
        empty_label='-- Select a Recipient --'
    )
    
    # Destination location dropdown (populates custodian automatically)
    destination_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'destination-location'
        }),
        label='Destination Location',
        empty_label='-- Select Destination --',
        required=False
    )
    
    # Manual assigned location entry
    assigned_location_text = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'gmail-input',
            'id': 'recipientLocation',
            'placeholder': 'Enter assigned location'
        }),
        label='Location'
    )
    
    # Multiple file uploads (custom field, not on model)
    attachments = forms.FileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png,.gif,.bmp,.webp',
            'id': 'file-input',
            'multiple': True
        }),
        label='Image Attachments (Optional)',
        help_text='Upload multiple images (Total max 5MB)'
    )
    
    class Meta:
        model = Transmittal
        fields = [
            'recipient_name',
            'recipient_email',
            'recipient_company',
            'recipient_department',
            'destination_location',
            'assigned_location_text',
            'description',
            'remarks',
        ]
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient name'
            }),
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient email'
            }),
            'recipient_company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient company',
                'required': True
            }),
            'recipient_department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient department',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter detailed description of the transmittal contents...'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional remarks or notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_attachments(self):
        """Validate multiple file attachments - images only, maximum 5MB total"""
        attachments = self.files.getlist('attachments')
        
        if attachments:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            max_total_size = 5 * 1024 * 1024  # 5MB total
            total_size = 0
            
            for file in attachments:
                # Check file extension
                file_ext = file.name[file.name.rfind('.'):].lower()
                
                if file_ext not in allowed_extensions:
                    raise forms.ValidationError(
                        f'Invalid file type "{file.name}". Only image files are allowed (JPG, PNG, GIF, BMP, WebP).'
                    )
                
                total_size += file.size
            
            # Check total size
            if total_size > max_total_size:
                total_mb = total_size / (1024 * 1024)
                raise forms.ValidationError(
                    f'Total attachment size ({total_mb:.2f}MB) exceeds the maximum limit of 5MB. Please remove some files.'
                )
        
        return attachments


class StatusUpdateForm(forms.Form):
    """
    Form for updating transmittal status.
    Used by Custodian (to mark Arrived) and Receiver (to mark Received).
    """
    STATUS_CHOICES = (
        ('arrived', 'Arrived'),
        ('received', 'Received'),
    )
    
    new_status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Update Status To'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes about this status update...'
        }),
        label='Notes'
    )


class CancelTransmittalForm(forms.Form):
    """
    Form for cancelling a transmittal (Sender only, while In Transit).
    """
    reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please provide a reason for cancellation...'
        }),
        label='Cancellation Reason'
    )
    
    confirm = forms.BooleanField(
        required=True,
        label='I confirm I want to cancel this transmittal'
    )

class PickTransmittalForm(forms.Form):
    """
    Form for marking a transmittal as picked by custodian.
    Allows custodian to add optional remarks about the pickup.
    """
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional remarks (e.g., care-of person details or pickup notes)...'
        }),
        label='Pick Remarks (Optional)',
        help_text='Add any optional remarks about the pickup'
    )
    
    confirm = forms.BooleanField(
        required=True,
        label='I confirm this transmittal has been picked',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class ReceiveTransmittalForm(forms.Form):
    """
    Form for marking a transmittal as received with signature.
    Allows receiver to upload their digital signature.
    """
    signature = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Digital Signature (Optional)',
        help_text='Upload an image of your signature (PNG or JPG format)'
    )
    
    confirm = forms.BooleanField(
        required=True,
        label='I confirm receipt of this transmittal',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_signature(self):
        """Validate signature image if provided"""
        signature = self.cleaned_data.get('signature')
        
        if signature:
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = signature.name[signature.name.rfind('.'):].lower()
            
            if file_ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Invalid file type. Only image files are allowed (JPG, PNG, GIF, BMP, WebP).'
                )
            
            # 5MB = 5242880 bytes
            max_size = 5 * 1024 * 1024
            
            if signature.size > max_size:
                raise forms.ValidationError(
                    f'Signature size exceeds maximum limit of 5MB.'
                )
        
        return signature


# ============================================================================
# EXTERNAL TRANSMITTAL FORMS
# ============================================================================

from datetime import date

class ExternalTransmittalForm(forms.ModelForm):
    """
    Form for creating a new external transmittal.
    
    Supports both For Keep and For Return types.
    - For Keep: No date_deadline required
    - For Return: date_deadline is mandatory; received_status auto-set to 'open' by the view
    
    Location is a plain text input from the sender.
    Image attachment stored directly on model — no separate table.
    received_status is NOT on this form; it is automatic.
    """

    # Plain text location input from sender


    class Meta:
        model = ExternalTransmittal
        fields = [
            'recipient_name',
            'recipient_email',
            'recipient_company_name',
            'recipient_company_address',
            'main_type',
            'date_return',
            'description',
            'remarks',
            'attachment',
        ]
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter recipient name'
            }),
            'recipient_email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., john@example.com, jane@example.com'
            }),
            'recipient_company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'recipient_company_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter company address'
            }),
            'main_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'main-type'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the items being transmitted...'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional remarks...'
            }),
            'date_return': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                }),
            'attachment': MultipleFileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png,.gif,.bmp,.webp,.pdf',
                'id': 'attachment-input',
                'multiple': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today_str = date.today().isoformat()
        # Date of Return field is not initially required (validated in clean())
        self.fields['date_return'].required = False
        self.fields['date_return'].label = 'Date of Return *'
        self.fields['date_return'].widget.attrs['min'] = today_str
        self.fields['recipient_email'].required = True
        self.fields['recipient_email'].help_text = 'Separate multiple emails with commas.'
        self.fields['attachment'].required = False
        self.fields['attachment'].label = 'Image Attachments (Optional)'
        self.fields['attachment'].help_text = 'Upload multiple files or images (JPG, PNG, GIF, WebP, PDF — max 10MB total)'
        # Set required fields - these must be filled
        self.fields['recipient_name'].required = True
        self.fields['recipient_email'].required = True
        self.fields['recipient_company_name'].required = True
        self.fields['recipient_company_address'].required = True
        self.fields['description'].required = True
        self.fields['main_type'].required = True
        # Add asterisks to required fields
        self.fields['recipient_name'].label = 'Recipient Name *'
        self.fields['recipient_email'].label = 'Email Address *'
        self.fields['recipient_company_name'].label = 'Company Name *'
        self.fields['recipient_company_address'].label = 'Company Address *'
        self.fields['main_type'].label = 'Transmittal Type *'
        self.fields['description'].label = 'Description *'

    def clean_attachment(self):
        """Validate multiple file attachments - max 10MB total"""
        attachments = self.files.getlist('attachment')
        
        if attachments:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.pdf']
            max_total_size = 10 * 1024 * 1024  # 10MB total
            total_size = 0
            
            for file in attachments:
                # Check file extension
                file_ext = file.name[file.name.rfind('.'):].lower()
                
                if file_ext not in allowed_extensions:
                    raise forms.ValidationError(
                        f'Invalid file type "{file.name}". Allowed: JPG, PNG, GIF, BMP, WebP, PDF.'
                    )
                
                total_size += file.size
            
            # Check total size
            if total_size > max_total_size:
                total_mb = total_size / (1024 * 1024)
                raise forms.ValidationError(
                    f'Total attachment size ({total_mb:.2f}MB) exceeds the maximum limit of 10MB. Please remove some files.'
                )
            
            # Return the first attachment for the model (or you could handle all in the view)
            return attachments[0]
        
        return None

    def clean_recipient_email(self):
        """Validate multiple comma-separated emails."""
        emails_raw = self.cleaned_data.get('recipient_email', '')
        if not emails_raw:
            return emails_raw
            
        # Split by comma and clean
        emails = [e.strip() for e in emails_raw.split(',') if e.strip()]
        
        # Validate each email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        for email in emails:
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError(f'"{email}" is not a valid email address.')
                
        # Re-join with proper spacing
        return ', '.join(emails)

    def clean_date_return(self):
        """Prevent backdating of the Date of Return."""
        date_return = self.cleaned_data.get('date_return')
        if date_return and date_return < date.today():
            raise forms.ValidationError(
                'Date of Return cannot be a past date. Please select today or a future date.'
            )
        return date_return



    def clean(self):
        """
        Validate that For Return type transmittals have a date_return.
        received_status is NOT set by the sender — it is auto-set to 'open' in the view.
        """
        cleaned_data = super().clean()
        main_type = cleaned_data.get('main_type')
        date_return = cleaned_data.get('date_return')

        if main_type == 'for_return':
            if not date_return:
                self.add_error('date_return', 'Date of Return is required for "For Return" type transmittals.')

        return cleaned_data


class ExternalTransmittalUpdateForm(forms.Form):
    """
    Form for resolving external transmittals with required attachment upload.
    
    Used for status transitions:
    - For Keep: Mark as Received (requires proof)
    - For Return: Full Return, Partial Return, Paid Sample, Convert to For Keep
    
    CRITICAL: Attachment is REQUIRED for all resolution actions.
    Form-level validation prevents submission without file.
    """
    
    ACTION_CHOICES = (
        ('mark_received', 'Mark as Received'),
        ('full_return', 'Full Return'),
        ('partial_return', 'Partial Return'),
        ('paid_sample', 'Paid Sample'),
        ('convert_to_keep', 'For Keep'),
    )
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'action'
        }),
        label='Resolution Action',
        required=True
    )
    
    # REQUIRED attachment - proof of delivery/return/RGA
    attachment = forms.FileField(
        required=True,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png,.gif,.bmp,.webp,.pdf,.doc,.docx',
            'id': 'proof-attachment',
            'multiple': True
        }),
        label='Proof of Delivery/Return/RGA (REQUIRED)',
        help_text='Upload proof document(s) or image(s) (JPG, PNG, PDF, DOC, DOCX — max 10MB total)'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes about this action...'
        }),
        label='Notes'
    )
    
    def clean(self):
        """
        Ensure attachment is provided for form submission.
        This prevents the form from being submitted without a file.
        """
        cleaned_data = super().clean()
        attachments = self.files.getlist('attachment')
        
        if not attachments:
            raise forms.ValidationError(
                'Proof attachment is required for this action. Please select at least one file.'
            )
        
        return cleaned_data
    
    def clean_attachment(self):
        """Validate multiple proof attachment files - max 10MB total"""
        attachments = self.files.getlist('attachment')
        
        if attachments:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.pdf', '.doc', '.docx']
            max_total_size = 10 * 1024 * 1024  # 10MB total
            total_size = 0
            
            for file in attachments:
                file_ext = file.name[file.name.rfind('.'):].lower()
                
                if file_ext not in allowed_extensions:
                    raise forms.ValidationError(
                        f'Invalid file type "{file.name}". Only images and documents are allowed.'
                    )
                
                total_size += file.size
            
            # Check total size
            if total_size > max_total_size:
                total_mb = total_size / (1024 * 1024)
                raise forms.ValidationError(
                    f'Total attachment size ({total_mb:.2f}MB) exceeds the maximum limit of 10MB. Please remove some files.'
                )
            
            # Return the first attachment for backward compatibility
            return attachments[0] if attachments else None
        
        return None
