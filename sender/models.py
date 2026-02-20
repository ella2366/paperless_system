from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django_otp import user_has_device
from django.contrib.auth.forms import UserCreationForm
from django import forms

# Roles for the system
ROLE_CHOICES = [
    ('employee', 'Employee'),
    ('head', 'Department Head'),
    ('executive', 'Executive'),
    ('governor', 'Governor'),
]

class Department(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    is_approved = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')
    history = HistoricalRecords() # Ito ang Audit Trail for Profiles

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Document(models.Model):
    title = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_docs')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_docs')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending Review'),
        ('approved', 'Approved & Signed'),
        ('rejected', 'Returned for Revision'),
    ])
    is_archived = models.BooleanField(default=False)
    signature_hash = models.CharField(max_length=100, blank=True, null=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords() # Audit Trail for Documents

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_received')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['timestamp']

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Kunin ang data mula sa form (custom fields)
            user_role = request.POST.get('role', 'employee')
            user_gender = request.POST.get('gender', 'Male')
            
            # Gawan ng Profile ang bagong user
            Profile.objects.create(
                user=user, 
                role=user_role, 
                gender=user_gender,
                is_approved=False # Default: needs admin approval
            )
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form, 'roles': ROLE_CHOICES})

@property
def is_verified(self):
    # Ito ang magsasabi kung ang user ay nakapag-setup na ng 2FA
    return user_has_device(self)

User.add_to_class('is_verified', is_verified)

# Gumawa ng custom form para kasama ang Email
class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

# 5. Ang iyong Final Register View
def register(request):
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(
                user=user, 
                role=request.POST.get('role', 'employee'), 
                gender=request.POST.get('gender', 'Male'),
                is_approved=False
            )
            return redirect('login')
    else:
        form = ExtendedUserCreationForm()
    return render(request, 'registration/register.html', {'form': form, 'roles': ROLE_CHOICES})

# --- ILAGAY ITO SA PINAKABABA NG MODELS.PY ---

def get_is_verified(self):
    # I-check kung may active 2FA device
    return user_has_device(self)

def set_is_verified(self, value):
    # Dummy setter: Tinatanggap ang value pero hindi isasave 
    # para hindi mag-crash ang library setters.
    pass

# I-delete muna kung exist na para i-overwrite nang tama
if hasattr(User, 'is_verified'):
    delattr(User, 'is_verified')

# I-attach ang property na may kasamang fget (getter) at fset (setter)
User.is_verified = property(fget=get_is_verified, fset=set_is_verified)