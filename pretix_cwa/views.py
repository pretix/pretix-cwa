import hashlib
import io
import logging
import qrcode
import qrcode.image.svg
import re
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils.timezone import now
from django.views import View
from django.views.generic import TemplateView
from pretix.base.models import Event
from pretix.control.views.event import EventSettingsFormView, EventSettingsViewMixin
from pretix.multidomain.urlreverse import build_absolute_uri

from .forms import CWASettingsForm
from .generator import generate_url

logger = logging.getLogger(__name__)


class SettingsView(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = CWASettingsForm
    template_name = "pretix_cwa/settings.html"
    permission = "can_change_settings"

    def get_success_url(self) -> str:
        return reverse(
            "plugins:pretix_cwa:settings",
            kwargs={
                "organizer": self.request.event.organizer.slug,
                "event": self.request.event.slug,
            },
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data()
        token = hashlib.sha256(
            (
                f"{settings.SECRET_KEY}:pretix_cwa:signage:{self.request.event.pk}"
            ).encode()
        ).hexdigest()[:16]
        ctx["url_png"] = build_absolute_uri(
            self.request.event,
            "plugins:pretix_cwa:signage.png",
            kwargs={"token": token},
        )
        ctx["url_svg"] = build_absolute_uri(
            self.request.event,
            "plugins:pretix_cwa:signage.svg",
            kwargs={"token": token},
        )
        ctx["url_html"] = build_absolute_uri(
            self.request.event,
            "plugins:pretix_cwa:signage.html",
            kwargs={"token": token},
        )
        return ctx


class SignageMixin:
    def dispatch(self, request, *args, **kwargs):
        token = hashlib.sha256(
            (
                f"{settings.SECRET_KEY}:pretix_cwa:signage:{self.request.event.pk}"
            ).encode()
        ).hexdigest()[:16]
        if kwargs.get("token") != token:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_url(self):
        subevent = None
        if self.request.event.has_subevents:
            # Get one that's currently running
            subevent = self.request.event.subevents.filter(
                Q(date_admission__lt=now()) | Q(date_from__lt=now()), date_to__gt=now()
            ).last()

            # Else, get one that last started, except that was yesterday, then use the next one
            if not subevent:
                last_subevent = self.request.event.subevents.filter(
                    date_from__lte=now()
                ).last()
                next_subevent = self.request.event.subevents.filter(
                    date_from__gt=now()
                ).first()
                if last_subevent and next_subevent:
                    if (
                        last_subevent.date_from.astimezone(
                            self.request.event.timezone
                        ).date()
                        == now().astimezone(self.request.event.timezone).date()
                    ):
                        subevent = last_subevent
                    else:
                        subevent = next_subevent
                elif last_subevent:
                    subevent = last_subevent
                elif next_subevent:
                    subevent = next_subevent

        return generate_url(self.request.event, subevent)


class SignagePNGView(SignageMixin, View):
    def get(self, request, *args, **kwargs):
        qr = qrcode.QRCode()
        qr.add_data(self.get_url()[0])
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes)
        return HttpResponse(img_bytes.getvalue(), content_type="image/png")


class SignageSVGView(SignageMixin, View):
    def get(self, request, *args, **kwargs):
        qr = qrcode.QRCode()
        qr.add_data(self.get_url()[0])
        qr.make(fit=True)
        svg = qr.make_image(image_factory=qrcode.image.svg.SvgPathFillImage)
        svg_bytes = io.BytesIO()
        svg.save(svg_bytes)
        return HttpResponse(svg_bytes.getvalue(), content_type="image/svg+xml")


class SignageHTMLView(SignageMixin, TemplateView):
    template_name = "pretix_cwa/signage.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        url, df, dt = self.get_url()
        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.make(fit=True)
        svg = qr.make_image(image_factory=qrcode.image.svg.SvgPathFillImage)
        svg_bytes = io.BytesIO()
        svg.save(svg_bytes)
        ctx["svg"] = re.sub(r"<\?[^?]+\?>", "", svg_bytes.getvalue().decode())
        ctx["event"] = self.request.event
        ctx["df"] = df
        ctx["dt"] = dt

        ctx["refresh"] = max(min((dt - now()).seconds - 60, 600), 15)

        return ctx
