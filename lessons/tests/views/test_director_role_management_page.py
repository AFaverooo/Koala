from django.test import TestCase
from lessons.tests.helpers import LogInTester, reverse_with_next
from django.urls import reverse

class DirectorRoleChangesTestCase(TestCase):
    """Tests for the director_manage_roles view."""

    def setUp(self):
        self.url = reverse('director_manage_roles')
        self.admin = UserAccount.objects.create_admin(
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123',
            gender = 'F',
        )

        self.director = UserAccount.objects.create_superuser(
            first_name='Jack',
            last_name='Smith',
            email='jsmith@example.org',
            password='Password123',
            gender = 'M',
        )

    def test_change_role_page_url(self):
        self.assertEqual(self.url,'/director_manage_roles/')


    def test_promote_admin_to_director(self):
        self.assertEqual(self.url,'/director_manage_roles/')
