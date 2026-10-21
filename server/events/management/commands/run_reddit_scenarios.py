import hashlib
import json
import os
from datetime import datetime, timezone
from urllib.parse import urlsplit
from uuid import NAMESPACE_URL, uuid5

import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


SCENARIOS = (
    ('VIEW_CONTENT', 'pixel', None),
    ('SEARCH', 'capi', None),
    ('ADD_TO_CART', 'dual', None),
    ('CONTACT', 'capi', None),
    ('CUSTOM', 'capi', 'SnooTestAlpha'),
    ('CUSTOM', 'capi', 'Snoo Test Beta'),
)
BROWSER_NAMES = {'VIEW_CONTENT': 'ViewContent', 'ADD_TO_CART': 'AddToCart'}


def build_plan(now, mode, daily_slot):
    minute = now.hour * 60 + now.minute
    daily = minute // 5 == daily_slot // 5
    if mode == 'daily' and not daily:
        return []
    slot = now.strftime('%Y-%m-%dT%H:') + str(now.minute // 5)
    plan = [dict(kind=k, channel=c, custom=n, count=20, target='main', slot=slot)
            for k, c, n in SCENARIOS]
    if daily:
        date = now.strftime('%Y-%m-%d')
        plan.extend([
            dict(kind='ADD_TO_WISHLIST', channel='capi', custom=None, count=5, target='main', slot=date),
            dict(kind='SEARCH', channel='capi', custom=None, count=10001, target='kdf', slot=date),
            dict(kind='LEAD', channel='capi', custom=None, count=1, target='kdf', slot=date),
        ])
    return plan


def make_event(scenario, index, pixel, now, site, user):
    identity = f"snootest:{pixel}:{scenario['slot']}:{scenario['kind']}:{scenario['custom']}:{index}"
    event_type = {'tracking_type': scenario['kind']}
    if scenario['custom']:
        event_type['custom_event_name'] = scenario['custom']
    return {
        'event_at': int(now.timestamp() * 1000), 'action_source': 'WEBSITE',
        'event_source_url': site + '/reddit-test.html', 'type': event_type,
        'metadata': {'conversion_id': str(uuid5(NAMESPACE_URL, identity))},
        'user': dict(user),
    }


class Command(BaseCommand):
    help = 'Run bounded Reddit-only Data Quality scenarios; defaults to an offline preview'

    def add_arguments(self, parser):
        parser.add_argument('--execute', action='store_true')
        parser.add_argument('--mode', choices=('rapid', 'daily'), default=os.getenv('REDDIT_TEST_MODE', 'daily'))

    def handle(self, *args, **options):
        mode = options['mode']
        if mode not in ('daily', 'rapid'):
            raise CommandError('REDDIT_TEST_MODE must be daily or rapid')
        try:
            hour, minute = map(int, os.getenv('REDDIT_TEST_DAILY_UTC', '12:00').split(':'))
            if not (0 <= hour < 24 and minute in range(0, 60, 5)):
                raise ValueError
        except ValueError:
            raise CommandError('REDDIT_TEST_DAILY_UTC must be HH:MM on a five-minute boundary')
        now = datetime.now(timezone.utc)
        plan = build_plan(now, mode, hour * 60 + minute)
        self.stdout.write(json.dumps({'mode': mode, 'execute': options['execute'], 'scenarios': plan}))
        if not options['execute'] or not plan:
            return
        pixels = {'main': settings.REDDIT_PIXEL_ID, 'kdf': os.getenv('REDDIT_TEST_KDF_PIXEL_ID', '')}
        if not settings.REDDIT_ACCESS_TOKEN or not pixels['main'] or not pixels['kdf'] or pixels['main'] == pixels['kdf']:
            raise CommandError('Set REDDIT_ACCESS_TOKEN and distinct REDDIT_PIXEL_ID / REDDIT_TEST_KDF_PIXEL_ID')
        site = os.getenv('REDDIT_TEST_SITE_URL', 'https://snoocommerce.onrender.com').rstrip('/')
        if urlsplit(site).scheme != 'https' or urlsplit(site).hostname != 'snoocommerce.onrender.com':
            raise CommandError('REDDIT_TEST_SITE_URL must use https://snoocommerce.onrender.com')
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    page.goto(site + '/reddit-test.html', wait_until='load', timeout=120000)
                    page.wait_for_function('window.redditTestReady === true', timeout=30000)
                    page.evaluate('(id) => window.rdt("init", id)', pixels['main'])
                    user = {'user_agent': page.evaluate('navigator.userAgent')}
                    email = os.getenv('REDDIT_TEST_EMAIL', '').strip().lower()
                    if email:
                        user['email'] = hashlib.sha256(email.encode()).hexdigest()
                    for scenario in plan:
                        pixel = pixels[scenario['target']]
                        events = [make_event(scenario, i, pixel, now, site, user) for i in range(scenario['count'])]
                        if scenario['channel'] in ('pixel', 'dual'):
                            for event in events:
                                with page.expect_response(lambda r: urlsplit(r.url).hostname == 'alb.reddit.com', timeout=30000) as response:
                                    page.evaluate('([name, id]) => window.rdt("track", name, {conversion_id: id})',
                                                  [BROWSER_NAMES[scenario['kind']], event['metadata']['conversion_id']])
                                if not response.value.ok:
                                    raise CommandError('Reddit Pixel transport failed; stopped without retry')
                        if scenario['channel'] in ('capi', 'dual'):
                            for start in range(0, len(events), 1000):
                                response = requests.post(
                                    f'https://ads-api.reddit.com/api/v3/pixels/{pixel}/conversion_events',
                                    headers={'Authorization': f'Bearer {settings.REDDIT_ACCESS_TOKEN}'},
                                    json={'data': {'events': events[start:start + 1000]}}, timeout=30,
                                )
                                if not response.ok:
                                    raise CommandError(f'Reddit CAPI HTTP {response.status_code}; stopped without retry')
                        self.stdout.write(f"Dispatched {scenario['count']} {scenario['kind']} via {scenario['channel']} to {scenario['target']}")
                finally:
                    browser.close()
        except CommandError:
            raise
        except Exception:
            raise CommandError('Scenario execution failed; stopped without retry. No credentials or raw responses logged.') from None
