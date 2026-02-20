from django.contrib import admin
from .models import PatientProfile, MedicalRecord, AIResult, MedicalAttachment, PatientDoctorRelationship

admin.site.register(PatientProfile)
admin.site.register(MedicalRecord)
admin.site.register(AIResult)
admin.site.register(MedicalAttachment)
admin.site.register(PatientDoctorRelationship)