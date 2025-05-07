from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list_view, name='complaint_list'),
    path('create/', views.complaint_create_view, name='complaint_create'),
    path('<int:complaint_id>/', views.complaint_detail_view, name='complaint_detail'),
    path('<int:complaint_id>/edit/', views.complaint_edit_view, name='complaint_edit'),
    path('<int:complaint_id>/delete/', views.complaint_delete_view, name='complaint_delete'),
] 