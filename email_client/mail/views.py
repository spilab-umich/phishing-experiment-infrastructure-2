from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Case, Value, When
from .models import Mail, User
from datetime import datetime, timezone
from django.core import serializers
from django.db import connection, connections
from django.views.decorators.clickjacking import xframe_options_exempt
import threading, time, logging, sys, string, random as rd


redirect_cases = {
    1: 'https://www.sprint.com/',
    2: 'https://www.walmart.com/',
    3: 'https://www.westernunion.com/',
    4: 'https://www.delta.com/',
}

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

# Set request error logger
error_logger = logging.getLogger('mail.error')
error_logger.setLevel(logging.INFO)
error_fh = logging.FileHandler('error_logs.log')
error_logger.addHandler(error_fh)

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

# These functions return the appropriate inbox view (inbox, flagged, approved, trash)
#~mail/flagged
def flagged_folder(request):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        user = request.user
        collect_log(request)
        emails = Mail.objects.filter(user=user,is_flagged=True).values()
        context = {
            'user': user,
            'emails': emails,
            'page': 'flag',
        }
        return render(request, 'mail/inbox.html', context)

#~mail/trash
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
            'page': 'trash', # shortcut for if deleted emails are shown
        }
        return render(request, 'mail/inbox.html', context)

#~mail/approved
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

#~/mail/inbox 
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

# These three functions handle when a user approves, flags, or delets an email
def flag(request, email_id, next_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        collect_log(request)
        user=request.user
        # tstart = time.perf_counter()
        Mail.objects.filter(user=user, ref=email_id).update(
            is_flagged=Case(
                When(is_flagged=True, then=Value(False)),
                When(is_flagged=False, then=Value(True))),
            is_deleted=Case(
                When(is_deleted=True, then=Value(False)),
                When(is_deleted=False, then=Value(False))),
            is_approved=Case(
                When(is_approved=True, then=Value(False)),
                When(is_approved=False, then=Value(False))))
        # tend = time.perf_counter()
        # time_taken = tend - tstart
        # print(f"{time_taken} seconds to FLAG")
        if int(next_id) < 1:
            # if "inbox" in request.META['HTTP_REFERER']:
            #     return redirect('mail:inbox')
            return redirect('mail:inbox')
        return redirect('mail:flagged_email', email_id=next_id)

def delete(request, email_id, next_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        collect_log(request)
        user=request.user
        # tstart = time.perf_counter()
        Mail.objects.filter(user=user, ref=email_id).update(
            is_deleted=Case(
                When(is_deleted=True, then=Value(False)),
                When(is_deleted=False, then=Value(True))),
            is_flagged=False,
            is_approved=False)
        # tend = time.perf_counter()
        # time_taken = tend - tstart
        # print(f"{time_taken} seconds to DELETE")
        if int(next_id) < 1:
            # if "inbox" in request.META['HTTP_REFERER']:
            #     return redirect('mail:inbox')
            return redirect('mail:inbox')
        return redirect('mail:trashed_email', email_id=next_id)

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
            is_deleted=False,
            is_flagged=False)
        if int(next_id) < 1:
            # if "inbox" in request.META['HTTP_REFERER']:
            #     return redirect('mail:inbox')
            return redirect('mail:inbox')
        return redirect('mail:approved_email', email_id=next_id)

# This function collects the appropriate email (flagged, approved, deleted) to display in an inbox page view
def return_emails(request, email_id, page="inbox"):
        #log the request on the server side
        collect_log(request)
        user = request.user
        # Get a dictionary list of mail objects belonging to this user
        email = Mail.objects.get(user=user, ref=email_id)
        # page = "NA"
        if (page == 'inbox'):
            emails = Mail.objects.filter(user=user).values()
        elif (page == 'trash'):
            emails = Mail.objects.filter(user=user, is_deleted=True).values() 
        elif (page == 'approve'):
            emails = Mail.objects.filter(user=user, is_approved=True).values()
        elif (page == 'flag'):
            emails = Mail.objects.filter(user=user, is_flagged=True).values()
        else:
            # Return inbox view if something goes wrong
            emails = Mail.objects.filter(user=user).values()
        
        # Evaluate the query set (hits the database)
        # len_emails = len(emails)
        # using count() does not hit the database
        len_emails = emails.count()
        read_status = bool(email.read)
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
        if read_status:
            Mail.objects.filter(user=user, ref=email_id).update(read=True)
            User.objects.filter(username=user.username).update(unread_count=F("unread_count")-1)
            user.unread_count -= 1
        # hard-coded for now
        warning_fname = 'mail/warnings/' + str(1) + '.html'
        
        context = {
            'email': email,
            'user': user,
            'email_fname': email_fname,   ## The file path of the selected email
            'next_email': next_email, ## Ref num of the next email if available
            'prev_email': prev_email,  ## Ref num of the previous email if available
            'order_num': this_index+1,  ## This indicates an email is "N of 10",
            'warning_fname': warning_fname, ## Warning number is needed to include warning html as django template
            ## ADD TARGET LINK BEFORE THIS
            'num_emails': len_emails,
            'page': page,
        }
        return context


#these functions display individual emails in the different pages
def flagged_email(request, email_id):
    #bounce the request if the user is not authenticated
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        context = return_emails(request, email_id)
    return render(request, 'mail/email.html', context)

def trashed_email(request, email_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        context = return_emails(request, email_id)
    return render(request, 'mail/email.html', context)

def approved_email(request, email_id):
    if not request.user.is_authenticated:
        return redirect('mail:index')
    else:
        context = return_emails(request, email_id)
    return render(request, 'mail/email.html', context)
            

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
        # username = res.user.username
        # this is recommended instead of accessing attribute directly
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
    except Exception as e:
        error_logger.info(username+',' + e)
    return

def collect_log(request):
    try:
        # username = request.user.username
        # this is recommended instead of accessing attribute directly
        username = request.user.get_username()
        link = request.path
        link_id = -1
        server_time = datetime.now(timezone.utc).strftime("%a %d %B %Y %H:%M:%S GMT")
        session_id = request.session.session_key
        # respondant id makes more sense to Florian
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
    except Exception as e:
        error_logger.info(username+',' + e)
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
            username = 'Available user names depleted. Please contact the research team at emailTaggingStudy@umich.edu.'
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
            if (request.META.get("RESPONSE_ID")):
                user.response_id = request.META.get("RESPONSE_ID")
            username = user.username
            password = assign_password()
            # Mark the username as 'assigned'
            user.assigned = True
            user.set_password(password)
            user.save()
            group_num = user.group_num
            code = user.code
            session_id = request.session.session_key
        context = {
            'username': username,
            'password': password,
            'group_num': group_num,
            'code': code,
            'session_id':session_id,
        }
        return JsonResponse(context)

def unread_check(request):
    if request.method == 'GET':
        # username = request.user.get_username()
        ## OR
        username = request.META.get('username')
        # unread_count = User.objects.filter(username=username).unread_count
        # get is preferred since only one object will reeturn
        # get works in manage.py shell/ so does .unread_count
        unread_count = User.objects.get(username=username).unread_count
        context = {
            'unread_count': unread_count
        }
        return JsonResponse(context)

@xframe_options_exempt # this frame decorator turns off x-frame-options in header for only this URI
def email_link(request, email_id):
    collect_log(request)
    result = redirect_cases.get(int(email_id), 'https://www.google.com/')
    return redirect(result)
