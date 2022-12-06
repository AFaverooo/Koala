"""Tests for the profile view."""
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
# from lessons.forms import CreateAdminForm
from lessons.models import Lesson,LessonType,LessonDuration,UserAccount,Gender,LessonStatus
# from lessons.tests.helpers import reverse_with_next
import datetime
from datetime import date
from django.utils import timezone

class ProfileViewTest(TestCase):
    """Test suite for the profile view."""


    def setUp(self):

        self.teacher = UserAccount.objects.create_teacher(
                first_name='Petra',
                last_name='Pickles',
                email= 'petra.pickles@example.org',
                password='Password123',
                gender = Gender.FEMALE,
            )

        self.student = Lesson.objects.create_student(
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123',
            gender = 'F',
        )

        self.current = Lesson.objects.create_teacher(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = datetime.datetime(2022, 12, 1, 12, 0, 0, 0).replace(tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = date(2022,10,25),
            lesson_status = LessonStatus.FULLFILLED,
        )

        # self.url = reverse('create_admin_page')

        # self.form_input = {
        #     'first_name': 'Jane2',
        #     'last_name': 'Doe2',
        #     'email': 'thenewjanedoe@example.org',
        #     'gender': 'M',
        #     'new_password': 'NewPassword123',
        #     'password_confirmation': 'NewPassword123',
        # }

    def test_succesful_lesson_update(self):

        self.client.login(email=self.current.email, password="Password123")

        lesson_count_before = Lesson.objects.count()

        self.update_lesson_url = reverse('admin_update_request', args=[self.lesson])
        response = self.client.post(self.update_lesson_url,self.form_input ,follow = True)

        lesson_count_after = Lesson.objects.count()
        
        self.assertEqual(lesson_count_before,lesson_count_after)

        #after sucessful lesson modification
        redirect_url = reverse('student_requests',args=[self.student.id])
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_student_requests_page.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        self.admin.refresh_from_db()
        self.assertEqual(self.admin.first_name, 'Jane2')
        self.assertEqual(self.admin.last_name, 'Doe2')
        self.assertEqual(self.admin.email, 'thenewjanedoe@example.org')
        self.assertEqual(self.admin.gender, 'M')
        # is_password_correct = check_password('NewPassword123', self.admin.password)
        # self.assertTrue(is_password_c`````````````````````orrect)


    def test_succesful_current_user_profile_update_(self):

        self.client.login(email=self.current.email, password="Password123")

        user_count_before = UserAccount.objects.count()
        self.update_user_url = reverse('update_user', args=[self.current.id])
        response = self.client.post(self.update_user_url,self.form_input ,follow = True)
        user_count_after = UserAccount.objects.count()
        self.assertEqual(user_count_before,user_count_after)

        response_url = reverse('home')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

        self.current.refresh_from_db()
        self.assertEqual(self.current.first_name, 'Jane2')
        self.assertEqual(self.current.last_name, 'Doe2')
        self.assertEqual(self.current.email, 'thenewjanedoe@example.org')
        self.assertEqual(self.current.gender, 'M')
        is_password_correct = check_password('NewPassword123', self.current.password)
        self.assertTrue(is_password_correct)


    def test_unsuccesful_profile_update(self):

        self.client.login(email=self.current.email, password="Password123")

        user_count_before = UserAccount.objects.count()
        self.update_user_url = reverse('update_user', args=[self.admin.id])
        self.form_input['email'] = 'BAD_EMAIL'
        response = self.client.post(self.update_user_url,self.form_input ,follow = True)
        user_count_after = UserAccount.objects.count()
        self.assertEqual(user_count_before,user_count_after)

        self.admin.refresh_from_db()
        self.assertEqual(self.admin.first_name, 'Jane')
        self.assertEqual(self.admin.last_name, 'Doe')
        self.assertEqual(self.admin.email, 'janedoe@example.org')
        self.assertEqual(self.admin.gender, 'F')
        is_password_correct = check_password('Password123', self.admin.password)
        self.assertTrue(is_password_correct)



    def test_unsuccesful_current_user_profile_update_due_to_used_email(self):

        self.client.login(email=self.current.email, password="Password123")

        user_count_before = UserAccount.objects.count()
        self.update_user_url = reverse('update_user', args=[self.admin.id])
        self.form_input['email'] = 'apedro@example.org'
        response = self.client.post(self.update_user_url,self.form_input ,follow = True)
        user_count_after = UserAccount.objects.count()
        self.assertEqual(user_count_before,user_count_after)

        self.admin.refresh_from_db()
        self.assertEqual(self.admin.first_name, 'Jane')
        self.assertEqual(self.admin.last_name, 'Doe')
        self.assertEqual(self.admin.email, 'janedoe@example.org')
        self.assertEqual(self.admin.gender, 'F')
        is_password_correct = check_password('Password123', self.admin.password)
        self.assertTrue(is_password_correct)
