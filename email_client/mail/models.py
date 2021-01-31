from django.db import models
from django.contrib.auth.models import AbstractUser

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