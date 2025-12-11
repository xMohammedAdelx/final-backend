from django.contrib import admin
from .models import PatientProfile, MedicalRecord, Prescription, PatientDoctorRelationship
# Register your models here.
admin.site.register(PatientProfile)
admin.site.register(MedicalRecord)
admin.site.register(Prescription)
admin.site.register(PatientDoctorRelationship)