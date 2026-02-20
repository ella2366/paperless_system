from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import DocumentForm
from .models import Document, Department, ChatMessage, Profile
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
import hashlib
import json
from django.conf import settings
from .tasks import send_document_email_task 

@login_required
def dashboard(request):
    # Palitan ang .order_back ng .order_by
    all_docs = Document.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        is_archived=False
    ).select_related('sender', 'receiver', 'department').order_by('-created_at')

    # Ang rest ng code ay pareho pa rin...
    all_users = User.objects.exclude(id=request.user.id)
    unread_chats = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()
    pending_notifs = Document.objects.filter(receiver=request.user, status='pending').count()
    
    context = {
        'all_documents': all_docs,
        'all_users': all_users,
        'received_count': pending_notifs,
        'sent_count': Document.objects.filter(sender=request.user, status='approved').count(),
        'rejected_count': Document.objects.filter(sender=request.user, status='rejected').count(),
        'unread_chats': unread_chats,
        'pending_notifs': pending_notifs,
        'total_notifications': unread_chats + pending_notifs,
    }
    
    return render(request, 'sender/dashboard.html', context)
# --- CHAT SYSTEM LOGIC ---

@login_required
def send_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        message_content = data.get('message')
        
        if receiver_id and message_content:
            receiver = get_object_or_404(User, id=receiver_id)
            ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message_content
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_messages(request, receiver_id):
    messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver_id=receiver_id)) |
        (Q(sender_id=receiver_id) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # Mark as read kapag nakuha na ang messages
    ChatMessage.objects.filter(sender_id=receiver_id, receiver=request.user).update(is_read=True)
    
    results = [{
        'sender': msg.sender.username,
        'content': msg.message,
        'time': msg.timestamp.strftime('%I:%M %p')
    } for msg in messages]
    
    return JsonResponse({'messages': results})

# --- DOCUMENT LOGIC ---

@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            selected_group = form.cleaned_data['department_group']
            dept_instance, _ = Department.objects.get_or_create(name=selected_group.name)
            
            document.sender = request.user
            document.department = dept_instance
            document.status = 'pending'
            document.save()

            if document.receiver and document.receiver.email:
                send_document_email_task.delay(document.id, document.receiver.email)
            return redirect('dashboard')
    else:
        form = DocumentForm()
    return render(request, 'sender/upload.html', {'form': form})

@login_required
def inbox(request):
    documents = Document.objects.filter(
        receiver=request.user
    ).select_related('sender', 'sender__profile', 'department').exclude(status='approved').order_by('-created_at')
    return render(request, 'sender/inbox.html', {'documents': documents})

@login_required
def review_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            document.status = 'approved'
            document.signed_at = timezone.now()
            sig_data = f"{document.id}-{request.user.username}-{timezone.now()}"
            document.signature_hash = hashlib.sha256(sig_data.encode()).hexdigest()
            document.save()

            # Email notification sa nag-upload
            if document.sender.email:
                send_document_email_task.delay(document.id, document.sender.email)
            
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
    archived_documents = Document.objects.filter(
        (Q(sender=request.user) | Q(receiver=request.user)),
        is_archived=True
    ).select_related('sender', 'receiver', 'department').order_by('-created_at')
    return render(request, 'sender/archived_list.html', {'documents': archived_documents})

@login_required
def unarchive_document(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    document.is_archived = False
    document.save()
    return redirect('archived_list')