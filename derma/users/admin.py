from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(CUSTOMUSER)
admin.site.register(QuizResponse)
admin.site.register(Report)
admin.site.register(SkincareRoutine)
# Register your models here.
