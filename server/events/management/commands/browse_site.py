import random
import time

import requests as http_requests
from django.core.management.base import BaseCommand

from events.fake_traffic import (
    SITE_URL,
    random_fbclid,
    random_rdt_cid,
    random_ttclid,
    random_user,
)

NAV_TIMEOUT = 90_000  # 90s — covers Render free-tier cold starts


class Command(BaseCommand):
    help = 'Simulate real browser traffic using Playwright to fire pixel JS and CAPI events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=5,
            help='Number of full user journeys (default: 5, ~4 events each)',
        )
        parser.add_argument(
            '--headless', action='store_true', default=True,
            help='Run browser in headless mode (default: true)',
        )
        parser.add_argument(
            '--no-headless', action='store_false', dest='headless',
            help='Run browser with visible UI',
        )

    def _warmup(self):
        """Wake the Render frontend + API before launching the browser."""
        self.stdout.write('Warming up Render services...')
        for url in [SITE_URL, f'{SITE_URL}/api/event-log']:
            try:
                resp = http_requests.get(url, timeout=120)
                self.stdout.write(f'  {url} -> {resp.status_code}')
            except Exception as e:
                self.stdout.write(f'  {url} -> {e}')

    def handle(self, *args, **options):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.stderr.write(self.style.ERROR(
                'Playwright is not installed. Run: pip install playwright && playwright install chromium'
            ))
            return

        count = options['count']
        headless = options['headless']
        total_events = 0

        self._warmup()

        self.stdout.write(f'Starting {count} browser journeys (headless={headless})...')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)

            for i in range(count):
                user = random_user()
                fbclid = random_fbclid()
                ttclid = random_ttclid()
                rdt_cid = random_rdt_cid()

                landing_url = (
                    f'{SITE_URL}/'
                    f'?fbclid={fbclid}'
                    f'&ttclid={ttclid}'
                    f'&rdt_cid={rdt_cid}'
                )

                context = browser.new_context(
                    user_agent=(
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/121.0.0.0 Safari/537.36'
                    ),
                )
                page = context.new_page()
                page.set_default_navigation_timeout(NAV_TIMEOUT)
                page.set_default_timeout(NAV_TIMEOUT)

                try:
                    journey_events = self._run_journey(page, landing_url, user, i + 1, count)
                    total_events += journey_events
                except Exception as e:
                    self.stderr.write(
                        self.style.WARNING(f'  Journey {i+1}/{count} failed: {e}')
                    )
                finally:
                    context.close()

                if i < count - 1:
                    time.sleep(random.uniform(1, 3))

            browser.close()

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. Completed {count} journeys, ~{total_events} pixel events fired.'
        ))

    def _run_journey(self, page, landing_url, user, journey_num, total):
        events = 0
        prefix = f'  [{journey_num}/{total}]'

        # 1. Home page — fires PageView pixels
        page.goto(landing_url, wait_until='domcontentloaded')
        page.wait_for_selector('button:has-text("Add to Cart")', timeout=NAV_TIMEOUT)
        page.wait_for_timeout(3000)
        events += 1
        self.stdout.write(f'{prefix} PageView (home)')

        # 2. Click a random "Add to Cart" button
        add_buttons = page.locator('button:has-text("Add to Cart")')
        btn_count = add_buttons.count()
        if btn_count > 0:
            idx = random.randint(0, btn_count - 1)
            add_buttons.nth(idx).click()
            page.wait_for_timeout(2000)
            events += 1
            self.stdout.write(f'{prefix} AddToCart')

        # 3. Navigate to /cart
        page.goto(f'{SITE_URL}/cart', wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        events += 1
        self.stdout.write(f'{prefix} PageView (cart)')

        # 4. Navigate to /payment (direct goto is more reliable than clicking links)
        page.goto(f'{SITE_URL}/payment', wait_until='domcontentloaded')
        page.wait_for_selector('#name', timeout=NAV_TIMEOUT)
        page.wait_for_timeout(2000)

        # 5. Fill payment form with fake user data
        page.fill('#name', user['name'])
        page.fill('#email', user['email'])
        page.fill('#phone', user['phone'])
        page.fill('#address', '123 Fake Street, Anytown, US 90210')

        # 6. Submit — fires Purchase pixel + CAPI
        submit_btn = page.locator('button[type="submit"]')
        if submit_btn.count() > 0:
            submit_btn.first.click()
            page.wait_for_timeout(5000)
            events += 1
            self.stdout.write(f'{prefix} Purchase ({user["name"]})')

        return events
