from django.utils.translation import gettext_lazy
from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    default = True
    name = "pretix_cwa"
    verbose_name = "CWA integration"

    class PretixPluginMeta:
        name = gettext_lazy("CWA integration")
        author = "pretix team"
        description = gettext_lazy(
            "Integrating pretix with the Corona Warn App (CWA) allows you to generate CWA event QR codes for your "
            "event on demand and email them to attendees after check-in."
        )
        picture = "pretix_cwa/logo.svg"
        visible = True
        version = __version__
        category = "INTEGRATION"
        compatibility = "pretix>=3.17.0"

    def ready(self):
        from . import signals  # NOQA


