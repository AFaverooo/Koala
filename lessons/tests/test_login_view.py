from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import LogInForm
from lessons.models import Student

class LogInTestCase(TestCase):
    """Tests of the login up view."""

    def setUp(self):
        self.url = reverse('log_in')

    def test_log_in_url(self):
        self.assertEqual(self.url,'/log_in/')

    def test_get_log_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)

    # 
    # def test_get_log_in_with_redirect(self):
    #     destination_url = reverse('user_list')
    #     self.url = reverse_with_next('log_in', destination_url)
    #     response = self.client.get(self.url) #getting the log in view
    #     self.assertEqual(response.status_code,200)
    #     self.assertTemplateUsed(response,'log_in.html')
    #     form = response.context['form']
    #     next = response.context['next']
    #     self.assertTrue(isinstance(form,LogInForm))
    #     self.assertFalse(form.is_bound)
    #     self.assertEqual(next, destination_url)
    #     messages_list = list(response.context['messages'])
    #     self.assertEqual(len(messages_list),0)
