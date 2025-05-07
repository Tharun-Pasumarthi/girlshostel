from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User

@login_required
def attendance_list_view(request):
    """List all attendance records."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    context = {
        'today': timezone.now().date(),
    }
    return render(request, 'attendance/attendance_list.html', context)

@login_required
def mark_attendance_view(request):
    """Mark attendance for students."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    context = {
        'today': timezone.now().date(),
    }
    return render(request, 'attendance/mark_attendance.html', context)

@login_required
def attendance_report_view(request):
    """View attendance reports."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    context = {
        'today': timezone.now().date(),
    }
    return render(request, 'attendance/attendance_report.html', context)

@login_required
def student_attendance_view(request, student_id):
    """View attendance for a specific student."""
    student = get_object_or_404(User, id=student_id, role='STUDENT')
    
    # Check if user has permission to view this student's attendance
    if request.user.role not in ['ADMIN', 'WARDEN'] and request.user != student:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    context = {
        'student': student,
        'today': timezone.now().date(),
    }
    return render(request, 'attendance/student_attendance.html', context)
