from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_document, name='upload_document'),
    path('inbox/', views.inbox, name='inbox'),
    path('review/<int:doc_id>/', views.review_document, name='review_document'),
    
    # Action: The process of moving a file to archive
    path('archive-action/<int:doc_id>/', views.archive_document, name='archive_document'),

    # Page: The list where archived files are viewed
    path('archived-files/', views.archived_list, name='archived_list'),
]