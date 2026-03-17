const DRAWER_CLOSE_DELAY_MS = 180;

export function openAfterDrawerClose(callback: () => void) {
  if (typeof window === "undefined") {
    callback();
    return;
  }

  window.setTimeout(callback, DRAWER_CLOSE_DELAY_MS);
}
