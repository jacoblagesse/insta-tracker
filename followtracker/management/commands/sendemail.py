from django.core.management.base import BaseCommand, CommandError
from followtracker.models import InstaUser
import logging

logger = logging.getLogger('instahacker.management')

class Command(BaseCommand):

    help = "Send an email to a user"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = InstaUser.objects.get(username=username)
        except InstaUser.DoesNotExist:
            logger.debug(f"No user with username {username}.")
        else:
            user.send_initial_email()