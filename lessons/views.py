from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import LogInForm,SignUpForm,RequestForm,CreateAdminForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.views import PasswordChangeView
from .models import UserRole, UserAccount, Lesson, LessonStatus, LessonType, Gender, Invoice

from django.core.exceptions import ObjectDoesNotExist

from django.db import IntegrityError
from django.utils import timezone
import datetime


# Create your views here.

from django.template.defaulttags import register

@register.filter
def get_lesson_duration(dictionary):
    return dictionary.get("Lesson Duration")

@register.filter
def get_lesson(dictionary):
    return dictionary.get("Lesson")

@register.filter
def get_lesson_date(dictionary):
    return dictionary.get("Lesson Date")

@register.filter
def get_teacher(dictionary):
    return dictionary.get("Teacher")


@register.filter
def get_lesson_request(dictionary):
    return dictionary.get("Lesson Request")


def make_unfulfilled_dictionary(student_user):
    unfulfilled_lessons = get_unfulfilled_lessons(student_user)

    unfulfilled_lessons_dict = {}

    request_count_id = 0
    for lesson in unfulfilled_lessons:
        lesson_type_str = ''

        if lesson.type == LessonType.INSTRUMENT:
            lesson_type_str = LessonType.INSTRUMENT.name
        elif lesson.type == LessonType.THEORY:
            lesson_type_str = LessonType.THEORY.name
        elif lesson.type == LessonType.PRACTICE:
            lesson_type_str = LessonType.PRACTICE.name
        elif lesson.type == LessonType.PERFORMANCE:
            lesson_type_str = LessonType.PERFORMANCE.name

        lesson_duration_str = f'{lesson.duration} minutes'

        case = {'Lesson Request': f'{request_count_id}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson': f'{lesson_type_str}', "Lesson Duration": f'{lesson_duration_str}', "Teacher": f'{lesson.teacher_id}'}
        unfulfilled_lessons_dict[lesson] = case
        request_count_id += 1

    return unfulfilled_lessons_dict

def invoice(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            student = request.user
            student_invoice = Invoice.objects.filter(student_ID = student.id) #this function filter out the invocie with the same student id as the current user
            return render(request, 'invoice.html', {'Invoice': student_invoice})
    else:
        return redirect('log_in')

def make_lesson_timetable_dictionary(student_user):
    fullfilled_lessons = get_fullfilled_lessons(student_user)

    fullfilled_lessons_dict = {}

    if len(fullfilled_lessons) == 0:
        return fullfilled_lessons_dict

    for lesson in fullfilled_lessons:
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
        fullfilled_lessons_dict[lesson] = case

    return fullfilled_lessons_dict


def get_saved_lessons(student):
    return Lesson.objects.filter(lesson_status = LessonStatus.SAVED, student_id = student)

def get_unfulfilled_lessons(student):
     return Lesson.objects.filter(lesson_status = LessonStatus.UNFULFILLED, student_id = student)

def get_fullfilled_lessons(student):
    return Lesson.objects.filter(lesson_status = LessonStatus.FULLFILLED, student_id = student)


def get_student_lessons(request,student):
    saved_lessons = Lesson.objects.filter(student_id = student)
    return render(request,'student_requests.html',{'saved_lessons':saved_lessons, 'student': student})

def update_request(request, id):
    lesson = Lesson.objects.get(lesson_id=id)
    # data = {
    #     'type' : lesson.type,
    #     'duration': lesson.duration,
    #     'lesson_date_time': lesson.lesson_date_time,
    #     'teachers' : lesson.teacher_id
    #        }
    form = RequestForm(instance=lesson)
    return render(request,'update_request.html', {'form': form , 'lesson': lesson})

def confirm_booking(request, current_lesson_id):
    lesson = Lesson.objects.get(lesson_id=current_lesson_id)
    lesson.lesson_status = 'BK'
    lesson.save()
    student = UserAccount.objects.get(id=lesson.student_id.id)
    saved_lessons = Lesson.objects.filter(student_id = student)
    return render(request,'student_requests.html',{'saved_lessons':saved_lessons, 'student': student})

def home(request):
    return render(request, 'home.html')

# def log_in(request):
#     form = LogInForm()
#     return render(request, 'log_in.html', {'form': form})
#
def log_out(request):
    logout(request)
    return redirect('home')

@login_required
def student_feed(request):
    #print("redirected")
    if request.user.is_authenticated:
        unfulfilled_lessons = get_unfulfilled_lessons(request.user)

        if len(unfulfilled_lessons) == 0:
            greeting_str = f'Welcome back {request.user} Below is your timetable for this term'
            fullfilled_lessons = make_lesson_timetable_dictionary(request.user)
            return render(request,'student_feed.html' ,{'fullfilled_lessons':fullfilled_lessons, 'greeting':greeting_str})
        else:
            unfulfilled_requests = make_unfulfilled_dictionary(request.user)
            greeting_str = f'Welcome back {request.user} Below are your lesson requests'
            return render(request,'student_feed.html', {'unfulfilled_requests':unfulfilled_requests, 'greeting':greeting_str})
    else:
        return redirect('log_in')

@login_required
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
    student = UserAccount.objects.values()
    return render(request,'admin_feed.html',{'student':student})


@login_required
def director_feed(request):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        return render(request,'director_feed.html')

    else:
        return redirect('log_in')


@login_required
def director_manage_roles(request):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        students = UserAccount.objects.filter(role = UserRole.STUDENT)
        teachers = UserAccount.objects.filter(role = UserRole.TEACHER)
        admins = UserAccount.objects.filter(role = UserRole.ADMIN)
        directors = UserAccount.objects.filter(role = UserRole.DIRECTOR)
        return render(request,'director_manage_roles.html',{'students':students, 'teachers':teachers, 'admins':admins, 'directors':directors})
    else:
        return redirect("log_in")



@login_required
def promote_director(request,current_user_email):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot promote yourself!")
            return redirect('director_manage_roles')
        else:
            user = UserAccount.objects.get(email=current_user_email)
            user.role = UserRole.DIRECTOR
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.add_message(request,messages.SUCCESS,f"{current_user_email} now has the role director")
            return redirect('director_manage_roles')
    else:
        return redirect("log_in")


@login_required
def promote_admin(request,current_user_email):

    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot demote yourself!")
            return redirect('director_manage_roles')
        else:
            user = UserAccount.objects.get(email=current_user_email)
            user.role = UserRole.ADMIN
            user.is_staff = True
            user.is_superuser = False
            user.save()
            messages.add_message(request,messages.SUCCESS,f"{current_user_email} now has the role admin")
            return redirect("director_manage_roles")
    else:

        return redirect("log_in")



@login_required
def disable_user(request,current_user_email):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot disable yourself!")
            return director_manage_roles(request)
        else:
            user = UserAccount.objects.get(email=current_user_email)
            if (user.is_active == True):
                user.is_active = False
                user.save()
                messages.add_message(request,messages.SUCCESS,f"{current_user_email} has been sucessfuly disabled!")
            else:
                user.is_active = True
                user.save()
                messages.add_message(request,messages.SUCCESS,f"{current_user_email} has been sucessfuly enabled!")

            return director_manage_roles(request)
    else:
        return redirect("log_in")



@login_required
def delete_user(request,current_user_email):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot delete yourself!")
            return director_manage_roles(request)
        else:
            user = UserAccount.objects.get(email=current_user_email)
            user.delete()
            messages.add_message(request,messages.SUCCESS,f"{current_user_email} has been sucessfuly deleted!")
            return director_manage_roles(request)
    else:
        return redirect("log_in")



def create_admin_page(request):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if request.method == 'POST':
            form = CreateAdminForm(request.POST)
            if form.is_valid():
                admin = form.save()
                return redirect('director_manage_roles')
        else:
            form = CreateAdminForm()

        return render(request,'director_create_admin.html',{'form': form})
    else:
        return redirect("log_in")


@login_required
def update_user(request,current_user_id):

    # if user is the current user, log out

    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:

        user = UserAccount.objects.get(id=current_user_id)
        form = CreateAdminForm(instance=user)

        if request.method == 'POST':
            form = CreateAdminForm(request.POST, instance = user)
            if form.is_valid():

                email = form.cleaned_data.get('email')
                fname = form.cleaned_data.get('first_name')
                lname = form.cleaned_data.get('last_name')
                gender = form.cleaned_data.get('gender')

                new_password = form.cleaned_data.get('new_password')

                user.email = email
                user.first_name = fname
                user.last_name = lname
                user.gender = gender

                user.set_password(new_password)
                user.save()

                # current user logged out if he edits himself
                if (int(request.user.id) == int(current_user_id)):
                    messages.add_message(request,messages.SUCCESS,f"You cant't edit yourself!")
                    return log_out(request)

                messages.add_message(request,messages.SUCCESS,f"{user.email} has been sucessfuly updated!")

                return redirect('director_manage_roles')

        return render(request,'director_update_user.html', {'form': form , 'user': user})


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
                     #redirect_url = request.POST.get('next') or 'admin_feed'
                     return redirect('admin_feed')
                 elif (user.role == UserRole.DIRECTOR.value):
                     redirect_url = request.POST.get('next') or 'director_feed'
                     return redirect(redirect_url)
                 else:
                     redirect_url = request.POST.get('next') or 'student_feed'
                     return redirect(redirect_url)

         messages.add_message(request,messages.ERROR,"The credentials provided is invalid!")
     form = LogInForm()
     next = request.GET.get('next') or ''
     return render(request,'log_in.html', {'form' : form, 'next' : next})


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
    if request.user.is_authenticated:
        current_student = request.user
        if request.method == 'POST':
            #test case, already unfulfilled lessons upon request
            previously_requested_lessons = get_unfulfilled_lessons(current_student)

            #import widget tweaks
            #in the case the student already has requests that are unfulfilled, extend for the given term when terms are introduced
            if previously_requested_lessons:
                print('already made a set of requests')
                messages.add_message(request,messages.ERROR,"You have already made requests for this term, contact admin to add extra lessons")
                form = RequestForm()
                return redirect('requests_page')

            #if current_student.role.is_student():
            request_form = RequestForm(request.POST)

            if request_form.is_valid():
                duration = request_form.cleaned_data.get('duration')
                lesson_date = request_form.cleaned_data.get('lesson_date_time')
                type = request_form.cleaned_data.get('type')
                teacher_id = request_form.cleaned_data.get('teachers')

                try:#if check_duplicate(timezone.now, lesson_date, current_student) is False:
                    Lesson.objects.create(type = type, duration = duration, lesson_date_time = lesson_date, teacher_id = teacher_id, student_id = current_student)
                except IntegrityError:
                    messages.add_message(request,messages.ERROR,"Duplicate lessons are not allowed")
                    return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})
                    #print('attempted to duplicate lesson')
                return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})


                #savedLessons = Lesson.objects.filter(lesson_status = LessonStatus.SAVED, student_id = current_student)
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
    if request.user.is_authenticated:
        current_student = request.user
        if request.method == 'POST':
            all_unsaved_lessons = get_saved_lessons(current_student)

            if len(all_unsaved_lessons) == 0:
                messages.add_message(request,messages.ERROR,"Lessons should be requested before attempting to save")
                form = RequestForm()
                return render(request,'requests_page.html', {'form': form})

            for eachLesson in all_unsaved_lessons:
                #print(eachLesson.lesson_status)
                eachLesson.lesson_status = LessonStatus.UNFULFILLED
                eachLesson.save()

            messages.add_message(request,messages.SUCCESS, "Lesson requests are now unfulfilled for validation by admin")
            form = RequestForm()
            return render(request,'requests_page.html', {'form': form})
        else:
            form = RequestForm()
            return render(request,'requests_page.html', {'form' : form ,'lessons': get_saved_lessons(current_student)})
    else:
        #print('user should be logged in')
        return redirect('log_in')
        #form = RequestForm()
        #return render(rquest,'requests_page.html', {'form':form})
