# ainalyzit/api/views.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from analysis.services import call_gemini_api, save_report_to_db, log_analysis_to_db # Correctly import log_analysis_to_db
from dashboard.services import log_meal_to_db # Keep this import for the manual log_meal view

def login_required(function):
    def wrapper(request, *args, **kwargs):
        if "user" not in request.session:
            return JsonResponse({"error": "Authentication required. Please log in."}, status=401)
        return function(request, *args, **kwargs)
    return wrapper


@csrf_exempt
@require_POST
@login_required
def analyze_image(request):
    """
    API endpoint to receive an image and serving size, get an analysis 
    from Gemini, save it, log it, and return the result.
    """
    try:
        user_info = request.session.get("user")
        user_id = user_info.get("userinfo", {}).get("sub")

        if not user_id:
            return JsonResponse({"error": "Could not identify user from session."}, status=403)

        image_file = request.FILES.get('image')
        serving_size = request.POST.get('servingSize')

        if not image_file or not serving_size:
            return JsonResponse({'error': 'Image file and serving size are required.'}, status=400)

        analysis_data_json = call_gemini_api(image_file, serving_size)
        analysis_data = json.loads(analysis_data_json)
        
        report_id = save_report_to_db(user_id, serving_size, analysis_data)
        
        # --- FIX: Log the analysis to the daily_logs collection ---
        log_analysis_to_db(user_id, analysis_data)
        
        return JsonResponse({
            'success': True,
            'report_id': str(report_id),
            'analysis': analysis_data
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Failed to parse AI response.'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


@csrf_exempt
@require_POST
@login_required
def log_meal(request):
    """
    API endpoint to log a meal that the user has eaten.
    """
    try:
        # --- FIX: Get the REAL user ID from the session ---
        user_info = request.session.get("user")
        user_id = user_info.get("userinfo", {}).get("sub")

        if not user_id:
            return JsonResponse({"error": "Could not identify user from session."}, status=403)
        
        data = json.loads(request.body)
        food_name = data.get('foodName')
        score = data.get('score')

        if not food_name or score is None:
            return JsonResponse({'error': 'Food name and score are required.'}, status=400)

        log_id = log_meal_to_db(user_id, food_name, score)

        return JsonResponse({'success': True, 'log_id': str(log_id)})

    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)