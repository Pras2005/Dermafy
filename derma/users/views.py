from django.contrib.auth import authenticate, login
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import logout, login

# Create your views here.

def home(request):
    return render(request, "index.html")

def user_login(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def user_logout(request):
    logout(request)
    return redirect("home") #Redirect to login page

def user_signup(request):
    if request.method =="POST":
        username = request.POST['username']
        password =request.POST['password1']
        password2=request.POST['password2']
        email = request.POST['email']
        phone_no = request.POST["phone_no"]


        if password != password2:
            return render("sign_up.html",{"error":"password do not match"})

        if CUSTOMUSER.objects.filter(email=email).exists():
            return render("sign_up.html",{"error":"email already exists"})

        user = CUSTOMUSER.objects.create_user(
            username=username,
            email=email,
            phone_no=phone_no,
            password=password
        )

        login(request,user)
        return redirect('quiz_view') # quiz_view will be the view of quizes after signup

    return render(request,"sign_up.html")
