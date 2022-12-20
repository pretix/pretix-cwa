from django.urls import re_path

from .views import SettingsView, SignageHTMLView, SignagePNGView, SignageSVGView

urlpatterns = [
    re_path(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/settings/cwa/$",
        SettingsView.as_view(),
        name="settings",
    ),
]

event_patterns = [
    re_path(
        r"^cwa/(?P<token>[^/]+)/qrcode.png$",
        SignagePNGView.as_view(),
        name="signage.png",
    ),
    re_path(
        r"^cwa/(?P<token>[^/]+)/qrcode.svg$",
        SignageSVGView.as_view(),
        name="signage.svg",
    ),
    re_path(
        r"^cwa/(?P<token>[^/]+)/qrcode.html$",
        SignageHTMLView.as_view(),
        name="signage.html",
    ),
]
