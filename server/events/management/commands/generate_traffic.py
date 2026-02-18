import hashlib
import json
import random
import time
import uuid

import requests as http_requests
from django.conf import settings
from django.core.management.base import BaseCommand

from events.fake_traffic import (
    random_event_source_url,
    random_ip,
    random_products,
    random_user,
    random_user_agent,
)
from events.views import _append_log

GRAPH_API_URL = 'https://graph.facebook.com/v24.0/{pixel_id}/events'

EVENT_WEIGHTS = [
    ('ViewContent', 50),
    ('AddToCart', 30),
    ('Purchase', 20),
]
EVENT_NAMES = [name for name, _ in EVENT_WEIGHTS]
EVENT_CUMULATIVE = []
_total = 0
for _name, _weight in EVENT_WEIGHTS:
    _total += _weight
    EVENT_CUMULATIVE.append(_total)


def pick_event_name():
    r = random.randint(1, EVENT_CUMULATIVE[-1])
    for i, threshold in enumerate(EVENT_CUMULATIVE):
        if r <= threshold:
            return EVENT_NAMES[i]
    return EVENT_NAMES[-1]


class Command(BaseCommand):
    help = 'Generate synthetic Meta CAPI traffic to simulate real user activity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=100,
            help='Number of events to send (default: 100)',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Build payloads but do not POST to Meta',
        )

    def handle(self, *args, **options):
        count = options['count']
        dry_run = options['dry_run']
        access_token = settings.META_ACCESS_TOKEN
        pixel_id = settings.META_PIXEL_ID

        if not access_token:
            self.stderr.write(self.style.ERROR('META_ACCESS_TOKEN is not set'))
            return

        url = GRAPH_API_URL.format(pixel_id=pixel_id)
        counters = {'ViewContent': 0, 'AddToCart': 0, 'Purchase': 0}
        errors = 0

        self.stdout.write(f'Generating {count} synthetic events (dry_run={dry_run})...')

        for i in range(count):
            event_name = pick_event_name()
            counters[event_name] = counters.get(event_name, 0) + 1

            user = random_user()
            products = random_products()
            event_id = str(uuid.uuid4())

            event_data = {
                'event_name': event_name,
                'event_time': int(time.time()),
                'event_id': event_id,
                'action_source': 'website',
                'event_source_url': random_event_source_url(event_name),
                'user_data': {
                    'client_user_agent': random_user_agent(),
                    'client_ip_address': random_ip(),
                    'em': [hashlib.sha256(user['email'].lower().strip().encode()).hexdigest()],
                    'ph': [hashlib.sha256(user['phone'].strip().encode()).hexdigest()],
                },
                'custom_data': {
                    'content_type': 'product',
                    'content_ids': [str(p['id']) for p in products],
                    'currency': 'USD',
                    'value': round(sum(p['price'] for p in products), 2),
                },
            }

            if dry_run:
                self.stdout.write(f'  [{i+1}/{count}] {event_name} (dry-run) id={event_id[:8]}...')
                continue

            payload = {
                'data': json.dumps([event_data]),
                'access_token': access_token,
            }

            try:
                resp = http_requests.post(url, data=payload, timeout=10)
                result = resp.json()

                log_entry = {
                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'event_name': event_name,
                    'event_id': event_id,
                    'payload_sent': event_data,
                    'meta_status_code': resp.status_code,
                    'meta_response': result,
                    'source': 'generate_traffic',
                }
                _append_log(log_entry)

                if resp.status_code != 200:
                    errors += 1
                    self.stderr.write(f'  [{i+1}/{count}] {event_name} FAILED {resp.status_code}: {result}')
                else:
                    self.stdout.write(f'  [{i+1}/{count}] {event_name} OK id={event_id[:8]}...')

            except Exception as e:
                errors += 1
                self.stderr.write(f'  [{i+1}/{count}] {event_name} ERROR: {e}')

            # Small delay to avoid hammering the API
            if i < count - 1:
                time.sleep(0.1)

        summary_parts = [f'{v} {k}' for k, v in counters.items() if v > 0]
        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Sent {count} events ({", ".join(summary_parts)}). Errors: {errors}'
        ))
