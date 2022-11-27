
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import LogInForm,SignUpForm,RequestForm
from django.contrib.auth import authenticate,login,logout
from .models import UserRole, UserAccount, Lesson, LessonStatus, LessonType, Gender

from django.core.exceptions import ObjectDoesNotExist

from django.db import IntegrityError
from django.utils import timezone
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

        teacher_str = ''

        if lesson.teacher_id.gender == Gender.FEMALE:
            teacher_str = f'Miss {lesson.teacher_id}'
        elif lesson.teacher_id.gender == Gender.MALE:
            teacher_str = f'Mr {lesson.teacher_id}'
        else:
            teacher_str = f'{lesson.teacher_id}'

        duration_str = f'{lesson_date_hr_str}:{lesson_date_minute_str} - {new_lesson_hr_str}:{new_time_minute_str}'

        case = {'Lesson': f'{lesson_type_str}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson Duration': f'{duration_str}', 'Teacher': f'{teacher_str}'}
        booked_lessons_dict[lesson] = case

    return booked_lessons_dict


def get_saved_lessons(student):
    return Lesson.objects.filter(is_booked = LessonStatus.SAVED, student_id = student)

def get_pending_lessons(student):
     return Lesson.objects.filter(is_booked = LessonStatus.PENDING, student_id = student)

def get_student_lessons(request,student):
    saved_lessons = Lesson.objects.filter(student_id = student)
    return render(request,'student_requests.html',{'saved_lessons':saved_lessons, 'student': student})



def home(request):
    return render(request, 'home.html')

def student_feed(request):
    if request.user.is_authenticated:
        #greeting_str = f'Welcome back {request.user} Below is your timetable for this term'
        #booked_lessons = make_lesson_timetable_dictionary(request.user)
        return render(request,'student_feed.html')#, {'booked_lessons':booked_lessons}) #, 'greeting':greeting_str})
    else:
        return redirect('log_in')

def requests_page(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            student = request.user
            savedLessons = get_saved_lessons(student)
            form = RequestForm()
            return render(request,'requests_page.html', {'form': form , 'lessons': savedLessons})
    else:
        #add message that the user should be logged in
        return redirect('log_in')

def admin_feed(request):
    #student = request.user

    student = UserAccount.objects.values()

    return render(request,'admin_feed.html',{'student':student})

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

def check_duplicate(request_date, lesson_date_time, student_id):
    duplicate_lesson = Lesson.objects.filter(request_date = request_date, lesson_date_time = lesson_date_time, student_id = student_id)

    return (len(duplicate_lesson) == 0)

def new_lesson(request):
    if request.user.is_authenticated:
        current_student = request.user
        if request.method == 'POST':
            #test case, already pending lessons upon request
            previously_requested_lessons = get_pending_lessons(current_student)

            #import widget tweaks
            #in the case the student already has requests that are pending, extend for the given term when terms are introduced
            if previously_requested_lessons:
                print('already made a set of requests')
                messages.add_message(request,messages.ERROR,"You have already made requests for this term, contact admin to add extra lessons")
                form = RequestForm()
                return render(request,'requests_page.html', {'form' : form})

            #if current_student.role.is_student():
            request_form = RequestForm(request.POST)

            if request_form.is_valid():
                duration = request_form.cleaned_data.get('duration')
                lesson_date = request_form.cleaned_data.get('lesson_date_time')
                type = request_form.cleaned_data.get('type')
                teacher_id = request_form.cleaned_data.get('teachers')

                if check_duplicate(timezone.now, lesson_date, current_student) is False:
                    Lesson.objects.create(type = type, duration = duration, lesson_date_time = lesson_date, teacher_id = teacher_id, student_id = current_student)
                else:
                    messages.add_message(request,messages.ERROR,"Duplicate lessons are not allowed")
                    return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})
                    #print('attempted to duplicate lesson')
                return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})


                #savedLessons = Lesson.objects.filter(is_booked = LessonStatus.SAVED, student_id = current_student)
                #return render(request,'requests_page.html', {'form': form, 'lessons' : savedLessons})
                return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})
            else:
                messages.add_message(request,messages.ERROR,"The lesson information provided is invalid!")
                savedLessons = get_saved_lessons(current_student)
                return render(request,'requests_page.html', {'form': request_form, 'lessons' : savedLessons})
        else:
            form = RequestForm()
            return render(request,'requests_page.html', {'form' : form ,'lessons': get_saved_lessons(current_student)})
    else:
        #print('user should be logged in')
        return redirect('log_in')



def save_lessons(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_student = request.user

            all_unsaved_lessons = Lesson.objects.filter(is_booked = LessonStatus.SAVED, student_id = current_student)

            if len(all_unsaved_lessons) == 0:
                messages.add_message(request,messages.ERROR,"Lessons should be requested before attempting to save")
                form = RequestForm()
                return render(request,'requests_page.html', {'form': form})

            for eachLesson in all_unsaved_lessons:
                #print(eachLesson.is_booked)
                eachLesson.is_booked = LessonStatus.PENDING
                eachLesson.save()

            #print('succesfully saved lessons')
            return redirect('student_feed')

        else:
            #print('user should be logged in')
            return redirect('log_in')
    else:
        return requests_page(request)
        #form = RequestForm()
        #return render(rquest,'requests_page.html', {'form':form})
