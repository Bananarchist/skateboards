from django.conf.urls import patterns, include, url
from views import ModEventDetail, ModEventList, ModEventCreate, ModEventDelete

modpatterns = patterns('',
    # entry object
    url(r'^/?$', ModEventList.as_view(), name='list'),
    url(r'^/(?P<pk>\d+)/?$', ModEventDetail.as_view(), name='view'),
    url(r'^/(?P<pk>\d+)/delete/?$', ModEventDelete.as_view(), name='delete'),
    url(r'^/create/?$', ModEventCreate.as_view(),  name='create'),
    #url(r'^/search/?$', ModEventList.as_view(), {'search':True}, name='search'),
)