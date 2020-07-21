from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    # The numeric represention of group assignment
    group_num = models.IntegerField(blank=True, null=True)
    # The number of unread_emails in a User's Inbox
    unread_count = models.IntegerField(default=10)
    # Indicates whether a User name has been taken
    assigned = models.BooleanField(default=False)
    # I think this is their unique Qualtrics response ID
    response_id = models.CharField(default="0", max_length=50, null=True)
    # I think this is their MTurk reward code?
    code = models.CharField(default="Not Found", max_length=25)

    def __str__(self):
        return str(self.username) + ' - ' + str(self.group_num)

class Mail(models.Model):
    # User associated with a particular Mail object
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Name of Email sender, displayed in Inbox
    sender = models.CharField(max_length=250)
    # Email's preview text in the inbox
    preview = models.CharField(max_length=500, default='This is the preview text')
    # The time the email was sent
    time_sent = models.CharField(max_length = 20)
    # The email's subject line
    subject = models.CharField(max_length = 250, default='This is the subject')
    # The address of the Mail's sender
    sender_address = models.CharField(max_length = 50)
    # Indicator for whether a User has read the Mail object
    read = models.CharField(max_length = 20, default='unread')
    # The reference number of the Mail object
    ref = models.IntegerField(default=-1)
    # The number of links in a Mail object
    num_links = models.IntegerField(default=-1)

    def __str__(self):
        return str(self.ref) + ' - ' + self.sender

# Log object; recorded user-client link interactions

## Separate these into Server_logs and Client_logs for increased performance?
class Server_Logs(models.Model):
    # The username that generated the Log
    username = models.CharField(max_length=50)
    # The URL of the link 
    link = models.CharField(max_length=500)
    # Django documentation says I can use:
    # client_time = models.DateTimeField('client_time')
    # The timestamp from the client when the log was generated
    client_time = models.CharField(max_length=100)
    # The timestamp from the server when the log was received
    server_time = models.CharField(max_length=100, null=True)
    # The numeric represention of group assignment
    group_num = models.IntegerField(blank=True, null=True)
    # I think this is their unique Qualtrics response ID
    response_id = models.CharField(default="0", max_length=50, null=True)
    # I think this is the session_ID from somewhere?
    session_id = models.CharField(default="0", max_length=50, null=True)
    # The screen height of the client when the log was generated
    # The action recorded; click, hover, etc.
    action = models.CharField(max_length=20)
    # Numeric identifiers for each link in each email
    # Server-side link_ids are -1
    # All email link_ids are > 0
    # all other events are 0
    link_id = models.IntegerField(default=0)
    # IP address of client (I think this is bad???)
    # IP = models.CharField(null=True, max_length = 20)

    def __str__(self):
        return str(self.username) + ', ' + str(self.link) + ', ' + str(self.timestamp)


class Client_Logs(models.Model):
    # The username that generated the Log
    username = models.CharField(max_length=50)
    # The URL of the link 
    link = models.CharField(max_length=500)
    # Django documentation says I can use:
    # client_time = models.DateTimeField('client_time')
    # The timestamp from the client when the log was generated
    client_time = models.CharField(max_length=100)
    # The timestamp from the server when the log was received
    server_time = models.CharField(max_length=100, null=True)
    # The numeric represention of group assignment
    group_num = models.IntegerField(blank=True, null=True)
    # I think this is their unique Qualtrics response ID
    response_id = models.CharField(default="0", max_length=50, null=True)
    # I think this is the session_ID from somewhere?
    session_id = models.CharField(default="0", max_length=50, null=True)
    # The screen height of the client when the log was generated
    screen_height = models.IntegerField(default=0)
    # The screen width of the client when the log was generated
    screen_width = models.IntegerField(default=0)
    # Whether the statusbar was displaying something when the log was generated
    statusbar_visible = models.CharField(null=True, max_length=20)
    # The action recorded; click, hover, etc.
    action = models.CharField(max_length=20)
    # Numeric identifiers for each link in each email
    # Server-side link_ids are -1
    # All email link_ids are > 0
    # all other events are 0
    link_id = models.IntegerField(default=0)
    # the amount of time hovered if log is a hover event
    hover_time = models.IntegerField(default=-1)
    # IP address of client (I think this is bad???)
    # IP = models.CharField(null=True, max_length = 20)

    def __str__(self):
        return str(self.username) + ', ' + str(self.link) + ', ' + str(self.timestamp)