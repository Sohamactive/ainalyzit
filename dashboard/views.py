# ainalyzit/dashboard/views.py

from django.shortcuts import render, redirect
from django.urls import reverse
from .services import get_user_stats

def dashboard_view(request):
    """
    Renders the user's dashboard with their meal analysis statistics.
    """
    user_info = request.session.get('user')
    if not user_info:
        return redirect(reverse('users:login'))

    user_id = user_info.get("userinfo", {}).get("sub")
    if not user_id:
        return render(request, 'error.html', {'message': 'Could not identify user from session.'})
    
    stats = get_user_stats(user_id)
    
    context = {
        'session': user_info,
        'average_score': stats.get('average_score', 0),
        'total_meals': stats.get('total_meals', 0),
        'best_meal': stats.get('best_meal'),
        'recent_meal_logs': stats.get('recent_meal_logs', []),
        'chart_labels': stats.get('chart_labels', []),
        'chart_data': stats.get('chart_data', [])
    }
    
    return render(request, 'dashboard.html', context)