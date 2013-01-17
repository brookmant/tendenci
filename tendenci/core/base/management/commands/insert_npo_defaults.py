from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Inserts default non-profit data"

    def handle(self, **options):

        suffix_list = [
            'auth_user',
            'profiles_profile',
            'user_groups',
            'events',
            'jobs',
            'memberships',
            'memberships_membershipdefault',
            'news',
            'photos',
            'boxes',
            'entities',
            'navs',
            'pages',
            'stories',
        ]

        # call loaddata on fixtures
        for suffix in suffix_list:
            filename = 'npo_default_%s.json' % suffix

            print filename

            call_command('loaddata', filename)
