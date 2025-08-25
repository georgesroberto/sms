from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Landing page
    path('', views.landing_page, name='index'),
]