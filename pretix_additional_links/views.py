from urllib.request import urlopen

import bleach
import lxml.html
from django import forms
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Max
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView, ListView, TemplateView, UpdateView,
)
from pretix.base.forms import I18nModelForm
from pretix.control.permissions import EventPermissionRequiredMixin, event_permission_required

from .models import Links


class LinksList(EventPermissionRequiredMixin, ListView):
    model = Links
    context_object_name = 'urls'
    paginate_by = 20
    template_name = 'pretix_additional_links/index.html'
    permission = 'can_change_event_settings'

    def get_queryset(self):
        return Links.objects.filter(event=self.request.event)

class LinksForm(I18nModelForm):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.get('event')
        super().__init__(*args, **kwargs)

    class Meta:
        model = Links
        fields = (
            'title', 'slug', 'link_url', 'link_in_footer', 'link_on_frontpage', 'link_in_head'
        )

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if Links.objects.filter(slug=slug, event=self.event).exists():
            raise forms.ValidationError(
                _('You already have a page on that Slug.'),
                code='duplicate_slug',
            )
        return slug

class LinksEditForm(LinksForm):
    slug = forms.CharField(label=_('Link Slug'), disabled=True)

    def clean_slug(self):
        return self.instance.slug


class LinksDetailMixin:
    def get_object(self, queryset=None) -> Links:
        try:
            return Links.objects.get(
                event=self.request.event,
                id=self.kwargs['page']
            )
        except Links.DoesNotExist:
            raise Http404(_("The requested link does not exist."))

    def get_success_url(self) -> str:
        return reverse('plugins:pretix_additional_links:index', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
        })


class LinksDelete(EventPermissionRequiredMixin, LinksDetailMixin, DeleteView):
    model = Links
    form_class = LinksForm
    template_name = 'pretix_additional_links/delete.html'
    context_object_name = 'links'
    permission = 'can_change_event_settings'

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.log_action('pretix_additional_links.links.deleted', user=self.request.user)
        self.object.delete()
        messages.success(request, _('The selected link has been deleted.'))
        self.request.event.cache.clear()
        return HttpResponseRedirect(self.get_success_url())


class LinksEditorMixin:

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.request.event
        return kwargs


class LinksUpdate(EventPermissionRequiredMixin, LinksDetailMixin, LinksEditorMixin, UpdateView):
    model = Links
    form_class = LinksEditForm
    template_name = 'pretix_additional_links/form.html'
    context_object_name = 'links'
    permission = 'can_change_event_settings'

    def get_success_url(self) -> str:
        return reverse('plugins:pretix_additional_links:edit', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
            'page': self.object.pk
        })

    @transaction.atomic
    def form_valid(self, form):
        messages.success(self.request, _('Your changes have been saved.'))
        if form.has_changed():
            self.object.log_action(
                'pretix_additional_links.links.changed', user=self.request.user, data={
                    k: form.cleaned_data.get(k) for k in form.changed_data
                }
            )
        self.request.event.cache.clear()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('We could not save your changes. See below for details.'))
        return super().form_invalid(form)


class LinksCreate(EventPermissionRequiredMixin, LinksEditorMixin, CreateView):
    model = Links
    form_class = LinksForm
    template_name = 'pretix_additional_links/form.html'
    permission = 'can_change_event_settings'
    context_object_name = 'links'

    def get_success_url(self) -> str:
        return reverse('plugins:pretix_additional_links:index', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug,
        })

    @transaction.atomic
    def form_valid(self, form):
        form.instance.event = self.request.event
        form.instance.event = self.request.event
        messages.success(self.request, _('The new link has been created.'))
        ret = super().form_valid(form)
        form.instance.log_action('pretix_additional_links.links.added', data=dict(form.cleaned_data),
                                 user=self.request.user)
        self.request.event.cache.clear()
        return ret

    def form_invalid(self, form):
        messages.error(self.request, _('We could not save your changes. See below for details.'))
        return super().form_invalid(form)
