from django.urls import path,include
from .views import *

urlpatterns =[
        path('',home,name='home'),
        path('user_login/',user_login, name='user_login'),
        path('user_logout/',user_logout,name='user_logout'),
        path('user_signup',user_signup,name='user_signup'),
        path("quiz/", submit_quiz, name="submit_quiz"),
        path('dashboard/', dashboard, name='dashboard'),
        path('reports/', reports, name='reports'),
        path('skincare/', skincare, name='skincare'),
        path('consult/', consult, name='consult'),
        path('dashboard/', login_required(dashboard), name='dashboard'),
        ]
