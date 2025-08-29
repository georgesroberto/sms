from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('sales/', views.sales_report, name='sales'),
    path('stock/', views.stock_list, name='stock'),
    path('record_sale/', views.record_sale, name='record_sales')
]