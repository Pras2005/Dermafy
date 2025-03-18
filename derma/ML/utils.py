import json
from django.conf import settings
import google.generativeai as genai
from google.generativeai import GenerativeModel

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
