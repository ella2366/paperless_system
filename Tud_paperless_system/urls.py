from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views # Idagdag ito

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sender/', include('sender.urls')),
    
    # Idagdag ang line na ito para sa logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)