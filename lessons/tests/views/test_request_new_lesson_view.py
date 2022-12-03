from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForm
from lessons.models import Lesson, UserAccount,Gender,UserRole,LessonType,LessonDuration,LessonStatus
from django.contrib import messages
from lessons.forms import RequestForm
from lessons.views import get_saved_lessons,get_unfulfilled_lessons

from django.utils import timezone
from datetime import time
import datetime
from lessons.tests.helpers import reverse_with_next

from django.db import IntegrityError
from django.db import transaction

class RequestNewLessonTest(TestCase):
    def setUp(self):

        self.admin = UserAccount.objects.create_admin(
            first_name='Bob',
            last_name='Jacobs',
            email='bobby@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

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
            'type': LessonType.INSTRUMENT,
            'duration': LessonDuration.THIRTY,
            'lesson_date_time' : datetime.datetime(2022, 4, 4, 15, 15, 15, tzinfo=timezone.utc),
            'teachers': self.teacher.id,
        }

    def create_saved_lessons(self):
        self.saved_lesson = Lesson.objects.create(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = datetime.datetime(2022, 11, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.SAVED
        )


        self.saved_lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.SAVED
        )

        self.saved_lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2022, 9, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.SAVED
        )

    def delete_saved_lessons(self):
        self.saved_lesson.delete()
        self.saved_lesson2.delete()
        self.saved_lesson3.delete()

    def test_new_lesson_url(self):
        self.assertEqual(self.url,'/new_lesson/')

    def test_valid_new_lesson_form(self):
        self.assertEqual(len(UserAccount.objects.filter(role = UserRole.TEACHER)), 1)
        form = RequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_unsuccesful_new_lesson_not_logged_in(self):
        redirect_url = reverse('home',)
        before_count = Lesson.objects.count()
        response = self.client.get(self.url,follow = True)
        after_count = Lesson.objects.count()
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(after_count, before_count)

    def test_get_new_lesson_without_lessons_saved(self):
        redirect_url = reverse('requests_page')
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url, follow = True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']

        self.assertEqual(len(response.context['lessons']),0)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

    def test_get_new_lesson_with_lessons_saved(self):
        redirect_url = reverse('requests_page')
        self.create_saved_lessons()
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url, follow = True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']
        self.assertEqual(len(response.context['lessons']),3)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)
        self.delete_saved_lessons()

    def test_unsuccesful_new_lesson_user_is_admin(self):
        self.client.login(email=self.admin.email, password="Password123")
        before_count = Lesson.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count)

        redirect_url = reverse('admin_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_feed.html')


    def test_unsuccesful_lesson_request_bad_data_lesson_type(self):
        self.client.login(email=self.student.email, password="Password123")
        self.form_input['type'] = 'BAD CHOICE'

        before_count = UserAccount.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = UserAccount.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RequestForm))
        self.assertTrue(form.is_bound)
        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'The lesson information provided is invalid!')
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_unsuccesful_lesson_request_bad_data_lesson_duration(self):
        self.client.login(email=self.student.email, password="Password123")
        self.form_input['duration'] = 'BAD DURATION CHOICE'

        before_count = UserAccount.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = UserAccount.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']
        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'The lesson information provided is invalid!')
        self.assertEqual(messages_list[0].level, messages.ERROR)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertTrue(form.is_bound)

    def test_succesful_request(self):
        self.client.login(email=self.student.email, password="Password123")
        before_count = Lesson.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count+1)
        form = response.context['form']
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

        lessons = response.context['lessons']
        self.assertEqual(len(lessons),1)

        self.assertEqual(lessons[0].type,LessonType.INSTRUMENT)
        self.assertEqual(lessons[0].duration, LessonDuration.THIRTY)
        self.assertEqual(lessons[0].lesson_date_time, datetime.datetime(2022, 4, 4, 15, 15, 15, tzinfo=timezone.utc))
        self.assertEqual(lessons[0].teacher_id, self.teacher)

        self.assertTemplateUsed(response, 'requests_page.html')
