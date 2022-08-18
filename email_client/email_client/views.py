from django.shortcuts import redirect

# Redirect to login page if top level domain is reached
def webpage(request):
    return redirect('mail:index')

def email_link(request):
    return redirect('https://www.google.com/')