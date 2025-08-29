from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Admin Urls
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('stock/', views.stock_list, name='stock'),
    
    # Vendor urls
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('sales/', views.vendor_sales, name='vendor_sales')
]