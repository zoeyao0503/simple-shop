from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from events.management.commands.run_reddit_scenarios import build_plan, make_event
from events.views import _send_to_reddit


class RedditScenarioTests(SimpleTestCase):
    def test_null_budget_across_eight_calendar_days_of_rapid_runs(self):
        start = datetime(2026, 10, 21, tzinfo=timezone.utc)
        totals = {'ADD_TO_WISHLIST': 0, 'LEAD': 0}
        kdf_total = 0
        for offset in range(8 * 24 * 12):
            plan = build_plan(start + timedelta(minutes=5 * offset), 'rapid', 720)
            for scenario in plan:
                if scenario['kind'] == 'ADD_TO_WISHLIST':
                    totals['ADD_TO_WISHLIST'] += scenario['count']
                if scenario['target'] == 'kdf':
                    kdf_total += scenario['count']
                    if scenario['kind'] == 'LEAD':
                        totals['LEAD'] += scenario['count']
        self.assertEqual(totals, {'ADD_TO_WISHLIST': 40, 'LEAD': 8})
        self.assertGreater(kdf_total, 10000)

    def test_daily_and_rapid_share_daily_only_budgets(self):
        noon = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
        self.assertEqual(build_plan(noon, 'daily', 720), build_plan(noon, 'rapid', 720))
        self.assertEqual(build_plan(noon + timedelta(minutes=5), 'daily', 720), [])
        self.assertFalse(any(s['kind'] == 'ADD_TO_WISHLIST'
                             for s in build_plan(noon + timedelta(minutes=5), 'rapid', 720)))

    def test_per_event_channel_isolation_and_custom_names(self):
        now = datetime(2026, 10, 21, 13, tzinfo=timezone.utc)
        plan = build_plan(now, 'rapid', 720)
        self.assertEqual([(s['kind'], s['channel']) for s in plan[:4]], [
            ('VIEW_CONTENT', 'pixel'), ('SEARCH', 'capi'),
            ('ADD_TO_CART', 'dual'), ('CONTACT', 'capi'),
        ])
        self.assertEqual([s['custom'] for s in plan if s['kind'] == 'CUSTOM'],
                         ['SnooTestAlpha', 'Snoo Test Beta'])

    def test_retries_keep_ids_but_events_pixels_dates_and_names_do_not_collide(self):
        now = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
        plan = build_plan(now, 'daily', 720)
        make = lambda s, i=0, pixel='main': make_event(s, i, pixel, now, 'https://example.com', {})
        event = make(plan[2])
        self.assertEqual(event, make(plan[2]))
        self.assertNotEqual(event['metadata'], make(plan[2], 1)['metadata'])
        self.assertNotEqual(event['metadata'], make(plan[2], pixel='other')['metadata'])
        self.assertNotEqual(make(plan[4])['metadata'], make(plan[5])['metadata'])
        tomorrow = build_plan(now + timedelta(days=1), 'daily', 720)
        self.assertNotEqual(event['metadata'], make(tomorrow[2])['metadata'])
        self.assertEqual(make(plan[5])['type'], {
            'tracking_type': 'CUSTOM', 'custom_event_name': 'Snoo Test Beta',
        })

    @override_settings(REDDIT_ACCESS_TOKEN='not-a-real-token')
    @patch('events.views.http_requests.post')
    def test_storefront_view_content_cannot_send_reddit_capi(self, post):
        self.assertEqual(_send_to_reddit({'event_name': 'ViewContent'}), (None, None))
        post.assert_not_called()

    @patch('events.management.commands.run_reddit_scenarios.requests.post')
    def test_preview_never_posts(self, post):
        from io import StringIO
        from django.core.management import call_command
        call_command('run_reddit_scenarios', mode='rapid', stdout=StringIO())
        post.assert_not_called()

    @override_settings(REDDIT_ACCESS_TOKEN='not-a-real-token', REDDIT_PIXEL_ID='main-pixel')
    def test_execute_routes_batches_and_shares_dual_ids(self):
        import sys
        from io import StringIO
        from types import ModuleType
        from django.core.management import call_command

        module = ModuleType('playwright.sync_api')
        module.sync_playwright = MagicMock()
        page = module.sync_playwright.return_value.__enter__.return_value.chromium.launch.return_value.new_page.return_value
        page.evaluate.return_value = 'test-agent'
        page.expect_response.return_value.__enter__.return_value.value.ok = True
        noon = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
        with patch.dict(sys.modules, {'playwright': ModuleType('playwright'), 'playwright.sync_api': module}), \
                patch.dict('os.environ', {'REDDIT_TEST_KDF_PIXEL_ID': 'kdf-pixel', 'REDDIT_TEST_DAILY_UTC': '12:00'}), \
                patch('events.management.commands.run_reddit_scenarios.datetime') as clock, \
                patch('events.management.commands.run_reddit_scenarios.requests.post') as post:
            clock.now.return_value = noon
            post.return_value.ok = True
            call_command('run_reddit_scenarios', mode='rapid', execute=True, stdout=StringIO())
        main_events = [e for c in post.call_args_list if '/main-pixel/' in c.args[0]
                       for e in c.kwargs['json']['data']['events']]
        kdf_events = [e for c in post.call_args_list if '/kdf-pixel/' in c.args[0]
                      for e in c.kwargs['json']['data']['events']]
        self.assertFalse(any(e['type']['tracking_type'] == 'VIEW_CONTENT' for e in main_events))
        self.assertEqual(sum(e['type']['tracking_type'] == 'ADD_TO_WISHLIST' for e in main_events), 5)
        self.assertEqual(len(kdf_events), 10002)
        self.assertTrue(all(len(c.kwargs['json']['data']['events']) <= 1000 for c in post.call_args_list))
        browser_events = [c.args[1] for c in page.evaluate.call_args_list if len(c.args) == 2 and isinstance(c.args[1], list)]
        self.assertEqual(len(browser_events), 40)
        self.assertEqual({name for name, _ in browser_events}, {'ViewContent', 'AddToCart'})
        dual_ids = {e['metadata']['conversion_id'] for e in main_events if e['type']['tracking_type'] == 'ADD_TO_CART'}
        self.assertEqual(dual_ids, {identifier for name, identifier in browser_events if name == 'AddToCart'})
