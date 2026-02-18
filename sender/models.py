from django.db import models
from django.contrib.auth.models import User, Group

# Ibalik ito para hindi mag-error ang admin.py
class Department(models.Model):
    name = models.CharField(max_length=100)
    

    def __str__(self):
        return self.name

STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('approved', 'Approved & Signed'),
    ('rejected', 'Returned for Revision'),
]

class Document(models.Model):
    is_archived = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_documents')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_documents')
    # Siguraduhin na ang ForeignKey ay tumuturo sa tamang model
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True) 
    file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    signature_hash = models.CharField(max_length=100, blank=True, null=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title