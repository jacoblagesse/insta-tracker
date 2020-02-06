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
    api = Client(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    profile = instaloader.Profile.from_username(L.context, username)
    profile_id = profile.userid
    follow_status = api.friendships_create(profile.userid)
    logger.debug(follow_status)
    if follow_status['friendship_status']['following']:
        #get_full_data(username)
        queue.enqueue(get_full_data, username)
    elif api.friendships_show(profile.userid)['outgoing_request']:
        queue.enqueue(wait_for_accept, username, profile_id)
    else:
        logger.debug("ERROR: " + username + " could not be followed 1")

def wait_for_accept(username, userid):
    api = Client(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    time.sleep(120)
    status = api.friendships_show(userid)
    if status['following']:
        queue.enqueue(get_full_data, username)
    else:
        logger.debug("ERROR: " + username + " could not be followed 2")

def get_full_data(username):
    profile = instaloader.Profile.from_username(L.context, username)
    user = User.objects.get(username=username)
    user.get_followers()
    user.get_followees()
    user.send_initial_email()

def update_data(user):
    new_follower_list, unfollower_list = user.update_followers()
    new_follower_list, unfollower_list = user.update_followers()
    for username in unfollower_list:
        print(username)
        logger.debug(username)
