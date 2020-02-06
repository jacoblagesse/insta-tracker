from django.core.management.base import BaseCommand, CommandError
from followtracker.models import User
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
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.debug(f"No user with username {username}.")
        else:
            queue.enqueue(update_data, user)

        