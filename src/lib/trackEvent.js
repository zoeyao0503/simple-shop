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

function buildTikTokContents(customData) {
  const ids = customData.content_ids || [];
  const names = customData.content_names || [];
  return ids.map((id, i) => ({
    content_id: id,
    content_type: customData.content_type || 'product',
    content_name: names[i] || '',
  }));
}

export function sendEvent({ eventName, eventSourceUrl, userData = {}, customData = {} }) {
  const eventId = generateEventId();
  const url = eventSourceUrl || window.location.href;

  // --- Meta Pixel (browser-side dedup) ---
  if (typeof window.fbq === 'function') {
    const pixelData = { ...customData };
    delete pixelData.content_names;
    window.fbq('track', platformEventName(eventName, 'meta'), pixelData, { eventID: eventId });
  }

  // --- TikTok Pixel (browser-side) ---
  if (typeof window.ttq !== 'undefined') {
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
