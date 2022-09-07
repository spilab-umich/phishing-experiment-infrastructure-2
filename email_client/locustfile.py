import time, random as rd
from locust import HttpUser, task, between, SequentialTaskSet
from locust.clients import HttpSession

usernames = ['tempuser'+str(x) for x in range(0,99)]

email_ids = [1, 2, 3, 4]

class LoginandCheckEmails(SequentialTaskSet):
    def on_start(self):
        self.username = usernames.pop()
        self.password = 'TestPassword'
        self.login()
    
    @task
    def login(self):    
        response = self.client.get('/mail/', name="homepage")
        csrftoken = response.cookies['csrftoken']
        self.csrftoken = csrftoken
        response = self.client.post('/mail/', {'username':self.username, 'password':self.password, 'csrfmiddlewaretoken':csrftoken,}, headers={'X-CSRFToken': csrftoken}, name='login')
        # print(response.history)

    @task
    def view_items(self):
        for item_id in email_ids:
            self.client.get(f"/mail/u/0/inbox/{item_id}")
            next_ids = [1, 2, 3, 4]
            next_ids.remove(item_id)
            next_id = rd.choice(next_ids)
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