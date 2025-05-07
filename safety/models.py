from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from django.conf import settings

class EmergencyContact(models.Model):
    """Emergency contact information for the hostel."""
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['designation', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.designation}"

class SafetyGuideline(models.Model):
    """Safety guidelines and rules for the hostel."""
    CATEGORY_CHOICES = [
        ('GENERAL', 'General Safety'),
        ('FIRE', 'Fire Safety'),
        ('ELECTRICAL', 'Electrical Safety'),
        ('MEDICAL', 'Medical Emergency'),
        ('SECURITY', 'Security'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"

class IncidentReport(models.Model):
    """Report of safety incidents or emergencies."""
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('REPORTED', 'Reported'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='REPORTED')
    reported_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_incidents'
    )
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-reported_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"

class EmergencyDrill(models.Model):
    """Records of emergency drills conducted."""
    TYPE_CHOICES = [
        ('FIRE', 'Fire Drill'),
        ('EARTHQUAKE', 'Earthquake Drill'),
        ('EVACUATION', 'Evacuation Drill'),
        ('OTHER', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    drill_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    scheduled_date = models.DateField()
    conducted_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_drills'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.get_drill_type_display()} - {self.title}" 