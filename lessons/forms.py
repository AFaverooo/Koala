from django import forms
from django.core.validators import RegexValidator
from .models import UserAccount, Gender, Lesson
from  django.contrib.admin.widgets import AdminSplitDateTime
from django.shortcuts import render
from .models import UserAccount, Gender, Lesson, UserRole, LessonStatus


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





class CreateAdminForm(forms.ModelForm):
    """Form enabling the creation of admins by director"""

    class Meta:
        """Form options."""

        model = UserAccount
        fields = ['first_name', 'last_name','email', 'gender']


    #TO:DO  ADD ABILITY TO CHANGE Password
    
    # new_password = forms.CharField(
    #     label='Password',
    #     widget=forms.PasswordInput(),
    #     validators=[RegexValidator(
    #         regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
    #         message='Password must contain an uppercase character, a lowercase '
    #                 'character and a number'
    #         )]
    # )
    # password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        admin = UserAccount.objects.create_admin(
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
            gender=self.cleaned_data.get('gender'),
        )

        return admin



class RequestForm(forms.ModelForm):
    """Form enabling unregistered users to sign up."""
    lesson_date_time = forms.SplitDateTimeField(widget=AdminSplitDateTime())

    class Meta:
        """Form options."""

        model = Lesson
        fields = ['type','duration']

    teachers = forms.ModelChoiceField(queryset = UserAccount.objects.filter(role = UserRole.TEACHER) , widget = forms.Select, empty_label = None, initial = 0)



    #This is the choice of teachers the student is able to pick out of
    #teacher_choices = []
    #teacher_name = forms.CharField(
    #    label = "Teacher Name: ",
    #    widget = forms.Select(choices = teacher_choices))

# class AdminUpdateRequestForm(RequestForm, forms.ModelForm):
#     REQUEST_STATUS = [
#         'saved', 'pending','booked'
#     ]
#     status = forms.CharField(label='What is your favorite fruit?', widget=forms.Select(choices=REQUEST_STATUS))
