from django import forms
from django.core.validators import RegexValidator
from .models import UserAccount, Gender, Lesson
from  django.contrib.admin.widgets import AdminSplitDateTime
from django.shortcuts import render
from .models import UserAccount, Gender, Lesson, UserRole
from django.forms import DateTimeInput
import datetime
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

class LogInForm(forms.Form):
    email = forms.CharField(label='email')
    password = forms.CharField(label='password',widget=forms.PasswordInput())

class DateInput(forms.DateInput):
    input_type = 'date'

class SignUpForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = UserAccount

        fields = ['first_name', 'last_name','email', 'gender']

    # dateOfBirth = forms.DateField(
    #     label = 'Date Of Birth',
    #     widget = DateInput())
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        #gender = self.cleaned_data.get('gender')
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        student = UserAccount.objects.create_student(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            gender=self.cleaned_data.get('gender'),
        )

        return student

    def save_child(self,parent):
        super().save(commit = False)
        child_student = UserAccount.objects.create_child_student(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            gender=self.cleaned_data.get('gender'),
            parent_of_user = parent,
        )

        return child_student


class RequestForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""


    class Meta:
        """Form options."""
        model = Lesson
        fields = ['type','duration','lesson_date_time']
        widgets = {
            "lesson_date_time": DateTimePickerInput(),}


    teachers = forms.ModelChoiceField(queryset = UserAccount.objects.filter(role = UserRole.TEACHER) , widget = forms.Select, empty_label = None, initial = 0)

    # def clean(self, request):
    #     """Clean the data and generate messages for any errors."""

    #     super().clean()
    #     #gender = self.cleaned_data.get('gender')
    #     self.data = self.data.copy()
    #     self.data['student_id'] = request.user
    #     self.data['teacher_id'] = self.data['teachers']


    def save(self,student_id):
         """Create a new Lesson."""

         super().save(commit=False)
         lesson = Lesson.objects.create(
             type=self.cleaned_data.get('type'),
             duration=self.cleaned_data.get('duration'),
             lesson_date_time=self.cleaned_data.get('lesson_date_time'),
             student_id=student_id,
             teacher_id=self.cleaned_data.get('teachers'),
         )

         return lesson

    def update_lesson(self, to_edit_lesson):
        duration = self.cleaned_data.get('duration')
        lesson_date = self.cleaned_data.get('lesson_date_time')
        type = self.cleaned_data.get('type')
        teacher_id = self.cleaned_data.get('teachers')

        to_edit_lesson.duration = duration
        to_edit_lesson.lesson_date_time = lesson_date
        to_edit_lesson.type = type
        to_edit_lesson.teacher_id = teacher_id
        to_edit_lesson.save()

        return to_edit_lesson
