from django.urls import path
from .views import *

urlpatterns = [
        path('skincare/',get_skincare,name="get_skincare"),
        path('report',scan_img,name='scan'),
        path('skincare_list/', skincare_list, name='skincare'),
        path('show_skincare/<int:pk>',show_skincare,name="show_skincare"),
        path('reports/', report_list, name='report_list'),  
        path('reports/<int:pk>/', show_report, name='show_report'),  
        path('reports/<int:pk>/download/', download_report, name='download_report'),  

            ]
