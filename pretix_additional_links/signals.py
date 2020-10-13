from django.dispatch import receiver
from django.template.loader import get_template
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _, get_language
from pretix.base.signals import logentry_display, event_copy_data
from pretix.control.signals import html_head, nav_event
from pretix.multidomain.urlreverse import eventreverse
from pretix.presale.signals import (
    footer_link, front_page_bottom, html_head as html_head_presale, checkout_confirm_messages, html_page_header
)

from .models import Links


@receiver(nav_event, dispatch_uid="links_nav")
def control_nav_links(sender, request=None, **kwargs):
    if not request.user.has_event_permission(request.organizer, request.event, 'can_change_event_settings',
                                             request=request):
        return []
    url = resolve(request.path_info)
    return [
        {
            'label': _('Links'),
            'url': reverse('plugins:pretix_additional_links:index', kwargs={
                'event': request.event.slug,
                'organizer': request.event.organizer.slug,
            }),
            'active': (url.namespace == 'plugins:pretix_additional_links'),
            'icon': 'list',
        }
    ]


@receiver(signal=event_copy_data, dispatch_uid="links_copy_data")
def event_copy_data_receiver(sender, other, **kwargs):
    for p in Links.objects.filter(event=other):
        p.pk = None
        p.event = sender
        p.save()


@receiver(signal=logentry_display, dispatch_uid="links_logentry_display")
def pretixcontrol_logentry_display(sender, logentry, **kwargs):
    event_type = logentry.action_type
    plains = {
        'pretix_additional_links.links.added': _('The link has been created.'),
        'pretix_additional_links.links.changed': _('The link has been modified.'),
        'pretix_additional_links.links.deleted': _('The link has been deleted.'),
    }

    if event_type in plains:
        return plains[event_type]


@receiver(footer_link, dispatch_uid="links_footer_links")
def footer_link_links(sender, request=None, **kwargs):
    cached = sender.cache.get('links_footer_links_' + get_language())
    if not cached:
        cached = [
            {
                'label': p.title,
                'url': p.link_url
                
            } for p in Links.objects.filter(event=sender, link_in_footer=True)
        ]
        sender.cache.set('links_footer_links_ ' + get_language(), cached)

    return cached

@receiver(html_page_header, dispatch_uid="links_html_page_header")
def html_page_header_links(sender, request=None, **kwargs):
    cached = sender.cache.get('links_html_page_header_' + get_language())
    if cached is None:
        urls = list(Links.objects.filter(event=sender, link_in_head=True))
        if urls:
            template = get_template('pretix_additional_links/page_header.html')
            cached = template.render({
                'event': sender,
                'urls': urls
            })
        else:
            cached = ""
        sender.cache.set('links_html_page_header_' + get_language(), cached)
    return cached

@receiver(signal=front_page_bottom, dispatch_uid="links_frontpage_links")
def pretixpresale_front_page_bottom(sender, **kwargs):
    cached = sender.cache.get('links_frontpage_links_' + get_language())
    if cached is None:
        urls = list(Links.objects.filter(event=sender, link_on_frontpage=True))
        if urls:
            template = get_template('pretix_additional_links/front_page.html')
            cached = template.render({
                'event': sender,
                'urls': urls
            })
        else:
            cached = ""
        sender.cache.set('links_frontpage_links_' + get_language(), cached)

    return cached
