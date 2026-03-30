# Transmittal System V2 - Quick Reference Card

## One-Page Developer Reference

---

## 🚀 Getting Started

```bash
# Setup
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Access
http://localhost:8000/admin/
http://localhost:8000/transmittals/dashboard/
```

---

## 📍 Location Model

```python
from transmittals.models import Location

# Create location
Location.objects.create(
    name='Pantoc',
    prefix='PAN',
    custodian=user,
    is_active=True
)

# Get custodian
loc = Location.objects.get(name='Pantoc')
print(loc.get_custodian_email())
```

---

## 📋 Transmittal Model

```python
from transmittals.models import Transmittal

# Create transmittal
t = Transmittal.objects.create(
    sender=request.user,
    recipient_name='John Doe',
    recipient_email='john@company.com',
    origin_location=origin_loc,
    destination_location=dest_loc,
    description='Test transmittal',
    status='in_transit'
)
# Reference number auto-generated!
print(t.reference_number)  # PAN-20260127-0001

# Status transitions
t.status = 'arrived'
t.arrived_at = timezone.now()
t.arrived_by = custodian_user
t.save()

# Check if can cancel
if t.can_cancel():
    t.status = 'cancelled'
    t.save()

# Get custodian
custodian = t.get_custodian()
email = t.get_custodian_email()
```

---

## 👤 Profile & Roles

```python
from accounts.models import Profile

# Assign role
profile = user.profile
profile.role = 'custodian'  # or 'user', 'receiver'
profile.assigned_location = 'Pantoc'
profile.status = 'approved'
profile.save()

# Check role
if user.profile.role == 'custodian':
    # Custodian actions
```

---

## 🔗 URL Routes

### Transmittal Operations
```
GET    /transmittals/dashboard/
GET    /transmittals/create/
POST   /transmittals/create/
GET    /transmittals/success/
GET    /transmittals/detail/<id>/
GET    /transmittals/print/<id>/
POST   /transmittals/mark-arrived/<id>/
POST   /transmittals/mark-received/<id>/
POST   /transmittals/cancel/<id>/
```

### Lists
```
GET    /transmittals/inbox/
GET    /transmittals/sent/
GET    /transmittals/trash/
```

### AJAX
```
GET    /transmittals/api/location/<id>/custodian/
```

---

## 📧 Email Templates

### Send transmittal email
```python
from transmittals.email_utils import send_transmittal_email

transmittal = Transmittal.objects.get(id=1)
success = send_transmittal_email(transmittal)
# Sends to: receiver + custodian
```

### Send status notification
```python
from transmittals.email_utils import send_status_notification

# When custodian marks as arrived
send_status_notification(transmittal, 'arrived')
# Recipients: sender + receiver

# When receiver marks as received
send_status_notification(transmittal, 'received')
# Recipients: sender
```

---

## 🔐 Permission Checks

```python
# Sender check
if transmittal.sender == request.user:
    # Can view, edit, cancel

# Custodian check
is_custodian = (
    transmittal.destination_location and 
    transmittal.destination_location.custodian == request.user
)

# Receiver check
is_receiver = transmittal.recipient_email == request.user.email

# Admin check
if request.user.is_staff:
    # Full access
```

---

## 📄 Forms

### Create Transmittal Form
```python
from transmittals.forms import TransmittalForm

form = TransmittalForm(request.POST or None, user=request.user)
if form.is_valid():
    t = form.save(commit=False)
    t.sender = request.user
    t.sender_department = request.user.profile.department
    t.origin_location = user_location
    t.save()
```

---

## 🎨 Template Tags

### Status Badge
```html
{{ transmittal.get_status_display }}
<!-- Outputs: "In Transit", "Arrived", "Received", "Cancelled" -->
```

### Transmittal Detail
```html
{{ transmittal.reference_number }}
{{ transmittal.sender.get_full_name }}
{{ transmittal.origin_location.name }}
{{ transmittal.destination_location.name }}
{{ transmittal.recipient_name }}
{{ transmittal.sent_at|date:"M d, Y" }}
```

### Action Buttons
```html
{% if can_cancel %}
    <a href="{% url 'transmittals:cancel' transmittal.id %}">Cancel</a>
{% endif %}

{% if can_mark_arrived %}
    <a href="{% url 'transmittals:mark_arrived' transmittal.id %}">Mark Arrived</a>
{% endif %}

{% if can_mark_received %}
    <a href="{% url 'transmittals:mark_received' transmittal.id %}">Mark Received</a>
{% endif %}
```

---

## 🗄️ Database Queries

### Get location transmittals
```python
# All incoming to Pantoc
Location.objects.get(name='Pantoc').incoming_transmittals.all()

# All outgoing from Pantoc
Location.objects.get(name='Pantoc').outgoing_transmittals.all()
```

### Get user transmittals
```python
# User's sent
user.sent_transmittals.all()

# User's received
Transmittal.objects.filter(recipient_email=user.email)

# User's as custodian
Transmittal.objects.filter(
    destination_location__custodian=user,
    status='in_transit'
)
```

### Filter by status
```python
# In transit
Transmittal.objects.filter(status='in_transit')

# Arrived
Transmittal.objects.filter(status='arrived')

# Received
Transmittal.objects.filter(status='received')

# Cancelled
Transmittal.objects.filter(status='cancelled')
```

### Date filtering
```python
from django.utils import timezone
from datetime import timedelta

# Today's transmittals
today = timezone.now().date()
Transmittal.objects.filter(sent_at__date=today)

# Last 7 days
week_ago = timezone.now() - timedelta(days=7)
Transmittal.objects.filter(sent_at__gte=week_ago)
```

---

## 🧪 Shell Testing

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from transmittals.models import Location, Transmittal
from accounts.models import Profile
from django.utils import timezone

# Create test data
location = Location.objects.first()
user = User.objects.first()

# Create transmittal
t = Transmittal.objects.create(
    sender=user,
    recipient_name='Test User',
    recipient_email='test@company.com',
    recipient_department='Sales',
    origin_location=location,
    destination_location=location,
    description='Test'
)

print(f'Reference: {t.reference_number}')
print(f'Status: {t.status}')
print(f'Custodian: {t.get_custodian()}')

# Update status
t.status = 'arrived'
t.arrived_at = timezone.now()
t.save()

# Soft delete
t.sender_deleted = True
t.sender_deleted_at = timezone.now()
t.save()
```

---

## 🔍 Common Queries

```python
# Count by status
from django.db.models import Count
Transmittal.objects.values('status').annotate(count=Count('id'))

# Most recent
Transmittal.objects.latest('sent_at')

# Pending (in transit)
Transmittal.objects.filter(
    status='in_transit',
    destination_location__custodian=user
)

# Search
Transmittal.objects.filter(
    reference_number__icontains='PAN-20260127'
)

# Location stats
location = Location.objects.get(name='Pantoc')
print(f'Outgoing: {location.outgoing_transmittals.count()}')
print(f'Incoming: {location.incoming_transmittals.count()}')
```

---

## 📊 Admin Actions

### Location Admin
- View: `/admin/transmittals/location/`
- Actions: Add, Edit, Delete, Filter by active
- Search: name, prefix, custodian

### Transmittal Admin
- View: `/admin/transmittals/transmittal/`
- Actions: View details, Filter by status/location/date
- Search: reference_number, sender, recipient

---

## 🔧 Configuration

### Email Settings
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

### Reference Number Format
```python
# In Transmittal.generate_reference_number()
# Format: [PREFIX]-[YYYYMMDD]-[XXXX]
# Prefix from origin_location.prefix
# Date: datetime.now().strftime('%Y%m%d')
# Sequence: Auto-increment per location per day
```

---

## 🐛 Debugging

```python
# Print transmittal info
t = Transmittal.objects.get(id=1)
print(f'Ref: {t.reference_number}')
print(f'Status: {t.status}')
print(f'Sender: {t.sender.username}')
print(f'Recipient: {t.recipient_email}')
print(f'Origin: {t.origin_location}')
print(f'Destination: {t.destination_location}')

# Check custodian
print(f'Custodian: {t.get_custodian()}')
print(f'Custodian Email: {t.get_custodian_email()}')

# Check permissions
print(f'Can cancel: {t.can_cancel()}')

# Check timestamps
print(f'Sent: {t.sent_at}')
print(f'Arrived: {t.arrived_at}')
print(f'Received: {t.received_at}')
```

---

## 📚 Documentation Links

- **Technical Docs:** [TRANSMITTAL_SYSTEM_V2.md](./TRANSMITTAL_SYSTEM_V2.md)
- **Implementation:** [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
- **Changelog:** [CHANGELOG.md](./CHANGELOG.md)
- **Completion:** [PROJECT_COMPLETION_SUMMARY.md](./PROJECT_COMPLETION_SUMMARY.md)
- **README:** [README_V2.md](./README_V2.md)

---

## ✅ Quick Checklist

- [ ] Migrations applied: `python manage.py migrate`
- [ ] 5 locations exist: Check admin or shell
- [ ] Users created with roles
- [ ] Email configured
- [ ] Test create transmittal
- [ ] Test status transitions
- [ ] Test email sending
- [ ] Test print functionality
- [ ] Test permissions
- [ ] Deploy to production

---

**Transmittal System V2 Quick Reference**
Version: 2.0.0 | Updated: January 27, 2026

For detailed information, refer to full documentation files.
