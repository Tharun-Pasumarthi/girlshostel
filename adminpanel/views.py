from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import psutil
import json

from accounts.models import User
from payments.models import Payment
from complaints.models import Complaint
from notifications.models import Notification
from adminpanel.models import AuditLog, SystemSettings

User = get_user_model()

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get total users count
    total_users = User.objects.count()
    
    # Get total revenue
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Get pending approvals
    pending_approvals = (
        Complaint.objects.filter(status='pending').count() +
        User.objects.filter(is_active=False).count()
    )
    
    # Get system health
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    system_health = 100 - max(cpu_usage, memory_usage, disk_usage)
    
    # Get recent activities
    activities = AuditLog.objects.select_related('user').order_by('-created_at')[:10]
    
    # Get recent logins
    recent_logins = User.objects.filter(
        last_login__isnull=False
    ).order_by('-last_login')[:5]
    
    # Get revenue data for chart
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    
    revenue_data = Payment.objects.filter(
        status='completed',
        created_at__gte=thirty_days_ago
    ).values('created_at__date').annotate(
        total=Sum('amount')
    ).order_by('created_at__date')
    
    revenue_labels = [str(item['created_at__date']) for item in revenue_data]
    revenue_values = [float(item['total']) for item in revenue_data]
    
    context = {
        'total_users': total_users,
        'total_revenue': total_revenue,
        'pending_approvals': pending_approvals,
        'system_health': round(system_health, 1),
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'disk_usage': disk_usage,
        'activities': activities,
        'recent_logins': recent_logins,
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_values),
        'last_updated': timezone.now(),
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard_stats(request):
    """API endpoint for updating dashboard stats"""
    total_users = User.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    pending_approvals = (
        Complaint.objects.filter(status='pending').count() +
        User.objects.filter(is_active=False).count()
    )
    
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    system_health = 100 - max(cpu_usage, memory_usage, disk_usage)
    
    return JsonResponse({
        'total_users': total_users,
        'total_revenue': total_revenue,
        'pending_approvals': pending_approvals,
        'system_health': round(system_health, 1),
    })
