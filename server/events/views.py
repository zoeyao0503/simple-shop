import hashlib
import json
import time
from datetime import datetime, timezone
import requests as http_requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET


META_GRAPH_API_URL = 'https://graph.facebook.com/v24.0/{pixel_id}/events'
TIKTOK_EVENTS_API_URL = 'https://business-api.tiktok.com/open_api/v1.3/pixel/track/'

EVENT_MAP = {
    'ViewContent': {'meta': 'ViewContent', 'tiktok': 'ViewContent', 'reddit': 'ViewContent'},
    'AddToCart':   {'meta': 'AddToCart',   'tiktok': 'AddToCart',   'reddit': 'AddToCart'},
    'Purchase':    {'meta': 'Purchase',    'tiktok': 'CompletePayment', 'reddit': 'Purchase'},
}


def platform_event_name(event_name, platform):
    entry = EVENT_MAP.get(event_name, {})
    return entry.get(platform, event_name)

MAX_LOG_ENTRIES = 100
event_log = []


def _sha256(value):
    return hashlib.sha256(value.lower().strip().encode()).hexdigest()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _send_to_meta(event_data):
    payload = {
        'data': json.dumps([event_data]),
        'access_token': settings.META_ACCESS_TOKEN,
    }
    url = META_GRAPH_API_URL.format(pixel_id=settings.META_PIXEL_ID)
    try:
        resp = http_requests.post(url, data=payload, timeout=10)
        result = resp.json()
        print(f'[Meta CAPI] {event_data["event_name"]} -> {resp.status_code}: {result}')
        return resp.status_code, result
    except Exception as e:
        print(f'[Meta CAPI] Error: {e}')
        return 500, {'error': str(e)}


def _build_tiktok_contents(custom_data):
    content_ids = custom_data.get('content_ids', [])
    content_names = custom_data.get('content_names', [])
    content_type = custom_data.get('content_type', 'product')
    return [
        {
            'content_id': cid,
            'content_type': content_type,
            'content_name': content_names[i] if i < len(content_names) else '',
        }
        for i, cid in enumerate(content_ids)
    ]


def _send_to_tiktok(event_data):
    if not settings.TIKTOK_ACCESS_TOKEN:
        return None, None

    event_name = event_data['event_name']
    tt_event = platform_event_name(event_name, 'tiktok')
    user_data = event_data.get('user_data', {})
    custom_data = event_data.get('custom_data', {})

    tt_payload = {
        'pixel_code': settings.TIKTOK_PIXEL_ID,
        'event': tt_event,
        'event_id': event_data.get('event_id', ''),
        'timestamp': datetime.fromtimestamp(
            event_data.get('event_time', int(time.time())), tz=timezone.utc
        ).strftime('%Y-%m-%dT%H:%M:%S%z'),
        'context': {
            'user_agent': user_data.get('client_user_agent', ''),
            'ip': user_data.get('client_ip_address', ''),
            'page': {
                'url': event_data.get('event_source_url', ''),
            },
        },
        'properties': {},
    }

    contents = _build_tiktok_contents(custom_data)
    if contents:
        tt_payload['properties']['contents'] = contents
    if custom_data.get('currency'):
        tt_payload['properties']['currency'] = custom_data['currency']
    if custom_data.get('value') is not None:
        tt_payload['properties']['value'] = custom_data['value']

    headers = {
        'Content-Type': 'application/json',
        'Access-Token': settings.TIKTOK_ACCESS_TOKEN,
    }

    try:
        resp = http_requests.post(TIKTOK_EVENTS_API_URL, json=tt_payload, headers=headers, timeout=10)
        result = resp.json()
        print(f'[TikTok EAPI] {tt_event} -> {resp.status_code}: {result}')
        return resp.status_code, result
    except Exception as e:
        print(f'[TikTok EAPI] Error: {e}')
        return 500, {'error': str(e)}


@csrf_exempt
@require_POST
def send_event(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    event_name = body.get('event_name')
    if not event_name:
        return JsonResponse({'error': 'event_name is required'}, status=400)

    user_data = body.get('user_data', {})
    user_data['client_ip_address'] = get_client_ip(request)

    event_data = {
        'event_name': event_name,
        'event_time': int(time.time()),
        'action_source': 'website',
        'user_data': user_data,
    }

    if body.get('event_id'):
        event_data['event_id'] = body['event_id']

    if body.get('event_source_url'):
        event_data['event_source_url'] = body['event_source_url']

    if body.get('custom_data'):
        event_data['custom_data'] = body['custom_data']

    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'event_name': event_name,
        'event_id': event_data.get('event_id'),
        'payload_sent': event_data,
    }

    meta_status, meta_result = _send_to_meta(event_data)
    log_entry['meta_status_code'] = meta_status
    log_entry['meta_response'] = meta_result

    tt_status, tt_result = _send_to_tiktok(event_data)
    if tt_status is not None:
        log_entry['tiktok_status_code'] = tt_status
        log_entry['tiktok_response'] = tt_result

    _append_log(log_entry)
    return JsonResponse(meta_result, status=meta_status)


def _append_log(entry):
    event_log.append(entry)
    if len(event_log) > MAX_LOG_ENTRIES:
        del event_log[:len(event_log) - MAX_LOG_ENTRIES]


@require_GET
def get_event_log(request):
    return JsonResponse(list(reversed(event_log)), safe=False)
