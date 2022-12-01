from django.test import TestCase
from lessons.tests.helpers import LogInTester, reverse_with_next
from django.urls import reverse
from lessons.views import promote_admin, promote_director

class DirectorRoleChangesTestCase(TestCase):
    """Tests for the director_manage_roles view."""

    def setUp(self):
        self.url = reverse('director_manage_roles')

        self.current_user = UserAccount.objects.create_admin(
            first_name='Ahmed',
            last_name='Ali',
            email='ahmedali@example.org',
            password='Password123',
            gender = 'M',
        )

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


    # Test for behaviors of the widgets related to each user

    def test_promote_admin_to_director(self):
        pass

    def test_demote_director_to_admin(self):
        pass


    def test_edit_director_info(self):
        pass

    def test_edit_admin_info(self):
        pass


    def test_disable_director_info(self):
        pass

    def test_disable_admin_info(self):
        pass


    def test_delete_director(self):
        pass

    def test_delete_admin(self):
        pass


    # Prevent/ allow actions dont on the current user

    def current_user_can_edit_himself(self):
        pass

    def current_user_cant_promote_himself(self):
        pass

    def current_user_demote_promote_himself(self):
        pass

    def current_user_cant_edit_himself(self):
        pass

    def current_user_cant_delete_himself(self):
        pass

    def current_user_cant_disable_himself(self):
        pass
