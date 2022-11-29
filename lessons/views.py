from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import LogInForm,SignUpForm,RequestForm
from django.contrib.auth import authenticate,login,logout
from .models import UserRole, UserAccount, Lesson, LessonStatus, LessonType, Gender, Invoice, Transaction, TransactionTypes, InvoiceStatus
from .helper import login_prohibited
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


@login_required
def balance(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            student = request.user
            student_invoice = get_student_invoice(student) #this function filter out the invocie with the same student id as the current user
            student_transaction = get_student_transaction(student) #this function filter out the transaction with the same student id as the current user
            student_balance = get_student_balance(student)
            return render(request, 'balance.html', {'Invoice': student_invoice, 'Transaction': student_transaction, 'Balance': student_balance})
    else:
        return redirect('log_in')

def get_student_invoice(student):
    return Invoice.objects.filter(student_ID = student.id)

def get_student_transaction(student):
    return Transaction.objects.filter( Student_ID_transaction = student.id)

def get_student_balance(student):
    return UserAccount.objects.filter(id = student.id).values_list('balance', flat=True)

# this function update the student balance once student transfer some money into their school balance
@login_required
def update_balance(request):
    if(request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        if(request.method == 'POST'):
            try:
                extra_fees = request.POST.get('inputFees')
                extra_fees_int = int(extra_fees)
            except ValueError:
                messages.add_message(request,messages.ERROR,"You cannot submit without enter a value!")
                return redirect('balance')

            student = request.user

            if(extra_fees_int < 1):
                messages.add_message(request,messages.ERROR,"You cannont insert a value less than 1!")
            elif(student.balance + extra_fees_int > 10000):
                messages.add_message(request,messages.ERROR,"Your account balance cannot exceed £10000!")
            else:
                student.balance += extra_fees_int
                student.save()
                Transaction.objects.create(Student_ID_transaction = student.id, transaction_type = TransactionTypes.IN, transaction_amount = extra_fees_int)
            return redirect('balance')
    else:
        return redirect('log_in')

@login_required
def pay_fo_invoice(request):
    if(request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        if(request.method == 'POST'):
            try:
                input_invoice_reference = request.POST.get('invocie_reference')
                input_amounts_pay = request.POST.get('amounts_pay')
                input_amounts_pay_int = int(input_amounts_pay)
            except ValueError:
                messages.add_message(request,messages.ERROR,"You cannot submit without enter a value!")
                return redirect('balance')
            
            student = request.user
            try:
                temp_invoice = Invoice.objects.get(reference_number = input_invoice_reference)
            except ObjectDoesNotExist:
                messages.add_message(request,messages.ERROR,"There isn't such invoice exist!")
                return redirect('balance')

            if(int(temp_invoice.student_ID) != int(student.id)):
                messages.add_message(request,messages.ERROR,"this invoice does not belong to you!")
            elif(temp_invoice.invoice_status == InvoiceStatus.PAID):
                messages.add_message(request,messages.ERROR,"This invoice has already been paid!")
            elif(int(student.balance) < input_amounts_pay_int):
                messages.add_message(request,messages.ERROR,"You dont have enough money!")
            else:
                if(temp_invoice.amounts_need_to_pay == input_amounts_pay_int):
                    temp_invoice.invoice_status = InvoiceStatus.PAID
                    temp_invoice.amounts_need_to_pay = 0
                elif(temp_invoice.amounts_need_to_pay > input_amounts_pay_int):
                    temp_invoice.invoice_status = InvoiceStatus.PARTIALLY_PAID
                    temp_invoice.amounts_need_to_pay -= input_amounts_pay_int
                elif(temp_invoice.amounts_need_to_pay < input_amounts_pay_int):
                    messages.add_message(request,messages.ERROR,"The amount you insert has exceed the amount you have to pay!")
                    return redirect('balance')
                student.balance -= input_amounts_pay_int
                student.save()
                temp_invoice.save()

                Transaction.objects.create(Student_ID_transaction = student.id, transaction_type = TransactionTypes.OUT, invoice_reference_transaction = input_invoice_reference, transaction_amount = input_amounts_pay_int)

            return redirect('balance')

        return redirect('balance')

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


def home(request):
    return render(request, 'home.html')


@login_required
def student_feed(request):
    #print("redirected")

    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        unfulfilled_lessons = get_unfulfilled_lessons(request.user)
        fullfilled_lessons = get_fullfilled_lessons(request.user)

        if len(fullfilled_lessons) > 0:
            greeting_str = f'Welcome back {request.user} Below is your timetable for this term'
            fullfilled_lessons = make_lesson_timetable_dictionary(request.user)
            return render(request,'student_feed.html' ,{'fullfilled_lessons':fullfilled_lessons, 'greeting':greeting_str})
        elif len(unfulfilled_lessons) > 0:
            unfulfilled_requests = make_unfulfilled_dictionary(request.user)
            greeting_str = f'Welcome back {request.user} Below are your lesson requests'
            return render(request,'student_feed.html', {'unfulfilled_requests':unfulfilled_requests, 'greeting':greeting_str})
        else:
            greeting_str = f'Welcome back {request.user}'
            return render(request,'student_feed.html', {'greeting':greeting_str})

    else:
        print('not authorised')
        return redirect('log_in')

@login_required
def requests_page(request):
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        if request.method == 'GET':
            student = request.user
            savedLessons = get_saved_lessons(student)
            form = RequestForm()
            return render(request,'requests_page.html', {'form': form , 'lessons': savedLessons})
    else:
        #add message that the user should be logged in
        return redirect('log_in')

@login_required
def admin_feed(request):
    if (request.user.is_authenticated and request.user.role == UserRole.ADMIN):
        return render(request,'admin_feed.html')
    else:
        return redirect('log_in')

@login_required
def director_feed(request):
    if (request.user.is_authenticated and request.user.role == UserRole.DIRECTOR):
        return render(request,'director_feed.html')
    else:
        return redirect('log_in')



@login_prohibited
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


def log_out(request):
    logout(request)
    return redirect('home')

@login_prohibited
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
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        current_student = request.user
        if request.method == 'POST':
            #test case, already unfulfilled lessons upon request
            previously_requested_lessons = get_unfulfilled_lessons(current_student)
            previously_booked_lessons = get_fullfilled_lessons(current_student)

            #import widget tweaks
            #in the case the student already has requests that are unfulfilled, extend for the given term when terms are introduced
            if previously_requested_lessons or previously_booked_lessons:
                print('already made a set of requests')
                messages.add_message(request,messages.ERROR,"You have already made requests for this term or have booked lessons, contact admin to add extra lessons")
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
                #return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})
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
            return redirect('student_feed')
        else:
            form = RequestForm()
            return render(request,'requests_page.html', {'form' : form ,'lessons': get_saved_lessons(current_student)})
    else:
        #print('user should be logged in')
        return redirect('log_in')
        #form = RequestForm()
        #return render(rquest,'requests_page.html', {'form':form})

def render_edit_request(request,lesson_id):
    try:
        to_edit_lesson = Lesson.objects.get(lesson_id = lesson_id) #used to be lesson_lesson_edit_id from get method
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Incorrect lesson ID passed")
        return redirect('student_feed')

    data = {'type': to_edit_lesson.type,
            'duration': to_edit_lesson.duration,
            'lesson_date_time': to_edit_lesson.lesson_date_time,
            'teachers': to_edit_lesson.teacher_id}

    form = RequestForm(data)
    #print('render')
    return render(request,'edit_request.html', {'form' : form, 'lesson_id':lesson_id})


def edit_lesson(request,lesson_id):
    if request.user.is_authenticated and request.user.role == UserRole.STUDENT:
        current_student = request.user

        try:
            to_edit_lesson = Lesson.objects.get(lesson_id = lesson_id)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "Incorrect lesson ID passed")
            return redirect('student_feed')

        if request.method == 'POST':
            request_form = RequestForm(request.POST)

            if request_form.is_valid():
                #request_date = timezone.now
                duration = request_form.cleaned_data.get('duration')
                lesson_date = request_form.cleaned_data.get('lesson_date_time')
                type = request_form.cleaned_data.get('type')
                teacher_id = request_form.cleaned_data.get('teachers')

                try:
                    to_edit_lesson.duration = duration
                    to_edit_lesson.lesson_date_time = lesson_date
                    to_edit_lesson.type = type
                    to_edit_lesson.teacher_id = teacher_id
                    to_edit_lesson.save()

                except IntegrityError:
                    messages.add_message(request,messages.ERROR,"Duplicate lessons are not allowed")
                    return render_edit_request(request,lesson_id)
                    #print('attempted to duplicate lesson')

                messages.add_message(request,messages.SUCCESS,"Succesfully edited lesson")
                return redirect('student_feed')
            else:
                messages.add_message(request,messages.ERROR,"Form is not valid")
                return render_edit_request(request,lesson_id)
        else:
            return render_edit_request(request,lesson_id)
    else:
        return redirect('log_in')

def check_correct_student_lesson_deletion(student_id, lesson_id):
    all_student_lessons = Lesson.objects.filter(student_id = student_id)
    for lesson in all_student_lessons:
        if lesson.lesson_id == lesson_id:
            return True

    return False

def delete_pending(request,lesson_id):
    if request.user.is_authenticated and request.user.role == UserRole.STUDENT:
        current_student = request.user

        if check_correct_student_lesson_deletion(current_student,lesson_id):
            if request.method == 'POST':
                    try:
                        #print(int(request.POST.get['lesson_delete_id']))
                        Lesson.objects.get(lesson_id = lesson_id).delete()
                        #print('delete' + request.POST.get('lesson_delete_id'))
                    except ObjectDoesNotExist:
                        messages.add_message(request, messages.ERROR, "Incorrect lesson ID passed")
                        return redirect('student_feed')

                    messages.add_message(request, messages.SUCCESS, "Lesson request deleted")
                    return redirect('student_feed')

            else:
                return redirect('student_feed')
        else:
            messages.add_message(request, messages.WARNING, "Attempted Deletion Not Permitted")
            return redirect('student_feed')
    else:
        return redirect('log_in')
