from django.test import TestCase
from lessons.tests.helpers import LogInTester, reverse_with_next
from django.urls import reverse
from lessons.views import promote_admin, promote_director
from lessons.models import UserAccount,UserRole
from django.contrib import messages

from django.test import Client

class DirectorRoleChangesTestCase(TestCase):
    """Tests for the director_manage_roles view."""

    def setUp(self):
        self.url = reverse('director_manage_roles')

        self.current = UserAccount.objects.create_superuser(
            first_name='Ahmed',
            last_name='Pedro',
            email='apedro@example.org',
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


    # tests assigning and unsigning super-admin privileges to a regular admin account
    def test_promote_admin_to_director(self):
        #Log into  a director account
        self.client.login(email=self.current.email, password="Password123")

        # Change an admin into a director
        self.promote_director_url = reverse('promote_director', args=[self.admin.email])
        admin_count_before = UserAccount.objects.filter(role = UserRole.ADMIN).count()
        response = self.client.get(self.promote_director_url, follow = True)
        admin_count_after = UserAccount.objects.filter(role = UserRole.ADMIN).count()
        self.assertEqual(admin_count_before-1,admin_count_after)

        redirect_url = reverse('director_manage_roles')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'director_manage_roles.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(messages_list[0].level, messages.SUCCESS)


    def test_demote_director_to_admin(self):
        #Log into a director account
        self.client.login(email=self.current.email, password="Password123")

        # Change a director into admin
        self.promote_admin_url = reverse('promote_admin', args=[self.director.email])
        director_count_before = UserAccount.objects.filter(role = UserRole.DIRECTOR).count()
        response = self.client.get(self.promote_admin_url, follow = True)
        director_count_after = UserAccount.objects.filter(role = UserRole.DIRECTOR).count()
        self.assertEqual(director_count_before-1,director_count_after)

        redirect_url = reverse('director_manage_roles')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'director_manage_roles.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(messages_list[0].level, messages.SUCCESS)



    def test_demote_current_director_to_admin(self):
        #Log into a current director account
        self.client.login(email=self.current.email, password="Password123")

        # Change current director into an admin
        self.promote_admin_url = reverse('promote_admin', args=[self.current.email])
        director_count_before = UserAccount.objects.filter(role = UserRole.DIRECTOR).count()
        response = self.client.get(self.promote_admin_url, follow = True)
        director_count_after = UserAccount.objects.filter(role = UserRole.DIRECTOR).count()
        self.assertEqual(director_count_before,director_count_after)

        redirect_url = reverse('director_manage_roles')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'director_manage_roles.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(messages_list[0].level, messages.ERROR)





        # before_count = UserAccount.objects.count()
        # response = self.client.get(self.promote_admin_url, follow = True)
        # after_count = UserAccount.objects.count()
        # redirect_url = reverse('director_manage_roles')
        # self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        # self.assertTemplateUsed(response, 'director_manage_roles.html')
        # self.assertEqual(before_count,after_count)

        # messages_list = list(response.context['messages'])
        # self.assertEqual(str(messages_list[0]), 'Incorrect lesson ID passed')
        # self.assertEqual(messages_list[0].level, messages.ERROR)

    # def test_demote_director_to_admin(self):
    #     pass
    #
    #
    # def test_edit_director_info(self):
    #     pass
    #
    # def test_edit_admin_info(self):
    #     pass
    #
    #
    # def test_disable_director_info(self):
    #     pass
    #
    # def test_disable_admin_info(self):
    #     pass
    #
    #
    # def test_delete_director(self):
    #     pass
    #
    # def test_delete_admin(self):
    #     pass
    #
    #
    # # Prevent/ allow actions dont on the current user
    #
    # def current_user_can_edit_himself(self):
    #     pass
    #
    # def current_user_cant_promote_himself(self):
    #     pass
    #
    # def current_user_demote_promote_himself(self):
    #     pass
    #
    # def current_user_cant_edit_himself(self):
    #     pass
    #
    # def current_user_cant_delete_himself(self):
    #     pass
    #
    # def current_user_cant_disable_himself(self):
    #     pass
