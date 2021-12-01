from django.utils.translation import gettext_lazy

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

__version__ = "1.0.1"


class PluginApp(PluginConfig):
    name = "pretix_cwa"
    verbose_name = "CWA integration"

    class PretixPluginMeta:
        name = gettext_lazy("CWA integration")
        author = "pretix team"
        description = gettext_lazy("pretix integration for the Corona Warn App (CWA)")
        visible = True
        version = __version__
        category = "INTEGRATION"
        compatibility = "pretix>=3.17.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = "pretix_cwa.PluginApp"
