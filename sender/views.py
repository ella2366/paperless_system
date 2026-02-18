from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import DocumentForm
from .models import Document, Department
from django.db.models import Q
from django.utils import timezone
import hashlib
from django.core.mail import send_mail
from django.conf import settings # Importante ito para sa EMAIL_HOST_USER
from .tasks import send_document_email_task # Import ang task

@login_required
def dashboard(request):
    # Filter: Ipakita lang ang mga HINDI naka-archive (Sent or Received)
    all_documents = Document.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        is_archived=False
    ).order_by('-created_at')
    
    received_count = Document.objects.filter(receiver=request.user, status='pending').count()
    sent_count = Document.objects.filter(sender=request.user, status='approved').count()
    
    # Bilangin ang mga rejected para kay Ella
    rejected_count = Document.objects.filter(sender=request.user, status='rejected').count()

    return render(request, 'sender/dashboard.html', {
        'all_documents': all_documents,
        'received_count': received_count,
        'sent_count': sent_count,
        'rejected_count': rejected_count
    })

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            
            selected_group = form.cleaned_data['department_group']
            dept_instance, created = Department.objects.get_or_create(name=selected_group.name)
            
            document.sender = request.user
            document.department = dept_instance
            document.status = 'pending'
            document.save()

            # --- CELERY ASYNC EMAIL TRIGGER ---
            # Ito ay parang "chat" na ihuhulog lang natin sa queue
            if document.receiver and document.receiver.email:
                send_document_email_task.delay(
                    document.receiver.email,
                    document.receiver.username,
                    request.user.username,
                    document.title,
                    document.file.path # Siguraduhin na 'file' ang tawag sa model field mo
                )

            return redirect('dashboard')
    else:
        form = DocumentForm()
    return render(request, 'sender/upload.html', {'form': form})
@login_required
def inbox(request):
    # Kinukuha ang mga documents kung saan ang logged-in user ang receiver
    # At hindi pa ito 'approved' o 'rejected' para sa review process
    documents = Document.objects.filter(receiver=request.user).exclude(status='approved').order_by('-created_at')
    return render(request, 'sender/inbox.html', {'documents': documents})

@login_required
def review_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            document.status = 'approved'
            document.signed_at = timezone.now()
            # Digital Signature Logic
            sig_data = f"{document.id}-{request.user.username}-{timezone.now()}"
            document.signature_hash = hashlib.sha256(sig_data.encode()).hexdigest()
            document.save()
            return redirect('dashboard')
            
        elif action == 'reject':
            document.status = 'rejected'
            document.save()
            return redirect('dashboard')

    return render(request, 'sender/review.html', {'document': document})

@login_required
def archive_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    document.is_archived = True
    document.save()
    return redirect('dashboard')

@login_required
def archived_list(request):
    # This matches the 'archived_list' URL name
    archived_documents = Document.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        is_archived=True
    ).order_by('-created_at')
    
    return render(request, 'sender/archived_list.html', {'documents': archived_documents})

# Optional but recommended: Add a way to "Unarchive"
@login_required
def unarchive_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    document.is_archived = False
    document.save()
    return redirect('archived_list')