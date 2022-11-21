from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForm
from lessons.models import Lesson, UserAccount,Gender,UserRole

from lessons.forms import RequestForm

class LessonRequestViewTestCase(TestCase):
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

        self.url = reverse('new_lesson')

        self.form_input = {
            'type': 'INSTR',
            'duration': '30',
            'lesson_date_time_0': '2020-04-04',
            'lesson_date_time_1': '12:12',
            
            'teachers': UserAccount.objects.filter(role = UserRole.TEACHER).first().id,
        }

    def test_valid_new_lesson_form(self):
        self.assertEqual(len(UserAccount.objects.filter(role = UserRole.TEACHER)), 1)
        form = RequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())


    def test_succesful_request(self):

        self.client.login(email=self.student.email, password="Password123")

        before_count = Lesson.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('requests_page')
        #self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'requests_page.html')
