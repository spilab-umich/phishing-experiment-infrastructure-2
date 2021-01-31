import os, django, sys, json
from pathlib import Path
json_path = Path("config/") # Before I change the file path, grab the path to the config file

sys.path.append('email_client/') # Change path so email_client.settings will work below
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_client.settings")
django.setup()

from mail.models import User, Mail
import random as rd
import string
from random import shuffle

n_users = 1000
n_of_groups = 7

#Load email metadata
json_fname = "emails.json"
json_path = Path("config/")
open_json_file = json_path / json_fname

with open(open_json_file) as f:
    d = json.load(f)

emails = []
for item in d["emails"]:
    emails.append(item)

# Load warning metadata
warning_json_fname = 'phish_domains.json'
warning_json_path = Path('config/')
open_warning_json_file = warning_json_path / warning_json_fname

with open(open_warning_json_file) as f:
    d = json.load(f)

warning_data = []
for item in d['phish_domains']:
    warning_data.append(item)

phish_email_ids = [x['email_id'] for x in warning_data]
# print(phish_email_ids)



# These are the dates each email displayed in the inbox
time_sent = ['Dec 1', 'Dec 6', 'Dec 7', 'Dec 9', 'Dec 10', 'Dec 12', 'Dec 14', 'Dec 17', 'Dec 18', 'Dec 23']

letter_pool = string.ascii_letters+'1234567890'
codelist = []

# Generate a random eight-string reward code
def generatecode():
    str_code = ''
    for i in range(8):
        str_code += rd.choice(letter_pool)
    return str_code

# Create a list of codes for each participant
while len(codelist) < n_users:
    code = generatecode()
    # Ensure no duplicate codes
    if code not in codelist:
        codelist.append(code)

# Generate the numbers to append to username
usernameNumbers = rd.sample(range(0,9999), n_users)

#initialize users
for i in range(0, n_users):
    shuffle(emails)
    user = User()
    # Initialize the numbers as usernameXXXX
    user.username = 'username{}'.format(usernameNumbers[i])
    # Assign to one of seven groups [0-6]
    user.group_num = i % n_of_groups
    user.code = codelist[i]
    user.assigned = False
    # user.set_password('pass1234')
    user.save()

    # This loop decrements so the dates append in the proper order
    # First email should have the last time_sent
    j=9 
    for email in emails:
        new = Mail()
        new.user = user
        new.sender = email['sender']
        new.preview = email['preview']
        new.time_sent = time_sent[j]
        new.subject = email['subject']
        new.sender_address = email['sender_address']
        new.read = "unread"
        new.ref = email['ref']
        new.num_links = email['num_links']
        # print(email['ref'])
        if email['ref'] in phish_email_ids:
            new.is_phish = True 
            new.phish_id = next((item['link_id'] for item in warning_data if item['email_id'] == new.ref))
            # print(new.phish_id)
        new.save()
        j-=1

# Create a user to login into
# This helps with checking the inbox
for i in range(0, 200):
    user = User()
    user.username = 'tempuser'+str(i)
    user.group_num = i % n_of_groups
    user.code = '432dsa4f'
    ### Set this password ###
    user.set_password('TestPassword')
    user.assigned = True
    user.save()
    j=9
    for email in emails:
        new = Mail()
        new.user = user
        new.sender = email['sender']
        new.preview = email['preview']
        new.time_sent = time_sent[j]
        new.subject = email['subject']
        new.sender_address = email['sender_address']
        new.read = "unread"
        new.ref = email['ref']
        new.num_links = email['num_links']
        if email['ref'] in phish_email_ids:
            # print('phish detected')
            new.is_phish = True 
            new.phish_id = next((item['link_id'] for item in warning_data if item['email_id'] == new.ref))
        new.save()
        j-=1
exit()
