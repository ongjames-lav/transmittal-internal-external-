
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Profile

class ProfileEditTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password',
            first_name='Test',
            last_name='User'
        )
        self.client = Client()
        
        # Profile is created by signal, get it
        self.profile = self.user.profile
        self.profile.contact = '1234567890'
        self.profile.address = 'Old Address'
        self.profile.save()

    def test_edit_profile(self):
        """Test editing profile via the edit view."""
        self.client.login(username='testuser', password='password')
        
        # Check initial state
        response = self.client.get('/accounts/dashboard/')
        self.assertContains(response, 'Old Address')
        
        # Get edit page
        response = self.client.get('/accounts/edit-profile/')
        self.assertEqual(response.status_code, 200)
        
        # Post new data
        response = self.client.post('/accounts/edit-profile/', {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'contact': '0987654321',
            'department': 'New Dept',
            'company': 'New Comp',
            'location': 'New Loc',
            'address': 'New Address'
        })
        
        # Should redirect to dashboard
        self.assertRedirects(response, '/accounts/dashboard/')
        
        # Verify changes in DB
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.profile.contact, '0987654321')
        self.assertEqual(self.profile.address, 'New Address')
        
        # Verify changes on dashboard
        response = self.client.get('/accounts/dashboard/')
        self.assertContains(response, 'New Address')
