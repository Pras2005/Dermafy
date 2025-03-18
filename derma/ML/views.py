from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from users.models import QuizResponse
from .models import SkincareRoutine
from .utils import generate_skincare_routine, scrape_products

import google.generativeai as genai
from django.conf import settings
import json

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
