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

import re

def add_newlines_before_all_caps(text):
    # This regex matches words that consist of 2 or more capital letters.
    pattern = re.compile(r'(?<!\n)(\b[A-Z]{2,}\b)')
    # Insert a newline before each all-caps word
    new_text = pattern.sub(r'\n\1', text)
    return new_text




def clean_response(text):
    """
    Cleans AI-generated text by:
    - Removing markdown characters (*, #, _)
    - Adding extra newlines for readability (optional).
    """
    # Remove any asterisks, hashes, underscores
    text = re.sub(r'[\*\#\_]', '', text)
    
    # Optionally, ensure paragraph spacing
    text = re.sub(r'\n+', '\n\n', text)

    text=add_newlines_before_all_caps(text)
    
    # Strip leading/trailing whitespace
    return text.strip()

def generate_skin_advice(model_response, user_description, quiz_response):
    """
    Generates a structured skin analysis report in clear, readable format.
    """
    # Updated system instruction: only formatting instructions are changed.
    sys_instruct = (
        "You are an expert dermatologist. "
        "Provide a detailed, structured skin condition report in plain English. "
        "Ensure readability with clear sections, new lines, and spacing. "
        "Do NOT use special characters like *, #, or _ for formatting. "
        "Each section should be clearly separated with a title on its own line, mimicking the structure of a skincare routine report. "
        "For example, include sections like 'Routine Steps:', 'Recommended Products:', and 'AI Analysis:'. "
        "Additionally, whenever a word contains two or more consecutive capital letters, insert a newline before and after that word."
    )

    formatted_conditions = "\n".join(
        [f"- {condition} (Confidence: {confidence:.2f})" for condition, confidence in model_response]
    )

    formatted_skin_profile = f"""
Primary Skin Concern: {quiz_response.primary_skin_concern}

Skin Type: {quiz_response.skin_type}

Breakout Frequency: {quiz_response.breakout_frequency}

Reaction to Skincare: {quiz_response.reaction_to_skincare}

Redness & Inflammation: {quiz_response.redness_inflammation}

Sunscreen Usage: {quiz_response.sunscreen_usage}

Skin Conditions: {quiz_response.skin_conditions}

After Washing Skin Feel: {quiz_response.after_washing_skin_feel}

Water Intake: {quiz_response.water_intake}

Dark Spots & Pigmentation: {quiz_response.dark_spots_pigmentation}

Visible Pores: {quiz_response.visible_pores}

Exfoliation Frequency: {quiz_response.exfoliation_frequency}

Fine Lines & Wrinkles: {quiz_response.fine_lines_wrinkles}

Dairy & Processed Food Intake: {quiz_response.dairy_processed_food_intake}

Current Skincare Routine: {quiz_response.skincare_routine}
    """.strip()

    prompt = f"""
BLOCK: SKIN ANALYSIS REPORT
This report is structured similarly to a skincare routine report.

BLOCK: AI-DETECTED SKIN CONDITIONS
{formatted_conditions}

BLOCK: USER-PROVIDED DESCRIPTION
{user_description if user_description.strip() else "No user description provided."}

BLOCK: USER SKIN PROFILE
{formatted_skin_profile}

BLOCK: MOST LIKELY CONDITION & SEVERITY
Explain the likely condition and indicate severity (Mild, Moderate, or Severe).

BLOCK: CAUSES AND CONTRIBUTING FACTORS
List common factors such as UV exposure, skin sensitivity, hormonal changes, and diet.

BLOCK: PERSONALIZED SKINCARE ROUTINE
Provide detailed morning and evening routines.

BLOCK: RECOMMENDED SKINCARE PRODUCTS
Offer brand-neutral suggestions including key ingredients.

BLOCK: WHEN TO SEEK MEDICAL ADVICE
List red flags and indications for professional help.

BLOCK: DISCLAIMER
State that the report is informational and not a substitute for an in-person consultation.

NOTE: For any word that contains two or more consecutive capital letters (e.g., "ABC" or "XYZ"), insert a newline before and after that word.
    """.strip()

    from google.generativeai import GenerativeModel
    model = GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=sys_instruct
    )

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.7,
            "response_mime_type": "text/plain"
        }
    )

    cleaned_text = clean_response(response.text)
    return cleaned_text



import markdown

def get_skin_diagnosis(model_path, image_path, user_description, skin_profile):
    """
    Generates a structured skin diagnosis report in HTML format.
    """

    # Load model
    model = load_model(model_path)

    # Get classification results
    top5_predictions = classify_image(model, image_path)

    # Generate structured report
    markdown_report = generate_skin_advice(top5_predictions, user_description, skin_profile)

    # Convert to HTML while preserving line breaks
    html_report = markdown.markdown(markdown_report, extensions=["extra", "nl2br"])

    formatted_html = f"""
    <div class="report-container">
        <h2>Skin Analysis Report</h2>
        <div class="report-content">{html_report}</div>
    </div>
    """

    return formatted_html

