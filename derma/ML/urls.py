from django.urls import path
from .views import *

urlpatterns = [
        path('skincare/',get_skincare,name="get_skincare"),
    # Add other paths here
]
