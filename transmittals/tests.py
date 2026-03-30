
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Transmittal
from datetime import datetime, timedelta
from django.core.management import call_command

class TransmittalTrashTests(TestCase):
    def setUp(self):
        # Create users
        self.sender = User.objects.create_user(username='sender', email='sender@example.com', password='password')
        self.recipient = User.objects.create_user(username='recipient', email='recipient@example.com', password='password')
        
        # Create transmittal
        self.transmittal = Transmittal.objects.create(
            sender=self.sender,
            recipient_name='Recipient',
            recipient_email='recipient@example.com',
            description='Test Email',
            remarks='Test'
        )
        
        self.client = Client()

    def test_soft_delete_and_trash(self):
        """Test moving to trash and viewing it."""
        self.client.login(username='recipient', password='password')
        
        # Delete email
        self.client.post('/transmittals/delete/', {
            'email_ids': [self.transmittal.id],
            'folder': 'inbox'
        })
        
        self.transmittal.refresh_from_db()
        self.assertTrue(self.transmittal.recipient_deleted)
        self.assertIsNotNone(self.transmittal.recipient_deleted_at)
        
        # Verify in trash
        response = self.client.get('/transmittals/trash/')
        self.assertContains(response, 'Test Email')

    def test_restore(self):
        """Test restoring from trash."""
        self.client.login(username='recipient', password='password')
        
        # Move to trash first
        self.transmittal.recipient_deleted = True
        self.transmittal.recipient_deleted_at = datetime.now()
        self.transmittal.save()
        
        # Restore
        self.client.post('/transmittals/restore/', {
            'email_ids': [self.transmittal.id]
        })
        
        self.transmittal.refresh_from_db()
        self.assertFalse(self.transmittal.recipient_deleted)
        self.assertIsNone(self.transmittal.recipient_deleted_at)
        
        # Verify not in trash
        response = self.client.get('/transmittals/trash/')
        self.assertNotContains(response, 'Test Email')

    def test_permanent_delete(self):
        """Test manual permanent delete (purge)."""
        self.client.login(username='recipient', password='password')
        
        # Move to trash
        self.transmittal.recipient_deleted = True
        self.transmittal.save()
        
        # Delete forever
        self.client.post('/transmittals/permanent-delete/', {
            'email_ids': [self.transmittal.id]
        })
        
        self.transmittal.refresh_from_db()
        self.assertTrue(self.transmittal.recipient_purged)
        
        # Verify not in trash
        response = self.client.get('/transmittals/trash/')
        self.assertNotContains(response, 'Test Email')

    def test_auto_cleanup(self):
        """Test management command for 30-day cleanup."""
        # Setup: Sender deleted 31 days ago, Recipient deleted today
        old_date = datetime.now() - timedelta(days=31)
        self.transmittal.sender_deleted = True
        self.transmittal.sender_deleted_at = old_date
        self.transmittal.sender_purged = False
        
        self.transmittal.recipient_deleted = True
        self.transmittal.recipient_deleted_at = datetime.now()
        self.transmittal.recipient_purged = False
        self.transmittal.save()
        
        # Run command
        call_command('delete_old_trash')
        
        self.transmittal.refresh_from_db()
        # Sender should be purged (auto)
        self.assertTrue(self.transmittal.sender_purged)
        # Recipient should NOT be purged (too fresh)
        self.assertFalse(self.transmittal.recipient_purged)
        # Record should still exist
        self.assertIsNotNone(self.transmittal.pk)
        
        # Now make recipient purged too
        self.transmittal.recipient_purged = True
        self.transmittal.save()
        
        # Run command again -> should delete row
        call_command('delete_old_trash')
        
        with self.assertRaises(Transmittal.DoesNotExist):
            Transmittal.objects.get(pk=self.transmittal.pk)
