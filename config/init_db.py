import os, django, sys, json, datetime, email, mimetypes, re
from bs4 import BeautifulSoup
from pathlib import Path

config_path = Path("config/") # Before we append the file path, grab the path to the config file
email_folder = config_path / Path("raw_eml/")

sys.path.append('email_client/') # Change path so email_client.settings will work below
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_client.settings")
django.setup()

# Input number of users
n_users = 3000

n_test_users = 33

# Input number of groups
n_of_groups = 11

# Load email metadata
## MOST RECENT EMAILS SHOULD GO FIRST
json_fname = "emails.json"
open_json_file = config_path / Path(json_fname)

with open(open_json_file) as f:
    d = json.load(f)

email_data = []
for item in d["emails"]:
    email_data.append(item)

from mail.models import User, Mail
import random as rd
import string
from random import shuffle

list_of_p_domains = {
    3:['https://www.hrzzhfs.xyz/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYv', 
       'https://www.financial-pay.info/global-service/?upn=9O-2F0uOvVudG71uY6JZBiNBA2kJ1h0T8XTI4yLNm5Md', 
       'https://www.westernunion-pay.com/global-service/track-transfer/?mid=IDS23031396257174xZOq8beIND'],
    2:['https://dkozzlfods.info/?upn=Q0VOMzaXxjJtwt0qTuNrrDpoPL8Q50aMecLQskTq49ebjSLEfnIc2sOFoyEqqh8XG3', 
       'https://www.online-shopping-payment.com/?ctPayload=H4sIAAAAAAAAA12QwW7CMBBE22F8VnKtmxHSc5FrXqsQ',
       'https://www.walmart-payment.com/?upn=31lcBBFrKkrK4MwiV2J2egimukuh7R5G2XSsnoDDvoYMcZXguaG-2BaZjU'],
    1:['https://etooicdfi.studio/f/a/LtmMzAePjiulEFh9JXydXg~~/AAAAAQA~/RgRloD6JP0QgaHR0cHM6Ly9zbWFydC5s',
       'https://www.client-mail-services.com/_t/c/A1020005-1735F31E6028AC6D-68C618EC?l=AABkT3mkCxlWQIg7',
       'https://mail.google-services.com/?code=hvAga1lsCwkvVdPMyOPhaiWXSCOIprz78ck43JEhgg6GosfY%2BzuPKA'],
}

# Read emails in folder, save to models in database
def read_emails():
    emails = os.listdir(email_folder)
    
    if emails is None:
        # Make sure adjustments have been made to emails, e.g., link ids, phishing URLs, etc
        print("No emails found. Please place .eml files into the config/raw_eml folder")
        exit()
    # Create an empty list to store email objects
    results = []
    # Create reference IDs for each email
    i = 1
    for mail in emails:
        with open(email_folder / Path(mail), 'r') as fp:
            msg = email.parser.Parser(policy=email.policy.SMTP).parse(fp)
            
            body = msg.get_body(preferencelist=('plain','html'))
            sepr = '<'
            sender = msg['from'].split(' ' + sepr)
            # Add the separator back if it was removed 
            # This is so sender addresses are in brackets <>
            if len(sender) > 1:
                sender[1] = sepr + sender[1]
            sender = [x.replace("\"","").rstrip() for x in sender] 

            ## Matches the .eml file to the correct email metadata
            ## Search email_data for the key value pair that matches current email_id
            email_metadata = next( item for item in email_data if item['email_id'] == i)
            email_to_add = {
                # 'from' item needs to be split into sender and sender address
                'from': sender,
                'subject': msg['subject'],
                'email_id': i,
                'num_links': email_metadata['num_links'],
                'phish_id': email_metadata['link_id'],
                'preview': email_metadata['preview'],
                'is_phish': email_metadata['is_phish']
            }
            results.append(email_to_add)
            ''' Write emails to HTML file '''
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_content_subtype() != 'html':
                    continue
                if part.get_content_maintype() == 'text':
                    with open(config_path / Path('raw_html') / Path(str(i)+'.html'), 'w', encoding='utf-8') as fol:
                        payload = part.get_payload(decode=True)

                        # Add ids to links and change the phishing url
                        rev_payload = revise_html(payload, email_to_add)
                        fol.write(str(rev_payload))
            i+=1
    return results

def revise_html(html, email):
    """Add Id numbers (#) to each hyperlink in each HTML file.
       Then change all hyperlink targets to _blank
    """
    email_id = email['email_id']
    p_link = email['phish_id']
    is_phish = email['is_phish']
    soup = BeautifulSoup(html, 'html.parser')
    for num, tag in enumerate(soup.find_all('a')):
        tag['id'] = (num+1) * 10
        tag['target'] = "_blank"
        # check if the current link id  matches the phish_id of the email
        if ((p_link == tag['id']) & is_phish):
        #     # pick a shuffled domain manipulation wrt the email_id
            tag['href'] = '{{email.p_url}}'
    return soup


all_emails = read_emails()

num_emails = len(all_emails)

def order_emails(emails):
    ''' Order the emails so that:
            - The emails appear in random order
            - All 3 phishing warnings appear in the first n-2 emails
            - The last 2 emails are benign '''

    phishing_emails = [x for x in all_emails if x['is_phish']]
    benign_emails = [x for x in all_emails if not x['is_phish']]
    shuffle(benign_emails)    
    first_emails = phishing_emails + benign_emails[:-2]
    shuffle(first_emails)
    last_emails = benign_emails[-2:]
    return first_emails+last_emails


# string.ascii_letters contains both upper and lower case letters
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
    user = User()
    # Append usernameNumber to 'username' (e.g. usernameXXXX)
    user.username = 'username{}'.format(usernameNumbers[i])
    # Assign to one of the group numbers
    user.group_num = i % n_of_groups
    user.unread_count = num_emails
    user.code = codelist[i]
    user.assigned = False
    # user.set_password('pass1234')
    user.save()

    domain_manip_available = [0, 1, 2]
    shuffle(domain_manip_available)

    # Most recent email should be saved first (hence .pop() below)
    dates = [
        'Fri, 4 Nov 2022 8:19:30 -0700',
        'Tue, 8 Nov 2022 9:19:30 -0700',
        'Sun, 13 Nov 2022 10:19:30 -0700',
        'Thu, 17 Nov 2022 7:19:30 -0700',
        'Thu, 17 Nov 2022 7:19:30 -0700',
        'Sat, 19 Nov 2022 9:19:30 -0700',
        'Mon, 21 Nov 2022 8:19:30 -0700',
        'Tue, 22 Nov 2022 9:19:30 -0700',
        'Fri, 25 Nov 2022 8:19:30 -0700',
        'Sun, 27 Nov 2022 10:19:30 -0700',
        'Wed, 30 Nov 2022 10:19:30 -0700',
        'Sat, 3 Dec 2022 1:19:30 -0700',
        'Sun, 4 Dec 2022 2:19:30 -0700',
        'Thu, 8 Dec 2022 2:19:30 -0700',
        'Sat, 10 Dec 2022 1:19:30 -0700',
        'Sun, 11 Dec 2022 10:19:30 -0700',
    ]
    email_counter = 1
    for email in order_emails(all_emails):
        new = Mail()
        new.user = user
        new.sender = email['from'][0]
        # sender always has an email address and optionally a name
        # e.g., ["Justin Petelka", "jpetelka@gmail.com"]
        # OR ["jpetelka@gmail.com"]
        if (len(email['from']) > 1):
            new.sender_address = email['from'][1]
        new.preview = email['preview']
        #Adjust date
        UTCdate = datetime.datetime.strptime(dates.pop(), '%a, %d %b %Y %H:%M:%S %z')
        readible_date = datetime.datetime.strftime(UTCdate, '%m/%d/%y')
        new.time_sent = readible_date
        new.subject = email['subject']
        new.ref = email['email_id']
        new.phish_id = email['phish_id']
        new.num_links = email['num_links']
        new.phish_id = email['phish_id']
        if email['is_phish']:
            new.is_phish = True 
            # TODO: SAVE DOMAIN MANIPULATION ID TO DB
            # domain_manip = int(domain_manip_available.pop())
            new.p_url = list_of_p_domains[int(email['email_id'])][int(domain_manip_available.pop())] # This lets us randomize domain manipulation, .pop avoids replacement
        if (num_emails - 1) == email_counter:
            new.is_fp = True
        new.save()
        email_counter+=1

# Create a user to login into
# This helps with checking the inbox
for i in range(0, n_test_users):
    user = User()
    user.username = 'tempuser'+str(i)
    user.group_num = i % n_of_groups
    user.unread_count = num_emails
    user.code = '432dsa4f'
    ### Set this password for test accounts ###
    user.set_password('TestPassword')
    user.assigned = True
    user.save()
    domain_manip_available = [0, 1, 2] # we used three forms of domain manipulation. domain manipulation is (a) random and (b) without replacement
    shuffle(domain_manip_available)
    dates = [
        'Fri, 4 Nov 2022 8:19:30 -0700',
        'Tue, 8 Nov 2022 9:19:30 -0700',
        'Sun, 13 Nov 2022 10:19:30 -0700',
        'Thu, 17 Nov 2022 7:19:30 -0700',
        'Thu, 17 Nov 2022 7:19:30 -0700',
        'Sat, 19 Nov 2022 9:19:30 -0700',
        'Mon, 21 Nov 2022 8:19:30 -0700',
        'Tue, 22 Nov 2022 9:19:30 -0700',
        'Fri, 25 Nov 2022 8:19:30 -0700',
        'Sun, 27 Nov 2022 10:19:30 -0700',
        'Wed, 30 Nov 2022 10:19:30 -0700',
        'Sat, 3 Dec 2022 1:19:30 -0700',
        'Sun, 4 Dec 2022 2:19:30 -0700',
        'Thu, 8 Dec 2022 2:19:30 -0700',
        'Sat, 10 Dec 2022 1:19:30 -0700',
        'Sun, 11 Dec 2022 10:19:30 -0700',
    ]
    email_counter = 1
    for email in order_emails(all_emails):
        new = Mail()
        new.user = user
        new.sender = email['from'][0]
        if (len(email['from']) > 1):
            new.sender_address = email['from'][1]
        new.preview = email['preview']
        #Adjust date for readability
        UTCdate = datetime.datetime.strptime(dates.pop(), '%a, %d %b %Y %H:%M:%S %z')
        readible_date = datetime.datetime.strftime(UTCdate, '%m/%d/%y')
        new.time_sent = readible_date
        new.subject = email['subject']
        new.ref = email['email_id']
        new.phish_id = email['phish_id']
        new.num_links = email['num_links']
        new.phish_id = email['phish_id']
        if email['is_phish']:
            new.is_phish = True 
            new.p_url = list_of_p_domains[int(email['email_id'])][int(domain_manip_available.pop())] # This lets us randomize domain manipulation, .pop() avoids replacement
        if (num_emails - 1) == email_counter:
            new.is_fp = True
        new.save()
        email_counter+=1
