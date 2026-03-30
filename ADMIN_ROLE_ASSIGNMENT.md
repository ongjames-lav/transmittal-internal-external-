# Admin Role Assignment Feature

## Overview
The admin panel now allows administrators to assign roles and locations to users directly from the Django admin interface.

## What Was Added

### 1. **Role Field in User Profile** (`accounts/models.py`)
- Added `ROLE_CHOICES` with three options:
  - **user**: Regular User
  - **custodian**: Custodian
  - **admin**: Administrator
- Added `role` field to Profile model with default value of 'user'

### 2. **Assigned Location Field** (`accounts/models.py`)
- Added `assigned_location` ForeignKey to Location model
- Only applicable for custodian roles
- Allows admin to assign a custodian to a specific location

### 3. **Enhanced Admin Interface** (`accounts/admin.py`)
- **ProfileAdmin Updates:**
  - Added role filter to sidebar
  - Added role badge display in list view (color-coded)
  - Added "Role Assignment" fieldset with role and assigned_location fields
  - Added `role_badge()` method to display colored role badges

- **ProfileInline Updates:**
  - Added role and assigned_location fields to inline editing

## How to Use

### Assigning a User as Custodian

1. Go to **Django Admin** → **Profiles**
2. Click on the user to edit
3. Scroll to **Role Assignment** section
4. Set **User Role** to "Custodian"
5. Set **Assigned Location** to the location they manage
6. Click **Save**

### Filtering Users by Role

1. In **Profiles** list view, use the **Role** filter on the right sidebar
2. Click to filter by: User, Custodian, or Admin

### Admin Interface Features

- **Role Badge**: Color-coded display
  - Gray: Regular User
  - Blue: Custodian
  - Red: Administrator

- **Filter Options**: Filter by Status, Role, Department, Company, and Created Date

## Database Changes

### Migration File
- `accounts/migrations/0003_alter_profile_assigned_location_alter_profile_role.py`

### Fields Added to Profile Model
```python
role = models.CharField(
    max_length=20,
    choices=ROLE_CHOICES,
    default='user',
    verbose_name="User Role"
)

assigned_location = models.ForeignKey(
    'transmittals.Location',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='assigned_staff',
    verbose_name="Assigned Location"
)
```

## Admin Panel Access

- **URL**: http://127.0.0.1:8000/admin/
- **Section**: Accounts → Profiles
- **Actions**: 
  - Create new users and assign roles
  - Edit existing users and change roles
  - Assign custodians to locations
  - Filter users by role

## Benefits

✅ Easy role management from admin interface
✅ Custodian assignment to locations
✅ Color-coded role display for quick identification
✅ Filter and search by role
✅ No need for manual database queries
✅ Audit trail of role changes

## Next Steps

- Admin can now directly assign:
  - Users as Custodians
  - Locations to Custodians
  - Other roles as needed
  
- System will use these role assignments for:
  - Email notifications
  - Permission checks
  - Workflow routing
