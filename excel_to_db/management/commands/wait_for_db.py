import os
import time
from django.core.management.base import BaseCommand
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_host = os.environ.get('MONGO_HOST', 'db')
        db_port = int(os.environ.get('MONGO_PORT', 27017))
        db_name = os.environ.get('MONGO_DATABASE_NAME', 'quresh_db')
        db_conn = None
        while not db_conn:
            try:
                client = MongoClient(f"mongodb://{db_host}:{db_port}/")
                # Try to access the specific database
                client[db_name].command('ismaster')
                db_conn = True
            except ConnectionFailure:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))