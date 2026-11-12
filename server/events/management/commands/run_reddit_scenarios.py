import hashlib
import json
import os
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit
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
BROWSER_NAMES = {'VIEW_CONTENT': 'ViewContent', 'ADD_TO_CART': 'AddToCart', 'SEARCH': 'Search'}
NO_KDF_PIXEL_ID = 'p2_18kzhk31x1bzs'


def build_no_kdf_plan(now):
    return [dict(kind='SEARCH', channel='capi', custom=None, count=20,
                 target='no_kdf', slot=now.strftime('%Y-%m-%d'))]


def build_plan(now, mode, daily_slot, include_contact=True, include_kdf=True, include_no_kdf=False):
    minute = now.hour * 60 + now.minute
    daily = minute // 5 == daily_slot // 5
    if mode == 'daily' and not daily:
        return []
    slot = now.strftime('%Y-%m-%dT%H:') + str(now.minute // 5)
    plan = [dict(kind=k, channel=c, custom=n, count=20, target='main', slot=slot)
            for k, c, n in SCENARIOS if include_contact or k != 'CONTACT']
    if daily:
        date = now.strftime('%Y-%m-%d')
        plan.append(dict(kind='ADD_TO_WISHLIST', channel='capi', custom=None, count=5, target='main', slot=date))
        if include_kdf:
            plan.extend([
                dict(kind='SEARCH', channel='capi', custom=None, count=10001, target='kdf', slot=date),
                dict(kind='LEAD', channel='capi', custom=None, count=1, target='kdf', slot=date),
            ])
        if include_no_kdf:
            plan.extend(build_no_kdf_plan(now))
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


def match_user(scenario, user_agent):
    email = os.getenv('REDDIT_TEST_EMAIL', '').strip().lower() or 'snootest@example.invalid'
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    external_hash = hashlib.sha256(b'snoocommerce:synthetic-profile:1').hexdigest()
    if scenario['target'] == 'kdf' or scenario['kind'] == 'CONTACT':
        return {'user_agent': user_agent}
    if scenario['custom'] == 'SnooTestAlpha':
        return {'email': email_hash}
    if scenario['custom'] == 'Snoo Test Beta':
        return {'external_id': external_hash}
    return {'email': email_hash, 'external_id': external_hash, 'user_agent': user_agent}


def matches_pixel_response(response, pixel, name, conversion_id):
    parts = urlsplit(response.url)
    if parts.hostname != 'alb.reddit.com' or parts.path not in ('/rp', '/rp.gif'):
        return False
    request = response.request
    fields = parse_qs(request.post_data or parts.query)
    expected_id = hashlib.sha256(conversion_id.encode()).hexdigest()
    return (fields.get('id') == [pixel] and fields.get('event') == [name]
            and fields.get('m.conversionId') == [expected_id])


def failure_message(response, tokens):
    try:
        body = response.json()
        error = body.get('error', body) if isinstance(body, dict) else {}
        message = error.get('message', '') if isinstance(error, dict) else error
        if not isinstance(message, str):
            return 'No safe error message'
        for token in tokens.values():
            message = message.replace(token, '[REDACTED]')
        return message[:500].replace('\n', ' ')
    except ValueError:
        return 'Non-JSON error response'


class Command(BaseCommand):
    help = 'Run bounded Reddit-only Data Quality scenarios; defaults to an offline preview'

    def add_arguments(self, parser):
        parser.add_argument('--execute', action='store_true')
        parser.add_argument('--no-kdf-fixture', action='store_true',
                            help='Manual-only: 20 CAPI Search events to the isolated NO-KDF candidate')
        parser.add_argument('--mode', choices=('rapid', 'daily'), default=os.getenv('REDDIT_TEST_MODE', 'daily'))

    def handle(self, *args, **options):
        mode = options['mode']
        if mode not in ('daily', 'rapid'):
            raise CommandError('REDDIT_TEST_MODE must be daily or rapid')
        try:
            hour, minute = map(int, os.getenv('REDDIT_TEST_DAILY_UTC', '21:20').split(':'))
            if not (0 <= hour < 24 and minute in range(0, 60, 5)):
                raise ValueError
        except ValueError:
            raise CommandError('REDDIT_TEST_DAILY_UTC must be HH:MM on a five-minute boundary')
        now = datetime.now(timezone.utc)
        plan = build_plan(now, mode, hour * 60 + minute,
                          include_contact=os.getenv('REDDIT_TEST_CONTACT_ENABLED', 'false').lower() == 'true',
                          include_kdf=os.getenv('REDDIT_TEST_KDF_ENABLED', 'false').lower() == 'true',
                          include_no_kdf=os.getenv('REDDIT_TEST_NO_KDF_ENABLED', 'false').lower() == 'true')
        if options['no_kdf_fixture']:
            plan = build_no_kdf_plan(now)
        if os.getenv('REDDIT_TEST_NO_KDF_LAST_SENT_UTC_DATE') == now.strftime('%Y-%m-%d'):
            plan = [s for s in plan if s['target'] != 'no_kdf']
        self.stdout.write(json.dumps({'mode': mode, 'execute': options['execute'], 'scenarios': plan}))
        if not options['execute'] or not plan:
            return
        pixels = {'main': settings.REDDIT_PIXEL_ID, 'kdf': os.getenv('REDDIT_TEST_KDF_PIXEL_ID', ''),
                  'no_kdf': NO_KDF_PIXEL_ID}
        tokens = {'main': os.getenv('REDDIT_FIRST_PIXEL_TOKEN') or settings.REDDIT_ACCESS_TOKEN,
                  'kdf': os.getenv('REDDIT_FIRST_PIXEL_TOKEN') or settings.REDDIT_ACCESS_TOKEN,
                  'no_kdf': os.getenv('REDDIT_FIRST_PIXEL_TOKEN') or settings.REDDIT_ACCESS_TOKEN}
        targets = {scenario['target'] for scenario in plan}
        capi_targets = {s['target'] for s in plan if s['channel'] in ('capi', 'dual')}
        if (any(not pixels[target] for target in targets)
                or any(not tokens[target] for target in capi_targets)
                or ('kdf' in targets and pixels['main'] == pixels['kdf'])
                or ('no_kdf' in targets and NO_KDF_PIXEL_ID in (pixels['main'], pixels['kdf']))):
            raise CommandError('Set valid credentials and distinct pixel IDs for the active scenarios')
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
                    user_agent = page.evaluate('navigator.userAgent')
                    for scenario in plan:
                        pixel = pixels[scenario['target']]
                        user = match_user(scenario, user_agent)
                        events = [make_event(scenario, i, pixel, now, site, user) for i in range(scenario['count'])]
                        if scenario['channel'] in ('pixel', 'dual'):
                            page.evaluate('([id, user]) => window.rdt("init", id, {email: user.email, externalId: user.external_id})',
                                          [pixel, user])
                            for event in events:
                                with page.expect_response(lambda r: matches_pixel_response(
                                        r, pixel, BROWSER_NAMES[scenario['kind']], event['metadata']['conversion_id']), timeout=30000) as response:
                                    page.evaluate('([name, id]) => window.rdt("track", name, {conversionId: id})',
                                                  [BROWSER_NAMES[scenario['kind']], event['metadata']['conversion_id']])
                                if not response.value.ok:
                                    raise CommandError('Reddit Pixel transport failed; stopped without retry')
                                self.stdout.write(f"Pixel HTTP {response.value.status} pixel={pixel} event={scenario['kind']} conversion_id={event['metadata']['conversion_id']}")
                        if scenario['channel'] in ('capi', 'dual'):
                            for start in range(0, len(events), 1000):
                                response = requests.post(
                                    f'https://ads-api.reddit.com/api/v3/pixels/{pixel}/conversion_events',
                                    headers={'Authorization': f"Bearer {tokens[scenario['target']]}"},
                                    json={'data': {'events': events[start:start + 1000]}}, timeout=30,
                                )
                                if not response.ok:
                                    raise CommandError(f"Reddit CAPI HTTP {response.status_code} for {scenario['target']} {scenario['kind']}: {failure_message(response, tokens)}; stopped without retry")
                                self.stdout.write(f"CAPI HTTP {response.status_code} {scenario['target']} {scenario['kind']} chunk {start // 1000 + 1}: {len(events[start:start + 1000])} submitted")
                        self.stdout.write(f"Dispatched {scenario['count']} {scenario['kind']} via {scenario['channel']} to {scenario['target']}")
                finally:
                    browser.close()
        except CommandError:
            raise
        except Exception:
            raise CommandError('Scenario execution failed; stopped without retry. No credentials or raw responses logged.') from None
