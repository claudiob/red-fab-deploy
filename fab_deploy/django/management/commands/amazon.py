# Run python manage.py sync to swipe, synchronize and pre-fill the database

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import logging

class Command(BaseCommand):
    help = "Spawn and/or setup Amazon instances."

    def handle(self, *args, **options):
        """
        Spawn and/or setup Amazon instances.
        """
        logging.info("TO DO")
