from django.urls import path, re_path

from . import views

app_name='mail'

urlpatterns = [
    path('', views.index, name='index'),
    path('u/0/inbox/', views.inbox, name='inbox'),
    re_path(r'^u/0/inbox/(?P<email_id>[0-9]+)$', views.email, name='email'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('ajax', views.ajax, name='ajax'),
    path('api', views.assign_credentials, name='api'),
    path('trash', views.trash, name='trash'),
    path('flagged', views.flagged, name='flagged'),
    # path('delete/<int:email_id>/<int:next_id>/', views.delete, name='delete'),
    # path('flag/<int:email_id>/<int:next_id>/', views.flag, name='flag'),
    re_path(r'^flag/(?P<email_id>[0-9]+)/(?P<next_id>-?[0-9]+)$', views.flag, name='flag'),
    re_path(r'^delete/(?P<email_id>[0-9]+)/(?P<next_id>-?[0-9]+)$', views.delete, name='delete'),
]