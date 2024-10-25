from django.contrib import admin
from .models import Signup_patient
from .models import Signup_doc


# Register your models here.


class PatientAdmin(admin.ModelAdmin):
    list_display = ("username", "f_name", "l_name")


class DoctorAdmin(admin.ModelAdmin):
    list_display = ("username", "f_name", "l_name")


admin.site.register(Signup_patient, PatientAdmin)
admin.site.register(Signup_doc, DoctorAdmin)
