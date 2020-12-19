from django.test import TestCase, RequestFactory
from django.test.client import Client

# Create your tests here.
import threading, time, os, pathlib, random as rd
from datetime import datetime, timezone, timedelta
from .models import Client_Logs, Server_Logs, Mail, User
from .views import collect_log, collect_ajax
from django.db import connection, connections

# def create_log(tme):
#     return Client_Logs(
#         username = 'test_username',
#         link = 'https://www.link.com/',
#         link_id = rd.randint(1,3),
#         server_time = tme,
#         session_id = 'some_session_key',
#         response_id = 'some_response_id',
#         action = 'click',
#         group_num = rd.randint(1,7),
#     )


def create_request_data():
    return {
        'link': 'https://www.link.com/',
        'link_id': rd.randint(1,3),
        'client_time': datetime.now(),
        'server_time': datetime.now() - timedelta(seconds=3),
        'action': 'hover',
        'hover_time': rd.randint(1,2500),
    }

class LoggingTests(TestCase):
    # client_logs.log file has to be deleted after every test run
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@testuser',
            password='top_secret',
            group_num= rd.randint(1,7),
            response_id= 'some_response_id',
        )
    def tearDown(self):
        # os.remove('client_logs.log')


    def test_collect_ajax(self):
        # Goal is to send num_reqs logs every second for num_secs seconds
        # Send 3000 logs every second for 10 seconds
        # I think a reasonable number of requests to expect is 2 * num_participants
        num_concur_participants = 1000
        num_reqs = 2 * num_concur_participants
        num_secs = 10
        requests = []
        # t1_start = time.perf_counter()
        t1_start = time.process_time()
        # Populate an array with a num_reqs of request objects
        for _ in range(num_reqs):
            # tme = datetime.now(timezone.utc).strftime("%a, %d %B %Y %H:%M:%S GMT")
            request = self.factory.post('/ajax', create_request_data())
            request.user = self.user
            request.session = self.client.session
            request.path = 'https://www.link.com/'
            requests.append(request)
        # Send requests in array to collect_ajax(), sleeping 1 second between rounds
        for _ in range(num_secs):
            for res in requests:
                collect_ajax(res)
            time.sleep(1)
        t1_end = time.process_time() - t1_start

        # time.sleep(60)
        fname = 'client_logs.log'
        i = 0
        with open(fname, 'r') as f:
            for line in f:
                i += 1
        print(f.closed)
        print(f'{num_reqs} logs saved {num_secs} times, taking {t1_end} seconds')
        print(f'{num_secs*num_reqs} logs created; {i} successfully written.')
        self.assertEqual(num_reqs*num_secs, i)
        


# class ViewTesting(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.client = Client()
#         self.user = User.objects.create_user(
#             username='test_user',
#             email='test_user@testuser',
#             password='top_secret'
#         )

#     def test_sending_one_request_to_ajax(self):
#         # session = self.client.session
#         request = self.factory.post('/ajax', create_request_data())
#         request.user = self.user
#         request.session = self.client.session
#         # request = create_request(request)
#         collect_ajax(request)
#         self.assertIsNotNone(Client_Logs.objects.all())
