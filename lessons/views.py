from django.shortcuts import render
from .forms import SignUpForm
# Create your views here.


def invoice(request):
	return render(request, 'invoice.html')

def home(request):
	return render(request, 'home.html')

def sign_up(request):

	if(request.method == 'GET'):
		form = SignUpForm()
	if(request.method == 'POST'):
		form = SignUpForm(request.POST)
		if form.is_valid():
			student = form.save()
			# login(request, student)

	return render(request, 'sign_up.html', {'form': form})