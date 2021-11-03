import os, django, sys, json, datetime, html2text
# from email.parser import Parser, BytesParser
# from email import policy
import email, mimetypes
from pathlib import Path
# from bs4 import BeautifulSoup
# import eml_parser
config_path = Path("config/") # Before we append the file path, grab the path to the config file
email_folder = config_path / Path("raw_emails/")

sys.path.append('email_client/') # Change path so email_client.settings will work below
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_client.settings")
django.setup()

# Input number of users
n_users = 0
# Input number of treatment groups
n_of_groups = 3

# def getmailheader(header_text, default='ascii'):
#     try:
#         headers = email.Header.decode_header(header_text)
#     except email.Errors.HeaderParseError:
#         return header_text.encode('ascii', 'replace').decode('ascii')
#     else:
#         for i, (text, charset) in enumerate(headers):
#             try:
#                 headers[i] = unicode(text, charset or default, errors='replace')
#                 except LookupError
#                 headers[i] = unicode(text, default, errors='replace')
#             return u"".join(headers)

# Read emails in folder, save to models in database
def read_emails():
    emails = os.listdir(email_folder)
    
    if emails is None:
        # Make sure adjustments have been made to emails, e.g., link ids, phishing URLs, etc
        print("No emails found. Please place .eml files into the config/raw_emails folder")
        exit()
    # Create an empty list to store email objects
    results = []
    # Create reference IDs for each email
    i = 1
    # Convert html to text for preview pane
    h = html2text.HTML2Text()
    h.ignore_links = True
    # pol = email.policy.SMTP
    for mail in emails:
        with open(email_folder / Path(mail), 'r') as f:
            msg = email.message_from_file(f)
            for part in msg.walk():
                # if part.get_content_maintype() == 'multipart':
                if part.is_multipart():
                    print("Multipart found")
                    print(part.is_multipart())
                    continue
                with open(Path('email_client/mail/templates/mail/emails') / Path(str(i)+'.html'), 'wb') as fol:
                    # new_payload = payload.replace('=\n', '')
                    fol.write(part.get_payload(decode=True))
                    i+=1
                
                

            # try:
            #     content = msg.get_body(preferencelist('plain','html'))
            # except KeyError:
            #     print("This message does not have a printable HTML body")
            #TO DO: clean eml files from 3D and =\n nonsense


            # THIS WORKS BELOW
            # raw_msg = f.read()
            # msg = email.message_from_string(raw_msg)
            # content = email.contentmanager.get_content(msg)
            
            # payload = msg.get_body(preferencelist=('plain')).get_content()

            # Uncomment past this
            # payload = msg.get_payload()
            # # write the eml file in it's entiriety
            # with open(Path('email_client/mail/templates/mail/emails') / Path(str(i)+'.html'), 'w') as fol:
            #     new_payload = payload.replace('=\n', '')
            #     fol.write(new_payload)
            # email_to_add = {
            #     # 'from' item needs to be split into sender and sender address
            #     'from': msg['from'].replace(" ","").replace(">","").replace("\"","").split('<'),
            #     'subject': msg['subject'],
            #     'date': msg['date'],
            #     # 'payload': msg.get_payload(),
            #     'preview': h.handle(payload)[:250],
            #     'ref': i,
            # }
            # results.append(email_to_add)
            # i += 1
    return 
# emails_to_add = 
read_emails()
exit()

from mail.models import User, Mail
import random as rd
import string
from random import shuffle

## Can get rid of this ##
# #Load email metadata
# json_fname = "emails.json"
# # json_path = Path("config/")
# open_json_file = json_path / json_fname

# with open(open_json_file) as f:
#     d = json.load(f)

# emails = []
# for item in d["emails"]:
#     emails.append(item)


## Maybe Keep This ##
# Load warning metadata
# warning_json_fname = 'phish_domains.json'
# warning_json_path = Path('config/')
# open_warning_json_file = warning_json_path / warning_json_fname

# with open(open_warning_json_file) as f:
    # d = json.load(f)

# warning_data = []
# for item in d['phish_domains']:
#     warning_data.append(item)

# phish_email_ids = [x['email_id'] for x in warning_data]
# print(phish_email_ids)



# These are the dates each email displayed in the inbox
# time_sent = ['Dec 1', 'Dec 6', 'Dec 7', 'Dec 9', 'Dec 10', 'Dec 12', 'Dec 14', 'Dec 17', 'Dec 18', 'Dec 23']

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
    shuffle(emails_to_add)
    user = User()
    # Initialize the numbers as usernameXXXX
    user.username = 'username{}'.format(usernameNumbers[i])
    # Assign to one of the group numbers
    user.group_num = i % n_of_groups
    user.code = codelist[i]
    user.assigned = False
    # user.set_password('pass1234')
    user.save()

    # This loop decrements so the dates append in the proper order
    # First email should have the last time_sent
    j=9 
    for email in emails_to_add:
        new = Mail()
        new.user = user
        new.sender = email['from'][0]
        if (len(email['from']) > 1):
            new.sender_address = email['from'][1]
        new.preview = email['preview']
        new.time_sent = email['date']
        new.subject = email['subject']
        # new.sender_address = email['sender_address']
        new.read = "unread"
        new.ref = email['ref']
        # new.num_links = email['num_links']
        # print(email['ref'])
        # if email['ref'] in phish_email_ids:
            # new.is_phish = True 
            # new.phish_id = next((item['link_id'] for item in warning_data if item['email_id'] == new.ref))
            # print(new.phish_id)
        new.save()
        j-=1

# Create a user to login into
# This helps with checking the inbox
for i in range(0, 30):
    user = User()
    user.username = 'tempuser'+str(i)
    user.group_num = i % n_of_groups
    user.code = '432dsa4f'
    ### Set this password ###
    user.set_password('TestPassword')
    user.assigned = True
    user.save()
    j=9
    for email in emails_to_add:
        new = Mail()
        new.user = user
        new.sender = email['from'][0]
        if (len(email['from']) > 1):
            new.sender_address = email['from'][1]
        new.preview = email['preview']
        new.time_sent = email['date']
        new.subject = email['subject']
        new.read = "unread"
        new.ref = email['ref']
        # new.num_links = email['num_links']
        # if email['ref'] in phish_email_ids:
            # print('phish detected')
            # new.is_phish = True 
            # new.phish_id = next((item['link_id'] for item in warning_data if item['email_id'] == new.ref))
        new.save()
        j-=1
exit()
