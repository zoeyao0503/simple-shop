from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from events.reddit_lead_capi import build_reddit_lead_payload, send_reddit_lead_events


class Command(BaseCommand):
    help = 'Generate local Reddit CAPI LEAD traffic for the additional Reddit pixel'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of LEAD events to send in one Reddit CAPI batch (default: 100)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Build the payload but do not POST to Reddit',
        )

    def handle(self, *args, **options):
        count = options['count']
        dry_run = options['dry_run']
        pixel_id = settings.REDDIT_LEAD_CAPI_PIXEL_ID

        try:
            payload = build_reddit_lead_payload(count)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Dry run built {count} Reddit LEAD events for pixel {pixel_id}'
                )
            )
            return

        reddit_token = settings.REDDIT_LEAD_CAPI_ACCESS_TOKEN
        if not reddit_token:
            self.stderr.write(self.style.ERROR('REDDIT_LEAD_CAPI_ACCESS_TOKEN is not set'))
            return

        status_code, result = send_reddit_lead_events(pixel_id, reddit_token, payload)
        if 200 <= status_code < 300:
            self.stdout.write(
                self.style.SUCCESS(f'Sent {count} Reddit LEAD events to {pixel_id}: {result}')
            )
        else:
            self.stderr.write(self.style.ERROR(f'Reddit LEAD CAPI failed {status_code}: {result}'))
