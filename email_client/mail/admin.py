from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Mail

admin.site.register(User, UserAdmin)
admin.site.register(Mail)

# Register your models here.
