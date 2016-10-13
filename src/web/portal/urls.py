from django.conf.urls import include, url
from src.web.portal import views as portal_views
from django.contrib.auth import views as auth_views
from src.web.portal.forms import LoginForm

urlpatterns = [
    url(r'^$', portal_views.index),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html', 'authentication_form': LoginForm}, name="login"),
    url(r'^logout/$', auth_views.logout, {'next_page': '/portal/login/'}),  
]
    