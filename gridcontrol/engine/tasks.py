from celery import task
from social_auth.models import UserSocialAuth
from django.contrib.auth.models import User
from django.conf import settings

from gridcontrol.engine.engine import GridControlEngine

import redis
def get_client():
	c = redis.Redis(
		host = settings.ENGINE_BROKER_HOST,
		port = settings.ENGINE_BROKER_PORT,
		db = settings.ENGINE_BROKER_DB
	)
	return c

@task(name='gridcontrol.engine.register_login')
def register_login(user):
	gce = GridControlEngine(get_client())
	gce.activate_user(user.id)

@task(name='gridcontrol.engine.register_logout')
def register_logout(user):
	gce = GridControlEngine(get_client())
	gce.deactivate_user(user.id)

@task(name='gridcontrol.engine.tick_all_users')
def tick_all_users():
	gce = GridControlEngine(get_client())
	gce.tick_environment()
	gce.tick_users()
