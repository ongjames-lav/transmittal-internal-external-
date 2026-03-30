# Sender Environment Details Implementation

## Overview
Extended the Transmittal model to persistently capture and store sender environment information (device, IP address, browser) at the time of transmittal creation.

## Files Modified/Created

### 1. **Model Updates** - `transmittals/models.py`
Added three new fields to the Transmittal model:
```python
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
```

### 2. **Helper Functions** - `transmittals/environment_utils.py` (NEW FILE)
Created utility module with the following functions:

#### `get_client_ip(request)`
- Extracts client IP address from request
- Respects `X-Forwarded-For` header for proxied requests
- Falls back to `REMOTE_ADDR`
- Returns: IPv4 or IPv6 address

#### `get_device_information(request)`
- Parses User-Agent header using `django-user-agents`
- Detects device type: Desktop, Mobile, Tablet, Unknown
- Captures OS name and version
- Returns: "Desktop Windows 10", "Mobile iOS 17.2", etc.

#### `get_browser_information(request)`
- Extracts browser name and version from User-Agent
- Uses `django-user-agents` library
- Returns: "Chrome 121.0", "Firefox 121.0", etc.

#### `capture_sender_environment(request)`
- Convenience function that captures all details in one call
- Returns: Dictionary with all three environment fields

### 3. **View Updates** - `transmittals/views.py`
Updated `create_transmittal` view:
```python
from .environment_utils import capture_sender_environment

# In the transmittal creation logic:
environment = capture_sender_environment(request)
transmittal.device_information = environment['device_information']
transmittal.ip_address = environment['ip_address']
transmittal.browser_of_sender = environment['browser_of_sender']
```

### 4. **Admin Configuration** - `transmittals/admin.py`
#### Added to readonly_fields:
- device_information
- ip_address
- browser_of_sender

#### Added fieldset:
```python
('Sender Environment', {
    'fields': ('device_information', 'ip_address', 'browser_of_sender'),
    'description': 'Device and browser information captured when the transmittal was sent',
    'classes': ('collapse',)
}),
```

#### Excel Export Enhancement:
- Added three new columns to export: Device Information, IP Address, Browser of Sender
- Set appropriate column widths (P, Q, R)
- Data is now included in the Excel export

### 5. **Template Updates** - `transmittals/templates/transmittals/detail.html`
Added new "Sender Environment Details" section:
- Displays with green accent (#00703c) to match system theme
- Shows device, IP address, and browser information
- Conditionally displays only if data exists
- Styled to match report layout

### 6. **Database Migration** - `transmittals/migrations/0012_transmittal_environment_fields.py`
Created migration that:
- Adds device_information CharField (max_length=255, null/blank)
- Adds ip_address GenericIPAddressField (null/blank)
- Adds browser_of_sender CharField (max_length=255, null/blank)

### 7. **Dependencies** - `requirements.txt`
Added:
```
django-user-agents==0.4.0
```

## Usage Examples

### Capturing Environment (Automatic in create_transmittal)
```python
from transmittals.environment_utils import capture_sender_environment

environment = capture_sender_environment(request)
# Returns:
# {
#     'device_information': 'Desktop Windows 10',
#     'ip_address': '192.168.1.100',
#     'browser_of_sender': 'Chrome 121.0'
# }
```

### Individual Functions
```python
from transmittals.environment_utils import get_client_ip, get_device_information, get_browser_information

ip = get_client_ip(request)  # '192.168.1.100'
device = get_device_information(request)  # 'Mobile iOS 17.2'
browser = get_browser_information(request)  # 'Safari 17.2'
```

## Data Examples

After implementation, new transmittal records will contain:

| Field | Example |
|-------|---------|
| device_information | "Desktop Windows 10" |
| ip_address | "192.168.1.82" or "2001:db8::1" |
| browser_of_sender | "Chrome 121.0" |

## Features

✅ **Automatic Capture**: Environment details captured automatically when transmittal is created
✅ **Proxy Support**: Respects X-Forwarded-For header for accurate IP detection
✅ **Device Detection**: Identifies Desktop, Mobile, or Tablet
✅ **OS Detection**: Captures operating system and version
✅ **Browser Detection**: Identifies browser name and version
✅ **Admin Interface**: Fields visible in collapsible "Sender Environment" section
✅ **Excel Export**: All three fields included in transmittal export
✅ **Report Display**: Displayed in transmittal detail view
✅ **Read-Only**: Fields are read-only in admin (captured at creation time)
✅ **Persistent Storage**: Data stored in database per row

## Installation Steps

1. Install dependency:
   ```bash
   pip install django-user-agents==0.4.0
   ```

2. Apply migration:
   ```bash
   python manage.py migrate transmittals
   ```

3. No other configuration needed - environment capture is automatic

## Technical Details

### IP Detection Logic
1. Check `HTTP_X_FORWARDED_FOR` header (for proxied requests)
2. Fall back to `REMOTE_ADDR`
3. Handles both IPv4 and IPv6

### Device Type Detection
Uses `django-user-agents` to parse User-Agent:
- `is_mobile` → "Mobile"
- `is_tablet` → "Tablet"
- `is_pc` → "Desktop"
- Default → "Unknown"

### Browser Parsing
Extracts from User-Agent:
- Browser family (Chrome, Firefox, Safari, etc.)
- Version string (if available)

## Data Retention

- Environment details are stored permanently with each transmittal
- Non-sensitive information only (no location data)
- Useful for auditing and troubleshooting
- Can be exported with Excel reports

## Future Enhancements

Possible extensions:
- Screen resolution capture
- JavaScript-enabled detection
- Geolocation based on IP (opt-in)
- User-Agent raw string storage
- Environment change tracking
