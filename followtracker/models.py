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
    user = models.ForeignKey('InstaUser', related_name='_followers', on_delete=models.CASCADE, null=True)
    num_followers = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class Followee(models.Model):
    username = models.CharField(max_length=200)
    user = models.ForeignKey('InstaUser', related_name='_followees', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username

class InstaUser(models.Model):
    username = models.CharField(max_length=200)
    email = models.CharField(max_length=200, default='')
    num_followers = models.IntegerField(default=0)
    num_followees = models.IntegerField(default=0)
    create_ts = models.DateTimeField(auto_now_add=True)
    last_update_ts = models.DateTimeField(auto_now_add=True)
    get_emails = models.BooleanField(default=0)

    def get_initial_stats(self):
        profile = instaloader.Profile.from_username(L.context, self.username)
        self.num_followers = profile.followers
        self.num_followees = profile.followees
        self.save()

    def get_followers(self):
        L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
        profile = instaloader.Profile.from_username(L.context, self.username)
        self.num_followers = profile.followers

        follow_list = []

        for _follower in profile.get_followers():
            _follower, created = self._followers.update_or_create(
                username=_follower.username,
            )
            follow_list.append(_follower.username)

        self.save()
        print(f"Finished getting followers for {self.username}")

    def get_followers_with_counts(self):
        L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
        profile = instaloader.Profile.from_username(L.context, self.username)

        for _follower in profile.get_followers():
            follower_profile = instaloader.Profile.from_username(L.context, _follower.username)
            _follower, created = self._follower_with_count.update_or_create(
                username=_follower.username,
                num_followers=follower_profile.followers
            )

        self.save()
        print(f"Finished getting followers for {self.username}")

    def get_followees(self):
        L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')

        profile = instaloader.Profile.from_username(L.context, self.username)
        self.num_followees = profile.followees

        follow_list = []

        for _followee in profile.get_followees():
            _followee, created = self._followees.update_or_create(
                username=_followee.username,
            )
            follow_list.append(_followee.username)

        self.save()
        print(f"Finished getting followees for {self.username}")

    def get_followes_not_followers(self, string_type):
        L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
        #L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
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

    def send_initial_email(self):

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
        print("Email sent")

    def update_followers(self):
        L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
        profile = instaloader.Profile.from_username(L.context, self.username)
        self.num_followers = profile.followers

        new_follower_list = []
        unfollower_list = []

        #----- Make lists of old and new follower usernames -----
        follower_list = []
        for _follower in profile.get_followers():
            follower_list.append(_follower.username)

        old_follower_list = []
        followers = self._followers.all()
        for follower in followers:
            old_follower_list.append(follower.username)

        #----- Create lists of new followers and unfollowers -----
        for follower_username in follower_list:
            if follower_username not in old_follower_list:
                new_follower_list.append(follower_username)

        for follower_username in old_follower_list:
            if follower_username not in follower_list:
                unfollower_list.append(follower_username)

        #----- Delete all old followers, replace with new list -----
        self._followers.all().delete()

        for follower_username in follower_list:
            _follower, created = self._followers.update_or_create(
                username=follower_username,
            )

        #----- Check for changed usernames -----
        for new_user in new_follower_list:
            new_profile = instaloader.Profile.from_username(L.context, new_user)
            new_profile_id = new_profile.userid
            for old_user in unfollower_list:
                old_profile = instaloader.Profile.from_username(L.context, old_user)
                old_profile_id = new_profile.userid
                if new_profile_id == old_profile_id:
                    new_follower_list.remove(new_user)
                    old_follower_list.remove(old_user)

        self.save()
        print(f"Updated followers for {self.username}")

        return new_follower_list, unfollower_list

    def update_followees(self):
        L.load_session_from_file(INSTAGRAM_USERNAME, filename='instaloader.session')
        profile = instaloader.Profile.from_username(L.context, self.username)
        self.num_followees = profile.followees

        new_followee_list = []
        unfollowee_list = []

        #----- Make lists of old and new followee usernames -----
        followee_list = []
        for _followee in profile.get_followees():
            followee_list.append(_followee.username)

        old_followee_list = []
        followees = self._followees.all()
        for followee in followees:
            old_followee_list.append(followee.username)

        #----- Create lists of new followees and unfollowees -----
        for followee_username in followee_list:
            if followee_username not in old_followee_list:
                new_followee_list.append(followee_username)

        for followee_username in old_followee_list:
            if followee_username not in followee_list:
                unfollowee_list.append(followee_username)

        #----- Delete all old followees, replace with new list -----
        self._followees.all().delete()

        for followee_username in followee_list:
            _followee, created = self._followees.update_or_create(
                username=followee_username,
            )

        #----- Check for changed usernames -----
        for new_user in new_followee_list:
            new_profile = instaloader.Profile.from_username(L.context, new_user)
            new_profile_id = new_profile.userid
            for old_user in unfollowee_list:
                old_profile = instaloader.Profile.from_username(L.context, old_user)
                old_profile_id = new_profile.userid
                if new_profile_id == old_profile_id:
                    new_followee_list.remove(new_user)
                    old_followee_list.remove(old_user)

        self.save()
        print(f"Updated followees for {self.username}")

        return new_followee_list, unfollowee_list

    def send_update_email(self, unfollower_list, new_follower_list):

        plaintext_string1 = ''
        plaintext_string2 = ''
        html_string1 = ''
        html_string2 = ''

        for i in unfollower_list:
            plaintext_string1 = plaintext_string1 + i + '\n'
            html_string1 = html_string1 + i + '<br>'

        for i in new_follower_list:
            plaintext_string2 = plaintext_string2 + i + '\n'
            html_string2 = html_string2 + i + '<br>'

        port = 465
        smtp_server = 'smtp.gmail.com'

        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Instagram Weekly Report'
        msg['From'] = EMAIL
        msg['To'] = self.email

        plaintext = 'These users unfollwed you: \n\n' + plaintext_string1 + '\nThese users followed you:\n\n' + plaintext_string2

        html = """\
        <html>
            <head></head>
            <body>
                <img src="cid:image1"><br>
                <h2>These users unfollowed you:</h2><br>
                <p>{list1}</p>
                <h2>These users followed you:</h2><br>
                <p>{list2}</p>
            </body>
        </html>
        """.format(list1=html_string1, list2=html_string2)

        part1 = MIMEText(plaintext, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        fp = open('followtracker/static/followtracker/images/emailheader.png', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        msgImage.add_header('Content-ID', '<image1>')
        msg.attach(msgImage)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(EMAIL, EMAIL_PASSWORD)
            server.sendmail(EMAIL, self.email, msg.as_string())
        print("Email sent")

    def __str__(self):
        return self.username
