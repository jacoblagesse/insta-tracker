from .models import InstaUser, Follower
from instagram_private_api import Client
import instaloader
import django_rq
import time
import logging
import random
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

def update_data(username):
    print(f"Starting to update data for {username}")
    user = InstaUser.objects.get(username=username)
    new_follower_list, unfollower_list = user.update_followers()
    new_followee_list, unfollowee_list = user.update_followees()
    for _username in unfollower_list:
        print(f"{_username} unfollowed {username}")
    for _username in new_follower_list:
        print(f"{_username} followed {username}")
    user.last_update_ts = datetime.now(tz=timezone.utc)
    print(f"Finished updating data for {username}")
    if user.get_emails == True:
        user.send_update_email(unfollower_list, new_follower_list)

def get_follower_counts(username):
    L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')

    remaining_followers = True
    user = InstaUser.objects.get(username=username)
    followers = user._followers.order_by('num_followers')[:50]

    while remaining_followers:
        count = 0
        for follower in followers:
            try:
                follower_profile = instaloader.Profile.from_username(L.context, follower.username)
                follower_count = follower_profile.followers
                if follower.num_followers != 0:
                    print("already has followers collected")
                    remaining_followers = False
                    break
                else:
                    follower.num_followers = follower_count
                follower.save()
                print(f"{follower.username} has {follower_count} followers ({count}/50)")
                count += 1
            except(instaloader.exceptions.ConnectionException):
                print("Too many queries")
                remaining_followers = False
                break

    if len(Follower.objects.filter(num_followers=0)) != 0:
        wait = random.randrange(480, 620)
        print(f"Still followers left, repeating in {wait/60} minutes")
        time.sleep(wait)
        get_follower_counts(username)

