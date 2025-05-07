from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from django.conf import settings

class DashboardStats(models.Model):
    total_students = models.IntegerField(default=0)
    total_rooms = models.IntegerField(default=0)
    occupied_rooms = models.IntegerField(default=0)
    total_complaints = models.IntegerField(default=0)
    pending_complaints = models.IntegerField(default=0)
    total_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pending_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Dashboard Statistics')
        verbose_name_plural = _('Dashboard Statistics')
    
    def __str__(self):
        return f"Dashboard Stats - {self.last_updated}"

class SystemSettings(models.Model):
    class SettingType(models.TextChoices):
        GENERAL = 'GENERAL', _('General')
        PAYMENT = 'PAYMENT', _('Payment')
        MESS = 'MESS', _('Mess')
        NOTIFICATION = 'NOTIFICATION', _('Notification')
        OTHER = 'OTHER', _('Other')
    
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    setting_type = models.CharField(max_length=20, choices=SettingType.choices)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Setting - {self.key}"

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', _('Create')
        UPDATE = 'UPDATE', _('Update')
        DELETE = 'DELETE', _('Delete')
        LOGIN = 'LOGIN', _('Login')
        LOGOUT = 'LOGOUT', _('Logout')
        OTHER = 'OTHER', _('Other')
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    details = models.JSONField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Audit Log - {self.user} - {self.action} - {self.model_name}"

class BackupLog(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
    
    backup_file = models.FileField(upload_to='backups/')
    status = models.CharField(max_length=20, choices=Status.choices)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    size = models.BigIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_backups')
    
    def __str__(self):
        return f"Backup - {self.backup_file.name} ({self.get_status_display()})"

class MaintenanceSchedule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ])
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_maintenance_schedules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"
