import os, django, sys, json, datetime, email, mimetypes, re, csv
from pathlib import Path

sys.path.append('email_client/') # Change path so email_client.settings will work below
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "email_client.settings")
django.setup()

from Mail.models import Mail

mail = Mail.objects.all().values_list()

fields = [field.name for field in mail[0]._meta.get_fields()]

with open('email_data.csv','w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for obj in mail:
            row = list(obj)
            writer.writerow(row)

