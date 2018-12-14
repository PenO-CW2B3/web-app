from django.utils.timezone import localtime
from django.db import models

# Create your models here.
class CustomUser(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    username = models.CharField(max_length=50)
    fingerprint_ID = models.CharField(max_length=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        permissions = (
            ("can_see_backup_password", "Can see backup password"),
        )

    def __str__(self):
        return self.username

    def details(self):
       return self.name, self.email, self.username

class Log(models.Model):
    username = models.CharField(max_length=200)
    timestamp = models.DateTimeField("date lock used")

    def __str__(self):
        time = localtime(self.timestamp)
        return str(time.strftime("%d-%m-%Y")) + ", " + str(time.strftime("%H:%M")) + ", " + self.username

class Active_Sessions(models.Model):
    user = models.CharField(max_length=200)
    session_key = models.CharField(max_length=200)
