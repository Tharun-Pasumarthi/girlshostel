from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Facility, FacilityBooking, MaintenanceRequest
from .forms import FacilityForm
from django.utils import timezone

# Create your views here.

@login_required
def facility_list(request):
    """View for listing all facilities."""
    facilities = Facility.objects.all()
    categories = dict(Facility.CATEGORY_CHOICES)
    return render(request, 'facilities/facility_list.html', {
        'facilities': facilities,
        'categories': categories
    })

@login_required
def facility_detail(request, facility_id):
    """View for displaying facility details."""
    facility = get_object_or_404(Facility, id=facility_id)
    maintenance_requests = MaintenanceRequest.objects.filter(
        facility=facility
    ).order_by('-created_at')[:5]
    return render(request, 'facilities/facility_detail.html', {
        'facility': facility,
        'maintenance_requests': maintenance_requests
    })

@login_required
def add_facility(request):
    """View for adding a new facility."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to add facilities.')
        return redirect('facilities:facility_list')
    
    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facility added successfully.')
            return redirect('facilities:facility_list')
    else:
        form = FacilityForm()
    
    return render(request, 'facilities/facility_form.html', {
        'form': form,
        'action': 'Add'
    })

@login_required
def edit_facility(request, facility_id):
    """View for editing a facility."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to edit facilities.')
        return redirect('facilities:facility_list')
    
    facility = get_object_or_404(Facility, id=facility_id)
    
    if request.method == 'POST':
        form = FacilityForm(request.POST, request.FILES, instance=facility)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facility updated successfully.')
            return redirect('facilities:facility_detail', facility_id=facility.id)
    else:
        form = FacilityForm(instance=facility)
    
    return render(request, 'facilities/facility_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
def book_facility(request, facility_id):
    """View for booking a facility."""
    facility = get_object_or_404(Facility, id=facility_id)
    
    if not facility.is_available:
        messages.error(request, 'This facility is not available for booking.')
        return redirect('facilities:facility_detail', facility_id=facility.id)
    
    if request.method == 'POST':
        booking_date = request.POST.get('booking_date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        purpose = request.POST.get('purpose')
        
        booking = FacilityBooking.objects.create(
            facility=facility,
            booked_by=request.user,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            purpose=purpose
        )
        messages.success(request, 'Booking request submitted successfully.')
        return redirect('facilities:booking_list')
    
    return render(request, 'facilities/booking_form.html', {
        'facility': facility
    })

@login_required
def booking_list(request):
    """View for listing facility bookings."""
    if request.user.role in ['ADMIN', 'WARDEN']:
        bookings = FacilityBooking.objects.all()
    else:
        bookings = FacilityBooking.objects.filter(booked_by=request.user)
    
    return render(request, 'facilities/booking_list.html', {
        'bookings': bookings
    })

@login_required
def update_booking(request, booking_id):
    """View for updating booking status."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to update bookings.')
        return redirect('facilities:booking_list')
    
    booking = get_object_or_404(FacilityBooking, id=booking_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        booking.status = status
        if status == 'APPROVED':
            booking.approved_by = request.user
        booking.save()
        messages.success(request, 'Booking status updated successfully.')
        return redirect('facilities:booking_list')
    
    return render(request, 'facilities/booking_list.html', {
        'bookings': FacilityBooking.objects.all()
    })

@login_required
def report_maintenance(request, facility_id):
    """View for reporting maintenance issues."""
    facility = get_object_or_404(Facility, id=facility_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        
        maintenance_request = MaintenanceRequest.objects.create(
            facility=facility,
            reported_by=request.user,
            title=title,
            description=description,
            priority=priority
        )
        messages.success(request, 'Maintenance request submitted successfully.')
        return redirect('facilities:maintenance_list')
    
    return render(request, 'facilities/maintenance_form.html', {
        'facility': facility
    })

@login_required
def maintenance_list(request):
    """View for listing maintenance requests."""
    if request.user.role in ['ADMIN', 'WARDEN']:
        requests = MaintenanceRequest.objects.all()
    else:
        requests = MaintenanceRequest.objects.filter(reported_by=request.user)
    
    return render(request, 'facilities/maintenance_list.html', {
        'requests': requests
    })

@login_required
def update_maintenance(request, request_id):
    """View for updating maintenance request status."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to update maintenance requests.')
        return redirect('facilities:maintenance_list')
    
    maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        resolution_notes = request.POST.get('resolution_notes')
        
        maintenance_request.status = status
        if status == 'COMPLETED':
            maintenance_request.completed_at = timezone.now()
        maintenance_request.resolution_notes = resolution_notes
        maintenance_request.save()
        
        messages.success(request, 'Maintenance request updated successfully.')
        return redirect('facilities:maintenance_list')
    
    return render(request, 'facilities/maintenance_list.html', {
        'requests': MaintenanceRequest.objects.all()
    })
