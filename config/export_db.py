import os, django, sys, json, datetime, email, mimetypes, re, csv
from pathlib import Path

sys.path.append('email_client/') # Change path so email_client.settings will work below
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_client.settings")
django.setup()

from mail.models import Mail

mail = Mail.objects.all()

fields = [field.name for field in mail[0]._meta.get_fields()]

with open('email_db_data.csv','w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for obj in mail.values_list():
            row = list(obj)
            writer.writerow(row)

from mail.models import User

users = User.objects.all()
fields = [field.name for field in users[0]._meta.get_fields()]
fields = fields[1:] # this prevents the 'mail' field from offsetting the csv

with open('user_db_data.csv','w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for obj in users.values_list():
            row = list(obj)
            writer.writerow(row)

