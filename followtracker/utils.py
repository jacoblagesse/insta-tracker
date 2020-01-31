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
logger=logging.getLogger(__name__)
queue = django_rq.get_queue('default')

def follow_user(username):
    profile = instaloader.Profile.from_username(L.context, username)
    api = Client(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    follow_status = api.friendships_create(profile.userid)
    logger.debug(follow_status)
    if follow_status['friendship_status']['following']:
        queue.enqueue(get_full_data, username)
    elif api.friendships_show(profile.userid)['outgoing_request']:
        queue.enqueue(wait_for_accept, username, profile.userid, api, 0)
    else:
        logger.debug("ERROR: " + username + " could not be followed 1")

def wait_for_accept(username, userid, api, loop):
    time.sleep(60)
    if loop <= 5:
        status = api.friendships_show(userid)
        if status['following']:
            queue.enqueue(get_full_data, username)
        elif status['outgoing_request']:
            loop += 1
            queue.enqueue(wait_for_accept, userid, username, api, loop)
        else:
            logger.debug("ERROR: " + username + " could not be followed 2")
    else:
        logger.debug("ERROR: " + username + " did not accept request in time")

def get_full_data(username):
    profile = instaloader.Profile.from_username(L.context, username)
    user = User.objects.get(_username=username)
    user.get_followers()
    user.get_followees()
    user.send_email()