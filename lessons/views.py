from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import LogInForm,SignUpForm
from django.contrib.auth import authenticate,login,logout
from .models import UserRole
# Create your views here.


def home(request):
    return render(request, 'home.html')

# def log_in(request):
#     form = LogInForm()
#     return render(request, 'log_in.html', {'form': form})
#


def student_feed(request):
    return render(request,'student_feed.html')

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
                 if (user.role == UserRole.ADMIN.label):
                     return redirect('admin_feed')
                 elif (user.role == UserRole.DIRECTOR.label):
                     return redirect('director_feed')
                 else:
                     return redirect('student_feed')

         messages.add_message(request,messages.ERROR,"The credentials provided is invalid!")
     form = LogInForm()
     return render(request,'log_in.html', {'form' : form})


def sign_up(request):

    if(request.method == 'GET'):
        form = SignUpForm()
    if(request.method == 'POST'):
        form = SignUpForm(request.POST)
        if form.is_valid():
            student = form.save()
            login(request, student)

    return render(request, 'sign_up.html', {'form': form})
