from django.shortcuts import render
from django.http import HttpResponse
from users.models import QuizResponse
from .utils import *  # Ensure this function is correctly imported

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

