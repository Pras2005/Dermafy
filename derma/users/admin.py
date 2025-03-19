from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(CUSTOMUSER)
admin.site.register(QuizResponse)
admin.site.register(Report)
# Register your models here.
