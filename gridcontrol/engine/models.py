from django.db import models
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from gridcontrol.engine.tasks import *

# Create your models here.

@receiver(user_logged_in)
def on_user_log_in(sender, request, user, **kwargs):
	register_login(user)
	print user, "logged in"

@receiver(user_logged_out)
def on_user_log_out(sender, request, user, **kwargs):
	register_logout(user)
	print user, "logged out"
