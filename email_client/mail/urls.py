from django.urls import path, re_path

from . import views

app_name='mail'

urlpatterns = [
    path('', views.index, name='index'), # ~/mail (signin page)
    path('u/0/inbox', views.inbox, name='inbox'), # ~/mail/u/0/inbox (main inbox page)
    path('u/0/trash', views.trash_folder, name='trash'), # ~/mail/u/0/trash (trashed emails page)
    path('u/0/approved', views.approved_folder, name='approved'), # ~/mail/u/0/approved (approved emails page)
    re_path(r'^u/0/inbox/(?P<email_id>[0-9]+)$', views.inbox_email, name='inbox_email'), # ~/mail/u/0/inbox/<email_id> (single inbox email page)
    re_path(r'^u/0/trash/(?P<email_id>[0-9]+)$', views.trashed_email, name='trashed_email'), # ~/mail/u/0/trash/<email_id> (single trashed email page)
    re_path(r'^u/0/approved/(?P<email_id>[0-9]+)$', views.approved_email, name='approved_email'), # ~/mail/u/0/approved/<email_id> (single approved email page)
    path('logout_user', views.logout_user, name='logout_user'), # ~/mail/logout_user (log out button)
    path('ajax', views.ajax, name='ajax'), # ~/mail/ajax (URL for receiving click data)
    path('api', views.assign_credentials, name='api'), # ~/mail/api (URL for assigning username and password to participants)
    path('check', views.unread_check, name='check'), # ~/mail/check (URL for retrieving a user's total unread count)
    re_path(r'^delete/(?P<email_id>[0-9]+)/(?P<next_id>-?[0-9]+)$', views.delete, name='delete'), # ~/mail/delete/<this_id>/<next_id> (deletes current email, forwards to next emaik) 
    re_path(r'^approve/(?P<email_id>[0-9]+)/(?P<next_id>-?[0-9]+)$', views.approve, name='approve'), # ~/mail/approve/<this_id>/<next_id> (approves current email, forwards to next emaik)
    re_path(r'^email_link/(?P<email_id>[0-9]+)$', views.email_link, name='email_link'), # ~/mail/email_link/<email_id> (forwards phishing link link to correct legitimate site)
]