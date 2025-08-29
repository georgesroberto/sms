from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('sales/', views.sales_report, name='sales'),
    path('stock/', views.stock_list, name='stock')
]