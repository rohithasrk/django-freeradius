import csv
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from django_freeradius.models import RadiusBatch, RadiusCheck


class Command(BaseCommand):
    help = "Add a batch of users from a file"

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str)

    def handle(self, *args, **options):
        with open(options['filepath'], 'rt') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            expiration_date = datetime.strptime(input('Enter expiration date, format d-m-y: '), '%d-%m-%Y')
            batch = RadiusBatch(expiration_date=expiration_date)
            batch.save()
            for row in reader:
                username, password = row
                user = get_user_model()(username=username)
                user.set_password(password)
                user.save()
                radcheck = RadiusCheck(username=username,
                                       attribute='Cleartext-Password',
                                       value=password,
                                       valid_until=expiration_date)
                radcheck.save()
                batch.users.add(user)
                batch.radcheck.add(radcheck)
            self.stdout.write('Added a batch of users to csv file')
