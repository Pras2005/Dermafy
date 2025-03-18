from django.urls import path
from .views import *

urlpatterns = [
        path('skincare/', skincare, name='skincare'),
        path('skincare_report/', skincare_report, name='skincare_report'),
        path('generate_skincare_report/', get_skincare, name='generate_skincare_report'),
    ]
