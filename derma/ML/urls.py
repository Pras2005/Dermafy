from django.urls import path
from .views import *

urlpatterns = [
        path('skincare/',get_skincare,name="get_skincare"),
        path('report',scan_img,name='scan'),
    # Add other paths here
]
