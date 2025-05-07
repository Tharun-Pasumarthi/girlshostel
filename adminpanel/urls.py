from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/stats/', views.admin_dashboard_stats, name='admin_dashboard_stats'),
] 