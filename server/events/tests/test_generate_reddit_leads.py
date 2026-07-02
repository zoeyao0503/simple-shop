from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings


@override_settings(
    REDDIT_LEAD_CAPI_ACCESS_TOKEN='test-token',
    REDDIT_LEAD_CAPI_PIXEL_ID='p2_18kzhk31x1bzs',
)
class GenerateRedditLeadsTests(SimpleTestCase):
    @patch('events.reddit_lead_capi.http_requests.post')
    def test_command_posts_lead_batch_to_additional_reddit_pixel(self, post):
        response = post.return_value
        response.status_code = 200
        response.json.return_value = {
            'data': {'message': 'Successfully processed 2 conversion events.'}
        }

        stdout = StringIO()
        call_command('generate_reddit_leads', count=2, stdout=stdout)

        post.assert_called_once()
        url = post.call_args.args[0]
        request_kwargs = post.call_args.kwargs

        self.assertEqual(
            url,
            'https://ads-api.reddit.com/api/v3/pixels/p2_18kzhk31x1bzs/conversion_events',
        )
        self.assertEqual(
            request_kwargs['headers']['Authorization'],
            'Bearer test-token',
        )
        self.assertEqual(request_kwargs['headers']['Content-Type'], 'application/json')

        payload = request_kwargs['json']
        self.assertIn('data', payload)
        self.assertIn('events', payload['data'])

        events = payload['data']['events']
        self.assertEqual(len(events), 2)
        for event in events:
            self.assertEqual(event['action_source'], 'WEBSITE')
            self.assertEqual(event['type']['tracking_type'], 'LEAD')
            self.assertIsInstance(event['event_at'], int)
            self.assertIn('event_source_url', event)
            self.assertIn('metadata', event)
            self.assertIn('conversion_id', event['metadata'])
            self.assertIn('click_id', event)
            self.assertIn('user', event)
            self.assertIn('email', event['user'])
            self.assertIn('ip_address', event['user'])
            self.assertIn('user_agent', event['user'])

        self.assertIn('Sent 2 Reddit LEAD events', stdout.getvalue())

    @patch('events.reddit_lead_capi.http_requests.post')
    def test_dry_run_builds_lead_batch_without_posting(self, post):
        stdout = StringIO()

        call_command('generate_reddit_leads', count=3, dry_run=True, stdout=stdout)

        post.assert_not_called()
        output = stdout.getvalue()
        self.assertIn('Dry run built 3 Reddit LEAD events', output)
        self.assertIn('p2_18kzhk31x1bzs', output)

    @override_settings(REDDIT_LEAD_CAPI_ACCESS_TOKEN='')
    @patch('events.reddit_lead_capi.http_requests.post')
    def test_missing_access_token_does_not_post(self, post):
        stderr = StringIO()

        call_command('generate_reddit_leads', count=1, stderr=stderr)

        post.assert_not_called()
        self.assertIn(
            'REDDIT_LEAD_CAPI_ACCESS_TOKEN is not set',
            stderr.getvalue(),
        )
