from django.shortcuts import render
from src.web.portal.forms import MessageForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

@login_required(login_url="login/")
@ensure_csrf_cookie
def index(request):
    if request.method == 'GET':
        if "formSubmit" in request.GET:
            return render(request, "landing_response.html", {'form': MessageForm()})
    return render(request, 'portal_landing.html', {'form': MessageForm()})
