import random
import time

from django.core.management.base import BaseCommand

from events.fake_traffic import (
    SITE_URL,
    random_fbclid,
    random_rdt_cid,
    random_ttclid,
    random_user,
)


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

        # 1. Home page -> fires PageView pixels
        page.goto(landing_url, wait_until='networkidle')
        page.wait_for_timeout(2000)
        events += 1
        self.stdout.write(f'{prefix} PageView (home)')

        # 2. Click a random "Add to Cart" button
        add_buttons = page.locator('button:has-text("Add to Cart")')
        btn_count = add_buttons.count()
        if btn_count > 0:
            idx = random.randint(0, btn_count - 1)
            add_buttons.nth(idx).click()
            page.wait_for_timeout(1000)
            events += 1
            self.stdout.write(f'{prefix} AddToCart')

        # 3. Navigate to /cart
        page.goto(f'{SITE_URL}/cart', wait_until='networkidle')
        page.wait_for_timeout(1500)
        events += 1
        self.stdout.write(f'{prefix} PageView (cart)')

        # 4. Click "Proceed to Payment" link/button
        pay_link = page.locator('a:has-text("Proceed to Payment"), a:has-text("Pay Now"), button:has-text("Pay")')
        if pay_link.count() > 0:
            pay_link.first.click()
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(1500)
        else:
            page.goto(f'{SITE_URL}/payment', wait_until='networkidle')
            page.wait_for_timeout(1500)

        # 5. Fill payment form with fake user data
        name_input = page.locator('#name')
        if name_input.count() > 0:
            name_input.fill(user['name'])
        email_input = page.locator('#email')
        if email_input.count() > 0:
            email_input.fill(user['email'])
        phone_input = page.locator('#phone')
        if phone_input.count() > 0:
            phone_input.fill(user['phone'])
        address_input = page.locator('#address')
        if address_input.count() > 0:
            address_input.fill('123 Fake Street, Anytown, US 90210')

        # 6. Submit -> fires Purchase pixel + CAPI
        submit_btn = page.locator('button[type="submit"]')
        if submit_btn.count() > 0:
            submit_btn.first.click()
            page.wait_for_timeout(3000)
            events += 1
            self.stdout.write(f'{prefix} Purchase ({user["name"]})')

        return events
