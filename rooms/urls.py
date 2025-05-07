from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    # Room management
    path('', views.room_list_view, name='room_list'),
    path('<int:room_id>/', views.room_detail_view, name='room_detail'),
    path('create/', views.room_create_view, name='room_create'),
    path('<int:room_id>/edit/', views.room_edit_view, name='room_edit'),
    path('<int:room_id>/delete/', views.room_delete_view, name='room_delete'),
    
    # Room allocation
    path('allocations/', views.allocation_list_view, name='allocation_list'),
    path('allocations/<int:allocation_id>/', views.allocation_detail_view, name='allocation_detail'),
    path('allocate/', views.allocate_room_view, name='allocate_room'),
    path('deallocate/<int:allocation_id>/', views.deallocate_room_view, name='deallocate_room'),
    
    # Room maintenance
    path('<int:room_id>/maintenance/', views.room_maintenance_view, name='room_maintenance'),
] 