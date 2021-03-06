from django.core.management.base import BaseCommand, CommandError
from followtracker.models import InstaUser
from followtracker.utils import update_data
import django_rq
import logging

logger = logging.getLogger('instahacker.management')
queue = django_rq.get_queue('default')

class Command(BaseCommand):

    help = "Queue update jobs for each user in database"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = InstaUser.objects.get(username=username)
        except User.DoesNotExist:
            print(f"No user with username {username}.")
        else:
            queue.enqueue(update_data, user)
            #update_data(user)

        