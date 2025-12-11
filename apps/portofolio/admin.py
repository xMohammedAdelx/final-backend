from django.contrib import admin
from .models import (
    DentistProfile,
    Project,
    FAQ,
    Certification,
    Education,
    Experience,
    Awards,
    Testimonial,
    SocialMedia,
    Skill,
    Service,
    Article,
    Gallery,
    Appointment,
)

# Register your models here.
admin.site.register(DentistProfile)
admin.site.register(Project)
admin.site.register(Gallery)
admin.site.register(FAQ)
admin.site.register(Certification)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Awards)
admin.site.register(Testimonial)
admin.site.register(SocialMedia)
admin.site.register(Skill)
admin.site.register(Service)
admin.site.register(Article)
admin.site.register(Appointment)
