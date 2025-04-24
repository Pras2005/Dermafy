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
import google.generativeai as genai
from django.conf import settings
import json
from django.shortcuts import render, get_object_or_404
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
#  Initialize Google Gemini API using the key from .env
genai.configure(api_key=settings.GOOGLE_API_KEY)


#  View to Display Skincare Routine in HTML Template
@login_required
def get_skincare(request):
    

    quiz_response = QuizResponse.objects.filter(user=request.user).order_by('-submitted_at').first()
    response = generate_skincare_routine(quiz_response)
    skincare_routine = SkincareRoutine.objects.create(
        user=request.user,
        routine=response["routine"],
        recommended_products=response["recommended_products"]
    )
    return render(request, "skincare.html", {"skincare_data": response})

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
        
        # Get latest quiz sresponse from user
        quiz_response = QuizResponse.objects.filter(user=request.user).latest("submitted_at")
        
        model_path = os.path.join(settings.BASE_DIR, "ML", "yolo_best.pt")
        model = load_model(model_path)
        top5_predictions = classify_image(model, image_path)
        title,severity = top5_predictions[0]
        
        full_report = generate_skin_advice(top5_predictions, user_description, quiz_response)
        summary = generate_skin_summary(top5_predictions)
        report = Report.objects.create(user=request.user, details=full_report, image=image, title=title, severity=severity)
        
        return render(request, "result.html", {
            "summary": summary,
            "full_report": full_report,
            "report": report,  # full Report object
            "created_at": report.date,
            "patient": request.user
        })

    
        

    
    return render(request, "upload.html")


def skincare_list(request):
    routines = SkincareRoutine.objects.filter(user=request.user)
    return render(request, 'skincare_list.html', {'routines': routines})

def show_skincare(request,pk):
    routine = get_object_or_404(SkincareRoutine, user=request.user, pk=pk)
    return render(request,"skincare.html",{"skincare_data": routine})

def report_list(request):
    reports = Report.objects.filter(user=request.user)
    return render(request,"reports.html",{"reports":reports})

# def show_report(request,pk):
#     reports = get_object_or_404(Report,user=request.user,pk=pk) 
#     summary = generate_skin_summary(classify_image(load_model("ML/yolo_best.pt"), reports.image.path))
#     return render(request, "result.html", {"report": summary, "created_at": reports.date, "patient": reports.user,"report_id": reports.id  })

def show_report(request, pk):
    """ This the new show report for not overwriting the existing report - RONIN"""
    report_obj = get_object_or_404(Report, user=request.user, pk=pk)
    summary = generate_skin_summary(classify_image(load_model("ML/yolo_best.pt"), report_obj.image.path))
    
    return render(request, "result.html", {
        "report": report_obj,  
        "summary": summary,
        "created_at": report_obj.date,
        "patient": report_obj.user
    })



def download_report(request, pk):
    report = get_object_or_404(Report, user=request.user, pk=pk)


    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report.pk}.pdf"'

    
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []


    elements.append(Paragraph(f"Skin Condition Report - {report.title if report.title else 'Untitled'}", styles["Title"]))
    elements.append(Spacer(1, 12))

    
    elements.append(Paragraph(f"<b>Date:</b> {report.date}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Severity:</b> {report.severity if report.severity else 'N/A'}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    
    elements.append(Paragraph("<b>AI Analysis:</b>", styles["Heading2"]))
    
    
    details = report.details.replace("\n", "<br/>")  
    for paragraph in details.split("<br/>"):  
        elements.append(Paragraph(paragraph, styles["Normal"]))
        elements.append(Spacer(1, 6))  

    
    elements.append(PageBreak())

    if report.image:
        image_path = report.image.path
        if os.path.exists(image_path):
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("<b>Attached Image:</b>", styles["Heading2"]))
            elements.append(Spacer(1, 12))
            elements.append(Image(image_path, width=400, height=250))  # Adjust image size
            elements.append(Spacer(1, 12))

    doc.build(elements)

    return response
