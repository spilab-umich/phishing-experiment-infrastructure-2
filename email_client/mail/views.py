from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import F
from .models import Mail, User
from datetime import datetime, timezone
from django.core import serializers
from django.db import connection, connections
import threading, time, logging, sys, string, random as rd

# Set client ajax logger
client_logger = logging.getLogger('mail.client')
client_logger.setLevel(logging.INFO)
client_fh = logging.FileHandler('client_logs.log')
client_fh.setLevel(logging.INFO)
client_logger.addHandler(client_fh)

# Set server request logger
server_logger = logging.getLogger('mail.server')
server_logger.setLevel(logging.INFO)
server_fh = logging.FileHandler('server_logs.log')
server_fh.setLevel(logging.INFO)
server_logger.addHandler(server_fh)

# Bring up the login page
def index(request):
    #if the request is POST, authenticate the user's credentials
    if request.method == "POST":
        username = request.POST['username'].lower()
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

    #if the request is not POST, return the index(login) page
    return render(request, 'mail/index.html')

def inbox(request):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        user = request.user
        collect_log(request)
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
        collect_log(request)
        #query the requisite email from the database
        user = request.user
        # Get a dictionary list of all mail objects belonging to this user
        emails = Mail.objects.filter(user=user).values()
        # Evaluate the query set (hits the database)
        len_emails = len(emails) - 1
        # Grab db ids for the first and last emails for this user
        first_id = emails[0]['id']
        last_id = emails[len_emails]['id']
        # Find the index of the matching email in emails
        this_index=0
        # Go through the query set and find the db id for the email id

        # """ I think I can use the filter function F() for this; """
        for mail in emails:
            if mail.get("ref") == int(email_id):
                this_id = mail.get("id")
                read_status = mail.get("read")
                # Once the id is found, we don't need to keep looking
                break
            this_index += 1 # Return the position of this email in the email_list
        if (this_id+1 > last_id): # See if the next id is out of bounds
            next_email = -1 # Set to -1
        else:
            next_email = emails[this_index+1]["ref"] # Else set the next email number to the next email ref number

        # See if the prev id is out of bounds
        if (this_id-1 < first_id):
            # Set to -1
            prev_email = -1
            # Else set this to the next email ref number
        else:
            prev_email = emails[this_index-1]["ref"]

        #path to each email (templates/mail/<email_id>.html)
        email_fname = 'mail/emails/' + str(email_id) + '.html'

        # If unread, change to read, decrement unread_count. 
        if read_status == "unread":
            Mail.objects.filter(user=user, ref=email_id).update(read="read")
            User.objects.filter(username=user.username).update(unread_count=F("unread_count")-1)

        ### Do I need this line below? ###
        warning_fname = 'mail/warnings/' + str(user.group_num) + '.html'
        context = {
            'email': emails[this_index],
            'user': user,
            'email_fname': email_fname,   ## The file path of the selected email
            'next_email': next_email, ## Ref num of the next email if available
            'prev_email': prev_email,  ## Ref num of the previous email if available
            'order_num': this_index+1,  ## This indicates an email is "N of 10",
            'warning_fname': warning_fname, ## Warning number is needed to include warning html as django template
        }
        return render(request, 'mail/email.html', context)

def ajax(request):
    # Catches POST requests from AJAX
    if request.method == 'POST':
        collect_ajax(request)
        return HttpResponse('Success')

def collect_ajax(res):
    username = res.user.username
    email_ref = res.POST['ref']
    link = res.POST['link']
    link_id = res.POST['link_id']
    action = res.POST['action']
    hover_time = res.POST['hover_time']
    client_time = res.POST['client_time']
    group_num = res.user.group_num
    response_id = res.user.response_id
    server_time = datetime.now(timezone.utc).strftime("%a %d %B %Y %H:%M:%S GMT")
    session_id = res.session.session_key
    # if (res.META.get('REMOTE_ADDR')):
        # log.IP = res.META.get('REMOTE_ADDR')
    # Convert this from .format to printf style message re: https://coralogix.com/log-analytics-blog/python-logging-best-practices-tips/
    client_logger.info('%(username)s,%(email_ref)s,%(link)s,%(link_id)s,%(action)s,%(hover_time)s,%(client_time)s,%(group_num)s,%(response_id)s,%(server_time)s,%(session_id)s'%
        {
            'username':username,
            'email_ref':email_ref,
            'link':link,
            'link_id':link_id,
            'action':action,
            'hover_time':hover_time,
            'client_time':client_time,
            'group_num':group_num,
            'response_id':response_id,
            'server_time':server_time,
            'session_id':session_id
        })
    # print('client log saved')
    return

def collect_log(request):
    username = request.user.username
    link = request.path
    link_id = -1
    server_time = datetime.now(timezone.utc).strftime("%a %d %B %Y %H:%M:%S GMT")
    session_id = request.session.session_key
    response_id = request.user.response_id
    group_num = request.user.group_num
    # server_logger.info('{},{},{},{},{},{},{}'.format(username,link,link_id,server_time,session_id,response_id,group_num))
    server_logger.info('%(username)s,%(link)s,%(link_id)s,%(group_num)s,%(response_id)s,%(server_time)s,%(session_id)s'%
        {
            'username':username,
            'link':link,
            'link_id':link_id,
            'group_num':group_num,
            'response_id':response_id,
            'server_time':server_time,
            'session_id':session_id
        })
    # print('server log saved')
    # if (request.META.get('REMOTE_ADDR')):
    #     log.IP = request.META.get('REMOTE_ADDR')
    return

def logout_user(request):
    collect_log(request)
    logout(request)
    return redirect('mail:index')

def assign_password():
    str_code = ''
    letter_pool = string.ascii_letters+'1234567890'
    for i in range(8):
        str_code += rd.choice(letter_pool)
    return str_code

def assign_credentials(request):
    if request.method == 'GET':
        # Return a list of the remaining available usernames
        users = User.objects.filter(assigned=False).filter(is_superuser=False)
        # users is a QuerySet. Calling len() on users caches the whole database at once
        # This avoids multiple db calls
        len_users = len(users)
        if len_users < 1:
            username = 'Available user names depleted. Please contact the research team.'
            password = ''
        else:
            # Choose a random available username
            # Try it twice just in case.
            try:
                user_index = rd.randint(0,len_users-1)
                user = users[user_index]
            except:
                user_index = rd.randint(0,len_users-1)
                user = users[user_index]
            # Save the response_id from Qualtrics
            if (request.META.get("PROLIFIC_PID")):
                user.response_id = request.META.get("PROLIFIC_PID")
            username = user.username
            password = assign_password()
            # Mark the username as 'assigned'
            user.assigned = True
            user.set_password(password)
            user.save()
            group_num = user.group_num
            code = user.code
        context = {
            'username': username,
            'password': password,
            'group_num': group_num,
            'code': code,
        }
        return JsonResponse(context)
