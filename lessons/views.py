
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import LogInForm,SignUpForm,RequestForm
from django.contrib.auth import authenticate,login,logout
from .models import UserRole, UserAccount, Lesson, LessonStatus, LessonType

from django.core.exceptions import ObjectDoesNotExist

import datetime
# Create your views here.

def make_lesson_timetable_dictionary(student_user):
    booked_lessons = Lesson.objects.filter(is_booked = LessonStatus.BOOKED, student_id = student_user)
    booked_lessons_dict = {}

    if len(booked_lessons) == 0:
        return booked_lessons_dict

    for lesson in booked_lessons:
        lesson_type_str = ''

        if lesson.type == LessonType.INSTRUMENT:
            lesson_type_str = LessonType.INSTRUMENT.label
        elif lesson.type == LessonType.THEORY:
            lesson_type_str = LessonType.THEORY.label
        elif lesson.type == LessonType.PRACTICE:
            lesson_type_str = LessonType.PRACTICE.label
        elif lesson.type == LessonType.PERFORMANCE:
            lesson_type_str = LessonType.PERFORMANCE.label


        new_time = lesson.lesson_date_time + datetime.timedelta(minutes=int(lesson.duration))

        new_lesson_hr_str = ''
        lesson_date_hr_str = ''

        new_time_minute_str = ''
        lesson_date_minute_str = ''

        #format minutes using :00 notation
        if new_time.minute < 10:
            new_time_minute_str = f'0{new_time.minute}'
        else:
            new_time_minute_str = f'{new_time.minute}'

        if lesson.lesson_date_time.minute < 10:
            lesson_date_minute_str = f'0{lesson.lesson_date_time.minute}'
        else:
            lesson_date_minute_str = f'{lesson.lesson_date_time.minute}'

        #format hours using 00: notation
        if new_time.hour < 10:
            new_lesson_hr_str = f'0{new_time.hour}'
        else:
            new_lesson_hr_str = f'{new_time.hour}'

        if lesson.lesson_date_time.hour < 10:
            lesson_date_hr_str = f'0{lesson.lesson_date_time.hour}'
        else:
            lesson_date_hr_str = f'{lesson.lesson_date_time.hour}'



        duration_str = f'{lesson_date_hr_str}:{lesson_date_minute_str} - {new_lesson_hr_str}:{new_time_minute_str}'

        case = {'Lesson': f'{lesson_type_str}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson Duration': f'{duration_str}', 'Teacher': f'{lesson.teacher_id}'}
        booked_lessons_dict[lesson] = case

    return booked_lessons_dict

def home(request):
    return render(request, 'home.html')

# def log_in(request):
#     form = LogInForm()
#     return render(request, 'log_in.html', {'form': form})
#

def student_feed(request):

    return render(request,'student_feed.html')

def requests_page(request):
    student = request.user
    unsavedLessons = Lesson.objects.filter(is_booked = LessonStatus.UNSAVED, student_id = student)
    form = RequestForm()
    return render(request,'requests_page.html', {'form': form , 'lessons': unsavedLessons})

def admin_feed(request):
    return render(request,'admin_feed.html')

def director_feed(request):
    return render(request,'director_feed.html')

def log_in(request):
     if request.method == 'POST':
         form = LogInForm(request.POST)
         if  form.is_valid():
             email = form.cleaned_data.get('email')
             password = form.cleaned_data.get('password')
             role = form.cleaned_data.get('role')
             user = authenticate(email=email, password=password)
             if user is not None:
                 login(request,user)

                 # redirects the user based on his role
                 if (user.role == UserRole.ADMIN.value):
                     return redirect('admin_feed')
                 elif (user.role == UserRole.DIRECTOR.value):
                     return redirect('director_feed')
                 else:
                     return redirect('student_feed')

         messages.add_message(request,messages.ERROR,"The credentials provided is invalid!")
     form = LogInForm()
     return render(request,'log_in.html', {'form' : form})


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            student = form.save()
            login(request, student)
            return redirect('student_feed')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})


def new_lesson(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_student = request.user

            previously_requested_lessons = Lesson.objects.filter(is_booked = LessonStatus.PENDING, student_id = current_student)

            #import widget tweaks
            #in the case the student already has requests that are pending, extend for the given term when terms are introduced
            if len(previously_requested_lessons) != 0:
                messages.add_message(request,messages.ERROR,"You have already made requests for this term, contact admin to add extra lessons")
                form = RequestForm()
                return render(request,'requests_page.html', {'form' : form})

            #if current_student.role.is_student():
            form = RequestForm(request.POST)
            if form.is_valid():
                duration = form.cleaned_data.get('duration')
                lesson_date = form.cleaned_data.get('lesson_date_time')
                type = form.cleaned_data.get('type')
                teacher_id = form.cleaned_data.get('teachers')

                lesson = Lesson.objects.create(type = type, duration = duration, lesson_date_time = lesson_date, teacher_id = teacher_id, student_id = current_student)
                #print('made lesson')
                unsavedLessons = Lesson.objects.filter(is_booked = LessonStatus.UNSAVED, student_id = current_student)

                return render(request,'requests_page.html', {'form': form, 'lessons' : unsavedLessons})
            else:
                messages.add_message(request,messages.ERROR,"The lesson information provided is invalid!")
        else:
            return redirect('log_in')
    else:
        form = RequestForm()

    return render(request,'requests_page.html', {'form' : form})

def save_lessons(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_student = request.user

            all_unsaved_lessons = Lesson.objects.filter(is_booked = LessonStatus.UNSAVED, student_id = current_student)

            for eachLesson in all_unsaved_lessons:
                #print(eachLesson.is_booked)
                eachLesson.is_booked = LessonStatus.PENDING
                eachLesson.save()

            return redirect('student_feed')

        else:
            return redirect('log_in')
    else:
        form = RequestForm()
        return render(rquest,'requests_page.html', {'form':form})
