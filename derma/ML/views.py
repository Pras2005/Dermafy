from django.shortcuts import render
from django.http import HttpResponse
from users.models import *
from .utils import *  # Ensure this function is correctly imported
from django.contrib.auth.decorators import login_required
import os
def get_skincare(request):
    try:
        latest_response = QuizResponse.objects.latest("submitted_at")
        ai_response = generate_skincare_routine(latest_response)

        if "error" in ai_response:
            return HttpResponse(f"<h1>Error:</h1><p>{ai_response['error']}</p>", status=500)

        routine = "<h2>Skincare Routine</h2><ul>"
        for step in ai_response["routine"]:
            routine += f"<li>{step}</li>"
        routine += "</ul>"

        product_list = ai_response["recommended_products"]
        # Assuming scrape_products is a function that fetches recommended product details
        scraped_products = scrape_products(product_list)

        products = "<h2>Recommended Products</h2><ul>"
        for product in scraped_products:
            products += f"<li>{product}</li>"
        products += "</ul>"

        return HttpResponse(f"<html><body>{routine}{products}</body></html>")

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

