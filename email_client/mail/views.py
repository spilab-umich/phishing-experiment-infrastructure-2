from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Case, Value, When
from .models import Mail, User
from datetime import datetime, timezone
from django.core import serializers
from django.db import transaction
from django.views.decorators.clickjacking import xframe_options_exempt
import time, logging, sys, string, os, random as rd

here = os.path.dirname(__file__)
client_path = os.path.join(here, 'client_logs.log')
server_path = os.path.join(here, 'server_logs.log')
error_path = os.path.join(here, 'error_logs.log')

# Legitimate URLs for each phising link per email id (1 - 3)
redirect_cases = {
    1: 'https://www.google.com/gmail/about/',
    2: 'https://www.walmart.com/',
    3: 'https://www.westernunion.com/',
}

# Set client ajax logger
client_logger = logging.getLogger('mail.client')
client_logger.setLevel(logging.INFO)
client_fh = logging.FileHandler(client_path)
client_fh.setLevel(logging.INFO)
client_logger.addHandler(client_fh)

# Set server request logger
server_logger = logging.getLogger('mail.server')
server_logger.setLevel(logging.INFO)
server_fh = logging.FileHandler(server_path)
server_fh.setLevel(logging.INFO)
server_logger.addHandler(server_fh)

# Set request error logger
error_logger = logging.getLogger('mail.error')
error_logger.setLevel(logging.INFO)
error_fh = logging.FileHandler(error_path)
error_logger.addHandler(error_fh)

# Bring up the login page
# ~/mail
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

    # if the request is not POST, return the index(login) page
    return render(request, 'mail/index.html')

# ~/mail/u/0/trash
def trash_folder(request):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        user = request.user
        collect_log(request)
        emails = Mail.objects.filter(user=user,is_deleted=True).values()
        context = {
            'user': user,
            'emails': emails,
            'page': 'trash', # marker to change email inbox page if trashed emails are shown
        }
        return render(request, 'mail/inbox.html', context)

# ~/mail/u/0/approved
def approved_folder(request):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        user = request.user
        collect_log(request)
        emails = Mail.objects.filter(user=user,is_approved=True).values()
        context = {
            'user': user,
            'emails': emails,
            'page': 'approve', # shortcut for if deleted emails are shown
        }
        return render(request, 'mail/inbox.html', context)

# ~/mail/u/0/inbox
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
            'page': 'inbox',
        }
        return render(request, 'mail/inbox.html', context)

# delete a single email
# ~/mail/delete/<this_id>/<next_id>
def delete(request, email_id, next_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        collect_log(request)
        user=request.user
        Mail.objects.filter(user=user, ref=email_id).update(
            is_deleted=Case(
                When(is_deleted=True, then=Value(False)),
                When(is_deleted=False, then=Value(True))),
            is_approved=False)
        if int(next_id) < 1:
            return redirect('mail:inbox')
        return redirect('mail:trashed_email', email_id=next_id)

# approve a single email
# ~/mail/approve/<this_id>/<next_id>
def approve(request, email_id, next_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        collect_log(request)
        user=request.user
        Mail.objects.filter(user=user, ref=email_id).update(
            is_approved=Case(
                When(is_approved=True, then=Value(False)),
                When(is_approved=False, then=Value(True))),
            is_deleted=False)
        if int(next_id) < 1:
            return redirect('mail:inbox')
        return redirect('mail:approved_email', email_id=next_id)

# This function collects the appropriate email (flagged, approved, deleted) to display in an inbox page view
def return_emails(request, email_id, page="inbox"):
        #log the request on the server side
        collect_log(request)
        user = request.user
        # Get a dictionary list of mail objects belonging to this user
        email = Mail.objects.get(user=user, ref=email_id)
        if (page == 'inbox'):
            emails = Mail.objects.filter(user=user).values()
        elif (page == 'trash'):
            emails = Mail.objects.filter(user=user, is_deleted=True).values() 
        elif (page == 'approve'):
            emails = Mail.objects.filter(user=user, is_approved=True).values()
        else:
            # Return default inbox view if something goes wrong
            emails = Mail.objects.filter(user=user).values()      
        # Evaluate the query set (hits the database)
        len_emails = emails.count()
        read_status = email.read
        this_id = email.pk
        prev_email = -1
        next_email = -1
        this_index = 0
        if len_emails > 1:
            this_index = -1
            for index, item in enumerate(emails):
                if item['id'] == this_id:
                    this_index = index
                    break
            # Grab db ids for the previous and next emails
            try:
                prev_email = emails[this_index-1]['ref']
            except:
                pass
            try:
                next_email = emails[this_index+1]['ref']
            except:
                pass
        #path to each email (templates/mail/<email_id>.html)
        email_fname = 'mail/emails/' + str(email_id) + '.html'

        # If unread, change to read, decrement unread_count. 
        if not read_status:
            Mail.objects.filter(user=user, ref=email_id).update(read=True)
            User.objects.filter(username=user.username).update(unread_count=F("unread_count")-1)
            user.unread_count -= 1

        context = {
            'email': email,
            'user': user,
            'email_fname': email_fname,   ## The file path of the selected email
            'next_email': next_email, ## Ref num of the next email if available
            'prev_email': prev_email,  ## Ref num of the previous email if available
            'order_num': this_index+1,  ## This indicates an email is "N of 10",
            'num_emails': len_emails,
            'page': page,
        }
        # Add warning template and function to context if a warning should be displayed
        if (email.is_phish | email.is_fp) & (user.group_num > 0):
            context['warning'] = build_warning_paramters(user.group_num)
            context ['fname'] = 'mail/warnings/' + str(1) + '.html'
        return context

# This function setts the warning parameters for a user based on their group number
# This sets (1) the time delay (0 - 5 seconds), (2) focused attention (True/False), and (3) the warning's subheader text (string)
def build_warning_paramters(group_num):
    '''Provide warning paramters if phish or false positive based on group num
        - focused attention
        - time delay
        - initial warning subtext
    '''
    subtext = ''
    if (group_num in [1,6]):
        time_delay = 0
    else:
        if (group_num in [2,7]):
            time_delay = 2
        elif (group_num in [3,8]):
            time_delay = 3
        elif (group_num in [4,9]):
            time_delay = 4
        elif (group_num in [5,10]):
            time_delay = 5
        else:
            time_delay = -100
    
    if (group_num < 6):
        focused_attention = False
        if not time_delay:
            subtext = 'Please check the link carefully before proceeding.'
    else:
        focused_attention = True
        if not time_delay:
            subtext = 'Please check the link carefully before proceeding. The link in the warning is active.'
    warning_context = {
        'time_delay': time_delay,
        'subtext': subtext,
        'focused_attention': focused_attention,
    }
    return warning_context
    
# ~/mail/u/0/trash/<email_id>
def trashed_email(request, email_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        context = return_emails(request, email_id)
    return render(request, 'mail/email.html', context)

# ~/mail/u/0/approved/<email_id>
def approved_email(request, email_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        context = return_emails(request, email_id)
    return render(request, 'mail/email.html', context)
            
# ~/mail/u/0/inbox/<email_id>
def inbox_email(request, email_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        context = return_emails(request, email_id)
    return render(request, 'mail/email.html', context)            

def ajax(request):
    # Catches POST requests from AJAX
    if request.method == 'POST':
        collect_ajax(request)
        return HttpResponse('Success')

def collect_ajax(res):
    try:    
        username = res.user.get_username()
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
    except Exception as e:
        log_type = 'client'
        error_logger.info('%(username)s,%(server_time)s,%(e)s,%(log_type)s'%
            {
                'username':username,
                'log_type':log_type,
                'server_time':server_time,
                'e': e
            })
    return

def collect_log(request):
    try:
        username = request.user.get_username()
        link = request.path
        link_id = -1
        server_time = datetime.now(timezone.utc).strftime("%a %d %B %Y %H:%M:%S GMT")
        session_id = request.session.session_key
        response_id = request.user.response_id
        group_num = request.user.group_num
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
    except Exception as e:
        log_type = 'server'
        error_logger.info('%(username)s,%(server_time)s,%(e)s,%(log_type)s'%
            {
                'username':username,
                'log_type':log_type,
                'server_time':server_time,
                'e': e
            })
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

# This function receives a request from Qualtrics and returns a username, password, and reward code for participant use
def assign_credentials(request):
    if request.method == 'GET':
        # Return a list of the remaining available usernames
        try:
            qual_group_num = int(request.META['HTTP_GROUP_NUM'])
        except Exception as e:
            error_logger.info(e,request.headers.META,request.headers)
            qual_group_num = rd.randint([0,10])
        # Put DB lock on the whole returned sub-table
        with transaction.atomic():
            # Select for update is needed for atomic block below
            users = User.objects.select_for_update().filter(assigned=False, group_num=qual_group_num, is_superuser=False) # maybe this will work?
            user = rd.choice(users)
            if not user:
                username = 'Available user names depleted. Please contact the research team at emailTaggingStudy@umich.edu.'
                password = ''
                code = ''
            else:
                # Duct tape fix to avoid race condition/concurrency issue from double assigning the same username between when the username is first assigned and then saved
                # user.update(assigned=True) 
                # Save the response_id from Qualtrics
                # This is really "PROLIFIC_PID" but I don't want to edit the model field
                if (request.META["HTTP_RESPONSE_ID"]):
                    user.response_id = request.META["HTTP_RESPONSE_ID"]
                username = user.username
                password = assign_password()
                # Mark the username as 'assigned'
                user.assigned = True
                user.set_password(password)
                code = user.code
                user.save()
        context = {
            'username': username,
            'password': password,
            'code': code,
        }
        return JsonResponse(context)

# This function receives a request from Qualtrics and returns the number of unread emails a participant has
def unread_check(request):
    if request.method == 'GET':
        username = request.GET['username']
        unread_count = User.objects.get(username=username).unread_count
        context = {
            'unread_count': unread_count
        }
        response = JsonResponse(context)
        return response

# This function records when a participant is being re-directed from a phishing link to the legitimate site, 
# then redirects the user to the legitimate site
@xframe_options_exempt # this frame decorator turns off x-frame-options in header for only this URI
def email_link(request, email_id):
    try:
        username = request.user.get_username()
        link = redirect_cases.get(int(email_id), 'https://www.google.com/')
        link_id = -1
        server_time = datetime.now(timezone.utc).strftime("%a %d %B %Y %H:%M:%S GMT")
        session_id = request.session.session_key
        response_id = request.user.response_id
        group_num = request.user.group_num
        client_time = datetime.now(timezone.utc).strftime("%a %d %B %Y %H:%M:%S GMT")
        group_num = request.user.group_num
        client_logger.info('%(username)s,%(email_ref)s,%(link)s,%(link_id)s,%(action)s,%(hover_time)s,%(client_time)s,%(group_num)s,%(response_id)s,%(server_time)s,%(session_id)s'%
            {
                'username':username,
                'email_ref':email_id,
                'link':link,
                'link_id':link_id,
                'action':'redirect',
                'hover_time':-100,
                'client_time':client_time,
                'group_num':group_num,
                'response_id':response_id,
                'server_time':server_time,
                'session_id':session_id
            })
    except Exception as e:
        log_type = 'redirect'
        error_logger.info('%(username)s,%(server_time)s,%(e)s,%(log_type)s'%
            {
                'username':username,
                'log_type':log_type,
                'server_time':server_time,
                'e': e
            })
    result = redirect_cases.get(int(email_id), 'https://www.google.com/')
    return redirect(result)
