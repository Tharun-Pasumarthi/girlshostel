from django import forms
from .models import Room, RoomAllocation
from accounts.models import User

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'floor', 'capacity', 'description', 'amenities', 'monthly_rent']
        widgets = {
            'amenities': forms.TextInput(attrs={'class': 'json-input'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'monthly_rent': forms.NumberInput(attrs={'step': '0.01'}),
        }

class RoomAllocationForm(forms.ModelForm):
    class Meta:
        model = RoomAllocation
        fields = ['room', 'student', 'allocation_date', 'check_in_date', 'remarks']
        widgets = {
            'allocation_date': forms.DateInput(attrs={'type': 'date'}),
            'check_in_date': forms.DateInput(attrs={'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available rooms
        self.fields['room'].queryset = Room.objects.filter(is_available=True)
        # Only show students without active allocations
        self.fields['student'].queryset = User.objects.filter(
            role='STUDENT'
        ).exclude(
            id__in=RoomAllocation.objects.filter(is_active=True).values('student_id')
        ) 