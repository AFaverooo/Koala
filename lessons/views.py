from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import LogInForm,SignUpForm,RequestForm,TermDatesForm
from django.contrib.auth import authenticate,login,logout
from .models import UserRole, UserAccount, Lesson, LessonStatus, LessonType, Gender, Invoice, Transaction, TransactionTypes, InvoiceStatus,Term
from .helper import login_prohibited
from django.core.exceptions import ObjectDoesNotExist

from django.db import IntegrityError
from django.utils import timezone
import datetime
from django.core.exceptions import ObjectDoesNotExist

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

@register.filter
def get_lesson_saved(dictionary):
    return dictionary.get("Saved")


def make_lesson_dictionary(student_user,lessonStatus):
    lessons = []
    if lessonStatus == 'Lesson Request':
        lessons = get_unfulfilled_lessons(student_user)
    else:
        lessons = get_saved_lessons(student_user)

    lessons_dict = {}

    id_count = 0
    for lesson in lessons:
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

        case = {lessonStatus: f'{id_count}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson': f'{lesson_type_str}', "Lesson Duration": f'{lesson_duration_str}', "Teacher": f'{lesson.teacher_id}'}
        lessons_dict[lesson] = case
        id_count += 1

    return lessons_dict


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
        return redirect('home')

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
        # return redirect('log_in')
        return redirect('home')

def get_all_transactions(request):
    all_transactions = Transaction.objects.all()
    total = 0 
    for each_transaction in all_transactions:
        if(each_transaction.transaction_type == TransactionTypes.OUT):
            total-= each_transaction.transaction_amount
        elif(each_transaction.transaction_type == TransactionTypes.IN):
            total+= each_transaction.transaction_amount

    return render(request,'transaction_history.html', {'all_transactions': all_transactions, 'total':total})

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


# Admin functionality view functions

def student_requests(request,student_id):
    saved_lessons = Lesson.objects.filter(student_id = student_id)
    student = UserAccount.objects.get(id=student_id)
    return render(request,'admin_student_requests_page.html',{'saved_lessons':saved_lessons, 'student': student})

def admin_update_request_page(request, lesson_id):
    try:
        lesson = Lesson.objects.get(lesson_id=lesson_id)
        data = {
            'type' : lesson.type,
            'duration': lesson.duration,
            'lesson_date_time': lesson.lesson_date_time,
            'teachers' : lesson.teacher_id
            }
        form = RequestForm(data)
        return render(request,'admin_update_request.html', {'form': form , 'lesson': lesson})
    except ObjectDoesNotExist:
        messages.add_message(request, messages.SUCCESS, 'Lesson was successfully updated!')
        return redirect('admin_feed')

def admin_update_request(request, lesson_id):
    try:
        lesson = Lesson.objects.get(lesson_id=lesson_id)
        form = RequestForm(request.POST)

        if form.is_valid():
            type = form.cleaned_data.get('type')
            duration = form.cleaned_data.get('duration')
            lesson_date_time = form.cleaned_data.get('lesson_date_time')
            teacher_id = form.cleaned_data.get('teachers')

        if (lesson.type == type and lesson.duration == duration and lesson.lesson_date_time == lesson_date_time and lesson.teacher_id == teacher_id):
            messages.add_message(request, messages.ERROR, 'Lesson details are the same as before!')
            return render(request,'admin_update_request.html', {'form': form , 'lesson': lesson})
        else:
            lesson.type = type
            lesson.duration = duration
            lesson.lesson_date_time = lesson_date_time
            lesson.teacher_id = teacher_id
            lesson.save()
            messages.add_message(request, messages.SUCCESS, 'Lesson was successfully updated!')

            student = UserAccount.objects.get(id=lesson.student_id.id)
            return redirect('student_requests',student.id)

    except ObjectDoesNotExist:
        return redirect('admin_feed')

def admin_confirm_booking(request, lesson_id):
    lesson = Lesson.objects.get(lesson_id=lesson_id)
    if(lesson.lesson_status == 'BK'):
        messages.add_message(request, messages.INFO, 'Already booked!')
    else:
        lesson.lesson_status = 'BK'
        lesson.save()
        messages.add_message(request, messages.SUCCESS, 'Successfully Booked!')
    student = UserAccount.objects.get(id=lesson.student_id.id)
    return redirect('student_requests',student.id)

def delete_lesson(request, lesson_id):
    lesson = Lesson.objects.get(lesson_id=lesson_id)
    if lesson is not None:
        lesson.delete()
        messages.add_message(request, messages.SUCCESS, 'Lesson was successfully deleted!')
        student = UserAccount.objects.get(id=lesson.student_id.id)
        return redirect('student_requests',student.id)


# Term view functions


def term_management_page(request):
    terms_list = Term.objects.all()
    return render(request,'term_management.html', {'terms_list': terms_list})
    # #terms_list = Term.objects.all()
    # term_form = TermDatesForm(request.POST)

    # if term_form.is_valid():
    #     term_number = term_form.cleaned_data.get('term_number')
    #     start_date = term_form.cleaned_data.get('start_date')
    #     type = term_form.cleaned_data.get('type')
    #     teacher_id = term_form.cleaned_data.get('teachers')

    # Lesson.objects.create(type = type, duration = duration, lesson_date_time = lesson_date, teacher_id = teacher_id, student_id = current_student)

def add_term_page(request):
    if len(Term.objects.all()) < 6:
        form = TermDatesForm()
        return render(request, 'create_term_form.html', {'form':form})
    else:
        terms_list = Term.objects.all()
        messages.add_message(request,messages.ERROR, "Cannot have more than 6 terms in a year, please edit or delete existing terms!")
        return render(request,'term_management.html', {'terms_list': terms_list})

def create_term(request):
    form = TermDatesForm(request.POST)
    if form.is_valid():
        form.save()
        terms_list = Term.objects.all()
        messages.add_message(request,messages.SUCCESS, "Successfully added term!")
        return render(request,'term_management.html', {'terms_list': terms_list})
    # else:
    #     terms_list = Term.objects.all()
    #     messages.add_message(request,messages.ERROR, "Term data is invalid!")
    #     return render(request,'term_management.html', {'terms_list': terms_list})
    terms_list = Term.objects.all()
    messages.add_message(request,messages.SUCCESS, "Successfully added term!")
    return render(request,'term_management.html', {'terms_list': terms_list})

# def save_term(request):
#     form = TermDatesForm(request.POST)
#     if form.is_valid():
#         form.save()
#         terms_list = Term.objects.all()
#         messages.add_message(request,messages.SUCCESS, "Successfully added term!")
#         return render(request,'term_management.html', {'terms_list': terms_list})
#     # else:
#     #     terms_list = Term.objects.all()
#     #     messages.add_message(request,messages.ERROR, "Term data is invalid!")
#     #     return render(request,'term_management.html', {'terms_list': terms_list})
#     terms_list = Term.objects.all()
#     messages.add_message(request,messages.SUCCESS, "Successfully added term!")
#     return render(request,'term_management.html', {'terms_list': terms_list})

def edit_term_details_page(request,term_number):
    term = Term.objects.get(term_number=term_number)

    previous_term = None
    if( int(term_number)-1 >0 ):
        previous_term = Term.objects.get(term_number=str(int(term_number)-1))

    next_term = None
    if( int(term_number)+1 <6 ):
        next_term = Term.objects.get(term_number=str(int(term_number)+1))

    data = {
        'term_number': term.term_number,
        'start_date': term.start_date,
        'end_date': term.end_date,
        }
    form = TermDatesForm(data)
    return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})

def update_term_details(request,term_number):
    try:
        term = Term.objects.get(term_number=term_number)
        form = TermDatesForm(request.POST)

        if form.is_valid():
            # term_number = form.cleaned_data.get('term_number')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

        if (term.start_date == start_date and term.end_date == end_date):
            terms_list = Term.objects.all()
            messages.add_message(request, messages.ERROR, 'Term details are the same as before!')
            return render(request,'term_management.html', {'terms_list': terms_list})
        
        previous_term = Term.objects.get(term_number=str(int(term_number)-1))
        next_term = Term.objects.get(term_number=str(int(term_number)+1))


        if(start_date > end_date or end_date < start_date):
            messages.add_message(request, messages.ERROR, "This term's end date and start date overlap with one another!")
            return render(request,'add_term_form.html', {'form': form, 'term':term})

        elif(end_date > next_term.start_date and start_date < previous_term.end_date):
            messages.add_message(request, messages.ERROR, "This term's end date and start date overlap with other terms!")
            return render(request,'add_term_form.html', {'form': form, 'term':term})


        elif(end_date > next_term.start_date):
            messages.add_message(request, messages.ERROR, "This term's end date overlaps with the next term's starting date!")
            return render(request,'add_term_form.html', {'form': form, 'term':term})

        elif(start_date < previous_term.end_date):
            messages.add_message(request, messages.ERROR, "This term's start date overlaps with the previous term's ending date!")
            return render(request,'add_term_form.html', {'form': form, 'term':term})

        
        term.start_date = start_date
        term.end_date = end_date
        term.save()
        messages.add_message(request, messages.SUCCESS, 'Term details were successfully updated!')

        terms_list = Term.objects.all()
        return render(request,'term_management.html', {'terms_list': terms_list})

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'ERROR')
        return redirect('admin_feed')


def delete_term(request, term_number):
    term = Term.objects.get(term_number=term_number)
    if term is not None:
        term.delete()
        messages.add_message(request, messages.SUCCESS, 'Term was successfully deleted!')
        return term_management_page(request)


# -----------


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
            unfulfilled_requests = make_lesson_dictionary(request.user,"Lesson Request")
            greeting_str = f'Welcome back {request.user} Below are your lesson requests'
            return render(request,'student_feed.html', {'unfulfilled_requests':unfulfilled_requests, 'greeting':greeting_str})
        else:
            greeting_str = f'Welcome back {request.user}'
            return render(request,'student_feed.html', {'greeting':greeting_str})

    else:
        print('not authorised')
        # return redirect('log_in')
        return redirect('home')

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
        #return redirect('log_in')
        return redirect('home')

@login_required
def admin_feed(request):
    if (request.user.is_authenticated and request.user.role == UserRole.ADMIN):
        student = UserAccount.objects.filter(role=UserRole.STUDENT.value)
        fulfilled_lessons = Lesson.objects.filter(lesson_status = LessonStatus.FULLFILLED)
        unfulfilled_lessons = Lesson.objects.filter(lesson_status = LessonStatus.UNFULFILLED)
        return render(request,'admin_feed.html',{'student':student,'fulfilled_lessons':fulfilled_lessons,'unfulfilled_lessons':unfulfilled_lessons})
    else:
        # return redirect('log_in')
        return redirect('home')

@login_required
def director_feed(request):
    if (request.user.is_authenticated and request.user.role == UserRole.DIRECTOR):
        return render(request,'director_feed.html')
    else:
        # return redirect('log_in')
        return redirect('home')



@login_prohibited
def home(request):
     if request.method == 'POST':
         form = LogInForm(request.POST)
         print(f"Is form valid: {form.is_valid()}")
         email = request.POST.get("email")
         print(email)
         password = request.POST.get("password")
         print(password)
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
     #return render(request,'log_in.html', {'form' : form, 'next' : next})
     return render(request,'home.html', {'form' : form, 'next' : next})


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
                messages.add_message(request,messages.ERROR,"Lesson requests have already been made for the term")
                return redirect('requests_page')

            #if current_student.role.is_student():
            request_form = RequestForm(request.POST)

            if request_form.is_valid():
                duration = request_form.cleaned_data.get('duration')
                lesson_date = request_form.cleaned_data.get('lesson_date_time')
                type = request_form.cleaned_data.get('type')
                teacher_id = request_form.cleaned_data.get('teachers')

                try:
                    Lesson.objects.create(type = type, duration = duration, lesson_date_time = lesson_date, teacher_id = teacher_id, student_id = current_student)
                except IntegrityError:
                    messages.add_message(request,messages.ERROR,"Lesson information provided already exists")
                    return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})

                return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(current_student)})
            else:
                messages.add_message(request,messages.ERROR,"The lesson information provided is invalid!")
                return render(request,'requests_page.html', {'form': request_form, 'lessons' : get_saved_lessons(current_student)})
        else:
            form = RequestForm()
            return render(request,'requests_page.html', {'form' : form ,'lessons': get_saved_lessons(current_student)})
    else:
        #print('user should be logged in')
        #return redirect('log_in')
        return redirect('home')

def save_lessons(request):
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        current_student = request.user
        if request.method == 'POST':
            all_unsaved_lessons = get_saved_lessons(current_student)

            if len(all_unsaved_lessons) == 0:
                messages.add_message(request,messages.ERROR,"Lessons should be requested before attempting to save")
                form = RequestForm()
                return render(request,'requests_page.html', {'form': form})

            for eachLesson in all_unsaved_lessons:
                eachLesson.lesson_status = LessonStatus.UNFULFILLED
                eachLesson.save()

            messages.add_message(request,messages.SUCCESS, "Lesson requests are now pending for validation by admin")
            return redirect('student_feed')
        else:
            form = RequestForm()
            return render(request,'requests_page.html', {'form' : form ,'lessons': get_saved_lessons(current_student)})
    else:
        #print('user should be logged in')
        return redirect('home')
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
        # return redirect('log_in')
        return redirect('home')

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
        # return redirect('log_in')
        return redirect('home')
