from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView, VideosListView, VideoDetailView

def healthz(_request):
    return HttpResponse("ok", content_type="text/plain")

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("videos/", VideosListView.as_view(), name="videos_list"),
    path("videos/<slug:slug>/", VideoDetailView.as_view(), name="video_detail"),
    path("admin/", admin.site.urls),
    path("ia/", include("ai_search.urls")),
    path("healthz", healthz),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
