
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from lessons.tests.helpers import LogInTester
from django.urls import reverse
from django.contrib import messages
from lessons.forms import LogInForm
from lessons.models import UserAccount

class LogInTestCase(TestCase,LogInTester):
    """Tests for the login up view."""

    def setUp(self):
        self.url = reverse('log_in')
        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
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

        self.student_form_input = {'email' : 'johndoe@example.org', 'password' : 'Password123'}
        self.admin_form_input = {'email' : 'janedoe@example.org', 'password' : 'Password123'}
        self.director_form_input = {'email' : 'jsmith@example.org', 'password' : 'Password123'}

    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)

    def test_unsucessful_student_log_in(self):
        self.student_form_input = {'email' : 'WrongEmail', 'password' : 'WrongPass'}
        response = self.client.post(self.url, self.student_form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        # tests if messages is being displayed
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),1)
        self.assertEqual(messages_list[0].level,messages.ERROR)

    # These tests check if user is redirected to the correct feed based on their roles
    def test_successful_student_login(self):
        response = self.client.post(self.url, self.student_form_input,follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('student_feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),0)

    def test_successful_admin_login(self):
        response = self.client.post(self.url, self.admin_form_input,follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('admin_feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_feed.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),0)

    def test_successful_director_login(self):
        response = self.client.post(self.url, self.director_form_input,follow=True)
        self.assertTrue(self._is_logged_in())
        response_url = reverse('director_feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'director_feed.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),0)


    def test_invalid_log_in_by_inactive_user(self):
        self.student.is_active = False
        self.student.save()
        response = self.client.post(self.url, self.student_form_input, follow = True)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'log_in.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list),1)
        messages_list = list(response.context['messages'])
        self.assertEqual(messages_list[0].level,messages.ERROR)
