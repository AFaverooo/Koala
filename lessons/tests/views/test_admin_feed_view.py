from django.test import TestCase
from django.urls import reverse

class StudentViewTestCase(TestCase):
    """Tests for the admin feed."""

    def setUp(self):
        self.url = reverse('admin_feed')

    def test_get_admin_feed_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_feed.html')
