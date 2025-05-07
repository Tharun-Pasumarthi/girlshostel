from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.http import JsonResponse
from .models import Report, DashboardWidget, NotificationPreference
from accounts.models import User
from rooms.models import Room, RoomAllocation
from attendance.models import Attendance
from fees.models import Fee, Payment
from complaints.models import Complaint
from facilities.models import FacilityBooking, MaintenanceRequest
from .forms import ReportForm, WidgetForm, NotificationPreferenceForm

@login_required
def dashboard(request):
    """Main dashboard view with customizable widgets."""
    # Get user's active widgets
    widgets = DashboardWidget.objects.filter(is_active=True).order_by('position')
    
    # Get statistics for different modules
    stats = {
        'total_students': User.objects.filter(role='STUDENT').count(),
        'total_rooms': Room.objects.count(),
        'occupied_rooms': RoomAllocation.objects.filter(is_active=True).count(),
        'pending_complaints': Complaint.objects.filter(status='PENDING').count(),
        'pending_maintenance': MaintenanceRequest.objects.filter(status='PENDING').count(),
        'upcoming_bookings': FacilityBooking.objects.filter(
            status='APPROVED',
            booking_date__gte=timezone.now().date()
        ).count(),
    }
    
    # Get recent activities
    recent_activities = {
        'complaints': Complaint.objects.order_by('-created_at')[:5],
        'maintenance': MaintenanceRequest.objects.order_by('-created_at')[:5],
        'bookings': FacilityBooking.objects.order_by('-created_at')[:5],
    }
    
    context = {
        'widgets': widgets,
        'stats': stats,
        'recent_activities': recent_activities,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def reports(request):
    """View for generating and managing reports."""
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.generated_by = request.user
            report.save()
            messages.success(request, 'Report generated successfully.')
            return redirect('dashboard:report_detail', report_id=report.id)
    else:
        form = ReportForm()
    
    reports = Report.objects.filter(generated_by=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'reports': reports,
    }
    return render(request, 'dashboard/reports.html', context)

@login_required
def report_detail(request, report_id):
    """View for displaying report details."""
    report = get_object_or_404(Report, id=report_id, generated_by=request.user)
    
    context = {
        'report': report,
    }
    return render(request, 'dashboard/report_detail.html', context)

@login_required
def customize_dashboard(request):
    """View for customizing dashboard widgets."""
    if request.method == 'POST':
        form = WidgetForm(request.POST)
        if form.is_valid():
            widget = form.save()
            messages.success(request, 'Widget added successfully.')
            return redirect('dashboard:dashboard')
    else:
        form = WidgetForm()
    
    widgets = DashboardWidget.objects.all().order_by('position')
    
    context = {
        'form': form,
        'widgets': widgets,
    }
    return render(request, 'dashboard/customize.html', context)

@login_required
def update_widget_position(request):
    """AJAX view for updating widget positions."""
    if request.method == 'POST':
        widget_id = request.POST.get('widget_id')
        new_position = request.POST.get('position')
        
        try:
            widget = DashboardWidget.objects.get(id=widget_id)
            widget.position = new_position
            widget.save()
            return JsonResponse({'status': 'success'})
        except DashboardWidget.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Widget not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def notification_preferences(request):
    """View for managing notification preferences."""
    try:
        preferences = NotificationPreference.objects.get(user=request.user)
    except NotificationPreference.DoesNotExist:
        preferences = NotificationPreference.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=preferences)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notification preferences updated successfully.')
            return redirect('dashboard:dashboard')
    else:
        form = NotificationPreferenceForm(instance=preferences)
    
    context = {
        'form': form,
    }
    return render(request, 'dashboard/notification_preferences.html', context)

@login_required
def get_widget_data(request, widget_id):
    """AJAX view for getting widget data."""
    widget = get_object_or_404(DashboardWidget, id=widget_id)
    
    # Get data based on widget type and data source
    if widget.widget_type == 'STATS':
        if widget.data_source == 'attendance':
            data = {
                'present': Attendance.objects.filter(
                    date=timezone.now().date(),
                    status='PRESENT'
                ).count(),
                'absent': Attendance.objects.filter(
                    date=timezone.now().date(),
                    status='ABSENT'
                ).count(),
                'late': Attendance.objects.filter(
                    date=timezone.now().date(),
                    status='LATE'
                ).count(),
            }
        elif widget.data_source == 'fees':
            data = {
                'total_collected': Payment.objects.filter(
                    payment_date__month=timezone.now().month
                ).aggregate(total=Sum('amount'))['total'] or 0,
                'pending_payments': Fee.objects.filter(
                    status='PENDING'
                ).count(),
            }
        # Add more data sources as needed
    
    return JsonResponse({'data': data})
