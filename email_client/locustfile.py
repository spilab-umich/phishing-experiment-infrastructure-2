import time, random as rd
from locust import HttpUser, task, between, SequentialTaskSet

OCCUPIED_USERNAMES = []
EMAIL_IDs = [1, 2, 3, 4]
USERNAMES = ['tempuser'+str(x) for x in range(0,3000)]


class LoginandCheckEmails(SequentialTaskSet):
    def on_start(self):
        in_use = True
        while (in_use):
            username_index = rd.randint(0,2999)
            if username_index not in OCCUPIED_USERNAMES:
                in_use = False
                OCCUPIED_USERNAMES.append(username_index)
        self.username = USERNAMES[username_index]
        self.password = 'TestPassword'
        # self.login()
    
    @task
    def login(self):    
        response = self.client.get('/mail/', name="homepage")
        csrftoken = response.cookies['csrftoken']
        self.csrftoken = csrftoken
        response = self.client.post('/mail/', {'username':self.username, 'password':self.password, 'csrfmiddlewaretoken':csrftoken,}, headers={'X-CSRFToken': csrftoken}, name='login')

    @task
    def view_items(self):
        for item_id in EMAIL_IDs:
            self.client.get(f"/mail/u/0/inbox/{item_id}")
            next_id = rd.randint(1,4)
            annotations = ['flag', 'delete', 'approve']
            annotate = rd.choice(annotations)
            time.sleep(2)
            self.client.get(f"/mail/{annotate}/{item_id}/{next_id}", name=annotate)
        self.interrupt(reschedule=False)
        locust.exception.StopUser

    def on_stop(self):
        self.client.get('/mail/logout_user')

class WebsiteUser(HttpUser):
    tasks = [LoginandCheckEmails]
    wait_time = between(3,5)