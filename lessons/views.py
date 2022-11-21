from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import LogInForm,SignUpForm,RequestForm
from django.contrib.auth import authenticate,login,logout
from .models import UserRole, UserAccount, Lesson

from .modelHelpers import produce_teacher_object
# Create your views here.


def home(request):
    return render(request, 'home.html')

# def log_in(request):
#     form = LogInForm()
#     return render(request, 'log_in.html', {'form': form})
#

def student_feed(request):
    return render(request,'student_feed.html')

def requests_page(request):
    form = RequestForm()
    return render(request,'requests_page.html', {'form': form})

def admin_feed(request):
    return render(request,'admin_feed.html')

def director_feed(request):
    return render(request,'director_feed.html')

def log_in(request):
     if request.method == 'POST':
         form = LogInForm(request.POST)
         if form.is_valid():
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
            #if current_student.role.is_student():
            form = RequestForm(request.POST)

            if form.is_valid():
                    #first_name = form.cleaned_data.get('teacher')
                    #last_name = form.cleaned_data.get('teacher')

                    #teacher_id = UserAccount.objects.get(first_name = teacher_name).pk
                duration = form.cleaned_data.get('duration')
                lesson_date = form.cleaned_data.get('lesson_date_time')
                type = form.cleaned_data.get('type')
                teacher_id = produce_teacher_object("johndoe@example.org")

                lesson = Lesson.objects.create(type = type, duration = duration, lesson_date_time = lesson_date, teacher_id = teacher_id)
                print('made lesson')
                return render(request,'requests_page.html')
            else:
                print('form is not valid')
            #else:
            #    print('user is not student')
        else:
            print('user is not authenitcated')
    return render(request,'student_feed.html')
