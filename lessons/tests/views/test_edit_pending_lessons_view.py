from django.test import TestCase
from django.urls import reverse
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration,LessonStatus
from lessons.views import make_lesson_timetable_dictionary,make_unfulfilled_dictionary
from lessons.views import RequestForm
from django.contrib import messages
import datetime
from django.utils import timezone
from django import forms
from lessons.tests.helpers import reverse_with_next
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

class StudentFeedEditLessonTestCase(TestCase):
    def setUp(self):
        self.teacher = UserAccount.objects.create_teacher(
            first_name='Barbare',
            last_name='Dutch',
            email='barbdutch@example.org',
            password='Password123',
            gender = Gender.FEMALE,
        )

        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

        self.lesson = Lesson.objects.create(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = datetime.datetime(2022, 11, 20, 15, 15, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED
        )

        self.edit_url = reverse('edit_lesson', kwargs={'lesson_id':self.lesson.lesson_id})

        self.admin = UserAccount.objects.create_admin(
            first_name='Bob',
            last_name='Jacobs',
            email='bobby@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

        self.teacher2 = UserAccount.objects.create_teacher(
            first_name='Amane',
            last_name='Hill',
            email='amanehill@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

        self.teacher3 = UserAccount.objects.create_teacher(
            first_name='Jonathan',
            last_name='Jacks',
            email='johnjacks@example.org',
            password='Password123',
            gender = Gender.PNOT,
        )

        self.lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 16, 00, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

        self.lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2022, 9, 20, 9, 45, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher2,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

        self.lesson4 = Lesson.objects.create(
            type = LessonType.PRACTICE,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 12, 25, 9, 45, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher2,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

        self.lesson5 = Lesson.objects.create(
            type = LessonType.PRACTICE,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 9, 25, 9, 45, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher3,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

    def change_lessons_status_to_unfulfilled(self):
        self.lesson.lesson_status = LessonStatus.UNFULFILLED
        self.lesson.save()
        self.lesson2.lesson_status = LessonStatus.UNFULFILLED
        self.lesson2.save()
        self.lesson3.lesson_status = LessonStatus.UNFULFILLED
        self.lesson3.save()
        self.lesson4.lesson_status = LessonStatus.UNFULFILLED
        self.lesson4.save()
        self.lesson5.lesson_status = LessonStatus.UNFULFILLED
        self.lesson5.save()


    def create_forms(self):
        self.form_input = {
            'type': LessonType.INSTRUMENT,
            'duration': LessonDuration.FOURTY_FIVE,
            'lesson_date_time' : datetime.datetime(2023, 8, 20, 16, 00, 00, tzinfo=timezone.utc),
            'teachers': self.teacher2.id,
        }

        self.form_input2 = {
            'type': LessonType.PERFORMANCE,
            'duration': LessonDuration.HOUR,
            'lesson_date_time' : datetime.datetime(2021, 8, 20, 16, 00, 00, tzinfo=timezone.utc),
            'teachers': self.teacher3.id,
        }

    #def create_duplicate_form(self):
    #    self.form_input_duplicate = {
    #        'type': LessonType.INSTRUMENT,
    #        'duration': LessonDuration.THIRTY,
    #        'lesson_date_time' : datetime.datetime(2022, 10, 20, 16, 00, 00, tzinfo=timezone.utc),
    #        'teachers': UserAccount.objects.filter(role = UserRole.TEACHER).first().id,
    #    }

    def test_edit_lesson_url(self):
        self.assertEqual(self.edit_url, f'/edit_lesson/{self.lesson.lesson_id}')

    def test_get_edit_pending_lesson_with_incorrect_lesson_id(self):
        self.edit_url = reverse('edit_lesson', kwargs={'lesson_id':0})
        before_count = Lesson.objects.count()

        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()
        response = self.client.get(self.edit_url, follow = True)
        after_count = Lesson.objects.count()

        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')

        self.assertEqual(before_count,after_count)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Incorrect lesson ID passed')
        self.assertEqual(messages_list[0].level, messages.ERROR)


    def test_not_logged_in_accessing_edit_pending_lessons(self):
        before_count = Lesson.objects.count()
        self.change_lessons_status_to_unfulfilled()
        response = self.client.get(self.edit_url, follow = True)
        after_count = Lesson.objects.count()

        redirect_url = reverse('log_in')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

        self.assertEqual(before_count,after_count)

    def test_not_student_accessing_editing_pending_lessons(self):
        self.client.login(email=self.admin.email, password="Password123")
        response = self.client.get(self.edit_url, follow = True)
        redirect_url = reverse('log_in')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'log_in.html')

    def test_get_edit_pending_lesson_with_correct_lesson_id(self):
        before_count = Lesson.objects.count()

        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()
        response = self.client.get(self.edit_url, follow = True)
        after_count = Lesson.objects.count()
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'edit_request.html')

        self.assertEqual(before_count,after_count)

        response_form = response.context['form']
        lesson_id = response.context['lesson_id']

        self.assertTrue(isinstance(response_form, RequestForm))
        self.assertTrue(response_form.is_bound)
        self.assertEqual(int(lesson_id),self.lesson.lesson_id)

        date_time_widget = response_form.fields['lesson_date_time'].widget
        self.assertTrue(isinstance(date_time_widget, DateTimePickerInput))

        self.assertTrue(isinstance(response_form.fields['type'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['duration'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['teachers'], forms.ModelChoiceField))

        self.assertTrue(response_form.is_valid())

        self.assertEqual(response_form.cleaned_data.get("type"), self.lesson.type)
        self.assertEqual(response_form.cleaned_data.get("duration"), self.lesson.duration)
        self.assertEqual(response_form.cleaned_data.get("teachers"),self.teacher)
        self.assertEqual(response_form.cleaned_data.get("lesson_date_time"),self.lesson.lesson_date_time)

    def test_get_edit_pending_lesson_with_correct_lesson_third(self):
        before_count = Lesson.objects.count()
        self.edit_url = reverse('edit_lesson', kwargs={'lesson_id':self.lesson3.lesson_id})

        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()
        response = self.client.get(self.edit_url, follow = True)
        after_count = Lesson.objects.count()
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'edit_request.html')

        self.assertEqual(before_count,after_count)

        response_form = response.context['form']
        lesson_id = response.context['lesson_id']

        self.assertTrue(isinstance(response_form, RequestForm))
        self.assertTrue(response_form.is_bound)
        self.assertEqual(int(lesson_id),self.lesson3.lesson_id)

        date_time_widget = response_form.fields['lesson_date_time'].widget
        self.assertTrue(isinstance(date_time_widget, DateTimePickerInput))

        self.assertTrue(isinstance(response_form.fields['type'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['duration'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['teachers'], forms.ModelChoiceField))

        self.assertTrue(response_form.is_valid())

        self.assertEqual(response_form.cleaned_data.get("type"),self.lesson3.type)
        self.assertEqual(response_form.cleaned_data.get("duration"),self.lesson3.duration)
        self.assertEqual(response_form.cleaned_data.get("teachers"),self.teacher2)
        self.assertEqual(response_form.cleaned_data.get("lesson_date_time"),self.lesson3.lesson_date_time)

    def test_edit_lesson_without_form(self):
        before_count = Lesson.objects.count()
        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()
        response = self.client.post(self.edit_url, follow = True)
        after_count = Lesson.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_request.html')
        self.assertEqual(before_count,after_count)

        response_form = response.context['form']
        lesson_id = response.context['lesson_id']

        self.assertTrue(isinstance(response_form, RequestForm))
        self.assertTrue(response_form.is_bound)
        self.assertEqual(int(lesson_id),self.lesson.lesson_id)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Form is not valid')
        self.assertEqual(messages_list[0].level, messages.ERROR)

        date_time_widget = response_form.fields['lesson_date_time'].widget
        self.assertTrue(isinstance(date_time_widget, DateTimePickerInput))

        self.assertTrue(response_form.is_valid())

        self.assertTrue(isinstance(response_form.fields['type'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['duration'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['teachers'], forms.ModelChoiceField))

        self.assertEqual(response_form.cleaned_data.get("type"), self.lesson.type)
        self.assertEqual(response_form.cleaned_data.get("duration"), self.lesson.duration)
        self.assertEqual(response_form.cleaned_data.get("teachers"),self.teacher)
        self.assertEqual(response_form.cleaned_data.get("lesson_date_time"),self.lesson.lesson_date_time)




    def test_edit_lesson_without_valid_form_type_data(self):
        self.create_forms()
        self.form_input['type'] = 'Incorrect type input'
        before_count = Lesson.objects.count()

        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()
        response = self.client.post(self.edit_url,self.form_input, follow = True)
        after_count = Lesson.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_request.html')
        self.assertEqual(before_count,after_count)

        response_form = response.context['form']
        lesson_id = response.context['lesson_id']

        self.assertTrue(isinstance(response_form, RequestForm))
        self.assertTrue(response_form.is_bound)
        self.assertEqual(int(lesson_id),self.lesson.lesson_id)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Form is not valid')
        self.assertEqual(messages_list[0].level, messages.ERROR)

        date_time_widget = response_form.fields['lesson_date_time'].widget
        self.assertTrue(isinstance(date_time_widget, DateTimePickerInput))

        self.assertTrue(response_form.is_valid())

        self.assertTrue(isinstance(response_form.fields['type'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['duration'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['teachers'], forms.ModelChoiceField))

        self.assertEqual(response_form.cleaned_data.get("type"), self.lesson.type)
        self.assertEqual(response_form.cleaned_data.get("duration"), self.lesson.duration)
        self.assertEqual(response_form.cleaned_data.get("teachers"),self.teacher)
        self.assertEqual(response_form.cleaned_data.get("lesson_date_time"),self.lesson.lesson_date_time)

    def test_apply_edit_to_lesson_succesfully(self):
        self.create_forms()
        request_date = self.lesson.request_date

        before_count = Lesson.objects.count()
        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()

        response = self.client.post(self.edit_url,self.form_input, follow = True)

        after_count = Lesson.objects.count()

        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')

        self.assertEqual(before_count,after_count)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Succesfully edited lesson')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        updated_lesson = Lesson.objects.get(lesson_id = self.lesson.lesson_id)

        self.assertEqual(updated_lesson.student_id,self.student)
        self.assertEqual(updated_lesson.type, LessonType.INSTRUMENT)
        self.assertEqual(updated_lesson.request_date, request_date)
        self.assertEqual(updated_lesson.duration, LessonDuration.FOURTY_FIVE)
        self.assertEqual(updated_lesson.teacher_id,self.teacher2)
        self.assertEqual(updated_lesson.lesson_date_time,datetime.datetime(2023, 8, 20, 16, 00, 00, tzinfo=timezone.utc))

    def test_apply_edit_to_lesson2_succesfully(self):
        self.create_forms()
        request_date = self.lesson2.request_date
        before_count = Lesson.objects.count()
        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()

        self.edit_url = reverse('edit_lesson', kwargs={'lesson_id':self.lesson2.lesson_id})
        response = self.client.post(self.edit_url,self.form_input2, follow = True)

        after_count = Lesson.objects.count()

        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')

        self.assertEqual(before_count,after_count)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Succesfully edited lesson')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        updated_lesson = Lesson.objects.get(lesson_id = self.lesson2.lesson_id)

        self.assertEqual(updated_lesson.student_id,self.student)
        self.assertEqual(updated_lesson.type, LessonType.PERFORMANCE)
        self.assertEqual(updated_lesson.request_date, request_date)
        self.assertEqual(updated_lesson.duration, LessonDuration.HOUR)
        self.assertEqual(updated_lesson.teacher_id,self.teacher3)
        self.assertEqual(updated_lesson.lesson_date_time,datetime.datetime(2021, 8, 20, 16, 00, 00, tzinfo=timezone.utc))

    """

    def test_apply_edit_to_lesson_causing_a_duplicate(self):
        self.create_duplicate_form()

        before_count = Lesson.objects.count()
        self.client.login(email=self.student.email, password="Password123")
        self.change_lessons_status_to_unfulfilled()

        response = self.client.post(self.edit_url,self.form_input_duplicate, follow = True)

        after_count = Lesson.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_request.html')

        self.assertEqual(before_count,after_count)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Duplicate lessons are not allowed')
        self.assertEqual(messages_list[0].level, messages.WARNING)

        response_form = response.context['form']
        lesson_id = response.context['lesson_id']

        self.assertTrue(isinstance(response_form, RequestForm))
        self.assertTrue(response_form.is_bound)
        self.assertEqual(int(lesson_id),self.lesson.lesson_id)

        date_time_widget = response_form.fields['lesson_date_time'].widget
        self.assertTrue(isinstance(date_time_widget, DateTimePickerInput))

        self.assertTrue(isinstance(response_form.fields['type'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['duration'], forms.TypedChoiceField))
        self.assertTrue(isinstance(response_form.fields['teachers'], forms.ModelChoiceField))

        self.assertTrue(response_form.is_valid())

        self.assertEqual(response_form.cleaned_data.get("type"), LessonType.INSTRUMENT)
        self.assertEqual(response_form.cleaned_data.get("duration"), LessonDuration.THIRTY)
        self.assertEqual(response_form.cleaned_data.get("teachers"),self.teacher)
        self.assertEqual(response_form.cleaned_data.get("lesson_date_time"),datetime.datetime(2022, 10, 20, 16, 00, 00, tzinfo=timezone.utc))
 """
