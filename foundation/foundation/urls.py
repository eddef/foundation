# Django.core
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from donations import views
from donations.models import *

urlpatterns = patterns('',

    (r'^join_nonprofits/$', views.new_organization),
    (r'^join_nonprofits/thanks/$', views.thanks),
    (r'^nonprofits/$', views.organization_list),
    (r'^nonprofit/(?P<organization_id>[0-9]+)/$', views.organization_detail),

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
