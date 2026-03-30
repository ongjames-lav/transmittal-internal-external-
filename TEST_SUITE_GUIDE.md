# Test Suite Guide - All Management Commands

## Quick Start

Run all tests with one command:

```bash
python test_all_commands_comprehensive.py
```

## What Gets Tested

### Test 1: `auto_receive_transmittals`
- **Purpose**: Auto-receives transmittals after 3 days in 'picked' status
- **Creates**: 3 test transmittals (3, 5, 1 days in picked status)
- **Expected Result**: 2 auto-received (3 and 5 days), 1 skipped (1 day)
- **Output**: Shows which transmittals were auto-received with details

### Test 2: `send_status_reminders`
- **Purpose**: Sends reminders for transmittals stuck 5+ days in same status
- **Creates**: 4 test transmittals (5, 6, 8, 3 days in status)
- **Expected Result**: 3 reminders sent (5, 6, 8 days), 1 skipped (3 days)
- **Output**: Shows which transmittals received reminders

### Test 3: `send_external_transmittal_notifications`
- **Purpose**: Sends deadline reminders for external transmittals
- **Requires**: Running during weekdays 8-10 AM only
- **Status**: SKIPPED if not in time window (runs automatically in production)
- **Output**: Shows if window is active or skipped

## How to Use Individual Test Environments

### Just create test data (don't run command):

```bash
# Auto-receive test data
python test_env_auto_receive.py

# Status reminders test data
python test_env_status_reminders.py

# External transmittals test data
python test_env_external_notifications.py
```

### Run commands individually:

```bash
# Auto-receive transmittals
python manage.py auto_receive_transmittals

# Send status reminders
python manage.py send_status_reminders

# Send external notifications (weekdays 8-10 AM only)
python manage.py send_external_transmittal_notifications
```

## Understanding the Output

### Success Indicators
- ✓ PASS = Command executed and worked correctly
- ⊘ SKIPPED = Command didn't run (outside time window or requirements not met)

### Key Metrics
- **auto_received count**: How many transmittals were automatically received
- **reminders sent count**: How many reminder emails were sent
- **external notified count**: How many external transmittals got deadline reminders

## Test Data Details

All test data is created with:
- Unique test users (sender, recipient, custodian)
- Realistic transmittal IDs (TAR-DATE-XXXX, TRM-DATE-XXXX format)
- Specific timestamps to match test scenarios
- Proper status and location information

## Troubleshooting

**Q: No output from test?**
- Check that Django can start properly
- Verify database is accessible

**Q: External test skipped?**
- This is normal if not running between 8-10 AM on a weekday
- The command is scheduled to run automatically at that time in production

**Q: Want to clean up test data?**
- Test data is in the same database
- You can delete by status (TAR-*, TRM-* prefixes) or by testing user IDs

## Production Scheduler

The comprehensive test ensures commands work before deployment. In production:
- `auto_receive_transmittals` runs hourly via Task Scheduler
- `send_status_reminders` runs hourly via Task Scheduler
- `send_external_transmittal_notifications` runs only weekdays 8-10 AM

All configured in `run_notifications.bat`
