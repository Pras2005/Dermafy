from django.urls import path,include
from .views import *

urlpatterns =[
        path('',home,name='home'),
        path('user_login/',user_login, name='user_login'),
        path('user_logout/',user_logout,name='user_logout'),
        path('user_signup',user_signup,name='user_signup'),
        path('dashboard/', dashboard, name='dashboard'),
        path('reports/', reports, name='reports'),
        path('skincare/', skincare, name='skincare'),
        path('consult/', consult, name='consult'),
        path('dashboard/', dashboard, name='dashboard'),
        path("submit_quiz/", submit_quiz, name="submit_quiz"),  # Add this line
        path('profile/add/', add_profile, name='add_profile'),
        path('profile/<int:pk>/update/', update_profile, name='update_profile'),
        path('profile/<int:pk>/delete/', delete_profile, name='delete_profile'),
        path('profile/<int:pk>/', profile_detail, name='profile_detail'),
        path("request-reset-otp/", request_reset_otp, name="request_reset_otp"),
        path("verify-reset-otp/", verify_reset_otp, name="verify_reset_otp"),
        path("reset-password/", reset_password, name="reset_password"),
        path('connect-google/', connect_google, name='connect_google'),
        #path('scan/',scan,name='scan'),
        
        ]
