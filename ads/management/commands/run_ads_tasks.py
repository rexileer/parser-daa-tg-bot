import os
import asyncio
import sys
import django
from django.core.management.base import BaseCommand

from ads.tasks import run_periodic_tasks

class Command(BaseCommand):
    help = 'Run periodic tasks to save ads from Redis to the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting periodic tasks...'))
        try:
            asyncio.run(run_periodic_tasks())
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Stopping periodic tasks...'))
            sys.exit(0) 