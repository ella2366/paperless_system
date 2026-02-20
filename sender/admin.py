from django.contrib import admin
from .models import Profile, Document, Department, ChatMessage
from simple_history.admin import SimpleHistoryAdmin
from django.core.mail import send_mail

@admin.register(Profile)
class ProfileAdmin(SimpleHistoryAdmin):
    list_display = ('user', 'role', 'is_approved', 'gender')
    list_filter = ('role', 'is_approved')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        for profile in queryset:
            profile.is_approved = True
            profile.save()
            # Gmail Notification Logic
            send_mail(
                'TUD System: Account Approved',
                f'Hi {profile.user.username}, your account as {profile.role} has been approved. You can now login.',
                'tudellamae1@gmail.com',
                [profile.user.email],
                fail_silently=False,
            )
    approve_users.short_description = "Approve selected users and send Email"

@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    list_display = ('title', 'sender', 'status', 'created_at')

admin.site.register(ChatMessage)
admin.site.register(Department)