from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Complaint
from django.utils import timezone

# Create your views here.

@login_required
def complaint_list_view(request):
    """List all complaints."""
    if request.user.role in ['ADMIN', 'WARDEN']:
        complaints = Complaint.objects.all()
    else:
        complaints = request.user.complaints.all()
    
    context = {
        'complaints': complaints,
    }
    return render(request, 'complaints/complaint_list.html', context)

@login_required
def complaint_create_view(request):
    """Create a new complaint."""
    if request.method == 'POST':
        title = request.POST.get('title')
        type = request.POST.get('type')
        description = request.POST.get('description')
        
        complaint = Complaint.objects.create(
            student=request.user,
            title=title,
            type=type,
            description=description,
        )
        
        messages.success(request, 'Complaint submitted successfully!')
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    return render(request, 'complaints/complaint_form.html')

@login_required
def complaint_detail_view(request, complaint_id):
    """View complaint details."""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check if user has permission to view this complaint
    if request.user.role not in ['ADMIN', 'WARDEN'] and complaint.student != request.user:
        messages.error(request, 'You do not have permission to view this complaint.')
        return redirect('complaints:complaint_list')
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complaints/complaint_detail.html', context)

@login_required
def complaint_edit_view(request, complaint_id):
    """Edit a complaint."""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check if user has permission to edit this complaint
    if request.user.role not in ['ADMIN', 'WARDEN'] and complaint.student != request.user:
        messages.error(request, 'You do not have permission to edit this complaint.')
        return redirect('complaints:complaint_list')
    
    if request.method == 'POST':
        if request.user.role in ['ADMIN', 'WARDEN']:
            status = request.POST.get('status')
            resolution_notes = request.POST.get('resolution_notes')
            
            complaint.status = status
            complaint.resolution_notes = resolution_notes
            
            if status == 'RESOLVED':
                complaint.resolved_by = request.user
                complaint.resolved_at = timezone.now()
        else:
            title = request.POST.get('title')
            type = request.POST.get('type')
            description = request.POST.get('description')
            
            complaint.title = title
            complaint.type = type
            complaint.description = description
        
        complaint.save()
        messages.success(request, 'Complaint updated successfully!')
        return redirect('complaints:complaint_detail', complaint_id=complaint.id)
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complaints/complaint_form.html', context)

@login_required
def complaint_delete_view(request, complaint_id):
    """Delete a complaint."""
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    # Check if user has permission to delete this complaint
    if request.user.role not in ['ADMIN', 'WARDEN'] and complaint.student != request.user:
        messages.error(request, 'You do not have permission to delete this complaint.')
        return redirect('complaints:complaint_list')
    
    if request.method == 'POST':
        complaint.delete()
        messages.success(request, 'Complaint deleted successfully!')
        return redirect('complaints:complaint_list')
    
    context = {
        'complaint': complaint,
    }
    return render(request, 'complaints/complaint_confirm_delete.html', context)
