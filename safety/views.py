from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EmergencyContact, SafetyGuideline, IncidentReport, EmergencyDrill
from django.utils import timezone

@login_required
def emergency_contacts(request):
    """View for displaying emergency contacts."""
    contacts = EmergencyContact.objects.filter(is_active=True)
    return render(request, 'safety/emergency_contacts.html', {
        'contacts': contacts
    })

@login_required
def safety_guidelines(request):
    """View for displaying safety guidelines."""
    guidelines = SafetyGuideline.objects.filter(is_active=True)
    guidelines_by_category = {}
    for guideline in guidelines:
        if guideline.category not in guidelines_by_category:
            guidelines_by_category[guideline.category] = []
        guidelines_by_category[guideline.category].append(guideline)
    return render(request, 'safety/guidelines.html', {
        'guidelines': guidelines_by_category
    })

@login_required
def report_incident(request):
    """View for reporting safety incidents."""
    if request.method == 'POST':
        title = request.POST.get('title')
        location = request.POST.get('location')
        severity = request.POST.get('severity')
        description = request.POST.get('description')
        
        incident = IncidentReport.objects.create(
            reported_by=request.user,
            title=title,
            location=location,
            severity=severity,
            description=description
        )
        messages.success(request, 'Incident reported successfully.')
        return redirect('safety:incident_detail', incident_id=incident.id)
    
    return render(request, 'safety/report_incident.html')

@login_required
def incident_list(request):
    """View for listing safety incidents."""
    incidents = IncidentReport.objects.all().order_by('-reported_at')
    return render(request, 'safety/incident_list.html', {
        'incidents': incidents
    })

@login_required
def incident_detail(request, incident_id):
    """View for displaying incident details."""
    incident = get_object_or_404(IncidentReport, id=incident_id)
    
    if request.method == 'POST' and request.user.role in ['ADMIN', 'WARDEN']:
        status = request.POST.get('status')
        resolution_notes = request.POST.get('resolution_notes')
        
        incident.status = status
        if status == 'RESOLVED':
            incident.resolved_at = timezone.now()
            incident.resolved_by = request.user
        incident.resolution_notes = resolution_notes
        incident.save()
        
        messages.success(request, 'Incident status updated successfully.')
        return redirect('safety:incident_detail', incident_id=incident.id)
    
    return render(request, 'safety/incident_detail.html', {
        'incident': incident
    })

@login_required
def emergency_drills(request):
    """View for displaying emergency drills."""
    upcoming_drills = EmergencyDrill.objects.filter(
        scheduled_date__gte=timezone.now().date()
    ).order_by('scheduled_date')
    
    past_drills = EmergencyDrill.objects.filter(
        scheduled_date__lt=timezone.now().date()
    ).order_by('-scheduled_date')
    
    return render(request, 'safety/drills.html', {
        'upcoming_drills': upcoming_drills,
        'past_drills': past_drills
    })

@login_required
def schedule_drill(request):
    """View for scheduling emergency drills."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to schedule drills.')
        return redirect('safety:emergency_drills')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        drill_type = request.POST.get('drill_type')
        scheduled_date = request.POST.get('scheduled_date')
        description = request.POST.get('description')
        
        drill = EmergencyDrill.objects.create(
            title=title,
            drill_type=drill_type,
            scheduled_date=scheduled_date,
            description=description
        )
        messages.success(request, 'Drill scheduled successfully.')
        return redirect('safety:emergency_drills')
    
    return render(request, 'safety/schedule_drill.html', {
        'today': timezone.now().date()
    })

@login_required
def update_drill(request, drill_id):
    """View for updating emergency drill details."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to update drills.')
        return redirect('safety:emergency_drills')
    
    drill = get_object_or_404(EmergencyDrill, id=drill_id)
    
    if request.method == 'POST':
        conducted_date = request.POST.get('conducted_date')
        notes = request.POST.get('notes')
        
        drill.conducted_date = conducted_date
        drill.notes = notes
        drill.conducted_by = request.user
        drill.save()
        
        messages.success(request, 'Drill updated successfully.')
        return redirect('safety:emergency_drills')
    
    return render(request, 'safety/update_drill.html', {
        'drill': drill
    }) 