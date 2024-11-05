from django.shortcuts import redirect

# Redirect to login page if top level domain is reached
def webpage(request):
    return redirect('mail:index')