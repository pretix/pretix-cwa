from django.dispatch import receiver
from django.urls import resolve, reverse
from django.utils.translation import gettext_noop, gettext_lazy as _
from i18nfield.strings import LazyI18nString
from pretix.base.email import SimpleFunctionalMailTextPlaceholder
from pretix.base.settings import settings_hierarkey
from pretix.base.signals import checkin_created, register_mail_placeholders
from pretix.control.signals import nav_event_settings

from pretix_cwa.generator import generate_url

from .tasks import send_email


@receiver(nav_event_settings, dispatch_uid="cwa_nav")
def navbar_info(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(
        request.organizer, request.event, "can_change_event_settings", request=request
    ):
        return []
    return [
        {
            "label": _("CWA"),
            "url": reverse(
                "plugins:pretix_cwa:settings",
                kwargs={
                    "event": request.event.slug,
                    "organizer": request.organizer.slug,
                },
            ),
            "active": url.namespace == "plugins:pretix_cwa",
        }
    ]


@receiver(signal=checkin_created, dispatch_uid="cwa_checkin_created")
def checkin_created_receiver(sender, checkin, **kwargs):
    if not sender.settings.cwa_checkin_email:
        return

    if checkin.position.checkins.count() == 1:
        # only once per ticket
        send_email.apply_async(
            kwargs=dict(event=sender.pk, position=checkin.position.pk)
        )


@receiver(register_mail_placeholders, dispatch_uid="cwa_mail_placeholders")
def base_placeholders(sender, **kwargs):
    ph = [
        SimpleFunctionalMailTextPlaceholder(
            "cwa_url",
            ["event", "position"],
            lambda event, position: generate_url(event, position.subevent)[0],
            lambda event: generate_url(event, event.subevents.first())[0],
        ),
    ]
    return ph


settings_hierarkey.add_default("cwa_mode", "daily", str)
settings_hierarkey.add_default("cwa_default_length", None, int)
settings_hierarkey.add_default("cwa_location_type", "0", str)
settings_hierarkey.add_default("cwa_checkin_email", "True", bool)
settings_hierarkey.add_default(
    "cwa_checkin_email_subject",
    LazyI18nString.from_gettext(
        gettext_noop("Welcome! Remember to check in with Corona Warn App")
    ),
    LazyI18nString,
)
settings_hierarkey.add_default(
    "cwa_checkin_email_body",
    LazyI18nString.from_gettext(
        gettext_noop(
            "Hello,\n\n"
            "now that you've arrived, we kindly ask you to check in with Corona Warn App by clicking the following link:\n\n"
            "{cwa_url}\n\n"
            "Have a great time!\n\n"
            "Best regards,\n"
            "Your {event} team"
        )
    ),
    LazyI18nString,
)
