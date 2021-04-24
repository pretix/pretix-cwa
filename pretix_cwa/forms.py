from django import forms
from django.utils.translation import gettext_lazy as _
from i18nfield.forms import I18nFormField, I18nTextarea, I18nTextInput
from pretix.base.email import get_available_placeholders
from pretix.base.forms import PlaceholderValidator, SettingsForm


class CWASettingsForm(SettingsForm):
    cwa_mode = forms.ChoiceField(
        label=_("QR code generation mode"),
        choices=(
            ("daily", _("New QR code per day")),
            (
                "subevent",
                _(
                    "New QR code per time slot (should only be used if your venue is guaranteed to be empty "
                    "after every time slot)"
                ),
            ),
        ),
    )

    cwa_location_type = forms.ChoiceField(
        label=_("Location type"),
        choices=(
            ("0", _("Unspecified")),
            ("3", _("Retail")),
            ("4", _("Food service (restaurant, hotel, bar)")),
            ("5", _("Craft")),
            ("6", _("Workplace")),
            ("7", _("Educational Institution (school, lecture hall, library)")),
            ("8", _("Public building (public office, museum)")),
            ("1", _("Other permanent location")),
            ("9", _("Cultural event (concert, exhibition, …)")),
            ("10", _("Club activity (sports, general assemblies)")),
            ("11", _("Private event")),
            ("12", _("Worship service")),
            ("2", _("Other event")),
        ),
    )

    cwa_default_length = forms.IntegerField(
        label=_("Default check-in length in minutes"),
        help_text=_("If kept empty, it will automatically be filled from the event"),
        required=False,
    )

    cwa_checkin_email = forms.BooleanField(
        label=_("Send email with CWA check-in link after ticket check-in scan"),
        required=False,
    )

    cwa_checkin_email_subject = I18nFormField(
        label=_("Email Subject"),
        required=True,
        widget=I18nTextInput,
    )

    cwa_checkin_email_body = I18nFormField(
        label=_("Email Body"),
        required=True,
        widget=I18nTextarea,
    )

    base_context = {
        "cwa_checkin_email_subject": ["event", "order", "position"],
        "cwa_checkin_email_body": ["event", "order", "position"],
    }

    def _set_field_placeholders(self, fn, base_parameters):
        phs = [
            "{%s}" % p
            for p in sorted(
                get_available_placeholders(self.event, base_parameters).keys()
            )
        ]
        ht = _("Available placeholders: {list}").format(list=", ".join(phs))
        if self.fields[fn].help_text:
            self.fields[fn].help_text += " " + str(ht)
        else:
            self.fields[fn].help_text = ht
        self.fields[fn].validators.append(PlaceholderValidator(phs))

    def __init__(self, *args, **kwargs):
        self.event = kwargs.get("obj")
        super().__init__(*args, **kwargs)
        for k, v in self.base_context.items():
            self._set_field_placeholders(k, v)
