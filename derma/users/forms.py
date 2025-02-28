from django import forms
from .models import *



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = PROFILE
        fields = ["image", "name", "age", "gender"]

