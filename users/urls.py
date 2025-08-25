from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication views
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard (protected view)
    path('dashboard/', views.dashboard, name='dashboard'),
]
