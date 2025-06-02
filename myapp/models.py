from django.db import models

class Register(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100)
    rights= models.CharField(max_length=20, default='User')
    def __str__(self):
        return self.name

class Hospital(models.Model):
    hname= models.CharField(max_length=100)
    hid= models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=200)
    city= models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip= models.CharField(max_length=10)
    email= models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100)
    rights= models.CharField(max_length=20, default='New Hospital')
    def __str__(self):
        return self.hname

class Department(models.Model):
    name = models.CharField(max_length=100)
    head= models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments')
    def __str__(self):
        return self.name
    
class Doctor(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors',null=True)
    dname= models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    qualification = models.CharField(max_length=100)
    department=models.CharField(max_length=100)
    email= models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True,null=True, blank=True)
    image= models.ImageField(upload_to='doctor_images/', null=True, blank=True)
    def __str__(self):
        return self.dname
    
class Appointment(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time = models.CharField(max_length=40)
    reason= models.TextField(null=True)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Appointment with {self.doctor.dname} on {self.date} at {self.time}"