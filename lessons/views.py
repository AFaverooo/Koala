from django.shortcuts import render
from .forms import LogInForm,SignUpForm
# Create your views here.


def home(request):
	return render(request, 'home.html')

def log_in(request):
	form = LogInForm()
	return render(request, 'log_in.html', {'form': form})


def sign_up(request):

	if(request.method == 'GET'):
		form = SignUpForm()
	if(request.method == 'POST'):
		form = SignUpForm(request.POST)
		if form.is_valid():
			student = form.save()
			login(request, student)

	return render(request, 'sign_up.html', {'form': form})
