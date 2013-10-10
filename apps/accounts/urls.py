from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',

    url(r'^current_user/$', views.CurrentUser.as_view(), name='current_user'),
    url(r'^login/$', views.Login.as_view(), name='login'),
    url(r'^logout/$', views.Logout.as_view(), name='logout'),
    url(r'^register/$', views.Register.as_view(), name='register'),
)

