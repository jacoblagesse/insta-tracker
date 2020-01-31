from django.db import models
import uuid
import smtplib, ssl
import instaloader
from django.conf import settings

INSTAGRAM_USERNAME = settings.INSTAGRAM_USERNAME
EMAIL = settings.EMAIL
EMAIL_PASSWORD = settings.EMAIL_PASSWORD

L = instaloader.Instaloader()

class Follower(models.Model):
    username = models.CharField(max_length=200)
    user = models.ForeignKey('User', related_name='_followers', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username

class Followee(models.Model):
    username = models.CharField(max_length=200)
    user = models.ForeignKey('User', related_name='_followees', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username

class User(models.Model):
    _username = models.CharField(max_length=200)
    email = models.CharField(max_length=200, default='')
    num_followers = models.IntegerField(default=0)
    num_followees = models.IntegerField(default=0)
    create_ts = models.DateTimeField(auto_now_add=True)

    def get_initial_stats(self):
        profile = instaloader.Profile.from_username(L.context, self._username)
        self.num_followers = profile.followers
        self.num_followees = profile.followees
        self.save()

    def get_followers(self):
        L.load_session_from_file(INSTAGRAM_USERNAME)
        profile = instaloader.Profile.from_username(L.context, self._username)
        self.num_followers = profile.followers

        follow_list = []
        count=0
        for _follower in profile.get_followers():
            _follower, created = self._followers.update_or_create(
                username=_follower.username,
            )
            follow_list.append(_follower.username)
            print(follow_list[count])
            count=count+1

        self.save()

    def get_followees(self):
        L.load_session_from_file(INSTAGRAM_USERNAME)
        profile = instaloader.Profile.from_username(L.context, self._username)
        self.num_followees = profile.followees

        follow_list = []
        count=0
        for _followee in profile.get_followees():
            _followee, created = self._followees.update_or_create(
                username=_followee.username,
            )
            follow_list.append(_followee.username)
            print(follow_list[count])
            count=count+1

        self.save()

    def get_followes_not_followers(self):
        L.load_session_from_file(INSTAGRAM_USERNAME)
        followers = self._followers.all()
        followees = self._followees.all()

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

    def send_email(self):

        port = 465
        smtp_server = 'smtp.gmail.com'

        subject = 'Instagram Data'

        text = 'These users do not follow you back: \n' + self.get_followes_not_followers()

        message = 'Subject: {}\n\n{}'.format(subject, text)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, self.email, message)

    def __str__(self):
        return self._username


