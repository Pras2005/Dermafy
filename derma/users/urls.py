from django.urls import path,include
from .views import *

urlpatterns =[
        path('',home,name='home'),
        path('user_login/',user_login, name='user_login'),
        path('user_logout/',user_logout,name='user_logout'),
        path('user_signup',user_signup,name='user_signup'),
        ]
