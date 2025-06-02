from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime,date,timedelta
from django.contrib import messages

from .models import *

def index(request):
    return render(request, "index.html")

def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = Register.objects.get(email=email, password=password,rights='User')
            request.session['user_id'] = user.id
            msg = "Success"
            return render(request, "user_login.html",{'msg':msg})
        except Register.DoesNotExist:
            msg = "Invalid"
            return render(request, "user_login.html", {"msg": msg})
    return render(request, "user_login.html")

def hospital_login(request):
    if request.method == "POST":
        hid = request.POST.get("hid")
        password = request.POST.get("password")
        try:
            hospital = Hospital.objects.get(hid=hid, password=password)
            if hospital.rights == 'Hospital':
                request.session['hospital_id'] = hospital.id
                msg= "Success"
            elif hospital.rights == 'New Hospital':
                msg = "New Hospital"
            return render(request, "hst_login.html", {'msg': msg})
        except Hospital.DoesNotExist:
            msg = "Invalid"
            return render(request, "hst_login.html", {"msg": msg})
    return render(request, "hst_login.html")

def user_reg(request):
    msg=""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        reg=Register(name=name, email=email, phone=phone, password=password)
        reg.save()
        msg='Success'
    return render(request, "user_reg.html", {"msg": msg})

# def hospital_reg(request):
#     msg = ""
#     if request.method == "POST":
#         hname = request.POST.get("hname")
#         hid = request.POST.get("hid")
#         address = request.POST.get("address")
#         city = request.POST.get("city")
#         state = request.POST.get("state")
#         zip_code = request.POST.get("zip")
#         email = request.POST.get("email")
#         phone = request.POST.get("phone")
#         password = request.POST.get("password")
#         hospital = Hospital(hname=hname, hid=hid, address=address, city=city,state=state, zip=zip_code, email=email, phone=phone,password=password)
#         hospital.save()
#         msg = 'Success'
#     return render(request, "hst_reg.html",{'msg': msg})

def user(request):
    return render(request, "user/user.html")

def hospital(request):
    return render(request, "hospital/hospital.html")

def users(request):
    users = Register.objects.exclude(rights='Admin')
    return render(request, "hospital/users.html", {'users': users})

def block_user(request, id):
    try:
        user = Register.objects.get(id=id)
        user.rights = 'Blocked'
        user.save()
        msg = "User blocked."
    except Register.DoesNotExist:
        msg = "User not found."
    return redirect('users')

def unblock_user(request, id):
    try:
        user = Register.objects.get(id=id)
        user.rights = 'User'
        user.save()
        msg = "User unblocked successfully."
    except Register.DoesNotExist:
        msg = "User not found."
    return redirect('users')

def view_department(request):
    hid= request.session.get('hospital_id')
    if not hid:
        return redirect('hospital_login')
    hospital = Hospital.objects.get(id=hid)
    departments = Department.objects.filter(hospital=hospital)
    return render(request, "hospital/manage-department.html", {'departments': departments})

def add_department(request):
    if request.method == "POST":
        name = request.POST.get("name")
        head = request.POST.get("head")
        phone = request.POST.get("phone")
        hospital_id = request.session.get('hospital_id')
        hospital = Hospital.objects.get(id=hospital_id)
        department = Department(name=name, head=head, phone=phone, hospital=hospital)
        department.save()
        msg = "Success"
        return redirect('view_department')
    return render(request, "hospital/manage-department.html", {'msg': msg})

def edit_department(request,id):
    if request.method == "POST":
        name = request.POST.get("name")
        head = request.POST.get("head")
        phone = request.POST.get("phone")
        hospital = Department.objects.filter(id=id)
        hospital.update(name=name, head=head, phone=phone)
        msg = "Success"
        return redirect('view_department')
    return render(request, "hospital/manage-department.html", {'msg': msg})

def delete_department(request,id):
    Department.objects.filter(id=id).delete()
    return redirect('view_department')

def manage_doctor(request):
    hid= request.session.get('hospital_id')
    if not hid:
        return redirect('hospital_login')
    hospital = Hospital.objects.get(id=hid)
    doctors = Doctor.objects.filter(hospital=hospital)
    dept= Department.objects.filter(hospital=hospital)
    return render(request, "hospital/manage-doctor.html", {'doctors': doctors, 'dept': dept})

def add_doctor(request):
    msg=''
    hospital_id = request.session.get('hospital_id')
    hospital = Hospital.objects.get(id=hospital_id)
    
    if request.method == "POST":
        image= request.FILES['image']
        dname = request.POST.get("dname")
        gender = request.POST.get("gender")
        qualification = request.POST.get("qualification")
        department = request.POST.get("department")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        doctor = Doctor(hospital=hospital,image=image, dname=dname,gender=gender, qualification=qualification, department=department, email=email, phone=phone)
        doctor.save()
        msg = "Success"
        return redirect('/manage_doctor/')
    return render(request, "hospital/manage-doctor.html", {'msg': msg})

def delete_doctor(request,id):
    Doctor.objects.filter(id=id).delete()
    return redirect('manage_doctor')

def edit_doctor(request,id):
    if request.method == "POST":
        image= request.FILES.get('image')
        dname = request.POST.get("dname")
        gender = request.POST.get("gender")
        qualification = request.POST.get("qualification")
        department = request.POST.get("department")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        dct=Doctor.objects.get(id=id)
        dct.image=image
        dct.dname=dname
        dct.gender=gender
        dct.qualification=qualification
        dct.department=department
        dct.email=email
        dct.phone=phone
        dct.save()
        msg = "Success"
    return redirect('/manage_doctor/')

def book_appointment(request):
    depts= Department.objects.all()
    user=request.session.get('user_id')
    if request.method=="POST":
        doctor_id = request.POST.get("doctor")
        date = request.POST.get("date")
        time = request.POST.get("time")
        reason= request.POST.get("reason")
        user_instance = Register.objects.get(id=user)
        doctor_instance = Doctor.objects.get(id=doctor_id)
        appointment = Appointment(user=user_instance, doctor=doctor_instance, date=date, time=time, reason=reason)
        appointment.save()
        return redirect(f'/payment/{appointment.id}/')
    return render(request, "user/appointment.html", {'depts': depts})

def get_doctors(request, department):
    doctors = Doctor.objects.filter(department=department).values('id', 'dname', 'qualification')
    return JsonResponse(list(doctors), safe=False)

def payment(request,id):
    msg=''
    appointment= Appointment.objects.get(id=id)
    if request.method=="POST":
        msg='Success'
    return render(request, "user/payment.html",{'msg': msg, 'appointment': appointment})

def my_appointments(request):
    user_id = request.session.get('user_id')
    msg=''
    if not user_id:
        return redirect('user_login')
    user = Register.objects.get(id=user_id)
    appointments = Appointment.objects.filter(user=user)
    if request.method=="POST":
        aid=request.POST.get("aid")
        Appointment.objects.filter(id=aid).update(status='Cancelled')
        msg='Success'
    return render(request, "user/my_appointment.html", {'appointments': appointments,'msg': msg})

def user_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_login')
    user = Register.objects.get(id=user_id)
    if request.method == "POST":
        user.name = request.POST.get("name")
        user.email = request.POST.get("email")
        user.phone = request.POST.get("phone")
        password=request.POST.get('password')
        if password:
            user.password=password
        user.save()
        msg = "Profile updated successfully."
        return render(request, "user/profile.html", {'user': user, 'msg': msg})
    return render(request, "user/profile.html", {'user': user})

def appointments(request):
    appointments = Appointment.objects.filter(status__in=['Pending','Approved','Admitted']).order_by('-date', '-time')
    depts = Department.objects.all()
    search_query = request.GET.get('search', '')
    selected_department = request.GET.get('department', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if search_query:
        appointments = appointments.filter(
            Q(user__name__icontains=search_query) |
            Q(user__phone__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(doctor__dname__icontains=search_query)
        )
    if selected_department:
        appointments = appointments.filter(department=selected_department)
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            appointments = appointments.filter(date__gte=start_date)
        except ValueError:
            messages.error(request, 'Invalid start date format.')
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            appointments = appointments.filter(date__lte=end_date)
        except ValueError:
            messages.error(request, 'Invalid end date.')
    active_patients = appointments.values('user').distinct().count()
    today_appointments = Appointment.objects.filter(date=date.today()).count()
    doctors_on_duty = Doctor.objects.all().count()
    return render(request, 'hospital/appointments.html', {'appointments': appointments,'depts': depts,'active_patients': active_patients,'today_appointments': today_appointments,'doctors_on_duty': doctors_on_duty,'search_query': search_query,'selected_department': selected_department,'start_date': start_date,'end_date': end_date,})

def approve_appointment(request, id):
    Appointment.objects.filter(id=id).update(status='Approved')
    return redirect('appointments')

def admit_patient(request, id):
    Appointment.objects.filter(id=id).update(status='Admitted')
    return redirect('appointments')

def discharge_patient(request, id):
    Appointment.objects.filter(id=id).update(status='Discharged')
    return redirect('appointments')

def complete_appointment(request, id):
    Appointment.objects.filter(id=id).update(status='Completed')
    return redirect('appointments')

def patients(request):
    patients = Appointment.objects.exclude(status='Pending')
    depts = Department.objects.all()
    search_query = request.GET.get('search', '')
    selected_department = request.GET.get('department', '')
    selected_status = request.GET.get('status', '')
    if search_query:
        patients = patients.filter(
            Q(user__name__icontains=search_query) |
            Q(user__phone=search_query) |
            Q(user__email__icontains=search_query)
        )
    if selected_department:
        patients = patients.filter(doctor__department=selected_department)
    if selected_status:
        patients = patients.filter(status=selected_status)
    total_patients = Appointment.objects.all().count()
    active_patients = Appointment.objects.filter(date__gte=date.today() - timedelta(days=30)).count()
    admitted_patients = Appointment.objects.filter(status='Admitted').count()
    return render(request, 'hospital/patients.html', {'patients': patients,'depts': depts,'total_patients': total_patients,'active_patients': active_patients,'admitted_patients': admitted_patients,'search_query': search_query,'selected_department': selected_department,'selected_status': selected_status,})

def hospital_profile(request):
    hospital_id = request.session.get('hospital_id')
    if not hospital_id:
        return redirect('hospital_login')
    hospital = Hospital.objects.get(id=hospital_id)
    edit_mode = request.GET.get('edit', 'false').lower() == 'true'
    if request.method == "POST":
        hospital.hname = request.POST.get("hname")
        hospital.address = request.POST.get("address")
        hospital.city = request.POST.get("city")
        hospital.state = request.POST.get("state")
        hospital.zip = request.POST.get("zip")
        hospital.email = request.POST.get("email")
        hospital.phone = request.POST.get("phone")
        password=request.POST.get('password')
        if password:
            hospital.password=password
        hospital.save()
        msg = "Profile updated successfully."
        return render(request, "hospital/profile.html", {'hospital': hospital, 'msg': msg,'edit_mode': edit_mode})
    return render(request, "hospital/profile.html", {'hospital': hospital,'edit_mode': edit_mode})