from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list_view, name='attendance_list'),
    path('mark/', views.mark_attendance_view, name='mark_attendance'),
    path('report/', views.attendance_report_view, name='attendance_report'),
    path('student/<int:student_id>/', views.student_attendance_view, name='student_attendance'),
] 