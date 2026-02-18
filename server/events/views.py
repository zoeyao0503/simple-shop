import json
import time
from datetime import datetime, timezone
import requests as http_requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET


GRAPH_API_URL = 'https://graph.facebook.com/v24.0/{pixel_id}/events'
MAX_LOG_ENTRIES = 100

event_log = []


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


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

    payload = {
        'data': json.dumps([event_data]),
        'access_token': settings.META_ACCESS_TOKEN,
    }

    url = GRAPH_API_URL.format(pixel_id=settings.META_PIXEL_ID)

    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'event_name': event_name,
        'event_id': event_data.get('event_id'),
        'payload_sent': event_data,
    }

    try:
        resp = http_requests.post(url, data=payload, timeout=10)
        result = resp.json()
        log_entry['meta_status_code'] = resp.status_code
        log_entry['meta_response'] = result
        print(f'[Meta CAPI] {event_name} -> {resp.status_code}: {result}')
        _append_log(log_entry)
        return JsonResponse(result, status=resp.status_code)
    except Exception as e:
        log_entry['meta_status_code'] = 500
        log_entry['meta_response'] = {'error': str(e)}
        print(f'[Meta CAPI] Error sending {event_name}: {e}')
        _append_log(log_entry)
        return JsonResponse({'error': str(e)}, status=500)


def _append_log(entry):
    event_log.append(entry)
    if len(event_log) > MAX_LOG_ENTRIES:
        del event_log[:len(event_log) - MAX_LOG_ENTRIES]


@require_GET
def get_event_log(request):
    return JsonResponse(list(reversed(event_log)), safe=False)
