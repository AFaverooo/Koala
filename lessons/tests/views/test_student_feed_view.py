

from django.test import TestCase
from django.urls import reverse

class LogInTestCase(TestCase):
    """Tests for the student feed."""

    def setUp(self):
        self.url = reverse('student_feed')

    def test_get_student_feed_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_feed.html')
