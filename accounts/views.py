from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import User, StudentProfile, WardenProfile
from .forms import UserRegistrationForm, UserProfileForm, PasswordChangeForm
from rooms.models import Room
from complaints.models import Complaint

def home_view(request):
    """Home page view."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    context = {
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(is_available=True).count(),
        'total_students': User.objects.filter(role='STUDENT').count(),
    }
    return render(request, 'accounts/home.html', context)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('accounts:login')

def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def dashboard_view(request):
    """Dashboard view based on user role."""
    if request.user.role == 'ADMIN':
        context = {
            'total_students': User.objects.filter(role='STUDENT').count(),
            'total_rooms': Room.objects.count(),
            'available_rooms': Room.objects.filter(is_available=True).count(),
            'total_wardens': User.objects.filter(role='WARDEN').count(),
            'recent_users': User.objects.all().order_by('-date_joined')[:5],
        }
    elif request.user.role == 'WARDEN':
        context = {
            'total_students': User.objects.filter(role='STUDENT').count(),
            'available_rooms': Room.objects.filter(is_available=True).count(),
            'pending_complaints': 0,  # TODO: Implement complaints
            'recent_complaints': [],  # TODO: Implement complaints
        }
    else:  # STUDENT
        context = {
            'room': request.user.room if hasattr(request.user, 'room') else None,
            'attendance_percentage': 0,  # TODO: Implement attendance
            'pending_fees': 0,  # TODO: Implement fees
            'recent_activities': [],  # TODO: Implement activities
        }
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user,
    }
    
    if user.role == 'STUDENT':
        context['profile'] = user.studentprofile
    elif user.role == 'WARDEN':
        context['profile'] = user.wardenprofile
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

def reset_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
            )
            
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset instructions sent to your email.')
            return redirect('accounts:login')
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
    
    return render(request, 'accounts/reset_password.html')

def reset_password_confirm_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password reset successful!')
                return redirect('accounts:login')
        else:
            form = PasswordChangeForm(user)
        
        return render(request, 'accounts/reset_password_confirm.html', {'form': form})
    else:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:login')

# Admin views
@login_required
def user_list_view(request):
    if not request.user.role == 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    users = User.objects.all()
    return render(request, 'accounts/admin/user_list.html', {'users': users})

@login_required
def user_detail_view(request, user_id):
    if not request.user.role == 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    return render(request, 'accounts/admin/user_detail.html', {'user_obj': user})

@login_required
def edit_user_view(request, user_id):
    if not request.user.role == 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('accounts:user_detail', user_id=user.id)
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'accounts/admin/edit_user.html', {'form': form, 'user_obj': user})

@login_required
def delete_user_view(request, user_id):
    if not request.user.role == 'ADMIN':
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/admin/delete_user.html', {'user_obj': user})

@login_required
def user_edit_view(request, user_id):
    """Edit a user's information."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to edit users.')
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Update user information
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        
        # Only admin can change role
        if request.user.role == 'ADMIN':
            user.role = request.POST.get('role')
        
        # Update password if provided
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        user.save()
        messages.success(request, 'User information updated successfully!')
        return redirect('accounts:user_detail', user_id=user.id)
    
    context = {
        'user_to_edit': user,
    }
    return render(request, 'accounts/user_form.html', context)

@login_required
def user_create_view(request):
    """Create a new user."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to create users.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'User created successfully!')
            return redirect('accounts:user_detail', user_id=user.id)
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'action': 'Create'
    })
