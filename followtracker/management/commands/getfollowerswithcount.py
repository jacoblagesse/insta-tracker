from django.core.management.base import BaseCommand, CommandError
from followtracker.models import InstaUser
from followtracker.utils import get_follower_counts
from datetime import date
import django_rq
import logging

logger = logging.getLogger('instahacker.management')
queue = django_rq.get_queue('default')

class Command(BaseCommand):

    help = "Queue update jobs for a user in the database"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = InstaUser.objects.get(username=username)
        except User.DoesNotExist:
            print(f"No user with username {username}.")
        else:
            queue.enqueue(get_follower_counts, user.username)
            #get_follower_counts(user.username)



        