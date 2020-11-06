from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView
from views import DeckDetail, DeckList, DeckCreate, DeckUpdate, DeckDelete, searchView
import datetime

deckpatterns = patterns('',
    # entry object
    url(r'^s?/?$', DeckList.as_view(), name='list'),
    url(r'^/(?P<pk>\d+)/?$', DeckDetail.as_view(), name='view'),
    url(r'^/(?P<pk>\d+)/update/?$', DeckUpdate.as_view(), name='update'),
    url(r'^/(?P<pk>\d+)/delete/?$', DeckDelete.as_view(), name='delete'),
    url(r'^/create/?$', DeckCreate.as_view(),  name='create'),
    url(r'^/search/?$', DeckList.as_view(), {'search':True}, name='search'),
)

votepatterns = patterns('',
    url(r'/entry/(?P<pk>\d+)/?$', 'entry.views.vote', name='deck'), #send vote
    #vote list
)

#urlpatterns += staticfiles_urlpatterns()