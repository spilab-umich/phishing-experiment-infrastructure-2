import os, django, sys, json, datetime, email, mimetypes, re
# from email.parser import Parser, BytesParser
# from email import policy
from html.parser import HTMLParser 
import lxml.html
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

n_test_users = 3000
# Input number of groups
n_of_groups = 7

# class MyHTMLParser(HTMLParser):
#     prev = ""

#     def handle_data(self, data):
#         data = data.strip()
#         if not '\\r\\n' in data and not 'b\'' in data and data is not "":   
#             self.prev += " " + data
#             # print(self.prev[:150])
#             # return data  
    
#     def get_preview(self):
#         # print(self.prev.strip())
#         return self.prev

# Load email metadata
## MOST RECENT EMAILS SHOULD GO FIRST
json_fname = "emails.json"
open_json_file = config_path / Path("emails.json")

with open(open_json_file) as f:
    d = json.load(f)

email_data = []
for item in d["emails"]:
    email_data.append(item)

num_emails = len(email_data)

from mail.models import User, Mail
import random as rd
import string
from random import shuffle

## Maybe Keep This ##
# Load warning metadata
warning_json_fname = 'phish_domains.json'
# warning_json_path = Path('config/') config_path
open_warning_json_file = config_path / warning_json_fname

with open(open_warning_json_file) as f:
    d = json.load(f)

warning_data = []
for item in d['phish_domains']:
    warning_data.append(item)

phish_email_ids = [x['email_id'] for x in warning_data]
# print(phish_email_ids)
# exit()
list_of_p_domains = {
    3:['https://www.hrzzhfs.xyz/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
    'https://www.financial-pay.info/global-service/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
    'https://www.westernunion-pay.com/global-service/track-transfer/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS'],
    2:['https://dkozzlfods.info/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
    'https://www.online-shopping-payment.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS',
    'https://www.walmartpay.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS'],
    1:['https://etooicdfi.studio/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS/',
    'https://www.client-mail-services.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS',
    'https://mail.google-services.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS'],
}

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
    # h = html2text.HTML2Text()
    # h.ignore_links = True
    # pol = email.policy.SMTP
    for mail in emails:
        with open(email_folder / Path(mail), 'r') as fp:
            msg = email.parser.Parser(policy=email.policy.SMTP).parse(fp)
            
            body = msg.get_body(preferencelist=('plain','html'))
            # print(type(body))
            # print(type(body.get_content()))
            # print(h.handle(body.get_content())[:250])
            # print(body.is_multipart())
            sepr = '<'
            sender = msg['from'].split(' ' + sepr)
            # Add the separator back if it was removed 
            # This is so sender addresses are in brackets <>
            if len(sender) > 1:
                sender[1] = sepr + sender[1]

            # Would this work?
            # sender = [[sender[0], sepr+sender[1] if len(sender) > 1]

            sender = [x.replace("\"","").rstrip() for x in sender] 
            # print(msg['From'])

            # Useful lines
            # print(part.get_content_maintype())

            # email.iterators._structure(msg)
            ''' Write emails to HTML file '''
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_content_subtype() != 'html':
                    continue
                if part.get_content_maintype() == 'text':
                    with open(Path('email_client/mail/templates/mail/emails') / Path(str(i)+'.html'), 'wb') as fol:
                        payload = part.get_payload(decode=True)
                        fol.write(payload)
                        
                        ### I LEFT OFF USING LXML LIBRARY TO PARSE OUT A TEXT PREVIEW ###
                        
                        # parser = lxml.etree.HTMLParser()
                        # tree = lxml.etree.parse(payload, parser)
                        # result = etree.tostring(tree.getroot(), pretty_print=True, method="html")
                        # print(result)
                        # exit()
                        # page = lxml.html.document_fromstring(str(payload)).text_content()
                        # print(page)


                        # parser = MyHTMLParser()
                        # parser.feed(str(payload))
                        # preview = parser.get_preview()                        
                        # test = preview.replace("<[^>]*>","")
                        # print(test[:150])
                        # exit()
                            # print("parsing failed")
                            # print(type(test)) # comes back as bytes
                            # print(payload)
                        # exit()
                        # preview = h.handle

                email_to_add = {
                    # 'from' item needs to be split into sender and sender address
                    'from': sender,
                    'subject': msg['subject'],
                    'date': msg['date'],
                    'email_id': i,
                    # 'preview': preview,
                }
            results.append(email_to_add)
            i+=1
    return results
all_emails = read_emails()
# print(emails_to_add)
# exit()

def order_emails(emails):
    ''' Order the emails so that:
            - The emails appear in random order
            - All 3 phishing warnings appear in the first n-2 emails
            - The last 2 emails are benign '''

    # phishing_emails = [x for x in all_emails if x['email_id'] in phish_email_ids]
    # benign_emails = shuffle([x for x in all_emails if x['email_id'] not in phish_email_ids])
    # first_emails = shuffle(phishing_emails + benign_emails[:-2])
    # last emails = benign_emails[-2:]
    # return first_emails+last_emails
    return shuffle(emails)





emails_to_add = order_emails(all_emails)



# phishing email id : [list_of_domain_manipulations,]
# list_of_p_domains = {
#     1:['https://www.hrzzhfs.xyz/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
#     'https://dkozzlfods.info/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
#     'https://etooicdfi.studio/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS/'],
#     2:['https://www.financial-pay.info/global-service/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
#     'https://www.online-shopping-payment.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
#     'https://www.client-mail-services.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS'],
#     3:['https://www.westernunion-pay.com/global-service/track-transfer/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS', 
#     'https://www.walmartpay.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS',
#     'https://mail.google-services.com/?dU=v0G4RBKTXg2Gtk9jdyT5C0QhB-NuuHcbnI3N3H6KuOOlwYtyYUs_03KA==&F=v0fUYvjHMDjRPMSh3tviDHXIoXcPxvDgUUCCPvXMWoX_1P8SSwvgaM7IqXN16ZyETrwcyS'],
# }

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

# def initialize_warnings(group_num):


#initialize users
for i in range(0, n_users):
    # shuffle(emails_to_add)
    user = User()
    # Initialize the numbers as usernameXXXX
    user.username = 'username{}'.format(usernameNumbers[i])
    # Assign to one of the group numbers
    user.group_num = i % n_of_groups
    user.unread_count = num_emails
    user.code = codelist[i]
    user.assigned = False
    # user.set_password('pass1234')
    user.save()

    # This loop decrements so the dates append in the proper order
    # First email should have the last time_sent
    # j=9 
    for email in emails_to_add:
        j = 1
        new = Mail()
        new.user = user
        new.sender = email['from'][0]
        # sender always has an email address and optionally a name
        # e.g., ["Justin Petelka", "jpetelka@gmail.com"]
        # OR ["jpetelka@gmail.com"]
        if (len(email['from']) > 1):
            new.sender_address = email['from'][1]
        # new.preview = email['preview']
        new.preview = "Test preview for now"
        #Adjust date
        UTCdate = datetime.datetime.strptime(email['date'], '%a, %d %b %Y %H:%M:%S %z')
        readible_date = datetime.datetime.strftime(UTCdate, '%m/%d/%y')
        # print(readible_date)
        new.time_sent = readible_date
        # new.time_sent = email['date']
        new.subject = email['subject']
        # new.sender_address = email['sender_address']
        new.read = "unread"
        new.ref = email['email_id']
        # new.num_links = email['num_links']
        # print(email['ref'])
        if email['email_id'] in phish_email_ids:
            new.is_phish = True 
            new.phish_id = next((item['link_id'] for item in warning_data if item['email_id'] == new.ref))
            
        else if num_emails - 2 == j:
            new.is_fp = True
            ## NEED TO ASSIGN LINK FOR FP 
        new.save()
        j += 1
        # j-=1

# exit()

# Create a user to login into
# This helps with checking the inbox
for i in range(0, n_test_users):
    # shuffle(emails_to_add)
    
    user = User()
    user.username = 'tempuser'+str(i)
    user.group_num = i % n_of_groups
    user.unread_count = num_emails
    user.code = '432dsa4f'
    ### Set this password ###
    user.set_password('TestPassword')
    user.assigned = False
    user.save()
    # j=num_emails-1
    domain_manip_available = [0, 1, 2] # we used three forms of domain manipulation, this is to ensure domain manipulation is (a) random and (b) without replacement
    shuffle(domain_manip_available)
    for email in emails_to_add:
        new = Mail()
        new.user = user
        new.sender = email['from'][0]
        if (len(email['from']) > 1):
            new.sender_address = email['from'][1]
        # new.preview = email['preview']
        new.preview = "Test preview for now"
        #Adjust date
        UTCdate = datetime.datetime.strptime(email['date'], '%a, %d %b %Y %H:%M:%S %z')
        readible_date = datetime.datetime.strftime(UTCdate, '%m/%d/%y')
        # print(readible_date)
        new.time_sent = readible_date
        new.subject = email['subject']
        new.read = "unread"
        new.ref = email['email_id']
        # new.num_links = email['num_links']
        if email['email_id'] in phish_email_ids:
            new.is_phish = True 
            new.phish_id = next((item['link_id'] for item in warning_data if item['email_id'] == new.ref))
            # print(new.phish_id)
            new.p_url = list_of_p_domains[int(email['email_id'])][int(domain_manip_available.pop())] # This lets us randomize domain manipulation, .pop avoids replacement
        new.save()
        # j-=1
exit()
