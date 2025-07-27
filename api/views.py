# File: api/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from analysis.services import call_gemini_api, save_report_to_db
from dashboard.services import log_meal_to_db

# This is a simple decorator function to check if a user is logged in
# by looking for the 'user' object in the Django session.
def login_required(function):
    def wrapper(request, *args, **kwargs):
        if "user" not in request.session:
            return JsonResponse({"error": "Authentication required. Please log in."}, status=401)
        return function(request, *args, **kwargs)
    return wrapper


@csrf_exempt
@require_POST
@login_required # This decorator now protects the view
def analyze_image(request):
    """
    API endpoint to receive an image and serving size, get an analysis 
    from Gemini, save it to the database, and return the result.
    """
    try:
        # --- FIX: Get the REAL user ID from the session ---
        user_info = request.session.get("user")
        # 'sub' is the standard field for a unique user ID in Auth0/OIDC tokens
        user_id = user_info.get("userinfo", {}).get("sub")

        if not user_id:
            return JsonResponse({"error": "Could not identify user from session."}, status=403)

        image_file = request.FILES.get('image')
        serving_size = request.POST.get('servingSize')

        if not image_file or not serving_size:
            return JsonResponse({'error': 'Image file and serving size are required.'}, status=400)

        # The rest of the process remains the same
        print("Calling Gemini service...")
        analysis_data_json = call_gemini_api(image_file, serving_size)
        analysis_data = json.loads(analysis_data_json)
        print("Successfully received data from Gemini.")

        print("Saving report to MongoDB...")
        report_id = save_report_to_db(user_id, serving_size, analysis_data)
        print(f"Report saved for user {user_id} with ID: {report_id}")

        return JsonResponse({
            'success': True,
            'report_id': str(report_id),
            'analysis': analysis_data
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Failed to parse AI response. The AI may have returned an invalid format.'}, status=500)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_exempt
@require_POST
def log_meal(request):
    """
    API endpoint to log a meal that the user has eaten.
    """
    try:
        user_id = "user_placeholder_123" # Placeholder
        
        data = json.loads(request.body)
        food_name = data.get('foodName')
        score = data.get('score')

        if not food_name or score is None:
            return JsonResponse({'error': 'Food name and score are required.'}, status=400)

        log_id = log_meal_to_db(user_id, food_name, score)
        print(f"Meal logged with ID: {log_id}")

        return JsonResponse({'success': True, 'log_id': str(log_id)})

    except Exception as e:
        print(f"An error occurred during meal logging: {e}")
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)