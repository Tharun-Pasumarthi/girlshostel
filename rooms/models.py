from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from django.conf import settings

class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('SINGLE', 'Single'),
        ('DOUBLE', 'Double'),
        ('TRIPLE', 'Triple'),
    )
    
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    floor = models.IntegerField()
    capacity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    amenities = models.JSONField(default=dict)
    monthly_rent = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    last_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"
    
    @property
    def current_occupants(self):
        return self.roomallocation_set.filter(is_active=True).count()
    
    @property
    def is_full(self):
        return self.current_occupants >= self.capacity

class RoomAllocation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='room_allocations_made'
    )
    allocation_date = models.DateField()
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['room', 'student', 'allocation_date']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - Room {self.room.room_number}"
    
    def save(self, *args, **kwargs):
        if self.is_active and not self.check_out_date:
            # Update room availability based on capacity
            current_occupants = self.room.current_occupants
            if current_occupants >= self.room.capacity:
                self.room.is_available = False
                self.room.save()
        super().save(*args, **kwargs)

class RoomChangeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_change_requests')
    current_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='current_room_requests')
    requested_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='requested_room_requests')
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='room_change_reviews')
    review_date = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Room Change Request - {self.student.get_full_name()}"

class RoomMaintenance(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='maintenance_records')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_reports')
    issue_type = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_room_maintenance')
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Maintenance - Room {self.room.room_number} - {self.issue_type}"
