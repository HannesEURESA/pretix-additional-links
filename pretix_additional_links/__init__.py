from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PluginApp(AppConfig):
    name = 'pretix_additional_links'
    verbose_name = 'Additional Links'

    class PretixPluginMeta:
        name = _('Additional Links')
        author = 'Hannes'
        category = 'FEATURE'
        description = _('Allows you to add static links to your event site, for example for a FAQ, '
                        'terms of service, etc.')
        visible = True
        version = '1.2.0'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_additional_links.PluginApp'
