"""
Registration and User Management Forms

This module contains all forms used for user registration and profile management.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Profile, Department
from transmittals.models import Location


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user creation form extending Django's UserCreationForm.
    
    This form handles user registration with the following fields:
    - Username
    - First Name
    - Last Name
    - Email
    - Password
    - Password confirmation
    """
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        }),
        label='First Name'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        }),
        label='Last Name'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        }),
        label='Email Address'
    )
    
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        }),
        label='Username'
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        help_text='Password must contain at least 8 characters'
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        """Validate that email is unique"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already registered.")
        return email
    
    def clean_username(self):
        """Validate that username is unique"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username
    
    def clean_password1(self):
        """Validate password strength"""
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password
    
    def clean(self):
        """Validate the entire form"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Passwords do not match.")
        
        return cleaned_data


class ProfileForm(forms.ModelForm):
    """
    Simplified registration profile form.
    Additional fields will be collected later after approval.
    """
    
    class Meta:
        model = Profile
        fields = ()


class ProfileEditForm(forms.ModelForm):
    """
    Form for admins to edit user profiles and update status.
    """
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )
    
    status = forms.ChoiceField(
        choices=Profile.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Approval Status'
    )
    
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Admin notes (internal use only)'
        }),
        label='Admin Notes'
    )
    
    class Meta:
        model = Profile
        fields = ('status', 'admin_notes')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate user fields from associated User object
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        """Save both Profile and User changes"""
        profile = super().save(commit=False)
        
        # Update associated User
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            profile.save()
        
        return profile


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for regular users to update their own profile.
    Allows editing contact info but NOT status or admin notes.
    """
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        }),
        label='First Name'
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        }),
        label='Last Name'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        }),
        label='Email'
    )
    
    # Profile fields with explicit widget definition to match layout
    contact = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contact Number'
        }),
        label='Contact Number'
    )
    

    company = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company'
        }),
        label='Company'
    )
    
    location = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Address'
        }),
        label='Full Address'
    )
    
    assigned_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'disabled': 'disabled'
        }),
        label='Assigned Location',
        empty_label='-- Select Location --',
        help_text='Your assigned location cannot be changed. Please contact your administrator if you need to update this.'
    )
    
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Address'
        }),
        label='Address'
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Profile Picture'
    )
    
    digital_signature = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='Digital Signature',
        help_text='Upload your digital signature (PNG or JPG format) to be used on transmittal reports'
    )

    class Meta:
        model = Profile
        fields = ('avatar', 'digital_signature', 'contact', 'company', 'location', 'assigned_location', 'address')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Refresh instance from database to get latest data
        if self.instance and self.instance.pk:
            self.instance.refresh_from_db()
        
        # Pre-populate user fields from associated User object
        if self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            
            # Hide email for custodians
            if self.instance.role == 'custodian':
                self.fields['email'].widget = forms.HiddenInput()
        
        # Make assigned_location read-only (disabled) so users cannot change it
        if self.instance.assigned_location:
            self.fields['assigned_location'].initial = self.instance.assigned_location
            self.fields['assigned_location'].disabled = True
        else:
            self.fields['assigned_location'].disabled = True
    
    def clean_email(self):
        """Validate email uniqueness (excluding current user)"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise ValidationError("This email address is already in use by another account.")
        return email
    
    def clean(self):
        """Preserve disabled field values"""
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        """Save both Profile and User changes"""
        profile = super().save(commit=False)
        
        # Update associated User
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        # Never modify department - it's locked for users
        # Keep original department
        profile.department = self.instance.department
        
        if commit:
            user.save()
            profile.save()
        
        return profile
