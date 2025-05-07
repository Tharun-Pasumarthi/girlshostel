from django.urls import path
from . import views

app_name = 'safety'

urlpatterns = [
    path('contacts/', views.emergency_contacts, name='emergency_contacts'),
    path('guidelines/', views.safety_guidelines, name='safety_guidelines'),
    path('incidents/report/', views.report_incident, name='report_incident'),
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('drills/', views.emergency_drills, name='emergency_drills'),
    path('drills/schedule/', views.schedule_drill, name='schedule_drill'),
    path('drills/<int:drill_id>/update/', views.update_drill, name='update_drill'),
] 