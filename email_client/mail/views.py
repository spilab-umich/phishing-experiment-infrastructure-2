from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import F
from .models import Mail, User, Server_Logs, Client_Logs
from datetime import datetime, timezone

# Bring up the login page
def index(request):
    # return render(request, 'mail/index.html')
    #if the request is POST, authenticate the user's credentials
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            #sometimes you need to ban or restrict users
            if user.is_active:
                login(request, user)
                #send an authenticated, active user and their randomized emails to the inbox
                return redirect('mail:inbox')
            else:
                return render(request, 'mail/index.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'mail/index.html', {'error_message': 'Invalid login'})

    #if the request is not POST, render the index(login) page
    return render(request, 'mail/index.html')

def inbox(request):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        user = request.user
        log_request(request)
        emails = Mail.objects.filter(user=user).values()
        context = {
            'user': user,
            'emails': emails,
        }
        return render(request, 'mail/inbox.html', context)

#~mail/email/email_id
#individual email view
def email(request, email_id):
    #bounce the request if the user is not authenticated
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        #log the request on the server side
        log_request(request)
        #query the requisite email from the database
        user = request.user
        # Get a dictionary list of all mail objects belonging to this user
        emails = Mail.objects.filter(user=user).values()
        # Evaluate the query set (hit the database)
        len_emails = len(emails) - 1
        # Grab db ids for the first and last emails for this user
        first_id = emails[0]['id']
        last_id = emails[len_emails]['id']
        # Find the index of the matching email in emails
        this_index=0
        # Go through the query set and find the db id for the email id
        for mail in emails:
            if mail.get("ref") == int(email_id):
                this_id = mail.get("id")
                read_status = mail.get("read")
                # Once the id is found, we don't need to keep looking
                break
            this_index += 1
        # See if the next id is out of bounds
        if (this_id+1 > last_id):
            # Set to -1
            next_email = -1
        # Else set this to the next email ref number
        else:
            next_email = emails[this_index+1]["ref"]

        # See if the prev id is out of bounds
        if (this_id-1 < first_id):
            # Set to -1
            prev_email = -1
            # Else set this to the next email ref number
        else:
            prev_email = emails[this_index-1]["ref"]

        #path to each email (templates/mail/<email_id>.html)
        email_fname = 'mail/emails/' + str(email_id) + '.html'

        # If unread, change to read, decrement unread_count, and save. 
        # I think I should be using update instead of save()

        ## I stopped working here, trying to figure out how to update the unread_count
        if read_status == "unread":
            Mail.objects.filter(user=user, ref=email_id).update(read="read")
            # this_mail.read="read"
            # user.unread_count -=1
            User.objects.filter(username=user.username).update(unread_count=F("unread_count")-1)
            # if user.unread_count > 0:
            #     user.unread_count -= 1
            #     user.save()
            # user.unread_count = F('unread_count') - 1
            # user.save()
        warning_fname = 'mail/warnings/' + str(user.group_num) + '.html'
        # Find the order_number of the email being retreived
        # order_num = emails.index()
        context = {
            'email': emails[this_index],
            'user': user,
            'email_fname': email_fname,   ## The file path of the selected email
            'next_email': next_email, ## Ref num of the next email if available
            'prev_email': prev_email,  ## Ref num of the previous email if available
            'order_num': this_index+1,  ## This indicates an email is "N of 10",
            'warning_fname': warning_fname,
        }
        return render(request, 'mail/email.html', context)

def receiver(request):
    # Catches POST requests from AJAX
    if request.method == 'POST':
        log = Client_Logs(
            username=request.POST['username'],
            link = request.POST['link'],
            link_id = request.POST['link_id'],
            action = request.POST['action'],
            hover_time = request.POST['hover_time'],
            screen_width = request.POST['screen_width'],
            screen_height = request.POST['screen_height'],
            statusbar_visible = request.POST['statusbar_visible'],
            client_time = request.POST['client_time'],
            group_num = request.user.group_num,
            response_id = request.user.response_id,
            server_time = datetime.now(timezone.utc).strftime("%a, %d %B %Y %H:%M:%S GMT"),
            session_id = request.session.session_key,
        )
            # if (request.META.get('REMOTE_ADDR')):
            #     log.IP = request.META.get('REMOTE_ADDR')
        log.save()
    return HttpResponse('')

def log_request(request):
    log = Server_Logs(
        username = request.user.username,
        link = request.path,
        link_id = -1,
        server_time = datetime.now(timezone.utc).strftime("%a, %d %B %Y %H:%M:%S GMT"),
        session_id = request.session.session_key,
        response_id = request.user.response_id,
        # Sun, 28 Jan 2018 04:05:02 GMT
        group_num = request.user.group_num,
    )
    # if (request.META.get('REMOTE_ADDR')):
    #     log.IP = request.META.get('REMOTE_ADDR')
    log.save()

def logout_user(request):
    log_request(request)
    logout(request)
    return redirect('mail:index')