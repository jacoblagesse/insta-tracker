from django.core.management.base import BaseCommand, CommandError
from followtracker.models import InstaUser
from followtracker.utils import update_data
from datetime import date
import django_rq
import logging

logger = logging.getLogger('instahacker.management')
queue = django_rq.get_queue('default')

class Command(BaseCommand):

    help = "Queue update jobs for a user in the database"

    def handle(self, *args, **options):
        if date.today().weekday() == 4:
            for user in InstaUser.objedcts.all():
                queue.enqueue(update_data, user)
                #update_data(user)
        else:
            pass



        