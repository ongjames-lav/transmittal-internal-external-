# Button Removed

I have successfully removed the "Mark as Received" button from the custodian's view of the detailed transmittal report.

**Verification:**
- Custodians viewing a transmittal detail page will no longer see the green "Mark as Received" button.
- Logic in `views.py` was updated to explicitly exclude `is_destination_custodian` from `can_mark_received`.

Please refresh the page to confirm.
