from .models import User
from instagram_private_api import Client
import instaloader
import django_rq
import time
import logging
from django.conf import settings

INSTAGRAM_USERNAME = settings.INSTAGRAM_USERNAME
INSTAGRAM_PASSWORD = settings.INSTAGRAM_PASSWORD

L = instaloader.Instaloader()
api = Client(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
logger=logging.getLogger(__name__)
queue = django_rq.get_queue('default')

def follow_user(username):
    profile = instaloader.Profile.from_username(L.context, username)
    profile_id = profile.userid
    follow_status = api.friendships_create(profile.userid)
    logger.debug(follow_status)
    if follow_status['friendship_status']['following']:
        queue.enqueue(get_full_data, username)
    elif api.friendships_show(profile.userid)['outgoing_request']:
        queue.enqueue(wait_for_accept, username, profile_id)
    else:
        logger.debug("ERROR: " + username + " could not be followed 1")

def wait_for_accept(username, userid):
    time.sleep(120)
    status = api.friendships_show(userid)
    if status['following']:
        queue.enqueue(get_full_data, username)
    else:
        logger.debug("ERROR: " + username + " could not be followed 2")

def get_full_data(username):
    profile = instaloader.Profile.from_username(L.context, username)
    user = User.objects.get(_username=username)
    user.get_followers()
    user.get_followees()
    user.send_email()