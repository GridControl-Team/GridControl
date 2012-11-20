from celery import task
from social_auth.models import UserSocialAuth
from django.contrib.auth.models import User

@task(name='gridcontrol.engine.register_login')
def register_login(user):
	pass

@task(name='gridcontrol.engine.register_logout')
def register_logout(user):
	pass

@task(name='gridcontrol.engine.tick_all_users')
def tick_all_users():
	for user in UserSocialAuth.objects.all():
		print "Tick:", user
