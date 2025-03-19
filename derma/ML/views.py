from django.shortcuts import render
from django.http import HttpResponse
from users.models import *
from .utils import *  # Ensure this function is correctly imported
from django.contrib.auth.decorators import login_required
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from users.models import QuizResponse
from .models import SkincareRoutine
from .utils import generate_skincare_routine, scrape_products, get_skin_diagnosis
import uuid
import google.generativeai as genai
from django.conf import settings
import json

def skin_diagnosis_view(request): # Recent change ronin
    # Replace these with your actual logic to obtain the model path, image path, user description, and skin profile
    model_path = "path/to/your/model.pt"
    image_path = "path/to/uploaded/image.jpg"
    user_description = request.POST.get("description", "")
    skin_profile = ...  # Retrieve the QuizResponse or similar instance
    
    # Get the context for the report
    context = get_skin_diagnosis(model_path, image_path, user_description, skin_profile)
    
    # Render the result.html template with the context
    return render(request, "result.html", context)

# ✅ Initialize Google Gemini API using the key from .env
genai.configure(api_key=settings.GOOGLE_API_KEY)

# ✅ Endpoint for AI-based Skincare Recommendations (JSON Response)
def get_skincare_recommendations(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            report_text = data.get("report_text")

            if not report_text:
                return JsonResponse({"status": "error", "message": "Report text is required."}, status=400)

            # ✅ Initialize Gemini Model
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(report_text)
            ai_response = response.text

            return JsonResponse({"status": "success", "data": ai_response})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ✅ View to Display Skincare Routine in HTML Template
@login_required
def get_skincare(request):
    try:
        latest_response = QuizResponse.objects.latest("submitted_at")
        ai_response = generate_skincare_routine(latest_response)

        if "error" in ai_response:
            return HttpResponse(f"<h1>Error:</h1><p>{ai_response['error']}</p>", status=500)

        # Save routine to database
        routine, created = SkincareRoutine.objects.get_or_create(
            user=request.user,
            defaults={
                "routine": ai_response["routine"],
                "recommended_products": ai_response["recommended_products"],
            }
        )

        # Format the skincare routine properly
        formatted_routine = [
            {
                "step": step.get("step", ""),
                "name": step.get("name", ""),
                "description": step.get("description", ""),
                "frequency": step.get("frequency", "")
            }
            for step in ai_response["routine"]
        ]

        # Format the product recommendations properly
        formatted_products = [
            {
                "type": product.get("product_type", ""),
                "key_ingredients": ", ".join(product.get("key_ingredients", [])),
                "avoid": ", ".join(product.get("avoid", []))
            }
            for product in ai_response["recommended_products"]
        ]

        context = {
            "routine": formatted_routine,
            "products": formatted_products,
            "created_at": routine.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return render(request, 'skincare.html', context)

    except QuizResponse.DoesNotExist:
        return HttpResponse("<h1>Error:</h1><p>No quiz responses found.</p>", status=404)
    except Exception as e:
        return HttpResponse(f"<h1>Unexpected Error:</h1><p>{str(e)}</p>", status=500)



@login_required
def scan_img(request):
    if request.method == "POST" and request.FILES.get("image"):
        user_description = request.POST.get("description", "")
        image = request.FILES["image"]
        
        # Save uploaded image
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        # Save uploaded image
        image_path = os.path.join(upload_dir, image.name)
        with open(image_path, "wb+") as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        # Get latest quiz response from user
        quiz_response = QuizResponse.objects.filter(user=request.user).latest("submitted_at")
        
        model_path = os.path.join(settings.BASE_DIR, "ML", "yolo_best.pt")
        model = load_model(model_path)
        top5_predictions = classify_image(model, image_path)
        
        html_report = generate_skin_advice(top5_predictions, user_description, quiz_response)
        
        # Store report in database
        report = Report.objects.create(user=request.user, details=html_report, image=image)
        
        return render(request, "result.html", {"report": html_report})
    
    return render(request, "upload.html")


def skincare(request):
    routines = SkincareRoutine.objects.all()
    return render(request, 'skincare.html', {'routines': routines})



def generate_skincare_report(request):
    # Logic to create or refresh the skincare report ( NOT ADDED YET BUT WILL WORK ON IT -RONIN )
    return redirect('skincare_report')

@login_required
def skincare_report(request):
    try:
        # Fetch the latest skincare routine for the user
        routine = SkincareRoutine.objects.filter(user=request.user).latest('created_at')

        context = {
            'routine': json.loads(routine.routine),
            'products': json.loads(routine.recommended_products),
            'created_at': routine.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return render(request, 'skincare_report.html', context)
    except SkincareRoutine.DoesNotExist:
        return HttpResponse("<h1>Error:</h1><p>No skincare report found.</p>", status=404)
    except Exception as e:
        return HttpResponse(f"<h1>Unexpected Error:</h1><p>{str(e)}</p>", status=500)

def save_uploaded_file(f): # -RONIN
    """Save the uploaded file and return its path."""
    file_name = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return file_path

def skin_scan_view(request): # RONIN
    if request.method == "POST":
        image_file = request.FILES.get("image")
        user_description = request.POST.get("description", "")
        body_part = request.POST.get("bodyPart", "")
        
        if not image_file:
            return render(request, "upload.html", {"error": "Please upload an image."})
        
        # Save the image and get its file path
        image_path = save_uploaded_file(image_file)
        
        # Create a dummy quiz response object; extend this if your form collects more data.
        quiz_response = QuizResponse()
        
        # Define the path to your YOLO model (adjust as necessary)
        model_path = os.path.join(settings.BASE_DIR, "path/to/yolo_model.pt")
        
        # Call the utility function to generate the HTML report
        report_html = get_skin_diagnosis(model_path, image_path, user_description, quiz_response)
        
        # Render a report template (report.html) passing the report HTML
        return render(request, "tempreport.html", {"report": report_html})
    
    # For GET requests, simply render the upload page
    return render(request, "upload.html")