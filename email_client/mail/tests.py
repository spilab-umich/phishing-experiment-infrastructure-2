from django.test import TestCase, RequestFactory
from django.test.client import Client

# Create your tests here.
import threading, time
from datetime import datetime, timezone
from .models import Client_Logs, Server_Logs, Mail, User
from .views import DBThread, collect_log, ajax
from django.db import connection, connections

def create_log(tme):
    return Client_Logs(
        username = 'test_username',
        link = 'https://www.link.com/',
        link_id = 1,
        server_time = tme,
        session_id = 'some_session_key',
        response_id = 'some_response_id',
        action = 'click',
        group_num = 4,
    )


def create_request_data():
    return {
        'username': 'test_user',
        'link': 'https://www.link.com/',
        'link_id': 1,
        'client_time': datetime.now(),
        'session_id': 'some_session_key',
        'response_id': 'some_response_id',
        'action': 'click',
        'group_num': 4,
        'hover_time': -1,
    }

class LogSavingTests(TestCase):

    def test_DBThread_stress_test(self):
        num_logs_to_save = 300
        # i = 1
        tme = datetime.now(timezone.utc).strftime("%a, %d %B %Y %H:%M:%S GMT")
        num_loops = 10
        # t1_start = time.perf_counter()
        t1_start = time.process_time()
        for _ in range(num_loops):
            for __ in range(num_logs_to_save):
                log = create_log(tme)
                # i -= 1
                t = DBThread(log)
                t.start()
            time.sleep(1)
        # t.join()
        # t1_end = time.perf_counter()-t1_start
        t1_end = time.process_time()-t1_start
        all_logs = Client_Logs.objects.all()
        # print(all_logs)
        logs_saved_to_db = len(all_logs)
        print(f'{num_logs_to_save} logs saved {num_loops} times, taking {t1_end} seconds')
        print(f'{num_loops*num_logs_to_save} logs created; {logs_saved_to_db} successfully written.')
        self.assertEqual(num_logs_to_save*num_loops, logs_saved_to_db)

class ViewTesting(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user',
            email='test_user@testuser',
            password='top_secret'
        )

    def test_sending_one_request_to_ajax(self):
        # session = self.client.session
        request = self.factory.post('/ajax', create_request_data())
        request.user = self.user
        request.session = self.client.session
        # request = create_request(request)
        ajax(request)
        self.assertIsNotNone(Client_Logs.objects.all())
        