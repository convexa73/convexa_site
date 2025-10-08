from django.views.generic import TemplateView, ListView, DetailView
from .models import Service, YouTubeVideo

class HomeView(TemplateView):
    template_name = "index.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["services"] = Service.objects.filter(active=True).order_by("order","title")[:12]
        # Só links de títulos (últimos 6)
        ctx["videos"] = YouTubeVideo.objects.filter(active=True).order_by("-published_at","-id")[:6]
        return ctx

class VideosListView(ListView):
    model = YouTubeVideo
    template_name = "videos/list.html"
    context_object_name = "videos"
    paginate_by = 18
    def get_queryset(self):
        return YouTubeVideo.objects.filter(active=True).order_by("-published_at","-id")

class VideoDetailView(DetailView):
    model = YouTubeVideo
    template_name = "videos/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug","")
        pk = slug.rsplit("-",1)[-1]
        return YouTubeVideo.objects.get(pk=pk)
