from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForm
from lessons.models import Lesson, UserAccount,Gender,UserRole,LessonType,LessonDuration,LessonStatus

from lessons.forms import RequestForm
from lessons.views import get_saved_lessons,get_unfulfilled_lessons
from django.contrib import messages
from django.utils import timezone
from datetime import time
import datetime
from lessons.tests.helpers import reverse_with_next

from django.db import IntegrityError
from django.db import transaction

class RequestSaveLessonsTest(TestCase):
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

        self.save_lessons_url = reverse('save_lessons')


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

    def test_get_saved_lessons(self):
        self.create_saved_lessons()
        saved_lessons = get_saved_lessons(self.student)
        self.assertEqual(len(saved_lessons),3)

    def test_save_lessons_url(self):
        self.assertEqual(self.save_lessons_url,'/save_lessons/')

    def test_unsuccesful_save_lessons_not_logged_in(self):
        redirect_url = reverse('home')
        before_count = Lesson.objects.count()
        response = self.client.get(self.save_lessons_url,follow = True)
        after_count = Lesson.objects.count()
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertEqual(after_count, before_count)


    def test_get_save_lessons_without_lessons_saved(self):
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.save_lessons_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']

        self.assertEqual(len(response.context['lessons']),0)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

    def test_get_save_lessons_with_lessons_saved(self):
        self.create_saved_lessons()
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.save_lessons_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']
        self.assertEqual(len(response.context['lessons']),3)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)
        self.delete_saved_lessons()

    def test_succesfull_save_lessons_post(self):
        self.create_saved_lessons()
        self.client.login(email = self.student.email, password = 'Password123')
        before_count = Lesson.objects.count()
        response = self.client.post(self.save_lessons_url, follow = True)
        after_count = Lesson.objects.count()

        self.assertEqual(before_count,after_count)

        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        all_student_lessons = Lesson.objects.filter(student_id = self.student)
        all_student_unfulfilled_lessons = Lesson.objects.filter(lesson_status = LessonStatus.UNFULFILLED, student_id = self.student)

        self.assertEqual(len(all_student_lessons),len(all_student_unfulfilled_lessons))

        for lesson in all_student_lessons:
            self.assertEqual(lesson.lesson_status, LessonStatus.UNFULFILLED)
            self.assertEqual(lesson.student_id, self.student)

        self.assertTemplateUsed(response, 'student_feed.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Lesson requests are now pending for validation by admin')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
