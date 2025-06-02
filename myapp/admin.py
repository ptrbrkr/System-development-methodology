from django.contrib import admin
from .models import *

admin.site.register(Register)
admin.site.register(Hospital)
admin.site.register(Department)
admin.site.register(Doctor)
admin.site.register(Appointment)