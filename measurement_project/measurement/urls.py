
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('capture_and_measure/', views.capture_and_measure, name='capture_and_measure'),
    path('calibrate/', views.calibrate, name='calibrate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
