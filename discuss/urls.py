from django.conf.urls import patterns, include, url
from views import (ThreadDetail, ThreadCreate, ThreadUpdate, ThreadDelete, ThreadList, 
                    CategoryDetail, CategoryUpdate, CategoryDelete, CategoryList, CategoryCreate, 
                    ChallengeDetail, ChallengeUpdate, ChallengeDelete, ChallengeList, ChallengeCreate, 
                    TagList, TagDetail, thread_challenge_view)
from lars import settings
import models, forms


newspatterns = patterns('',
    url(r'^s?/?$', CategoryDetail.as_view(), {'pk':settings.NEWS_CATEGORY_PK}, name='list'),
    url(r'^/(?P<pk>\d+)/?$', ThreadDetail.as_view(), name='view'),
    url(r'^/(?P<pk>\d+)/update/?$', ThreadUpdate.as_view(form_class=forms.NewsForm), name='update'),
    url(r'^/create/?$', ThreadCreate.as_view(form_class=forms.NewsForm), name='create'),
    url(r'^/(?P<thread_pk>\d+)/challenge/?$', thread_challenge_view, name='attach_challenge'),
)

threadpatterns = patterns('',
    url(r'^s?/?$', CategoryList.as_view(), name='list'),
    url(r'^/(?P<pk>\d+)/?$', ThreadDetail.as_view(), name='view'),
    url(r'^/(?P<pk>\d+)/update/?$', ThreadUpdate.as_view(), name='update'),
    url(r'^/(?P<pk>\d+)/delete/?$', ThreadDelete.as_view(), name='delete'),
    url(r'^/create/?$', ThreadCreate.as_view(), name='create'),
    url(r'^/(?P<thread_pk>\d+)/challenge/?$', thread_challenge_view, name='attach_challenge'),
    url(r'^/search/?$', ThreadList.as_view(), {'search':True}, name='search'),
)

forumpatterns = patterns('',
    url(r'^s?/?$', CategoryList.as_view(), name='list'),
    url(r'^/(?P<pk>\d+)/?$', CategoryDetail.as_view(), name='view'),
    url(r'^/(?P<pk>\d+)/?$', CategoryUpdate.as_view(), name='update'),
    url(r'^/(?P<pk>\d+)/?$', CategoryDelete.as_view(), name='delete'),                         
    url(r'^/create/?$', CategoryCreate.as_view(), name='create'),
    url(r'^/search/?$', ThreadList.as_view(), {'search':True}, name='search'),
)

challengepatterns = patterns('',
    url(r'^s?/?$', ChallengeList.as_view(), name='list'),
    url(r'^/(?P<pk>\d+)/?$', ChallengeDetail.as_view(), name='view'),
    url(r'^/(?P<pk>\d+)/update/?$', ChallengeUpdate.as_view(), name='update'),
    url(r'^/(?P<pk>\d+)/delete/?$', ChallengeDelete.as_view(), name='delete'),                         
)

tagpatterns = patterns('', 
    url(r'^s?/?$', TagList.as_view(), name='list'),
    url(r'^/(?P<pk>\d+)/?$', TagDetail.as_view(), name='view'),
)