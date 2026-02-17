from django.contrib import admin
from .models import (
    DentistProfile,
    Testimonial,
    #Service,
    Gallery,
    Appointment,
)

# Register your models here.
admin.site.register(DentistProfile)
#admin.site.register(Service)
admin.site.register(Gallery)
admin.site.register(Appointment)
admin.site.register(Testimonial)