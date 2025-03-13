from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib.auth import authenticate, login, logout, get_backends
from .models import *
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .utils import *
from django.urls import reverse
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


def home(request):
    return render(request, "index.html")



def user_login(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")#dasboard funtion write the blo0ody thing prayag
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("home") #Redirect to login page

def user_signup(request):
    if request.method == "POST":
        print(request.POST)  # Debugging: Check if data is correctly received

        username = request.POST.get('username', '')
        password = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        email = request.POST.get('email', '')
        phone_no = request.POST.get("phone_no", '')

        if password != password2:
            return render(request,"sign_up.html", {"error": "Passwords do not match"})

        if CUSTOMUSER.objects.filter(email=email).exists():
            return render(request,"sign_up.html", {"error": "Email already exists"})

        try:
            user = CUSTOMUSER.objects.create_user(username=username, email=email, password=password)
            user.phone_no = phone_no  # If phone_no isn't part of create_user()
            user.save()
        except Exception as e: # Debugging
            return render(request, "sign_up.html", {"error": "User creation failed. Try again."})
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        return redirect('connect_google')  # Ensure this matches `urls.py`

    return render(request, "sign_up.html")

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
        return redirect("dashboard")  # Redirect to a report or homepage

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

@login_required
def add_profile(request):
    if request.method == "POST":
        image = request.FILES.get('image')
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')

        profile = PROFILE.objects.create(
            user=request.user,
            image=image,
            name=name,
            age=age,
            gender=gender
        )
        return redirect('profile_detail', pk=profile.pk)  # Redirect to profile detail view

    return render(request, 'profile_form.html')

@login_required
def update_profile(request, pk):
    profile = get_object_or_404(PROFILE, pk=pk, user=request.user)  # Ensure users can only edit their own profile

    if request.method == "POST":
        profile.image = request.FILES.get('image', profile.image)
        profile.name = request.POST.get('name', profile.name)
        profile.age = request.POST.get('age', profile.age)
        profile.gender = request.POST.get('gender', profile.gender)
        profile.save()

        return redirect('profile_detail', pk=profile.pk)

    return render(request, 'profile_form.html', {'profile': profile})

@login_required
def delete_profile(request, pk):
    profile = get_object_or_404(PROFILE, pk=pk, user=request.user)

    if request.method == "POST":
        profile.delete()
        return redirect('home')  # Redirect to home or profile list

    return render(request, 'profile_confirm_delete.html', {'profile': profile})

@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(PROFILE, pk=pk)
    return render(request, 'profile_detail.html', {'profile': profile})

def request_reset_otp(request):
    """View to request an OTP for password reset"""
    if request.method == "POST":
        email = request.POST.get("email")
        send_otp_mail(request, email)
        messages.success(request, "An OTP has been sent to your email.")
        return redirect("verify_reset_otp")
    
    return render(request, "request_reset_otp.html")

def verify_reset_otp(request):
    """View to verify the OTP"""
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        is_valid, message, email = validate_otp(request, user_otp)

        if is_valid:
            messages.success(request, "OTP verified. You may now reset your password.")
            return redirect("reset_password")  # Redirect to password reset page

        messages.error(request, message)  # Show error message

    return render(request, "verify_reset_otp.html")

def reset_password(request):
    """View to reset password after successful OTP verification"""
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        email = request.session.get("user_email")

        if not email:
            messages.error(request, "Session expired. Request a new OTP.")
            return redirect("request_reset_otp")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reset_password")

        # Reset the user's password
        
        user = CUSTOMUSER.objects.filter(email=email).first()
        if user:
            user.set_password(new_password)
            user.save()
            clear_otp(request)  # Clear session after reset
            messages.success(request, "Password reset successfully. You can now log in.")
            return redirect("user_login")

        messages.error(request, "User not found.")
    
    return render(request, "reset_password.html")

def connect_google(request):
    if request.method == "POST":
        if "skip" in request.POST:
            return redirect("submit_quiz")  # Redirect to quiz if skipped
        return redirect(reverse('socialaccount_login') + "?process=connect&next=" + reverse("submit_quiz"))
 

    return render(request, "connect_google.html")
def scan(request):
    return render(request,"scan.html")
