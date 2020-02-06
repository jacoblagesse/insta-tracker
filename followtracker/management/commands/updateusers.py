from django.core.management.base import BaseCommand, CommandError
from followtracker.models import User
from followtracker.utils import update_data
import django_rq
import logging

logger = logging.getLogger('instahacker.management')
queue = django_rq.get_queue('default')

class Command(BaseCommand):

    help = "Queue update jobs for a user in the database"

    def handle(self, *args, **options):
        
        for user in User.objects.all():
            queue.enqueue(update_data, user)
            #update_data(user)



        