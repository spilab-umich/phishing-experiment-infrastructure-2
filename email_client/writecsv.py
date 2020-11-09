import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
django.setup()
import csv
# from django.db.models.loading import get_model
	# """
	# Takes in a Django queryset and spits out a CSV file.
    #
	# Usage::
    #
	# 	>> from utils import dump2csv
	# 	>> from dummy_app.models import *
	# 	>> qs = DummyModel.objects.all()
	# 	>> dump2csv.dump(qs, './data/dump.csv')
    #
	# Based on a snippet by zbyte64::
    #
	# 	http://www.djangosnippets.org/snippets/790/
    #
	# """
from mail.models import Client_Logs, Server_Logs, User, Mail

def dump(qs, outfile_path):
	model = qs.model
	writer = csv.writer(open(outfile_path, 'w', newline=''))
	headers = []
	for field in model._meta.fields:
		headers.append(field.name)
	writer.writerow(headers)

	for obj in qs:
		row = []
		for field in headers:
			val = getattr(obj, field)
			if callable(val):
				val = val()
			# if type(val) == unicode:
				# val = val.encode("utf-8")
			row.append(val)
		writer.writerow(row)

client_logs = Client_Logs.objects.all()
server_logs = Server_Logs.objects.all()
users = User.objects.all()
emails = Mail.objects.all()
dump(logs, 'logs.csv')
dump(users, 'users.csv')
dump(emails[:10], 'emails.csv')