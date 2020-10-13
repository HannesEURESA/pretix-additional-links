from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/links/$',
        views.LinksList.as_view(),
        name='index'),
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/links/create$',
        views.LinksCreate.as_view(),
        name='create'),
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/links/(?P<page>\d+)/$',
        views.LinksUpdate.as_view(),
        name='edit'),
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/links/(?P<page>\d+)/delete$',
        views.LinksDelete.as_view(),
        name='delete'),
]

# event_patterns = [
#     url(r'^page/(?P<slug>[^/]+)/$', views.ShowPageView.as_view(), name='show'),
# ]
