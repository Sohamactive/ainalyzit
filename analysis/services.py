# File: analysis/services.py

import os, json
import datetime
from pymongo import MongoClient
import google.generativeai as genai
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pathlib import Path
import openfoodfacts

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

def get_db_handle():
    mongo_user = os.getenv("MONGO_USER")
    mongo_pass = os.getenv("MONGO_PASS")
    mongo_cluster_url = os.getenv("MONGO_CLUSTER_URL")
    if not all([mongo_user, mongo_pass, mongo_cluster_url]):
        raise ValueError("Missing Mongo credentials")

    escaped_user = quote_plus(mongo_user)
    escaped_pass = quote_plus(mongo_pass)
    mongo_uri = f"mongodb+srv://{escaped_user}:{escaped_pass}@{mongo_cluster_url}/?retryWrites=true&w=majority&appName=ainalyzit"
    client = MongoClient(mongo_uri)
    return client['ainalyzit_db'], client

def save_report_to_db(user_id, serving_size, analysis_data):
    db, client = get_db_handle()
    result = db['reports'].insert_one({
        "userId": user_id,
        "createdAt": datetime.datetime.now(datetime.timezone.utc),
        "userInput": {"servingSize": serving_size},
        "analysis": analysis_data
    })
    client.close()
    return result.inserted_id

def get_openfoodfacts_data(product_name):
    try:
        res = openfoodfacts.products.text_search(product_name)
        product = res.get("products", [None])[0]
        return {
            "nutri_score": product.get("nutriscore_grade", "N/A").upper() if product else "N/A",
            "eco_score": product.get("ecoscore_grade", "N/A").upper() if product else "N/A",
        }
    except Exception as e:
        print(f"OpenFoodFacts error: {e}")
        return {"nutri_score": "N/A", "eco_score": "N/A"}

def call_gemini_api(image_file, serving_size):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Missing Gemini API Key")

    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    image_bytes = image_file.read()

    prompt = f"""
    You are a nutritional analyst for 'ainalyzit'.
    Analyze the image of food's ingredients and nutrition facts.
    User's serving size: "{serving_size}".

    Respond with a JSON object with the following structure:
    {{
      "productName": "string",
      "ingredients": [{{ "name": "string", "score": "number", "description": "string" }}],
      "processingScore": {{ "score": "number", "label": "string" }},
      "healthierAlternatives": [{{ "name": "string", "reason": "string", "score": "number" }}],
      "overallSummary": {{ "title": "string", "report": "string" }}
    }}
    """

    response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_bytes}])
    raw_text = response.text.strip().replace("```json", "").replace("```", "")

    try:
        analysis_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print("Gemini returned invalid JSON:", raw_text)
        raise e

    # Normalize ingredient scores
    try:
        for ing in analysis_data.get("ingredients", []):
            ing["score"] = int(float(ing.get("score", 0)))
        analysis_data["processingScore"]["score"] = int(float(analysis_data["processingScore"].get("score", 0)))
    except Exception as e:
        print("Score coercion failed:", e)

    # Add Open Food Facts data
    product_name = analysis_data.get("productName", "")
    off_data = get_openfoodfacts_data(product_name)
    analysis_data["nutri_score"] = off_data["nutri_score"]
    analysis_data["eco_score"] = off_data["eco_score"]

    return json.dumps(analysis_data)

# In analysis/services.py

# ... (keep all your existing functions like get_db_handle, call_gemini_api, etc.) ...

# Add this new function at the end of the file
def log_analysis_to_db(user_id, analysis_data):
    """
    Logs the result of a food analysis to the 'daily_logs' collection in MongoDB.
    """
    if not analysis_data:
        print("No analysis data provided to log.")
        return

    db, client = get_db_handle()
    logs_collection = db['daily_logs']
    
    try:
        # Prepare the document to be inserted
        log_entry = {
            "userId": user_id,
            "foodName": analysis_data.get("productName", "Unknown Food"),
            "nutritionalScore": analysis_data.get("processingScore", {}).get("score", 0),
            "analysis": analysis_data, # Store the full analysis object
            "timestamp": datetime.now(datetime.timezone.utc)
        }
        
        # Insert the document into the collection
        logs_collection.insert_one(log_entry)
        print(f"Successfully logged analysis for user {user_id}")
        
    except Exception as e:
        print(f"Error logging analysis to MongoDB: {e}")
    finally:
        client.close()