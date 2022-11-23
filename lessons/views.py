from django.shortcuts import render
from .forms import SignUpForm
from .models import *
# Create your views here.


def invoice(request):
	b = Invoice.objects.get(reference_number = '111-11')
	return render(request, 'invoice.html', {'Invoice': b})

def updateInvoice(request):
	Invoice.create_new_invoice()

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