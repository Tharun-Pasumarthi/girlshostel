from django.urls import path
from . import views

app_name = 'mess'

urlpatterns = [
    path('menu/', views.menu_list, name='menu_list'),
    path('menu/<int:menu_id>/', views.menu_detail, name='menu_detail'),
    path('menu/<int:menu_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('special-meal/', views.special_meal_request, name='special_meal_request'),
    path('special-meal/list/', views.request_list, name='request_list'),
    path('special-meal/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('leave/', views.mess_leave_request, name='mess_leave_request'),
    path('leave/list/', views.leave_list, name='leave_list'),
    path('leave/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
] 