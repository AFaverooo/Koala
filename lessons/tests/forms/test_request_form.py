from django import forms
from lessons.forms import RequestForm
from django.test import TestCase
from lessons.models import Lesson, LessonType,LessonDuration,LessonStatus,Gender, UserAccount
import datetime
from django.utils import timezone
from django.urls import reverse


class RequestFormTestCase(TestCase):
    """Unit tests of the sign up form."""

    fixtures = ['lessons/tests/fixtures/useraccounts.json']


    
    def setUp(self):

        self.teacher = UserAccount.objects.get(email='barbdutch@example.org')
        self.student = UserAccount.objects.get(email='johndoe@example.org')
        # self.teacher = UserAccount.objects.create_teacher(
        #     first_name='Barbare',
        #     last_name='Dutch',
        #     email='barbdutch@example.org',
        #     password='Password123',
        #     gender = Gender.FEMALE,
        # )
        self.form_input = {
            'type': LessonType.INSTRUMENT,
            'duration': LessonDuration.THIRTY,
            'lesson_date_time' : datetime.datetime(2023, 4, 4, 15, 15, 15, tzinfo=timezone.utc),
            'teachers': self.teacher.id,
            'selectedStudent': self.student.email,
        }

        self.url = reverse('new_lesson')
    def test_valid_request_form(self):
        form = RequestForm(data = self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = RequestForm()
        self.assertIn('type', form.fields)
        self.assertIn('duration', form.fields)
        self.assertIn('lesson_date_time', form.fields)
        self.assertIn('teachers', form.fields)
        date_time_field = form.fields['lesson_date_time']
        self.assertTrue(isinstance(date_time_field, forms.DateTimeField))


    # def test_succesful_request(self):
    #     self.client.login(email=self.student.email, password="Password123")
    #     before_count = Lesson.objects.count()
    #     response = self.client.post(self.url, self.form_input, follow = True)
    #     after_count = Lesson.objects.count()
    #     self.assertEqual(after_count, before_count+1)
    #     form = response.context['form']
    #     self.assertTrue(isinstance(form, RequestForm))
    #     self.assertFalse(form.is_bound)

    #     lessons = response.context['lessons']
    #     self.assertEqual(len(lessons),1)
    #     #check lessons size is now 4 for the user
    #     self.assertEqual(lessons[0].student_id.email, self.student.email)
    #     self.assertEqual(lessons[0].type,LessonType.INSTRUMENT)
    #     self.assertEqual(lessons[0].duration, LessonDuration.THIRTY)
    #     self.assertEqual(lessons[0].lesson_date_time, datetime.datetime(2023, 4, 4, 15, 15, 15, tzinfo=timezone.utc))
    #     self.assertEqual(lessons[0].teacher_id, self.teacher)

    #     self.assertTemplateUsed(response, 'requests_page.html')
