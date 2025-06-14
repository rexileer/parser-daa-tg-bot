import os
import asyncio
import sys
import django
from django.core.management.base import BaseCommand

from ads.tasks import run_periodic_tasks, DEFAULT_CLEANUP_DAYS, DEFAULT_TASK_INTERVAL

class Command(BaseCommand):
    help = 'Run periodic tasks to save ads from Redis to the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup-days',
            type=int,
            default=DEFAULT_CLEANUP_DAYS,
            help=f'Number of days to keep ads before deletion (default: {DEFAULT_CLEANUP_DAYS})'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=DEFAULT_TASK_INTERVAL,
            help=f'Interval in seconds between task runs (default: {DEFAULT_TASK_INTERVAL})'
        )

    def handle(self, *args, **options):
        cleanup_days = options['cleanup_days']
        interval = options['interval']
        
        self.stdout.write(self.style.SUCCESS(
            f'Starting periodic tasks with cleanup_days={cleanup_days}, interval={interval}s...'
        ))
        
        try:
            asyncio.run(run_periodic_tasks(cleanup_days=cleanup_days, interval=interval))
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Stopping periodic tasks...'))
            sys.exit(0) 