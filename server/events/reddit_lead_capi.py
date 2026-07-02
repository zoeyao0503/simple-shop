import hashlib
import time
import uuid

import requests as http_requests

from events.fake_traffic import (
    random_event_source_url,
    random_ip,
    random_rdt_cid,
    random_user,
    random_user_agent,
)


REDDIT_CAPI_URL = 'https://ads-api.reddit.com/api/v3/pixels/{pixel_id}/conversion_events'
REDDIT_LEAD_TRACKING_TYPE = 'LEAD'
MAX_EVENTS_PER_REQUEST = 1000


def _sha256(value):
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()


def _canonicalize_email(email):
    email = email.strip().lower()
    if '@' not in email:
        return email

    local_part, domain = email.split('@', 1)
    local_part = local_part.split('+', 1)[0].replace('.', '')
    return f'{local_part}@{domain}'


def _build_user_match_keys(user):
    ip_address = random_ip()
    return {
        'email': _sha256(_canonicalize_email(user['email'])),
        'phone_number': _sha256(user['phone']),
        'ip_address': _sha256(ip_address),
        'user_agent': random_user_agent(),
    }


def build_reddit_lead_event():
    user = random_user()
    event_id = str(uuid.uuid4())

    return {
        'event_at': int(time.time() * 1000),
        'action_source': 'WEBSITE',
        'event_source_url': random_event_source_url('Lead'),
        'click_id': random_rdt_cid(),
        'type': {
            'tracking_type': REDDIT_LEAD_TRACKING_TYPE,
        },
        'metadata': {
            'conversion_id': event_id,
        },
        'user': _build_user_match_keys(user),
    }


def build_reddit_lead_payload(count):
    if count < 1:
        raise ValueError('count must be at least 1')
    if count > MAX_EVENTS_PER_REQUEST:
        raise ValueError('count must be 1000 or fewer for one Reddit CAPI request')

    return {
        'data': {
            'events': [build_reddit_lead_event() for _ in range(count)],
        },
    }


def send_reddit_lead_events(pixel_id, access_token, payload):
    url = REDDIT_CAPI_URL.format(pixel_id=pixel_id)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    try:
        response = http_requests.post(url, json=payload, headers=headers, timeout=10)
        try:
            result = response.json()
        except ValueError:
            result = {'raw': response.text}
        return response.status_code, result
    except Exception as exc:
        return 500, {'error': str(exc)}
