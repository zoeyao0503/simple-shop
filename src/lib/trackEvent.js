import { getClickIds } from './clickIds';

const META_PIXEL_ID = '2881174115331441';

const EVENT_MAP = {
  ViewContent: { meta: 'ViewContent', tiktok: 'ViewContent', reddit: 'ViewContent' },
  AddToCart:   { meta: 'AddToCart',   tiktok: 'AddToCart',   reddit: 'AddToCart' },
  Purchase:    { meta: 'Purchase',    tiktok: 'CompletePayment', reddit: 'Purchase' },
};

function platformEventName(eventName, platform) {
  const entry = EVENT_MAP[eventName];
  return entry?.[platform] || eventName;
}

function generateEventId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export async function sha256(value) {
  if (!value) return '';
  const data = new TextEncoder().encode(value.trim().toLowerCase());
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function buildTikTokContents(customData) {
  const ids = customData.content_ids || [];
  const names = customData.content_names || [];
  return ids.map((id, i) => ({
    content_id: id,
    content_type: customData.content_type || 'product',
    content_name: names[i] || '',
  }));
}

export async function sendEvent({ eventName, eventSourceUrl, userData = {}, customData = {} }) {
  const eventId = generateEventId();
  const url = eventSourceUrl || window.location.href;
  const clickIds = getClickIds();

  // --- Meta Pixel (browser-side dedup) ---
  if (typeof window.fbq === 'function') {
    if (userData.em || userData.ph || userData.fn || userData.ln) {
      const metaMatch = {};
      if (userData.em) metaMatch.em = userData.em;
      if (userData.ph) metaMatch.ph = userData.ph;
      if (userData.fn) metaMatch.fn = userData.fn;
      if (userData.ln) metaMatch.ln = userData.ln;
      window.fbq('init', META_PIXEL_ID, metaMatch);
    }
    const pixelData = { ...customData };
    delete pixelData.content_names;
    window.fbq('track', platformEventName(eventName, 'meta'), pixelData, { eventID: eventId });
  }

  // --- TikTok Pixel (browser-side) ---
  if (typeof window.ttq !== 'undefined') {
    if (userData.em || userData.ph) {
      const ttIdentify = {};
      if (userData.em) ttIdentify.email = userData.em;
      if (userData.ph) ttIdentify.phone_number = userData.ph;
      window.ttq.identify(ttIdentify);
    }
    const ttData = {
      contents: buildTikTokContents(customData),
    };
    if (customData.value != null) ttData.value = customData.value;
    if (customData.currency) ttData.currency = customData.currency;
    window.ttq.track(platformEventName(eventName, 'tiktok'), ttData);
  }

  // --- Reddit Pixel (browser-side, with conversion_id for dedup) ---
  if (typeof window.rdt === 'function') {
    const rdtEvent = platformEventName(eventName, 'reddit');
    const rdtProps = { conversion_id: eventId };
    if (customData.value != null) rdtProps.value = customData.value;
    if (customData.currency) rdtProps.currency = customData.currency;
    if (customData.content_ids) rdtProps.itemCount = customData.content_ids.length;
    window.rdt('track', rdtEvent, rdtProps);
  }

  // --- Server-side call (Django handles Meta CAPI + TikTok EAPI + Reddit CAPI) ---
  const payload = {
    event_name: eventName,
    event_id: eventId,
    event_source_url: url,
    user_data: {
      client_user_agent: navigator.userAgent,
      ...userData,
    },
  };

  if (clickIds.fbclid) {
    payload.user_data.fbc = `fb.1.${Date.now()}.${clickIds.fbclid}`;
  }
  if (clickIds.ttclid) {
    payload.user_data.ttclid = clickIds.ttclid;
  }
  if (clickIds.rdt_cid) {
    payload.click_id = clickIds.rdt_cid;
  }

  if (Object.keys(customData).length > 0) {
    payload.custom_data = customData;
  }

  fetch('/api/event', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).catch((err) => {
    console.warn('[TrackEvent] Failed to send event:', eventName, err);
  });
}

export { sendEvent as sendMetaEvent };
