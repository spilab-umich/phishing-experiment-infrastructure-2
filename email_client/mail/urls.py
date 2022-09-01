from django.urls import path, re_path

from . import views

app_name='mail'

urlpatterns = [
    path('', views.index, name='index'),
    path('u/0/inbox', views.inbox, name='inbox'),
    path('u/0/trash', views.trash, name='trash'),
    path('u/0/flagged', views.flagged, name='flagged'),
    path('u/0/approved', views.approved, name='approved'),
    re_path(r'^u/0/inbox/(?P<email_id>[0-9]+)$', views.inbox_email, name='inbox_email'),
    re_path(r'^u/0/flagged/(?P<email_id>[0-9]+)$', views.flagged_email, name='flagged_email'),
    re_path(r'^u/0/trash/(?P<email_id>[0-9]+)$', views.trashed_email, name='trashed_email'),
    re_path(r'^u/0/approved/(?P<email_id>[0-9]+)$', views.approved_email, name='approved_email'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('ajax', views.ajax, name='ajax'),
    path('api', views.assign_credentials, name='api'),
    path('check', views.unread_check, name='check'),
    # path('delete/<int:email_id>/<int:next_id>/', views.delete, name='delete'),
    # path('flag/<int:email_id>/<int:next_id>/', views.flag, name='flag'),
    re_path(r'^flag/(?P<email_id>[0-9]+)/(?P<next_id>-?[0-9]+)$', views.flag, name='flag'),
    re_path(r'^delete/(?P<email_id>[0-9]+)/(?P<next_id>-?[0-9]+)$', views.delete, name='delete'),
    re_path(r'^approve/(?P<email_id>[0-9]+)/(?P<next_id>-?[0-9]+)$', views.approve, name='approve'),
    re_path(r'^email_link/(?P<email_id>[0-9]+)$', views.email_link, name='email_link'),
]