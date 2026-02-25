const CLICK_ID_KEYS = ['fbclid', 'ttclid', 'rdt_cid'];
const STORAGE_PREFIX = 'snoo_cid_';

function captureFromUrl() {
  try {
    const params = new URLSearchParams(window.location.search);
    for (const key of CLICK_ID_KEYS) {
      const val = params.get(key);
      if (val) {
        sessionStorage.setItem(STORAGE_PREFIX + key, val);
      }
    }
  } catch {
    // sessionStorage may be unavailable in private browsing
  }
}

export function getClickIds() {
  const ids = {};
  try {
    for (const key of CLICK_ID_KEYS) {
      const val = sessionStorage.getItem(STORAGE_PREFIX + key);
      if (val) ids[key] = val;
    }
  } catch {
    // noop
  }
  return ids;
}

captureFromUrl();
