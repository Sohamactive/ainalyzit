
from django.shortcuts import render

def index(request):
    """
    Routes the user to the correct page based on their login status.
    - If logged in, shows the main analysis tool (index.html).
    - If not logged in, shows the beautiful landing page (landing.html).
    """
    if request.session.get('user'):
        # User is logged in, show them the main application
        context = {
            'session': request.session.get('user')
        }
        return render(request, 'index.html', context)
    else:
        # User is a guest, show them the landing page
        return render(request, 'landing.html')