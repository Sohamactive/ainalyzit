from django.shortcuts import render
from .services import get_user_stats

def dashboard_view(request):
    """
    Renders the user's dashboard with their daily score and streak.
    This view should require a user to be logged in.
    """
    user_info = request.session.get('user')
    if not user_info:
        # If the user is not logged in, redirect them to the login page.
        # You would typically use Django's redirect shortcut here.
        # from django.shortcuts import redirect
        # return redirect('users:login')
        # For now, we'll render an error message on a simple page.
        return render(request, 'error.html', {'message': 'Please log in to view your dashboard.'})

    # Get the real user ID from the session
    user_id = user_info.get("userinfo", {}).get("sub")
    
    stats = get_user_stats(user_id)
    
    context = {
        'daily_score': stats['daily_score'],
        'streak': stats['streak'],
        'session': user_info # Pass the full session info for the header
    }
    
    return render(request, 'dashboard.html', context)
