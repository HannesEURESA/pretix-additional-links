from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from i18nfield.fields import I18nCharField, I18nTextField
from pretix.base.models import LoggedModel


class Links(LoggedModel):
    event = models.ForeignKey('pretixbase.Event', on_delete=models.CASCADE)
    slug = models.CharField(
        max_length=150, db_index=True, verbose_name=_('Link Slug'),
        validators=[
            RegexValidator(
                regex="^[a-zA-Z0-9.-]+$",
                message=_("The slug may only contain letters, numbers, dots and dashes.")
            ),
        ],
        help_text=_("This will be used to generate the Slug of the Link. Please only use latin letters, "
                    "numbers, dots and dashes. You cannot change this afterwards.")
    )
    position = models.IntegerField(default=0)
    title = I18nCharField(verbose_name=_('Link title'))
    link_url = I18nCharField(verbose_name=_('Link url'))
    link_on_frontpage = models.BooleanField(default=False, verbose_name=_('Show link on the event start page'))
    link_in_footer = models.BooleanField(default=False, verbose_name=_('Show link on the event page within the Footer'))
    link_in_head = models.BooleanField(default=False, verbose_name=_('Show link on the event page within the Header'))
    

    class Meta:
        ordering = ['position', 'title']
