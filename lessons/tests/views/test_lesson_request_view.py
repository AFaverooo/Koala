from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForm
from lessons.models import Lesson, UserAccount,Gender,UserRole,LessonType,LessonDuration,LessonStatus

from lessons.forms import RequestForm
from lessons.views import get_student_and_child_objects
from django import forms
from django.utils import timezone
from datetime import time
import datetime
from lessons.tests.helpers import reverse_with_next
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from django.db import IntegrityError
from django.db import transaction

class LessonRequestViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('requests_page')

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

    def create_child_student(self):
        self.child = UserAccount.objects.create_child_student(
            first_name = 'Bobby',
            last_name = 'Lee',
            email = 'bobbylee@example.org',
            password = 'Password123',
            gender = Gender.MALE,
            parent_of_user = self.student,
        )

    def change_lessons_status_to_unfulfilled(self):
        self.saved_lesson.lesson_status = LessonStatus.UNFULFILLED
        self.saved_lesson.save()
        self.saved_lesson2.lesson_status = LessonStatus.UNFULFILLED
        self.saved_lesson2.save()

    def test_request_url(self):
        self.assertEqual(self.url,'/requests_page/')

    def test_get_request_page_without_being_logged_in(self):
        redirect_url = reverse_with_next('home', self.url)
        response = self.client.get(self.url,follow = True)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    def test_not_student_accessing_request_page(self):
        self.client.login(email=self.admin.email, password="Password123")
        response = self.client.get(self.url, follow = True)
        redirect_url = reverse('admin_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_feed.html')

    def test_drop_down_of_users_is_populated_with_student_and_child(self):
        self.create_child_student()
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')

        student_options = response.context['students_option']

        self.assertEqual(len(student_options),2)

    def test_drop_down_of_users_is_populated_with_student(self):
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')

        student_options = response.context['students_option']

        self.assertEqual(len(student_options),1)

    def test_function_to_get_student_and_children(self):
        #self.fail()
        self.create_child_student()
        options = get_student_and_child_objects(self.student)

        self.assertEqual(len(options),2)

        self.assertEqual(options[0].email,self.student.email)
        self.assertEqual(options[1].email,self.child.email)

        self.assertTrue(options[0].is_parent)
        self.assertEqual(options[0].parent_of_user,None)
        self.assertEqual(options[1].parent_of_user.email,self.student.email)

        self.assertEqual(options[0].role,UserRole.STUDENT)
        self.assertEqual(options[1].role,UserRole.STUDENT)

    def test_get_request_page_with_saved_lessons(self):
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')

        form = response.context['form']
        self.assertEqual(len(response.context['lessons']),2)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

        date_time_widget = form.fields['lesson_date_time'].widget
        self.assertTrue(isinstance(date_time_widget, DateTimePickerInput))

        self.assertTrue(isinstance(form.fields['type'], forms.TypedChoiceField))
        self.assertTrue(isinstance(form.fields['duration'], forms.TypedChoiceField))
        self.assertTrue(isinstance(form.fields['teachers'], forms.ModelChoiceField))

    def test_get_request_page_without_saved_lessons(self):
        self.change_lessons_status_to_unfulfilled()
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')

        form = response.context['form']
        self.assertEqual(len(response.context['lessons']),0)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

        date_time_widget = form.fields['lesson_date_time'].widget
        self.assertTrue(isinstance(date_time_widget, DateTimePickerInput))

        self.assertTrue(isinstance(form.fields['type'], forms.TypedChoiceField))
        self.assertTrue(isinstance(form.fields['duration'], forms.TypedChoiceField))
        self.assertTrue(isinstance(form.fields['teachers'], forms.ModelChoiceField))

    def test_post_request_page_forbidden(self):
        before_count = Lesson.objects.count()
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.post(self.url, follow = True)
        after_count = Lesson.objects.count()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(before_count, after_count)
