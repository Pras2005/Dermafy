from django.contrib.auth import authenticate, login
from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "index.html")

def user_login(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dash_board")#dasboard funtion write the blo0ody thing prayag
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
        return redirect('submit_quiz') # quiz_view will be the view of quizes after signup

    return render(request,"sign_up.html")

# Changes by RONIN
@login_required
def submit_quiz(request):
    if request.method == "POST":
        QuizResponse.objects.create(
            user=request.user,
            primary_skin_concern=request.POST.get("primary_skin_concern"),
            skin_type=request.POST.get("skin_type"),
            breakout_frequency=request.POST.get("breakout_frequency"),
            reaction_to_skincare=request.POST.get("reaction_to_skincare"),
            redness_inflammation=request.POST.get("redness_inflammation"),
            sunscreen_usage=request.POST.get("sunscreen_usage"),
            skin_conditions=request.POST.get("skin_conditions"),
            after_washing_skin_feel=request.POST.get("after_washing_skin_feel"),
            water_intake=request.POST.get("water_intake"),
            dark_spots_pigmentation=request.POST.get("dark_spots_pigmentation"),
            visible_pores=request.POST.get("visible_pores"),
            exfoliation_frequency=request.POST.get("exfoliation_frequency"),
            fine_lines_wrinkles=request.POST.get("fine_lines_wrinkles"),
            dairy_processed_food_intake=request.POST.get("dairy_processed_food_intake"),
            skincare_routine=request.POST.get("skincare_routine"),
        )
        messages.success(request, "Quiz submitted successfully!")
        return redirect("quiz_report")  # Redirect to a report or homepage

    return render(request, "quiz_form.html")
#

# Dashboard -RONIN
@login_required
def dashboard(request):
    user = request.user  # Now this will never be AnonymousUser
    reports = Report.objects.filter(user=user).order_by('-date')
    skin_progress = SkinProgress.objects.filter(user=user).order_by('-date')

    context = {
        'reports': reports,
        'skin_progress': skin_progress,
    }
    return render(request, 'dashboard.html', context)


def reports(request):
    all_reports = Report.objects.filter(user=request.user).order_by('-date')
    return render(request, 'reports.html', {'all_reports': all_reports})

def skincare(request):
    return render(request, 'skincare.html')

def consult(request):
    return render(request, 'consult.html')

#