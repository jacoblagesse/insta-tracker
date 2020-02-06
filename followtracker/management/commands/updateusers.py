from django.core.management.base import BaseCommand, CommandError
from followtracker.models import User
import django_rq
import logging

logger = logging.getLogger('instahacker.management')

class Command(BaseCommand):

    help = "Queue update jobs for a user in the database"

    def handle(self, *args, **options):
        queue = django_rq.get_queue('default')
        
        try:
            user = User.objects.get(_username=username)
        except User.DoesNotExist:
            logger.debug(f"No user with username {username}.")
        else:
            queue.enqueue(update_data, user)

        