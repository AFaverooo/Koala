from django.test import TestCase
from django.urls import reverse
from lessons.models import UserAccount, Gender
from lessons.tests.helpers import reverse_with_next

class LogInTestCase(TestCase):
    """Tests for the student feed."""

    def setUp(self):

        self.url = reverse('student_feed')

    def test_get_student_feed_in(self):
        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            gender = Gender.MALE,
        )
        self.client.login(email='johndoe@example.org', password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_feed.html')

    def test_get_student_feed_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
