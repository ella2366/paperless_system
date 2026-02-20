from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_document, name='upload_document'),
    path('inbox/', views.inbox, name='inbox'),
    path('review/<int:doc_id>/', views.review_document, name='review_document'),
    path('archive-action/<int:doc_id>/', views.archive_document, name='archive_document'),
    path('archived-files/', views.archived_list, name='archived_list'),
    
    path('send-chat/', views.send_chat, name='send_chat'),
    path('get-messages/<int:receiver_id>/', views.get_messages, name='get_messages'),

    # Password Reset Routes - Eto lang dapat ang nandito
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    # BURAHIN YUNG NASA ILALIM NITO NA MAY (...)
]