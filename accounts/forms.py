from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm as DjangoPasswordChangeForm
from .models import User, StudentProfile, WardenProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        
        if commit:
            user.save()
            
            # Create corresponding profile based on role
            if user.role == 'STUDENT':
                StudentProfile.objects.create(user=user)
            elif user.role == 'WARDEN':
                WardenProfile.objects.create(user=user)
        
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('roll_number', 'course', 'semester', 'blood_group', 
                 'parent_name', 'parent_phone', 'parent_email')
        widgets = {
            'parent_phone': forms.TextInput(attrs={'pattern': '[0-9]{10}'}),
        }

class WardenProfileForm(forms.ModelForm):
    class Meta:
        model = WardenProfile
        fields = ('designation', 'department', 'joining_date')
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'}) 