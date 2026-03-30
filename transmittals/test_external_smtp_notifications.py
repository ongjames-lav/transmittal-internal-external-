"""
Test cases for External Transmittal SMTP Email Notifications

This test suite verifies that email notifications are automatically sent
when status changes occur in external transmittals with attachments.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core import mail
from transmittals.models import ExternalTransmittal, ExternalTransmittalAttachment
from transmittals.email_utils import send_external_transmittal_resolution_email
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from datetime import date


class ExternalTransmittalEmailNotificationTests(TestCase):
    """
    Test suite for automatic SMTP email notifications on external transmittal status changes.
    
    Feature: When a user uploads an attachment and marks as received (or other status changes),
    an SMTP email is automatically sent to both sender and recipient with full details.
    """
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create test users
        self.sender_user = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        
        self.recipient_email = 'recipient@example.com'
        
        # Create test transmittal
        self.transmittal = ExternalTransmittal.objects.create(
            sender_email=self.sender_user.email,
            sender_name='Test Sender',
            sender_company='Test Company',
            recipient_email=self.recipient_email,
            recipient_name='Test Recipient',
            main_type='for_keep',
            description='Test item for external transmittal',
            status='in_transit',
            reference_number='TR-TEST-2026-001'
        )
    
    def test_mark_received_sends_email_with_attachment(self):
        """
        Test that marking transmittal as received sends email with attachment details.
        
        FEATURE: When user marks as received and uploads proof attachment,
        email should automatically be sent with attachment information.
        """
        # Create proof attachment
        proof_file = SimpleUploadedFile(
            "delivery_proof_20260305.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        attachment = ExternalTransmittalAttachment.objects.create(
            transmittal=self.transmittal,
            file=proof_file,
            attachment_type='Proof of Delivery',
            uploaded_by_email=self.sender_user.email
        )
        
        # Update status
        self.transmittal.status = 'received'
        self.transmittal.received_at = timezone.now()
        self.transmittal.save()
        
        # Send email notification
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='mark_received',
            notes='Item received in good condition'
        )
        
        # Verify email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        # Verify email recipients
        email = mail.outbox[0]
        self.assertIn(self.sender_user.email, email.to)
        self.assertIn(self.recipient_email, email.to)
        
        # Verify email subject
        self.assertIn('Marked as Received', email.subject)
        self.assertIn(self.transmittal.reference_number, email.subject)
        
        # Verify email contains attachment information
        self.assertIn('Attachments Uploaded', email.body)
        self.assertIn('Proof of Delivery', email.body)
        self.assertIn('delivery_proof_20260305.pdf', email.body)
        
        # Verify HTML version contains attachment details
        self.assertEqual(len(email.alternatives), 1)
        html_content = email.alternatives[0][0]
        self.assertIn('📎', html_content)
        self.assertIn('Attachments', html_content)
    
    def test_full_return_sends_email_with_rga(self):
        """
        Test that recording full return sends email with RGA attachment.
        """
        # Create transmittal with For Return type
        self.transmittal.main_type = 'for_return'
        self.transmittal.status = 'received'
        self.transmittal.received_status = 'open'
        self.transmittal.date_return = date.today()
        self.transmittal.save()
        
        # Create RGA attachment
        rga_file = SimpleUploadedFile(
            "rga_20260305.pdf",
            b"rga_content",
            content_type="application/pdf"
        )
        
        attachment = ExternalTransmittalAttachment.objects.create(
            transmittal=self.transmittal,
            file=rga_file,
            attachment_type='Proof of Full Return',
            uploaded_by_email=self.sender_user.email
        )
        
        # Update status
        self.transmittal.status = 'closed'
        self.transmittal.sub_type = 'full'
        self.transmittal.save()
        
        # Send email
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='full_return',
            notes='All items returned in original condition'
        )
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Full Return', email.subject)
        self.assertIn('rga_20260305.pdf', email.body)
        self.assertIn('Proof of Full Return', email.body)
    
    def test_partial_return_sends_email(self):
        """
        Test that recording partial return sends email.
        """
        self.transmittal.main_type = 'for_return'
        self.transmittal.status = 'received'
        self.transmittal.date_return = date.today()
        self.transmittal.save()
        
        # Create attachment
        proof_file = SimpleUploadedFile(
            "partial_return_20260305.pdf",
            b"content",
            content_type="application/pdf"
        )
        
        ExternalTransmittalAttachment.objects.create(
            transmittal=self.transmittal,
            file=proof_file,
            attachment_type='Proof of Partial Return',
            uploaded_by_email=self.sender_user.email
        )
        
        self.transmittal.sub_type = 'partial'
        self.transmittal.save()
        
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='partial_return',
            notes='Partial items returned'
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Partial Return', email.subject)
        self.assertIn('partial_return_20260305.pdf', email.body)
    
    def test_admin_override_sends_email(self):
        """
        Test that admin override status change sends email.
        """
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='admin_override',
            notes='Admin override: Correcting status to received'
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertIn('Admin Override', email.subject)
        self.assertIn('Admin override: Correcting status to received', email.body)
    
    def test_email_contains_timestamp(self):
        """
        Test that email contains timestamp of status change.
        """
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='mark_received'
        )
        
        self.assertTrue(result)
        email = mail.outbox[0]
        
        # Verify timestamp is in email
        self.assertIn('Updated At:', email.body)
        # Should contain date format YYYY-MM-DD HH:MM:SS
        self.assertRegex(email.body, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    
    def test_email_html_format(self):
        """
        Test that email has both HTML and plain text versions.
        """
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='mark_received'
        )
        
        self.assertTrue(result)
        email = mail.outbox[0]
        
        # Verify HTML alternative exists
        self.assertEqual(len(email.alternatives), 1)
        self.assertEqual(email.alternatives[0][1], 'text/html')
        
        # Verify HTML contains styling
        html = email.alternatives[0][0]
        self.assertIn('<style>', html)
        self.assertIn('background:', html)
        self.assertIn('color:', html)
    
    def test_email_with_multiple_attachments(self):
        """
        Test that email correctly lists multiple attachments.
        """
        # Create multiple attachments
        for i in range(3):
            file_obj = SimpleUploadedFile(
                f"document_{i}.pdf",
                b"content",
                content_type="application/pdf"
            )
            ExternalTransmittalAttachment.objects.create(
                transmittal=self.transmittal,
                file=file_obj,
                attachment_type=f'Document {i}',
                uploaded_by_email=self.sender_user.email
            )
        
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='mark_received'
        )
        
        self.assertTrue(result)
        email = mail.outbox[0]
        
        # Verify all attachments are listed
        for i in range(3):
            self.assertIn(f'document_{i}.pdf', email.body)
            self.assertIn(f'Document {i}', email.body)
    
    def test_email_error_handling(self):
        """
        Test that email function handles errors gracefully.
        """
        # Create transmittal with invalid email
        invalid_transmittal = ExternalTransmittal.objects.create(
            sender_email='invalid@',
            sender_name='Test',
            recipient_email='also@invalid',
            main_type='for_keep',
            description='Test',
            status='in_transit',
            reference_number='TR-INVALID-001'
        )
        
        # This should handle error gracefully (not crash)
        try:
            result = send_external_transmittal_resolution_email(
                transmittal=invalid_transmittal,
                action_type='mark_received'
            )
            # Result should be False due to invalid emails
            self.assertFalse(result)
        except Exception as e:
            # Should not raise exception - should handle gracefully
            self.fail(f"Email function should handle errors gracefully: {e}")
    
    def test_transmittal_description_in_email(self):
        """
        Test that email includes transmittal description.
        """
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='mark_received'
        )
        
        self.assertTrue(result)
        email = mail.outbox[0]
        self.assertIn(self.transmittal.description, email.body)
    
    def test_email_subject_format(self):
        """
        Test that email subject has correct format with reference number.
        """
        result = send_external_transmittal_resolution_email(
            transmittal=self.transmittal,
            action_type='mark_received'
        )
        
        self.assertTrue(result)
        email = mail.outbox[0]
        
        # Subject should be: [REFERENCE] Transmittal Action
        self.assertTrue(email.subject.startswith('['))
        self.assertIn(self.transmittal.reference_number, email.subject)
        self.assertIn('Marked as Received', email.subject)


class ExternalTransmittalViewEmailTests(TestCase):
    """
    Integration tests for email sending from views.
    """
    
    def setUp(self):
        self.client = Client()
        self.sender_user = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='pass123'
        )
        self.client.login(username='sender', password='pass123')
        
        self.transmittal = ExternalTransmittal.objects.create(
            sender_email=self.sender_user.email,
            sender_name='Test Sender',
            recipient_email='recipient@test.com',
            recipient_name='Test Recipient',
            main_type='for_keep',
            description='Test transmittal',
            status='in_transit',
            reference_number='TR-TEST-001'
        )
    
    def test_mark_received_view_sends_email(self):
        """
        Test that mark_received view sends email.
        """
        # Create proof file
        proof_file = SimpleUploadedFile(
            "proof.pdf",
            b"content",
            content_type="application/pdf"
        )
        
        # POST to mark_received
        response = self.client.post(
            f'/transmittals/external/{self.transmittal.pk}/mark-received/',
            {
                'attachment': proof_file,
                'notes': 'Received successfully',
            },
            follow=True
        )
        
        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn('Marked as Received', email.subject)


if __name__ == '__main__':
    import unittest
    unittest.main()
