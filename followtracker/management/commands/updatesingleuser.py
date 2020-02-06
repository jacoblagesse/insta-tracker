from django.core.management.base import BaseCommand, CommandError
from followtracker.models import User
import django_rq
import logging

logger = logging.getLogger('instahacker.management')

class Command(BaseCommand):

    help = "Queue update jobs for each user in database"

	def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']
        queue = django_rq.get_queue('default')
        
        for user in User.objects.all():
            queue.enqueue(update_data, user)

        