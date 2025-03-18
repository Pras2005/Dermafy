import json
from django.conf import settings
import google.generativeai as genai
from google.generativeai import GenerativeModel
from ultralytics import YOLO
import cv2
import numpy as np
import markdown
# Configure Google Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_skincare_routine(quiz_response):
    sys_instruct = (
        "You are an expert dermatologist specializing in personalized skincare recommendations. "
        "Your responses should be precise, structured, and informative."
    )
    
    prompt = f"""
    Based on the following user skin profile, generate:
    1. A detailed, step-by-step skincare routine.
    2. A list of recommended skincare products (brand-neutral) suitable for this skin type.
    
    User Skin Profile:
    - Primary Skin Concern: {quiz_response.primary_skin_concern}
    - Skin Type: {quiz_response.skin_type}
    - Breakout Frequency: {quiz_response.breakout_frequency}
    - Reaction to Skincare: {quiz_response.reaction_to_skincare}
    - Redness & Inflammation: {quiz_response.redness_inflammation}
    - Sunscreen Usage: {quiz_response.sunscreen_usage}
    - Skin Conditions: {quiz_response.skin_conditions}
    - After Washing Skin Feel: {quiz_response.after_washing_skin_feel}
    - Water Intake: {quiz_response.water_intake}
    - Dark Spots & Pigmentation: {quiz_response.dark_spots_pigmentation}
    - Visible Pores: {quiz_response.visible_pores}
    - Exfoliation Frequency: {quiz_response.exfoliation_frequency}
    - Fine Lines & Wrinkles: {quiz_response.fine_lines_wrinkles}
    - Dairy & Processed Food Intake: {quiz_response.dairy_processed_food_intake}
    - Skincare Routine: {quiz_response.skincare_routine}
    
    Format the output as a JSON object with two keys:
    - "routine": A list of steps for skincare.
    - "recommended_products": A list of product types and key ingredients to look for.
    
    IMPORTANT: Your response must be valid JSON only, with no additional text or formatting.
    """
    
    # Create the model with system instructions
    model = GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=sys_instruct
    )
    
    # Generate content with explicit JSON request
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "application/json"  # Request JSON specifically
        }
    )
    
    # Debugging
    print("Raw API Response:", response)
    print("Response text:", response.text)
    
    try:
        # Parse the JSON response
        structured_response = json.loads(response.text)
        return structured_response
    except json.JSONDecodeError as e:
        # Handle failed JSON parsing with better debugging
        print(f"JSON Decode Error: {e}")
        print(f"Response content type: {type(response.text)}")
        print(f"Response content: {response.text[:500]}...")  # Print first 500 chars
        
        # Attempt to manually extract JSON if possible
        try:
            # Try to find JSON content if it's embedded in other text
            import re
            json_match = re.search(r'(\{.*\})', response.text, re.DOTALL)
            if json_match:
                extracted_json = json_match.group(1)
                return json.loads(extracted_json)
            else:
                # If no JSON found, create a fallback response
                return {
                    "routine": ["Cleanse", "Moisturize", "Sun Protection"],
                    "recommended_products": [
                        "Gentle Cleanser", 
                        "Moisturizer appropriate for skin type", 
                        "Broad-spectrum SPF 30+ sunscreen"
                    ],
                    "error_note": f"Generated fallback due to parsing error: {str(e)}"
                }
        except Exception as nested_e:
            return {"error": f"Failed to parse AI response: {str(e)}. Additional error: {str(nested_e)}"}
    except (AttributeError, IndexError) as e:
        return {"error": f"Failed to access AI response data: {str(e)}"}

def scrape_products(product_list):
    
    formatted_products = []
    
    for product in product_list:
        if isinstance(product, dict) and "type" in product and "ingredients" in product:
            formatted_products.append(
                f"{product['type']} - Look for ingredients: {', '.join(product['ingredients'])}"
            )
        elif isinstance(product, str):
            formatted_products.append(product)
        else:
            formatted_products.append(f"Recommended: {str(product)}")
            
    return formatted_products

def load_model(model_path):
    return YOLO(model_path) 

def classify_image(model, image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    results = model(image_path)
    
    top5_indices = results[0].probs.top5
    top5_confidences = results[0].probs.data[top5_indices]  
    
    top5_classes = [(model.names[idx], conf.item()) for idx, conf in zip(top5_indices, top5_confidences)]
    
    return top5_classes


def generate_skin_advice(model_response, user_description, quiz_response):
    """
    Generates a structured Markdown report based on AI skin condition classification, user input, and quiz response.
    
    Returns:
        Markdown text formatted for conversion into an HTML report.
    """
    
    sys_instruct = (
        "You are an expert dermatologist specializing in detailed skin condition analysis. "
        "Your responses should be precise, medically accurate, and well-structured. Format the output in Markdown."
        "your response should avoid mention of ai and technical jargon and should be catered towards a layman"
    )

    # Format AI model's predictions for better readability
    formatted_conditions = "\n".join(
        [f"- **{condition}** (Confidence: {confidence:.2f})" for condition, confidence in model_response]
    )

    # Format user-provided skin profile details
    formatted_skin_profile = f"""
    - **Primary Skin Concern**: {quiz_response.primary_skin_concern}
    - **Skin Type**: {quiz_response.skin_type}
    - **Breakout Frequency**: {quiz_response.breakout_frequency}
    - **Reaction to Skincare**: {quiz_response.reaction_to_skincare}
    - **Redness & Inflammation**: {quiz_response.redness_inflammation}
    - **Sunscreen Usage**: {quiz_response.sunscreen_usage}
    - **Skin Conditions**: {quiz_response.skin_conditions}
    - **After Washing Skin Feel**: {quiz_response.after_washing_skin_feel}
    - **Water Intake**: {quiz_response.water_intake}
    - **Dark Spots & Pigmentation**: {quiz_response.dark_spots_pigmentation}
    - **Visible Pores**: {quiz_response.visible_pores}
    - **Exfoliation Frequency**: {quiz_response.exfoliation_frequency}
    - **Fine Lines & Wrinkles**: {quiz_response.fine_lines_wrinkles}
    - **Dairy & Processed Food Intake**: {quiz_response.dairy_processed_food_intake}
    - **Current Skincare Routine**: {quiz_response.skincare_routine}
    """

    # Construct improved AI prompt for better response structuring
    prompt = f"""
    # **Comprehensive Skin Condition Report**
    
        ---
    
    ## **1. AI Diagnosis Summary**
    <strong>AI-Detected Skin Conditions:</strong>
    
    {formatted_conditions}
    
    <strong>User-Provided Skin Description:</strong>  
    {user_description if user_description.strip() else "<em>No user description provided.</em>"}
    
    <strong>User Skin Profile:</strong>  
    {formatted_skin_profile}
    
    ---
    
    ## **2. Most Likely Condition & Severity Assessment**
    - **Condition:** _(To be inferred from AI analysis & user description)_
    - **Severity Rating:** _Mild / Moderate / Severe (based on AI assessment)_
    
    ## **3. Causes and Contributing Factors**
    - 🔹 **UV Radiation Exposure:** Prolonged sun exposure without protection.
    - 🔹 **Skin Type Sensitivity:** Certain skin types are more prone to irritation and hyperpigmentation.
    - 🔹 **Hormonal Influence:** Conditions like acne and melasma may be triggered by hormonal changes.
    - 🔹 **Lifestyle & Diet:** Processed foods, dairy intake, and hydration levels affect skin health.
    
    ## **4. Personalized Skincare Routine**
    
    **Morning Routine:**
    1️⃣ <strong>Gentle Cleanser:</strong> Removes dirt & excess oil without stripping moisture.
    2️⃣ <strong>Antioxidant Serum:</strong> Vitamin C to protect against environmental damage.
    3️⃣ <strong>Broad-Spectrum Sunscreen (SPF 50+):</strong> Essential to prevent UV damage.

    **Evening Routine:**
    1️⃣ <strong>Gentle Cleanser:</strong> Removes makeup, pollutants, and excess oil.
    2️⃣ <strong>(Optional) Gentle Exfoliant (1-2x per week):</strong> Low-percentage lactic acid for mild exfoliation.
    3️⃣ <strong>Moisturizer:</strong> Hydrating and non-comedogenic to lock in moisture.

    ## **5. Recommended Skincare Products (Brand-Neutral)**
    🧴 <strong>Cleanser:</strong> Hydrating, fragrance-free options (e.g., Cerave, Cetaphil).  
    💧 <strong>Moisturizer:</strong> Lightweight, oil-free hydration (e.g., Neutrogena Hydro Boost).  
    🌞 <strong>Sunscreen:</strong> Mineral SPF 50+ (e.g., EltaMD, La Roche-Posay).  

    ---
    
    ## **6. When to Seek Medical Advice**
    ❗ <strong>Immediate consultation required if:</strong>
    - The condition worsens or spreads rapidly.
    - Any lesion changes shape, size, or starts bleeding.
    - Skin irritation persists despite skincare adjustments.

    <em>**Disclaimer:** This AI-generated report is for informational purposes only and should not be considered a substitute for professional medical advice.</em>
    """

    # Generate AI response
    model = GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=sys_instruct
    )
    
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "text/plain"  # Markdown-compatible response
        }
    )
    
    return response.text



import markdown
from ultralytics import YOLO

def get_skin_diagnosis(model_path, image_path, user_description, skin_profile):
    """
    Generates a structured skin diagnosis report in HTML format.
    
    Args:
        model_path (str): Path to the trained YOLO model.
        image_path (str): Path to the input image for classification.
        user_description (str): User-provided text describing skin concerns.
        skin_profile (QuizResponse): User's detailed skin profile.

    Returns:
        str: HTML-formatted diagnosis report with key highlights.
    """
    # Load model
    model = load_model(model_path)

    # Get classification results
    top5_predictions = classify_image(model, image_path)

    # Generate markdown report
    markdown_report = generate_skin_advice(top5_predictions, user_description, skin_profile)

    # Convert markdown to HTML with strong emphasis on headers
    html_report = markdown.markdown(markdown_report, extensions=["extra"])

    # Wrap report in strong tags for better emphasis
    formatted_html = f"""
    <div class="report-container">
        <h2><strong>Skin Analysis Report</strong></h2>
        <div class="report-content"><strong>{html_report}</strong></div>
    </div>
    """
    
    return formatted_html

