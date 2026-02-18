// In dev: empty string (Vite proxy handles /api -> localhost:8000)
// In prod: full Render backend URL (e.g. https://snoocommerce-api.onrender.com)
const API_BASE = import.meta.env.VITE_API_URL || '';

function generateEventId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function sendMetaEvent({ eventName, eventSourceUrl, userData = {}, customData = {} }) {
  const eventId = generateEventId();
  const url = eventSourceUrl || window.location.href;

  // Browser-side Pixel dedup: fire the same event with matching eventID
  if (typeof window.fbq === 'function') {
    const pixelData = { ...customData };
    window.fbq('track', eventName, pixelData, { eventID: eventId });
  }

  // Server-side Conversions API call
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

  fetch(`${API_BASE}/api/event`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).catch((err) => {
    console.warn('[Meta CAPI] Failed to send event:', eventName, err);
  });
}
