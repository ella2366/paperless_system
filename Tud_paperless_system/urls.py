from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    # 1. 2FA URLs (Dapat mauna ito para ma-override ang default login)
    path('', include(tf_urls)), 

    # 2. Admin Interface
    path('admin/', admin.site.urls),

    # 3. Main App URLs
    path('sender/', include('sender.urls')),
    
    # 4. Authentication (Logout)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]

# 5. Media Files handling
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)