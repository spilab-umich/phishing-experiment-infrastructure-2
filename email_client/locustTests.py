import time, random as rd
from locust import HttpUser, SequentialTaskSet, task, between
from locust.clients import HttpSession

usernames = ['username'+str(x) for x in range(0,99)]

email_ids = [1, 2, 3, 4]

class LoginAndViewEmails(SequentialTaskSet):
    def on_start(self):
        self.username = usernames.pop()
        self.password = 'TestPassword'
        self.login()

    @task 
    def login(self):    
        response = self.api_client.get('/mail/')
        csrftoken = response.cookies['csrftoken']
        self.csrftoken = csrftoken
        response = self.api_client.post('/mail/', {'username':self.username, 'password':self.password, 'csrfmiddlewaretoken':csrftoken,}, headers={'X-CSRFToken': csrftoken})
        print(response.history)
        # self.s = HttpSession()    
        # res = self.HttpSession.get(url='/mail/')
        # csrftoken = res.cookies['csrftoken']
        # self.csrftoken = csrftoken
        # req = self.s.post('/mail/', {'username':self.username, 'password':self.password, 'csrfmiddlewaretoken':csrftoken,}, headers={'X-CSRFToken': csrftoken})
        # print(req)
        
        

    @task
    def view_items(self):
        for item_id in email_ids:
            self.client.get(f"/mail/u/0/inbox/{item_id}")
            time.sleep(1)
            next_ids = [1, 2, 3, 4]
            next_ids.remove(item_id)
            next_id = rd.choice(next_ids)
            annotations = ['flag', 'delete', 'approve']
            annotate = rd.choice(annotations)
            # print(annotate)
            # print(next_id)
            self.client.get(f"/mail/{annotate}/{item_id}/{next_id}")
            time.sleep(1)
            self.client.get(f"/mail/{annotate}/{item_id}/{next_id}")
            time.sleep(1)
            self.client.get(f"/mail/{annotate}/{item_id}/{next_id}")
            time.sleep(1)
        self.interrupt(reschedule=False)
        locust.exception.StopUser

    def on_stop(self):
        self.client.get('/mail/logout_user')   

class WebsiteUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        host = 'http://127.0.0.1:8000'
        self.client = HttpSession(base_url=host)
    
    tasks = [LoginAndViewEmails]
    wait_time = between(3,5)