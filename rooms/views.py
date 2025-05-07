from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import Room, RoomAllocation
from .forms import RoomForm, RoomAllocationForm
from accounts.models import User

@login_required
def room_list_view(request):
    rooms = Room.objects.all()
    
    # Filter by availability
    availability = request.GET.get('availability')
    if availability:
        rooms = rooms.filter(is_available=(availability == 'available'))
    
    # Filter by room type
    room_type = request.GET.get('type')
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    
    # Filter by floor
    floor = request.GET.get('floor')
    if floor:
        rooms = rooms.filter(floor=floor)
    
    context = {
        'rooms': rooms,
        'room_types': Room.ROOM_TYPE_CHOICES,
        'floors': Room.objects.values_list('floor', flat=True).distinct(),
    }
    return render(request, 'rooms/room_list.html', context)

@login_required
def room_detail_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    current_allocations = room.roomallocation_set.filter(is_active=True)
    past_allocations = room.roomallocation_set.filter(is_active=False)
    
    context = {
        'room': room,
        'current_allocations': current_allocations,
        'past_allocations': past_allocations,
    }
    return render(request, 'rooms/room_detail.html', context)

@login_required
def room_create_view(request):
    if not request.user.role in ['ADMIN', 'WARDEN']:
        messages.error(request, 'Access denied.')
        return redirect('rooms:room_list')
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            messages.success(request, 'Room created successfully!')
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm()
    
    return render(request, 'rooms/room_form.html', {'form': form, 'action': 'Create'})

@login_required
def room_edit_view(request, room_id):
    if not request.user.role in ['ADMIN', 'WARDEN']:
        messages.error(request, 'Access denied.')
        return redirect('rooms:room_list')
    
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully!')
            return redirect('rooms:room_detail', room_id=room.id)
    else:
        form = RoomForm(instance=room)
    
    return render(request, 'rooms/room_form.html', {'form': form, 'action': 'Edit'})

@login_required
def room_delete_view(request, room_id):
    if not request.user.role == 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('rooms:room_list')
    
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        if room.roomallocation_set.filter(is_active=True).exists():
            messages.error(request, 'Cannot delete room with active allocations.')
        else:
            room.delete()
            messages.success(request, 'Room deleted successfully!')
            return redirect('rooms:room_list')
    
    return render(request, 'rooms/room_confirm_delete.html', {'room': room})

@login_required
def allocation_list_view(request):
    if request.user.role == 'STUDENT':
        allocations = RoomAllocation.objects.filter(student=request.user)
    else:
        allocations = RoomAllocation.objects.all()
        
        # Filter by student
        student_id = request.GET.get('student')
        if student_id:
            allocations = allocations.filter(student_id=student_id)
        
        # Filter by room
        room_id = request.GET.get('room')
        if room_id:
            allocations = allocations.filter(room_id=room_id)
        
        # Filter by status
        status = request.GET.get('status')
        if status:
            allocations = allocations.filter(is_active=(status == 'active'))
    
    context = {
        'allocations': allocations,
        'students': User.objects.filter(role='STUDENT'),
        'rooms': Room.objects.all(),
    }
    return render(request, 'rooms/allocation_list.html', context)

@login_required
def allocation_detail_view(request, allocation_id):
    if request.user.role == 'STUDENT':
        allocation = get_object_or_404(RoomAllocation, id=allocation_id, student=request.user)
    else:
        allocation = get_object_or_404(RoomAllocation, id=allocation_id)
    
    return render(request, 'rooms/allocation_detail.html', {'allocation': allocation})

@login_required
def allocate_room_view(request):
    if not request.user.role in ['ADMIN', 'WARDEN']:
        messages.error(request, 'Access denied.')
        return redirect('rooms:allocation_list')
    
    if request.method == 'POST':
        form = RoomAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.allocated_by = request.user
            
            # Check if student already has an active allocation
            if RoomAllocation.objects.filter(student=allocation.student, is_active=True).exists():
                messages.error(request, 'Student already has an active room allocation.')
            # Check if room has space
            elif allocation.room.is_full:
                messages.error(request, 'Room is already full.')
            else:
                allocation.save()
                messages.success(request, 'Room allocated successfully!')
                return redirect('rooms:allocation_detail', allocation_id=allocation.id)
    else:
        form = RoomAllocationForm()
    
    return render(request, 'rooms/allocation_form.html', {'form': form})

@login_required
def deallocate_room_view(request, allocation_id):
    if not request.user.role in ['ADMIN', 'WARDEN']:
        messages.error(request, 'Access denied.')
        return redirect('rooms:allocation_list')
    
    allocation = get_object_or_404(RoomAllocation, id=allocation_id)
    
    if request.method == 'POST':
        allocation.is_active = False
        allocation.check_out_date = timezone.now().date()
        allocation.save()
        
        # Update room availability
        room = allocation.room
        if room.current_occupants < room.capacity:
            room.is_available = True
            room.save()
        
        messages.success(request, 'Room deallocated successfully!')
        return redirect('rooms:allocation_list')
    
    return render(request, 'rooms/allocation_confirm_deallocate.html', {'allocation': allocation})

@login_required
def room_maintenance_view(request, room_id):
    if not request.user.role in ['ADMIN', 'WARDEN']:
        messages.error(request, 'Access denied.')
        return redirect('rooms:room_list')
    
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        room.last_maintenance = timezone.now().date()
        room.save()
        messages.success(request, 'Maintenance date updated successfully!')
        return redirect('rooms:room_detail', room_id=room.id)
    
    return render(request, 'rooms/room_maintenance.html', {'room': room})
