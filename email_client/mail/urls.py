from django.urls import path, re_path

from . import views

app_name='mail'

urlpatterns = [
    path('', views.index, name='index'),
    path('u/0/inbox', views.inbox, name='inbox'),
    re_path(r'^u/0/inbox/(?P<email_id>[0-9]+)$', views.email, name='email'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('ajax', views.ajax, name='ajax'),
    path('api', views.assign_credentials, name='api'),
]