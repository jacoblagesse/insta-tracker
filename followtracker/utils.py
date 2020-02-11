from .models import InstaUser
from instagram_private_api import Client
import instaloader
import django_rq
import time
import logging
from django.conf import settings
from datetime import datetime
from django.utils import timezone

INSTAGRAM_USERNAME = settings.INSTAGRAM_USERNAME
INSTAGRAM_PASSWORD = settings.INSTAGRAM_PASSWORD

L = instaloader.Instaloader()
logger=logging.getLogger(__name__)
queue = django_rq.get_queue('default')

def follow_user(username):
    api = Client(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
    profile = instaloader.Profile.from_username(L.context, username)
    profile_id = profile.userid
    follow_status = api.friendships_create(profile.userid)
    print(follow_status)
    if follow_status['friendship_status']['following']:
        #get_full_data(username)
        queue.enqueue(get_full_data, username)
    elif api.friendships_show(profile.userid)['outgoing_request']:
        queue.enqueue(wait_for_accept, username, profile_id)
    else:
        print("ERROR: " + username + " could not be followed 1")

def wait_for_accept(username, userid):
    L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
    time.sleep(120)
    status = api.friendships_show(userid)
    if status['following']:
        queue.enqueue(get_full_data, username)
    else:
        print("ERROR: " + username + " could not be followed 2")

def get_full_data(username):
    profile = instaloader.Profile.from_username(L.context, username)
    user = InstaUser.objects.get(username=username)
    print(f"Starting to get followers for {username}")
    user.get_followers()
    print(f"Starting to get followees for {username}")
    user.get_followees()
    print(f"Starting process of sending initial email to {user.email}")
    user.send_initial_email()

def update_data(user):
    print(f"Starting to update data for {user.username}")
    new_follower_list, unfollower_list = user.update_followers()
    new_follower_list, unfollower_list = user.update_followers()
    for username in unfollower_list:
        print(username)
        print(f"{username} unfollowed {user.username}")
    user.last_update_ts = datetime.now(tz=timezone.utc)
    print(f"Finished updating data for {user.username}")
