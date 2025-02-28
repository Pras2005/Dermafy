from django.urls import path,include
from .views import *
from .views import home, user_login, user_logout, user_signup,edit_profile, delete_profile

urlpatterns =[
        path('',home,name='home'),
        path('user_login/',user_login, name='user_login'),
        path('user_logout/',user_logout,name='user_logout'),
        path('user_signup',user_signup,name='user_signup'),
        path("quiz/", submit_quiz, name="submit_quiz"),
        path('edit-profile/', edit_profile, name='edit_profile'),
        path('delete-profile/', delete_profile, name='delete_profile'),

        ]


   
    