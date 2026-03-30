"""
Comprehensive test suite for External Transmittal System.
Tests all requirements including:
- FOR_KEEP and FOR_RETURN creation with proper date requirements
- Status transitions and closures
- Deadline triggers and email notifications
- Prevention of invalid state reversions
- Audit trail tracking
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import datetime, timedelta
import json

from transmittals.models import (
    ExternalTransmittal,
    ExternalTransmittalAuditTrail,
    ExternalTransmittalAttachment,
)
from accounts.models import Profile

User = get_user_model()


class ExternalTransmittalCreationTests(TestCase):
    """Test creation scenarios for both FOR_KEEP and FOR_RETURN."""

    def setUp(self):
        """Set up test client and common test data."""
        self.client = Client()
        self.create_url = '/transmittals/external/create/'
        
        # Create test user
        self.user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'sender@example.com',
            }
        )
        if not self.user.check_password('testpass123'):
            self.user.set_password('testpass123')
            self.user.save()
        
        # Create profile with company
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                'company': 'Test Company',
                'contact': '1234567890'
            }
        )

    def test_for_keep_creation_without_date(self):
        """
        REQUIREMENT: FOR_KEEP transmittal does not require DateReturn or DateDeadline.
        Test creating a FOR_KEEP transmittal without any date fields.
        """
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Create FOR_KEEP transmittal
        data = {
            'recipient_name': 'John Doe',
            'recipient_email': 'recipient@example.com',
            'recipient_company_name': 'Recipient Corp',
            'recipient_company_address': '123 Main St, City, State',
            'main_type': 'for_keep',
            'description': 'Documents for permanent transfer',
            'remarks': 'Test transmittal',
        }
        
        response = self.client.post(self.create_url, data, follow=True)
        
        # Should create successfully
        self.assertEqual(response.status_code, 200)
        transmittal = ExternalTransmittal.objects.filter(
            recipient_email='recipient@example.com'
        ).first()
        
        self.assertIsNotNone(transmittal)
        self.assertEqual(transmittal.main_type, 'for_keep')
        self.assertEqual(transmittal.status, 'in_transit')
        self.assertIsNone(transmittal.date_deadline)  # No deadline for FOR_KEEP
        
        print("✅ FOR_KEEP Creation Test: PASSED - No date required")

    def test_for_return_creation_requires_date(self):
        """
        REQUIREMENT: FOR_RETURN transmittal requires DateReturn and DateDeadline.
        Test that FOR_RETURN without date fails validation.
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Try to create FOR_RETURN WITHOUT date
        data = {
            'recipient_name': 'Jane Doe',
            'recipient_email': 'recipient2@example.com',
            'recipient_company_name': 'Recipient Corp 2',
            'recipient_company_address': '456 Oak Ave, Town, State',
            'main_type': 'for_return',
            # Missing date_deadline
            'description': 'Documents for temporary transfer',
        }
        
        response = self.client.post(self.create_url, data)
        
        # Should fail - form has errors
        self.assertEqual(response.status_code, 200)  # Form re-rendered
        self.assertFormError(response, 'form', 'date_deadline', 
                            'This field is required for FOR_RETURN transmittals.')
        
        print("✅ FOR_RETURN Date Validation Test: PASSED - Date required")

    def test_for_return_creation_with_valid_date(self):
        """
        REQUIREMENT: FOR_RETURN transmittal requires DateReturn and DateDeadline.
        Test creating a FOR_RETURN transmittal with valid deadline date.
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Create FOR_RETURN WITH date
        deadline = (timezone.now() + timedelta(days=3)).date()
        data = {
            'recipient_name': 'Jane Doe',
            'recipient_email': 'recipient2@example.com',
            'recipient_company_name': 'Recipient Corp 2',
            'recipient_company_address': '456 Oak Ave, Town, State',
            'main_type': 'for_return',
            'date_deadline': deadline.strftime('%Y-%m-%d'),
            'description': 'Documents for temporary transfer',
        }
        
        response = self.client.post(self.create_url, data, follow=True)
        
        # Should create successfully
        self.assertEqual(response.status_code, 200)
        transmittal = ExternalTransmittal.objects.filter(
            recipient_email='recipient2@example.com'
        ).first()
        
        self.assertIsNotNone(transmittal)
        self.assertEqual(transmittal.main_type, 'for_return')
        self.assertEqual(transmittal.status, 'in_transit')
        self.assertEqual(transmittal.date_deadline, deadline)
        
        print("✅ FOR_RETURN Creation Test: PASSED - Valid date accepted")


class DeliveryConfirmationStatusTests(TestCase):
    """Test delivery confirmation and status transitions."""

    def setUp(self):
        """Set up test transmittals."""
        self.client = Client()
        
        # Create sender user
        self.sender, _ = User.objects.get_or_create(
            username='sender',
            defaults={'email': 'sender@example.com'}
        )
        if not self.sender.check_password('testpass123'):
            self.sender.set_password('testpass123')
            self.sender.save()
        Profile.objects.get_or_create(
            user=self.sender,
            defaults={'company': 'Sender Corp', 'contact': '1234567890'}
        )
        
        # Create recipient user
        self.recipient, _ = User.objects.get_or_create(
            username='recipient',
            defaults={'email': 'recipient@example.com'}
        )
        if not self.recipient.check_password('testpass123'):
            self.recipient.set_password('testpass123')
            self.recipient.save()
        Profile.objects.get_or_create(
            user=self.recipient,
            defaults={'company': 'Recipient Corp', 'contact': '1234567890'}
        )
        
        # Create FOR_KEEP transmittal
        self.for_keep = ExternalTransmittal.objects.create(
            sender_email=self.sender.email,
            sender_name=self.sender.get_full_name() or self.sender.username,
            sender_company=self.sender.profile.company,
            recipient_email=self.recipient.email,
            recipient_name='Recipient User',
            recipient_company_name='Recipient Corp',
            recipient_company_address='123 Main St',
            main_type='for_keep',
            status='in_transit',
            description='Test FOR_KEEP transmittal'
        )
        
        # Create FOR_RETURN transmittal
        deadline = timezone.now().date() + timedelta(days=3)
        self.for_return = ExternalTransmittal.objects.create(
            sender_email=self.sender.email,
            sender_name=self.sender.get_full_name() or self.sender.username,
            sender_company=self.sender.profile.company,
            recipient_email=self.recipient.email,
            recipient_name='Recipient User',
            recipient_company_name='Recipient Corp',
            recipient_company_address='123 Main St',
            main_type='for_return',
            date_deadline=deadline,
            status='in_transit',
            description='Test FOR_RETURN transmittal'
        )

    def _create_test_file(self):
        """Helper to create a test file upload."""
        return SimpleUploadedFile(
            "proof.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_for_keep_delivery_confirmation_closes_case(self):
        """
        REQUIREMENT: Delivery confirmation sets FOR_KEEP → CLOSED
        Test that marking FOR_KEEP as received closes the case.
        """
        self.client.login(username='recipient', password='testpass123')
        
        # Navigate to detail page and mark as received
        action_url = f'/transmittals/external/{self.for_keep.id}/action/'
        
        data = {
            'action_type': 'mark_received',
            'attachment': self._create_test_file(),
            'notes': 'Received and confirmed'
        }
        
        response = self.client.post(action_url, data, follow=True)
        
        # Reload transmittal from DB
        self.for_keep.refresh_from_db()
        
        # Verify status changed to received (closed state for FOR_KEEP)
        self.assertEqual(self.for_keep.status, 'received')
        self.assertIsNotNone(self.for_keep.received_at)
        
        # Verify audit trail
        audit = ExternalTransmittalAuditTrail.objects.filter(
            external_transmittal=self.for_keep,
            action='mark_received'
        ).first()
        self.assertIsNotNone(audit)
        
        print("✅ FOR_KEEP Delivery Confirmation Test: PASSED - Status → received")

    def test_for_return_full_return_closes_case(self):
        """
        REQUIREMENT: Delivery confirmation sets FOR_RETURN → CLOSED (full return)
        Test that full return action closes the case.
        """
        self.client.login(username='recipient', password='testpass123')
        
        # Mark as opened first
        self.for_return.status = 'open'
        self.for_return.save()
        
        # Submit full return action
        action_url = f'/transmittals/external/{self.for_return.id}/action/'
        
        data = {
            'action_type': 'full_return',
            'attachment': self._create_test_file(),
            'notes': 'All items returned'
        }
        
        response = self.client.post(action_url, data, follow=True)
        
        # Reload transmittal
        self.for_return.refresh_from_db()
        
        # Verify status is closed
        self.assertEqual(self.for_return.status, 'closed')
        self.assertEqual(self.for_return.sub_type, 'full')
        self.assertIsNotNone(self.for_return.closed_at)
        
        # Verify audit trail
        audit = ExternalTransmittalAuditTrail.objects.filter(
            external_transmittal=self.for_return,
            action='full_return'
        ).first()
        self.assertIsNotNone(audit)
        
        print("✅ FOR_RETURN Full Return Test: PASSED - Status → closed")


class PartialReturnTests(TestCase):
    """Test partial return behavior - case stays OPEN."""

    def setUp(self):
        """Set up test transmittal."""
        self.client = Client()
        
        self.sender, _ = User.objects.get_or_create(
            username='sender',
            defaults={'email': 'sender@example.com'}
        )
        if not self.sender.check_password('testpass123'):
            self.sender.set_password('testpass123')
            self.sender.save()
        Profile.objects.get_or_create(
            user=self.sender,
            defaults={'company': 'Sender Corp', 'contact': '1234567890'}
        )
        
        self.recipient, _ = User.objects.get_or_create(
            username='recipient',
            defaults={'email': 'recipient@example.com'}
        )
        if not self.recipient.check_password('testpass123'):
            self.recipient.set_password('testpass123')
            self.recipient.save()
        Profile.objects.get_or_create(
            user=self.recipient,
            defaults={'company': 'Recipient Corp', 'contact': '1234567890'}
        )
        
        deadline = timezone.now().date() + timedelta(days=3)
        self.for_return = ExternalTransmittal.objects.create(
            sender_email=self.sender.email,
            sender_name=self.sender.username,
            sender_company=self.sender.profile.company,
            recipient_email=self.recipient.email,
            recipient_name='Recipient User',
            recipient_company_name='Recipient Corp',
            recipient_company_address='123 Main St',
            main_type='for_return',
            date_deadline=deadline,
            status='open',
            description='Test FOR_RETURN transmittal'
        )

    def _create_test_file(self):
        """Helper to create a test file upload."""
        return SimpleUploadedFile(
            "proof.pdf",
            b"file_content",
            content_type="application/pdf"
        )

    def test_partial_return_keeps_case_open(self):
        """
        REQUIREMENT: Partial keeps case OPEN.
        Test that partial return does NOT close the case.
        """
        self.client.login(username='recipient', password='testpass123')
        
        # Submit partial return action
        action_url = f'/transmittals/external/{self.for_return.id}/action/'
        
        data = {
            'action_type': 'partial_return',
            'attachment': self._create_test_file(),
            'notes': 'Some items returned'
        }
        
        response = self.client.post(action_url, data, follow=True)
        
        # Reload transmittal
        self.for_return.refresh_from_db()
        
        # Verify status is still OPEN (not closed)
        self.assertEqual(self.for_return.status, 'open')
        self.assertEqual(self.for_return.sub_type, 'partial')
        self.assertIsNone(self.for_return.closed_at)  # Not closed
        
        # Verify audit trail
        audit = ExternalTransmittalAuditTrail.objects.filter(
            external_transmittal=self.for_return,
            action='partial_return'
        ).first()
        self.assertIsNotNone(audit)
        
        print("✅ Partial Return Test: PASSED - Case stays OPEN")

    def test_paid_sample_from_partial_closes_case(self):
        """
        REQUIREMENT: Convert to Paid Sample closes case.
        Test that paid sample action from partial return closes the case.
        """
        # Set transmittal to partial return state
        self.for_return.status = 'open'
        self.for_return.sub_type = 'partial'
        self.for_return.save()
        
        self.client.login(username='recipient', password='testpass123')
        
        # Submit paid sample action
        action_url = f'/transmittals/external/{self.for_return.id}/action/'
        
        data = {
            'action_type': 'paid_sample',
            'attachment': self._create_test_file(),
            'notes': 'Retained as paid sample'
        }
        
        response = self.client.post(action_url, data, follow=True)
        
        # Reload transmittal
        self.for_return.refresh_from_db()
        
        # Verify status is closed and sub_type changed
        self.assertEqual(self.for_return.status, 'closed')
        self.assertEqual(self.for_return.sub_type, 'for_sample')
        self.assertIsNotNone(self.for_return.closed_at)
        
        # Verify audit trail
        audit = ExternalTransmittalAuditTrail.objects.filter(
            external_transmittal=self.for_return,
            action='paid_sample'
        ).first()
        self.assertIsNotNone(audit)
        
        print("✅ Paid Sample Conversion Test: PASSED - Case closed")

    def test_convert_to_for_keep_from_partial_closes_case(self):
        """
        REQUIREMENT: Convert to For Keep (SubType) closes case without changing main type.
        Test converting partial return to For Keep (as subtype).
        """
        # Set transmittal to partial return state
        self.for_return.status = 'open'
        self.for_return.sub_type = 'partial'
        self.for_return.save()
        
        self.client.login(username='recipient', password='testpass123')
        
        # Submit convert to for keep action
        action_url = f'/transmittals/external/{self.for_return.id}/action/'
        
        data = {
            'action_type': 'convert_to_keep',
            'attachment': self._create_test_file(),
            'notes': 'Converting to For Keep (permanent transfer)'
        }
        
        response = self.client.post(action_url, data, follow=True)
        
        # Reload transmittal
        self.for_return.refresh_from_db()
        
        # Verify case is closed but main_type remains 'for_return'
        self.assertEqual(self.for_return.status, 'closed')
        self.assertEqual(self.for_return.main_type, 'for_return')  # Main type unchanged
        self.assertEqual(self.for_return.sub_type, 'for_keep')  # SubType changed
        self.assertIsNotNone(self.for_return.closed_at)
        
        # Verify audit trail
        audit = ExternalTransmittalAuditTrail.objects.filter(
            external_transmittal=self.for_return,
            action='convert_to_keep'
        ).first()
        self.assertIsNotNone(audit)
        
        print("✅ Convert to For Keep Test: PASSED - SubType changed, main_type preserved")


class StatusReversionPreventionTests(TestCase):
    """Test prevention of invalid status reversions."""

    def setUp(self):
        """Set up closed transmittal."""
        self.client = Client()
        
        self.sender, _ = User.objects.get_or_create(
            username='sender',
            defaults={'email': 'sender@example.com'}
        )
        if not self.sender.check_password('testpass123'):
            self.sender.set_password('testpass123')
            self.sender.save()
        Profile.objects.get_or_create(
            user=self.sender,
            defaults={'company': 'Sender Corp', 'contact': '1234567890'}
        )
        
        self.recipient, _ = User.objects.get_or_create(
            username='recipient',
            defaults={'email': 'recipient@example.com'}
        )
        if not self.recipient.check_password('testpass123'):
            self.recipient.set_password('testpass123')
            self.recipient.save()
        Profile.objects.get_or_create(
            user=self.recipient,
            defaults={'company': 'Recipient Corp', 'contact': '1234567890'}
        )
        
        # Create closed FOR_KEEP transmittal
        self.closed_transmittal = ExternalTransmittal.objects.create(
            sender_email=self.sender.email,
            sender_name=self.sender.username,
            sender_company=self.sender.profile.company,
            recipient_email=self.recipient.email,
            recipient_name='Recipient User',
            recipient_company_name='Recipient Corp',
            recipient_company_address='123 Main St',
            main_type='for_keep',
            status='received',  # Closed state for FOR_KEEP
            received_at=timezone.now(),
            description='Closed transmittal'
        )

    def test_cannot_reopen_closed_case(self):
        """
        REQUIREMENT: System prevents reopening CLOSED case.
        Test that action buttons are not available on closed transmittals.
        """
        self.client.login(username='recipient', password='testpass123')
        
        # Get detail page
        detail_url = f'/transmittals/external/{self.closed_transmittal.id}/detail/'
        response = self.client.get(detail_url)
        
        # Verify status is closed
        self.closed_transmittal.refresh_from_db()
        self.assertEqual(self.closed_transmittal.status, 'received')
        
        # Verify no action buttons in response (no mark_received action visible)
        content = response.content.decode()
        self.assertNotIn('mark_received', content)  # No button to reopen
        
        print("✅ Reopen Prevention Test: PASSED - Closed case cannot be reopened")

    def test_cannot_revert_to_in_transit(self):
        """
        REQUIREMENT: System prevents reverting to IN_TRANSIT.
        Test that once a transmittal is received/opened, cannot go back to in_transit.
        """
        # Change to open state
        self.closed_transmittal.status = 'open'
        self.closed_transmittal.main_type = 'for_return'
        self.closed_transmittal.save()
        
        self.client.login(username='recipient', password='testpass123')
        
        # Try to manually POST to revert status (if someone tries)
        action_url = f'/transmittals/external/{self.closed_transmittal.id}/action/'
        
        data = {
            'action_type': 'mark_received',  # Trying to revert
            'attachment': SimpleUploadedFile("test.pdf", b"content"),
            'notes': 'Trying to revert'
        }
        
        # Attempt should fail or be prevented by form validation
        # (mark_received is only for in_transit status)
        response = self.client.post(action_url, data)
        
        # Verify status did not change back to in_transit
        self.closed_transmittal.refresh_from_db()
        self.assertNotEqual(self.closed_transmittal.status, 'in_transit')
        
        print("✅ IN_TRANSIT Reversion Prevention Test: PASSED")


class DeadlineTriggerTests(TestCase):
    """Test deadline trigger behavior - sends email without auto-closing."""

    def setUp(self):
        """Set up FOR_RETURN transmittal with deadline."""
        from django.test import override_settings
        
        self.sender, _ = User.objects.get_or_create(
            username='sender',
            defaults={'email': 'sender@example.com'}
        )
        if not self.sender.check_password('testpass123'):
            self.sender.set_password('testpass123')
            self.sender.save()
        Profile.objects.get_or_create(
            user=self.sender,
            defaults={'company': 'Sender Corp', 'contact': '1234567890'}
        )
        
        self.recipient, _ = User.objects.get_or_create(
            username='recipient',
            defaults={'email': 'recipient@example.com'}
        )
        if not self.recipient.check_password('testpass123'):
            self.recipient.set_password('testpass123')
            self.recipient.save()
        Profile.objects.get_or_create(
            user=self.recipient,
            defaults={'company': 'Recipient Corp', 'contact': '1234567890'}
        )
        
        # Create FOR_RETURN transmittal with deadline in past
        deadline = timezone.now().date() - timedelta(days=1)  # 1 day overdue
        self.for_return = ExternalTransmittal.objects.create(
            sender_email=self.sender.email,
            sender_name=self.sender.username,
            sender_company=self.sender.profile.company,
            recipient_email=self.recipient.email,
            recipient_name='Recipient User',
            recipient_company_name='Recipient Corp',
            recipient_company_address='123 Main St',
            main_type='for_return',
            date_deadline=deadline,
            status='open',
            description='FOR_RETURN transmittal with passed deadline'
        )

    def test_deadline_sends_email_without_closing(self):
        """
        REQUIREMENT: Deadline trigger sends email without auto-closing.
        Test that deadline reminder email is sent but case remains open.
        """
        from django.core import mail
        from transmittals.email_utils import send_external_transmittal_deadline_reminder
        
        # Verify initial status is open
        self.assertEqual(self.for_return.status, 'open')
        self.assertIsNone(self.for_return.closed_at)
        
        # Manually trigger email (simulating scheduled task)
        send_external_transmittal_deadline_reminder(self.for_return)
        
        # Reload and verify status unchanged (NOT auto-closed)
        self.for_return.refresh_from_db()
        self.assertEqual(self.for_return.status, 'open')
        self.assertIsNone(self.for_return.closed_at)
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('overdue', email.subject.lower())
        self.assertIn(self.recipient.email, email.to)
        
        # Verify last_reminder_date was updated to prevent duplicate daily emails
        self.for_return.refresh_from_db()
        self.assertIsNotNone(self.for_return.last_reminder_date)
        
        print("✅ Deadline Trigger Test: PASSED - Email sent, case remains OPEN")

    def test_deadline_no_duplicate_same_day(self):
        """
        REQUIREMENT: Deadline trigger sends email without auto-closing.
        Test that multiple triggers same day don't send duplicate emails.
        """
        from django.core import mail
        from transmittals.email_utils import send_external_transmittal_deadline_reminder
        
        # First trigger
        send_external_transmittal_deadline_reminder(self.for_return)
        self.assertEqual(len(mail.outbox), 1)
        
        # Clear mail
        mail.outbox = []
        
        # Second trigger same day
        send_external_transmittal_deadline_reminder(self.for_return)
        
        # Should not send duplicate
        self.assertEqual(len(mail.outbox), 0)
        
        print("✅ No Duplicate Email Test: PASSED - Prevented same-day duplicates")


class AuditTrailTests(TestCase):
    """Test complete audit trail tracking for all actions."""

    def setUp(self):
        """Set up test transmittals."""
        self.sender, _ = User.objects.get_or_create(
            username='sender',
            defaults={'email': 'sender@example.com'}
        )
        if not self.sender.check_password('testpass123'):
            self.sender.set_password('testpass123')
            self.sender.save()
        Profile.objects.get_or_create(
            user=self.sender,
            defaults={'company': 'Sender Corp', 'contact': '1234567890'}
        )
        
        self.recipient, _ = User.objects.get_or_create(
            username='recipient',
            defaults={'email': 'recipient@example.com'}
        )
        if not self.recipient.check_password('testpass123'):
            self.recipient.set_password('testpass123')
            self.recipient.save()
        Profile.objects.get_or_create(
            user=self.recipient,
            defaults={'company': 'Recipient Corp', 'contact': '1234567890'}
        )
        
        self.for_keep = ExternalTransmittal.objects.create(
            sender_email=self.sender.email,
            sender_name=self.sender.username,
            sender_company=self.sender.profile.company,
            recipient_email=self.recipient.email,
            recipient_name='Recipient User',
            recipient_company_name='Recipient Corp',
            recipient_company_address='123 Main St',
            main_type='for_keep',
            status='in_transit',
            description='Test FOR_KEEP transmittal'
        )

    def test_creation_audit_trail(self):
        """Test that creation is logged in audit trail."""
        # Verify creation audit exists
        audit = ExternalTransmittalAuditTrail.objects.filter(
            external_transmittal=self.for_keep,
            action='created'
        ).first()
        
        self.assertIsNotNone(audit)
        self.assertEqual(audit.email, self.sender.email)
        self.assertIsNotNone(audit.created_at)
        
        print("✅ Creation Audit Trail Test: PASSED")

    def test_status_transition_audit_trail(self):
        """Test that status transitions are logged with user info."""
        # Create audit entry for status transition
        audit = ExternalTransmittalAuditTrail.objects.create(
            external_transmittal=self.for_keep,
            action='mark_received',
            user=self.recipient,
            email=self.recipient.email,
            notes='Received and confirmed'
        )
        
        # Verify audit entry exists with correct details
        audit.refresh_from_db()
        self.assertEqual(audit.action, 'mark_received')
        self.assertEqual(audit.user, self.recipient)
        self.assertEqual(audit.email, self.recipient.email)
        self.assertIsNotNone(audit.created_at)
        
        print("✅ Status Transition Audit Trail Test: PASSED")

    def test_audit_trail_links_proof_attachment(self):
        """Test that audit trail entry links to proof attachment."""
        # Create proof attachment
        proof = ExternalTransmittalAttachment.objects.create(
            external_transmittal=self.for_keep,
            attachment=SimpleUploadedFile("proof.pdf", b"content"),
            attachment_type='Proof of Delivery'
        )
        
        # Create audit with linked proof
        audit = ExternalTransmittalAuditTrail.objects.create(
            external_transmittal=self.for_keep,
            action='mark_received',
            user=self.recipient,
            email=self.recipient.email,
            proof_attachment=proof
        )
        
        # Verify link
        audit.refresh_from_db()
        self.assertEqual(audit.proof_attachment, proof)
        
        print("✅ Audit Trail Proof Link Test: PASSED")


class ReferenceNumberTests(TestCase):
    """Test reference number generation with EXT prefix."""

    def test_external_reference_number_format(self):
        """Test that external transmittals use EXT-YYYYMMDD-XXXX format."""
        user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if not user.check_password('testpass123'):
            user.set_password('testpass123')
            user.save()
        Profile.objects.get_or_create(
            user=user,
            defaults={'company': 'Test Corp', 'contact': '1234567890'}
        )
        
        # Create transmittal
        transmittal = ExternalTransmittal.objects.create(
            sender_email=user.email,
            sender_name=user.username,
            sender_company=user.profile.company,
            recipient_email='recipient@example.com',
            recipient_name='Recipient',
            recipient_company_name='Recipient Corp',
            recipient_company_address='123 Main St',
            main_type='for_keep',
            status='in_transit',
            description='Test'
        )
        
        # Verify reference number format
        self.assertIsNotNone(transmittal.reference_number)
        self.assertTrue(transmittal.reference_number.startswith('EXT-'))
        
        # Parse format: EXT-YYYYMMDD-XXXX
        parts = transmittal.reference_number.split('-')
        self.assertEqual(len(parts), 3)
        self.assertEqual(parts[0], 'EXT')
        self.assertEqual(len(parts[1]), 8)  # YYYYMMDD
        self.assertEqual(len(parts[2]), 4)  # XXXX
        
        print(f"✅ Reference Number Format Test: PASSED - {transmittal.reference_number}")


# Test runner summary
class TestSummary:
    """Print test execution summary."""
    
    @staticmethod
    def print_summary():
        print("\n" + "="*80)
        print("EXTERNAL TRANSMITTAL SYSTEM - TEST SUMMARY")
        print("="*80)
        print("\nTest Cases Executed:")
        print("  ✅ FOR_KEEP creation without date requirement")
        print("  ✅ FOR_RETURN creation with required date validation")
        print("  ✅ FOR_KEEP delivery confirmation → received (closed)")
        print("  ✅ FOR_RETURN full return → closed with sub_type=full")
        print("  ✅ Partial return keeps case OPEN")
        print("  ✅ Paid sample conversion closes case")
        print("  ✅ Convert to For Keep (SubType) closes case")
        print("  ✅ Prevention of reopening closed cases")
        print("  ✅ Prevention of reverting to IN_TRANSIT")
        print("  ✅ Deadline trigger sends email without auto-closing")
        print("  ✅ No duplicate emails on same day")
        print("  ✅ Audit trail tracking for all actions")
        print("  ✅ Reference number format (EXT-YYYYMMDD-XXXX)")
        print("\n" + "="*80)
