import secrets
import time
from django.core.mail import send_mail
from django.conf import settings
import re

OTP_EXPIRY_SECONDS = 300  
OTP_MAX_ATTEMPTS = 3  

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def store_otp(request, email, otp):
    request.session['reset_otp'] = otp
    request.session['reset_otp_time'] = int(time.time())
    request.session['reset_otp_attempts'] = 0
    request.session['user_email'] = email

def get_otp(request):
    return (
        request.session.get('reset_otp'),
        request.session.get('reset_otp_time'),
        request.session.get('reset_otp_attempts', 0),
        request.session.get('user_email')
    )

def validate_otp(request, user_otp):
    stored_otp, otp_time, attempts, email = get_otp(request)

    if not stored_otp or not otp_time:
        return False, "OTP expired or invalid. Request a new OTP."

    if int(time.time()) - otp_time > OTP_EXPIRY_SECONDS:
        clear_otp(request)
        return False, "OTP expired. Request a new one."

    if attempts >= OTP_MAX_ATTEMPTS:
        return False, "Too many incorrect attempts. Try again later."

    if str(user_otp) == str(stored_otp):
        clear_otp(request)  # OTP correct → clear session
        return True, "OTP verified successfully.", email

    request.session["reset_otp_attempts"] = attempts + 1  # Increment attempt count
    return False, "Invalid OTP. Try again.", None

def clear_otp(request):
    request.session.pop("reset_otp", None)
    request.session.pop("reset_otp_time", None)
    request.session.pop("reset_otp_attempts", None)
    

def send_otp_mail(request, email):
    otp = generate_otp()
    store_otp(request, email, otp)  # Store OTP before sending
    subject = "Password Reset OTP"
    message = f"Your OTP for resetting your password is: {otp}. It is valid for 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


def is_valid_password(password):
    """
    Validates password:
    - At least 8 characters long
    - At least one special character
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character."
    
    return None  # No errors, password is valid
