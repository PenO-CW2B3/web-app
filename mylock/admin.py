from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import CustomUser,Log

# Register your models here.
admin.site.register(Permission)
admin.site.register(CustomUser)
admin.site.register(Log)
