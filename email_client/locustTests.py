import time
from locust import HttpUser, SequentialTaskSet, task, between
from locust.clients import HttpSession

usernames = ['username'+str(x) for x in range(0,150)]

email_ids = [2,3,6,7,10,12,13,18,19,20]

class LoginAndViewEmails(SequentialTaskSet):
    def on_start(self):
        self.username = usernames.pop()
        self.password = 'TestPassword'
        self.login()
        
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
            self.api_client.get(f"/mail/u/0/inbox/{item_id}")
            time.sleep(1)
        self.interrupt(reschedule=False)
        locust.exception.StopUser

    def on_stop(self):
        self.client.get('/mail/logout_user')   

class WebsiteUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        host = 'http://127.0.0.1:8000'
        self.api_client = HttpSession(base_url=host)
    
    tasks = [LoginAndViewEmails]
    wait_time = between(3,5)