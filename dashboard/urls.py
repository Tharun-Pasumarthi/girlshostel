from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('customize/', views.customize_dashboard, name='customize'),
    path('widgets/update-position/', views.update_widget_position, name='update_widget_position'),
    path('widgets/<int:widget_id>/data/', views.get_widget_data, name='get_widget_data'),
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
] 