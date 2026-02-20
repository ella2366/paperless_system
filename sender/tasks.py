from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Document  # Siguraduhing tama ang import path
import os

@shared_task
def send_document_email_task(doc_id, receiver_email):
    try:
        # Kunin ang document object gamit ang ID
        doc = Document.objects.get(id=doc_id)
        
        email = EmailMessage(
            subject=f'New TUD Document: {doc.title}',
            body=f'Hi {doc.receiver.username}!\n\n{doc.sender.username} sent you a document for review. Check it out!',
            from_email=settings.EMAIL_HOST_USER,
            to=[receiver_email],
        )
        
        # I-attach ang file gamit ang path mula sa database
        if doc.file and os.path.exists(doc.file.path):
            email.attach_file(doc.file.path)
        
        email.send()
        return f"Email sent for doc {doc_id} to {receiver_email}"
        
    except Document.DoesNotExist:
        return f"Error: Document {doc_id} not found."