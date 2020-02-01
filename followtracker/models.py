from django.db import models
import uuid
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import instaloader
import logging
from django.conf import settings

INSTAGRAM_USERNAME = settings.INSTAGRAM_USERNAME
INSTAGRAM_PASSWORD = settings.INSTAGRAM_PASSWORD
EMAIL = settings.EMAIL
EMAIL_PASSWORD = settings.EMAIL_PASSWORD

L = instaloader.Instaloader()
logger=logging.getLogger(__name__)

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
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
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
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
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

    def get_followes_not_followers(self, string_type):
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
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
                print(followee.username + ' does not follow you back')
                dont_follow_back.append(followee.username)

        plaintext_string = ''
        html_string = ''
        for i in dont_follow_back:
            plaintext_string = plaintext_string + i + '\n'
            html_string = html_string + i + '<br>'

        if string_type == 1:
            return html_string
        else:
            return plaintext_string

    def send_email(self):

        port = 465
        smtp_server = 'smtp.gmail.com'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Instagram Data'
        msg['From'] = EMAIL
        msg['To'] = self.email

        htmllist = self.get_followes_not_followers(1)
        plaintext = 'These users do not follow you back: \n' + self.get_followes_not_followers(0)

        html = """\
        <html>
            <head></head>
            <body>
                <img src="cid:image1"><br>
                <h2>These users do not follow you back:</h2><br>
                <p>{list}</p>
            </body>
        </html>
        """.format(list=htmllist)

        part1 = MIMEText(plaintext, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        fp = open('followtracker/static/followtracker/images/emailheader.png', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        msgImage.add_header('Content-ID', '<image1>')
        msg.attach(msgImage)

        #message = 'Subject: {}\n\n{}'.format(subject, text)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, self.email, msg.as_string())
            logger.debug("email sent")

    def __str__(self):
        return self._username


