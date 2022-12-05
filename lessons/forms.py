from django import forms
from django.core.validators import RegexValidator
from .models import UserAccount, Gender, Lesson, Term
from  django.contrib.admin.widgets import AdminSplitDateTime
from django.shortcuts import render
from .models import UserAccount, Gender, Lesson, UserRole, Term
from django.forms import DateTimeInput
import datetime
from bootstrap_datepicker_plus.widgets import DateTimePickerInput, DatePickerInput
from django.core.exceptions import ObjectDoesNotExist

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




class CreateAdminForm(forms.ModelForm):
    """Form enabling the creation of admins by director"""

    class Meta:
        """Form options."""

        model = UserAccount
        fields = ['first_name', 'last_name','email', 'gender']

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
            new_password = self.cleaned_data.get('new_password')
            password_confirmation = self.cleaned_data.get('password_confirmation')
            if new_password != password_confirmation:
                self.add_error('password_confirmation', 'Confirmation does not match password.')


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



class TermDatesForm(forms.ModelForm):
    # def __init__ (self,*args,**kwargs):
    #     super(TermDatesForm,self).__init__(self,*args,**kwargs)
    #     self.fields['term_number'].disabled = True

    class Meta:
        """Form options."""
        model = Term
        fields = ['term_number','start_date','end_date']
        widgets = {
            "start_date": DatePickerInput(),
            "end_date": DatePickerInput(),
            }
        ordering = ['term_number']

    # def clean(self):
    #     """Clean the data and generate messages for any errors."""

    #     super().clean()
    #     term_number = self.cleaned_data.get('term_number')
    #     start_date = self.cleaned_data.get('start_date')
    #     end_date = self.cleaned_data.get('end_date')
    #     # if new_password != password_confirmation:
    #     #     self.add_error('password_confirmation', 'Confirmation does not match password.')

    # def save(self):
    #     """Create a new user."""

    #     super().save(commit=False)
    #     term = Term.objects.create(
    #         # self.cleaned_data.get('username'),
    #         term_number=self.cleaned_data.get('term_number'),
    #         start_date=self.cleaned_data.get('start_date'),
    #         end_date=self.cleaned_data.get('end_date'),
    #     )
    #     return term


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

    # def set_lesson_term_details(lesson):
    #     terms_list = Term.objects.all()

    #     for eachterm in terms_list :

    #         #Calculate mid-term date
    #         start = eachterm.start_date 
    #         end = eachterm.end_date
    #         mid_term_date = start + (end - start)/2
    #         close_to_end_of_term = end-(end - mid_term_date)/6

    #         try:
    #             next_term = Term.objects.get(term_number = eachterm.term_number + 1)
    #         except ObjectDoesNotExist:
    #             next_term = None

    #         #Display term number only if the lesson starts before mid-term
    #         if(eachterm.start_date <= lesson.lesson_date_time.date()  <= mid_term_date):
    #             lesson.term = 'Term : ' + str(eachterm.term_number) + '            For reference : ' + str(lesson.lesson_date_time.date())
    #             # lesson.save()
    #             return lesson.term

    #         #Set term date for next term if the current term is close to finishing
    #         elif (next_term != None and close_to_end_of_term <= lesson.lesson_date_time.date()  < next_term.start_date):
    #             term = eachterm.term_number + 1
    #             lesson.term = 'Term : ' + str(term) + '(Close to next term)               For reference : ' + str(lesson.lesson_date_time.date())
    #             # lesson.save()
    #             return lesson.term

    #         #Set term date for next term if the current term is close to finishing and the is no next term set
    #         elif(next_term == None and close_to_end_of_term <= lesson.lesson_date_time.date()  < end):
    #             term = eachterm.term_number + 1
    #             lesson.term = 'Term : ' + str(term) + '(Close to next term)        (No next term)       For reference : ' + str(lesson.lesson_date_time.date())
    #             # lesson.save()
    #             return lesson.term

    #     #If lesson is not before mid term and is not close to end of term 
    #     lesson.term = 'N/A' 
    #     return lesson.term


    def save(self,student_id):
        """Create a new Lesson."""

        super().save(commit=False)
        lesson = Lesson.objects.create(
            type=self.cleaned_data.get('type'),
            duration=self.cleaned_data.get('duration'),
            lesson_date_time=self.cleaned_data.get('lesson_date_time'),
            student_id=student_id,
            teacher_id=self.cleaned_data.get('teachers'),
            term = 'N/A',
        )

        terms_list = Term.objects.all()

        for eachterm in terms_list :

            #Calculate mid-term date
            start = eachterm.start_date 
            end = eachterm.end_date
            mid_term_date = start + (end - start)/2
            close_to_end_of_term = end-(end - mid_term_date)/6

            try:
                next_term = Term.objects.get(term_number = eachterm.term_number + 1)
            except ObjectDoesNotExist:
                next_term = None

            #Display term number only if the lesson starts before mid-term
            if(eachterm.start_date <= lesson.lesson_date_time.date()  <= mid_term_date):
                lesson.term = 'Term : ' + str(eachterm.term_number) + '            For reference : ' + str(lesson.lesson_date_time.date())
                # lesson.save()
                return lesson.term

            #Set term date for next term if the current term is close to finishing
            elif (next_term != None and close_to_end_of_term <= lesson.lesson_date_time.date()  < next_term.start_date):
                term = eachterm.term_number + 1
                lesson.term = 'Term : ' + str(term) + '(Close to next term)               For reference : ' + str(lesson.lesson_date_time.date())
                # lesson.save()
                return lesson.term

            #Set term date for next term if the current term is close to finishing and the is no next term set
            elif(next_term == None and close_to_end_of_term <= lesson.lesson_date_time.date()  < end):
                term = eachterm.term_number + 1
                lesson.term = 'Term : ' + str(term) + '(Close to next term)        (No next term)       For reference : ' + str(lesson.lesson_date_time.date())
                # lesson.save()
                return lesson.term

        #If lesson is not before mid term and is not close to end of term 
        lesson.term = 'N/A' 

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
