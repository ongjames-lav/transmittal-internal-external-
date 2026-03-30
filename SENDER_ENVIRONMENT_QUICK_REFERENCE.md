# Sender Environment Details - Quick Reference

## What Was Added

Three new database columns capture sender information when transmittals are created:

| Column | Type | Example | Purpose |
|--------|------|---------|---------|
| `device_information` | CharField | "Desktop Windows 10" | Device type & OS |
| `ip_address` | GenericIPAddressField | "192.168.1.82" | Sender's IP address |
| `browser_of_sender` | CharField | "Chrome 121.0" | Browser name & version |

## Where to See It

### Django Admin
1. Go to Transmittals > Transmittal list
2. Click on any transmittal
3. Scroll to **"Sender Environment"** section (collapsed by default)
4. View Device Information, IP Address, Browser of Sender

### Transmittal Report
1. Open transmittal detail page
2. Look for **"Sender Environment Details"** section below Remarks
3. Shows all three captured fields

### Excel Export
1. In Django admin, select transmittals
2. Choose action **"📥 Export selected to Excel"**
3. Download includes three new columns:
   - Column P: Device Information
   - Column Q: IP Address  
   - Column R: Browser of Sender

## How It Works

```
User creates transmittal → System captures request details → Stored in database
                                        ↓
                    Device type, OS, Browser info
                    IP address (respects proxies)
                                        ↓
                    Permanently stored with transmittal
                                        ↓
              Available in admin, reports, and exports
```

## Technical Stack

- **Library**: django-user-agents 0.4.0 (for User-Agent parsing)
- **Database Fields**: 3 new columns in transmittal table
- **Capture Method**: Automatic in create_transmittal view
- **Storage**: Persistent in database
- **Access**: Via Django ORM as `transmittal.device_information`, etc.

## Usage Examples

### Access in Code
```python
transmittal = Transmittal.objects.get(id=1)
print(transmittal.device_information)  # "Desktop Windows 10"
print(transmittal.ip_address)  # "192.168.1.82"
print(transmittal.browser_of_sender)  # "Chrome 121.0"
```

### Query Examples
```python
# Find transmittals from mobile devices
mobile_transmittals = Transmittal.objects.filter(
    device_information__icontains='Mobile'
)

# Find transmittals from specific IP
ip_transmittals = Transmittal.objects.filter(
    ip_address='192.168.1.82'
)

# Find Chrome users
chrome_transmittals = Transmittal.objects.filter(
    browser_of_sender__icontains='Chrome'
)
```

## Data Examples

### Windows Desktop
```
Device: Desktop Windows 10
IP: 192.168.1.82
Browser: Chrome 121.0
```

### iPhone
```
Device: Mobile iOS 17.2
IP: 203.0.113.45
Browser: Safari 17.2
```

### Tablet (Android)
```
Device: Tablet Android 13
IP: 2001:db8::1 (IPv6)
Browser: Firefox 121.0
```

## Migration Info

Database migration: `0012_transmittal_environment_fields.py`

To apply:
```bash
python manage.py migrate transmittals
```

## Notes

✓ Captured automatically - no manual entry needed
✓ Non-sensitive information only
✓ Respects proxy headers (X-Forwarded-For)
✓ Works with IPv4 and IPv6
✓ Read-only in admin (set at creation)
✓ Exported in Excel reports
✓ Useful for auditing and troubleshooting
