from django.contrib import admin
from .models import Student, Department, Recruiter, Product, Service, Job, NoticeType, Notice, CallbackRequest, Applications, Admin_Details

# Register your models here.
# admin.site.register(ADMIN)
# admin.site.register(STUDENT)

admin.site.register(Student)
admin.site.register(Department)
admin.site.register(Recruiter)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(Job)
admin.site.register(NoticeType)
admin.site.register(Notice)
admin.site.register(CallbackRequest)
admin.site.register(Applications)
admin.site.register(Admin_Details)
