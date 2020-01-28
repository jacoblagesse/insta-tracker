from django.core.management.base import BaseCommand, CommandError
from followtracker.models import User
import logging

logger = logging.getLogger('instahacker.management')

class Command(BaseCommand):

    help = "Send an email to a user"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(_username=username)
        except User.DoesNotExist:
            logger.debug(f"No user with username {username}.")
        else:
            user.send_email()