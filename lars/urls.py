from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import settings
from django.contrib import admin
from django.views.generic import TemplateView
from discuss.urls import threadpatterns, forumpatterns, challengepatterns, tagpatterns, newspatterns
from discuss.views import CategoryDetail, ThreadCreate
from entry.urls import deckpatterns, votepatterns
from entry.views import DeckList
from moderation.urls import modpatterns

admin.autodiscover()

urlpatterns = patterns('',
    #home page
    url(r'^/?$', 'lars.views.viewHome', name='view_home'),
    #admin page
    url(r'^admin/', include(admin.site.urls)),
    #Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    #various app urls
    #entry
    url(r'^deck', include(deckpatterns, app_name='entry', namespace='deck')),
    #vote
    url(r'^vote', include(votepatterns, app_name='entry', namespace='vote')),
    #other apps
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^comments/mod_flagged/?$', 'lars.views.flaggedComments_view', name='view_flagged_comments'),
    url(r'^comments/', include('django.contrib.comments.urls')),
    #discuss
    url(r'^news', include(newspatterns, app_name='discuss', namespace='news')),
    url(r'^thread', include(threadpatterns, app_name='discuss', namespace='thread')),
    url(r'^forum', include(forumpatterns, app_name='discuss', namespace='forum')),
    url(r'^challenge', include(challengepatterns, app_name='discuss', namespace='challenge')),
    url(r'^tag', include(tagpatterns, app_name='discuss', namespace='tag')),
    #moderation
    url(r'^moderation', include(modpatterns, app_name='moderation', namespace='mod')),
    #account-related urls
    url(r'^user/(?P<pk>\d+)/?$', 'lars.views.viewUser', name='view_user_profile'),
    url(r'^login/?$', 'lars.views.login_view', name='login_page'),
    url(r'^logout/?$', 'lars.views.logout_view', name='logout_page'),
    url(r'^account_disabled/?$', 'lars.views.accountDisabled_view', name='account_disabled_page'),
    url(r'^register/?$', 'lars.views.registration_view', name='registration_page'),
    url(r'^register/success.html$', TemplateView.as_view(template_name='registration_success.html'), name='registration_successful_page'),
    url(r'^prefs/?$', 'lars.views.preferences_view', name='preferences_page'),
    #static pages
    url(r'^about/?$', TemplateView.as_view(template_name='about.html'), name='about_page'),
    url(r'^contact/?$', TemplateView.as_view(template_name='contact.html'), name='contact_page'),
)


if getattr(settings, 'DEBUG', False) or getattr(settings, 'DEBUG_MEDIA', False):
    murl = getattr(settings, 'MEDIA_URL', '/media/').lstrip('/')
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % murl, 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT })
    )
    
urlpatterns += staticfiles_urlpatterns()