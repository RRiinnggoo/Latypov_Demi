from django.contrib import admin

from .models import EnrollmentRequest, LearnerProfile, Program, ServiceReview


admin.site.register(LearnerProfile)
admin.site.register(Program)
admin.site.register(EnrollmentRequest)
admin.site.register(ServiceReview)
 