from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
import os

@shared_task
def send_document_email_task(receiver_email, receiver_username, sender_username, doc_title, file_path):
    email = EmailMessage(
        subject=f'New TUD Document: {doc_title}',
        body=f'Hi {receiver_username}!\n\n{sender_username} sent you a document for review. Check it out!',
        from_email=settings.EMAIL_HOST_USER,
        to=[receiver_email],
    )
    
    # I-attach ang file (.docx, .pdf, etc)
    if os.path.exists(file_path):
        email.attach_file(file_path)
    
    email.send()
    return f"Email sent to {receiver_email}"