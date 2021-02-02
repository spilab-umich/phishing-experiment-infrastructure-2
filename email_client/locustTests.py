import time
from locust import HttpUser, SequentialTaskSet, task, between

usernames = ['username'+str(x) for x in range(0,150)]

email_ids = [2,3,6,7,10,12,13,18,19,20]

class LoginAndViewEmails(SequentialTaskSet):
    def on_start(self):
        self.username = usernames.pop()
        self.password = 'TestPassword'
        self.login()
        
    def login(self):    
        response = self.client.get('/mail/')
        csrftoken = response.cookies['csrftoken']
        self.csrftoken = csrftoken
        response = self.client.post('/mail/', {'username':self.username, 'password':self.password, 'csrfmiddlewaretoken':csrftoken,}, headers={'X-CSRFToken': csrftoken})

    @task
    def view_items(self):
        for item_id in email_ids:
            self.client.get(f"/mail/u/0/inbox/{item_id}")
            time.sleep(1)
        self.interrupt(reschedule=False)
        locust.exception.StopUser
        # self.environment.runner.quit()
        # return

    def on_stop(self):
        self.client.get('/mail/logout_user')   

class WebsiteUser(HttpUser):
    tasks = [LoginAndViewEmails]

    wait_time = between(3,5)  