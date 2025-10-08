from .models import SiteSettings, SiteTheme

def site_settings(request):
	ss = SiteSettings.objects.select_related("theme").first()
	theme = (ss.theme if ss and ss.theme else SiteTheme.objects.first())
	return {
		"SITE_SETTINGS": ss,
		"SITE_THEME": theme,
	}
