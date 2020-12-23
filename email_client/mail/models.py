from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser): 
    group_num = models.IntegerField(blank=True, null=True)  # The numeric represention of group assignment
    unread_count = models.IntegerField(default=10)  # The number of unread_emails in a User's Inbox
    assigned = models.BooleanField(default=False)  # Indicates whether a User name has been taken
    response_id = models.CharField(default="0", max_length=50, null=True)  # Survey response ID
    code = models.CharField(default="Not Found", max_length=25) # User's reward code

    def __str__(self):
        return str(self.username) + ' - ' + str(self.group_num)

class Mail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # User associated with a particular Mail object
    sender = models.CharField(max_length=250) # Name of Email sender, displayed in Inbox
    preview = models.CharField(max_length=500, default='This is the preview text') # Email's preview text in the inbox
    time_sent = models.CharField(max_length = 20) # The time the email was sent
    subject = models.CharField(max_length = 250, default='This is the subject') # The email's subject line
    sender_address = models.CharField(max_length = 50) # The address of the Mail's sender
    read = models.CharField(max_length = 20, default='unread') # Indicator for whether a User has read the Mail object
    ref = models.IntegerField(default=-1) # The reference number of the Mail object
    num_links = models.IntegerField(default=-1) # The number of links in a Mail object
    is_phish = models.BooleanField(default=False)
    phish_id = models.IntegerField(default=-1)

    def __str__(self):
        return str(self.ref) + ' - ' + self.sender

# Log object; recorded user-client link interactions

# ## Separate these into Server_logs and Client_logs for increased performance?
# class Server_Logs(models.Model):
#     username = models.CharField(max_length=50) # The username that generated the Log
#     link = models.CharField(max_length=500) # The URL of the link 
#     # Django documentation says I can use:
#     # client_time = models.DateTimeField('client_time')
#     # client_time = models.CharField(max_length=100) # The timestamp from the client when the log was generated
#     server_time = models.CharField(max_length=100, null=True) # The timestamp from the server when the log was received
#     group_num = models.IntegerField(blank=True, null=True) # The numeric represention of group assignment
#     response_id = models.CharField(default="0", max_length=50, null=True) # I think this is their unique Qualtrics response ID
#     session_id = models.CharField(default="0", max_length=50, null=True) # I think this is the session_ID from somewhere?
#     action = models.CharField(max_length=20) # The action recorded; click, hover, etc. # The screen height of the client when the log was generated
#     # Numeric identifiers for each link in each email
#     # Server-side link_ids are -1 
#     # All email link_ids are > 0
#     # all other events are 0
#     link_id = models.IntegerField(default=0)
#     # IP address of client (I think this is bad???)
#     # IP = models.CharField(null=True, max_length = 20)

#     def __str__(self):
#         return str(self.username) + ', ' + str(self.link) + ', ' + str(self.server_time)


# class Client_Logs(models.Model):
#     # The username that generated the Log
#     username = models.CharField(max_length=50)
#     # The URL of the link 
#     link = models.CharField(max_length=500)
#     # Django documentation says I can use:
#     # client_time = models.DateTimeField('client_time')
#     client_time = models.CharField(max_length=100) # The timestamp from the client when the log was generated
#     server_time = models.CharField(max_length=100, null=True) # The timestamp from the server when the log was received
#     group_num = models.IntegerField(blank=True, null=True) # The numeric represention of group assignment
#     response_id = models.CharField(default="0", max_length=50, null=True) # I think this is their unique Qualtrics response ID
#     session_id = models.CharField(default="0", max_length=50, null=True) # I think this is the session_ID from somewhere?
#     # screen_height = models.IntegerField(default=0) # The screen height of the client when the log was generated
#     # screen_width = models.IntegerField(default=0) # The screen width of the client when the log was generated
#     # statusbar_visible = models.CharField(null=True, max_length=20) # Whether the statusbar was displaying something when the log was generated
#     action = models.CharField(max_length=20) # The action recorded; click, hover, etc.
#     # Numeric identifiers for each link in each email
#     # Server-side link_ids are -1
#     # All email link_ids are > 0
#     # all other events are 0
#     link_id = models.IntegerField(default=0)
#     hover_time = models.IntegerField(default=-1) # the amount of time hovered if log is a hover event
#     # IP address of client (I think this is bad???)
#     # IP = models.CharField(null=True, max_length = 20)

#     def __str__(self):
#         return str(self.username) + ', ' + str(self.link) + ', ' + str(self.client_time)