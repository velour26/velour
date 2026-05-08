from .models import SiteSettings


def site_settings(request):
    try:
        settings = SiteSettings.get()
    except Exception:
        settings = None
    return {'site_settings': settings}
