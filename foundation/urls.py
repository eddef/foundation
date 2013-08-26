# Django.core
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.shortcuts import redirect

def forum_hack(request, anystring):
    url = 'http://freicoin.freeforums.org/%s' % anystring

    if request.META['QUERY_STRING']:
        url += '?%s' % request.META['QUERY_STRING']
    return redirect(url)

urlpatterns = patterns('',

    # Foundation
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^copyright/$', TemplateView.as_view(template_name='copyright.html'), name='copyright'),

    # Included apps and their root
    url(r'', include('apps.accounts.urls')),
    url(r'^faucet/', include('apps.faucet.urls')),
    url(r'^nonprofits/', include('apps.donations.urls')),

    url(r'^(?P<anystring>.+)/$', forum_hack),
    # Examples:
    # url(r'^$', 'foundation.views.home', name='home'),
    # url(r'^foundation/', include('foundation.foo.urls')),

    ###################
    # Admin Interface #
    ###################

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
