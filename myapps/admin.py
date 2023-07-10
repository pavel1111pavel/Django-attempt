from django.contrib import admin
from myapps.models import CustomUser, Teacher, Student

admin.site.register(CustomUser)
admin.site.register(Teacher)
admin.site.register(Student)

# Register your models here.
