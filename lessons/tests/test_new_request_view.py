from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForm
from lessons.models import Lesson, UserAccount,Gender


class RequestViewTestCase(TestCase):
    def setUp(self):

        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

        self.teacher = UserAccount.objects.create_teacher(
            first_name='Barbare',
            last_name='Dutch',
            email='barbdutch@example.org',
            password='Password123',
            gender = Gender.FEMALE,
        )

        self.url = reverse('make_request')
        self.form_input = {
            'type': 'INSTR',
            'duration': '30',
            'lesson_date_time': '2006-10-25 14:30:59',
        }

    def test_succesful_request(self):

        self.client.login(email=self.student.email, password="Password123")

        before_count = Lesson.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('requests_page')
        #self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'requests_page.html')
