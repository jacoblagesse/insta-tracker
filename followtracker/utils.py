import django_rq
from redis import Redis
from .worker import conn
from .models import User
import time
from django.forms.models import model_to_dict
from django.conf import settings

INSTAGRAM_USERNAME = settings.INSTAGRAM_USERNAME
INSTAGRAM_PASSWORD = settings.INSTAGRAM_PASSWORD
EMAIL = settings.EMAIL
EMAIL_PASSWORD = settings.EMAIL_PASSWORD

def get_full_data(username):
    user = User.objects.get(_username=username)
    user.get_followers()
    user.get_followees()
    user.send_email()

def get_followers(user):
    L = instaloader.Instaloader()
    L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    profile = instaloader.Profile.from_username(L.context, user._username)
    user.num_followers = profile.followers

    follow_list = []
    count=0
    for _follower in profile.get_followers():
        _follower, created = user._followers.update_or_create(
            username=_follower.username,
        )
        follow_list.append(_follower.username)
        print(follow_list[user])
        count=count+1

    user.save()

def get_followees(user):
    L = instaloader.Instaloader()
    L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)

    profile = instaloader.Profile.from_username(L.context, user._username)
    user.num_followees = profile.followees

    follow_list = []
    count=0
    for _followee in profile.get_followees():
        _followee, created = user._followees.update_or_create(
            username=_followee.username,
        )
        follow_list.append(_followee.username)
        print(follow_list[count])
        count=count+1

    user.save()

def get_followes_not_followers(user):
    followers = user._followers.all()
    followees = user._followees.all()

    follower_usernames = []
    for dude in followers:
        follower_usernames.append(dude.username)

    dont_follow_back = []
    for followee in followees:
        if followee.username in follower_usernames:
            print(followee.username + ' follows you back')
        else:
            print(followee.username + ' is a little bitch')
            dont_follow_back.append(followee.username)

    disloyal_string = ''
    for i in dont_follow_back:
        disloyal_string = disloyal_string + i + '\n'

    print(disloyal_string)
    return disloyal_string

def send_email(user):

    port = 465
    smtp_server = 'smtp.gmail.com'

    subject = 'Instagram Data'

    text = 'These users do not follow you back: \n' + get_followes_not_followers(user)

    message = 'Subject: {}\n\n{}'.format(subject, text)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(EMAIL, EMAIL_PASSWORD)
        server.sendmail(EMAIL, user.email, message)