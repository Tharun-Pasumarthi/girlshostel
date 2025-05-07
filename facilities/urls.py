from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('', views.facility_list, name='facility_list'),
    path('<int:facility_id>/', views.facility_detail, name='facility_detail'),
    path('add/', views.add_facility, name='add_facility'),
    path('<int:facility_id>/edit/', views.edit_facility, name='edit_facility'),
    path('<int:facility_id>/book/', views.book_facility, name='book_facility'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/update/', views.update_booking, name='update_booking'),
    path('<int:facility_id>/maintenance/', views.report_maintenance, name='report_maintenance'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/<int:request_id>/update/', views.update_maintenance, name='update_maintenance'),
] 