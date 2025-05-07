from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_list_view, name='fee_list'),
    path('create/', views.fee_create_view, name='fee_create'),
    path('<int:fee_id>/', views.fee_detail_view, name='fee_detail'),
    path('<int:fee_id>/edit/', views.fee_edit_view, name='fee_edit'),
    path('<int:fee_id>/delete/', views.fee_delete_view, name='fee_delete'),
    path('pay/<int:fee_id>/', views.fee_payment_view, name='fee_payment'),
    path('history/', views.payment_history_view, name='payment_history'),
] 