import { useState, useCallback } from 'react';
import { api } from '../lib/api';

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function usePushSubscription() {
  const [permission, setPermission] = useState<NotificationPermission>(() => {
    return typeof Notification !== 'undefined' ? Notification.permission : 'denied';
  });
  const [isSubscribing, setIsSubscribing] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const subscribeToPush = useCallback(async () => {
    if (
      typeof window === 'undefined' ||
      !('serviceWorker' in navigator) ||
      !('PushManager' in window)
    ) {
      setError('Push notifications are not supported in this browser.');
      return false;
    }

    try {
      setIsSubscribing(true);
      setError(null);

      const grantedPermission = await Notification.requestPermission();
      setPermission(grantedPermission);

      if (grantedPermission !== 'granted') {
        setError('Notification permission was not granted.');
        setIsSubscribing(false);
        return false;
      }

      // Fetch VAPID public key from backend
      const { public_key } = await api.get('/push/vapid-public-key');
      const applicationServerKey = urlBase64ToUint8Array(public_key);

      const registration = await navigator.serviceWorker.ready;
      let subscription = await registration.pushManager.getSubscription();

      if (!subscription) {
        subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: applicationServerKey as unknown as BufferSource,
        });
      }

      // Sync subscription with backend
      await api.post('/push/subscribe', { subscription: subscription.toJSON() });

      setIsSubscribed(true);
      setIsSubscribing(false);
      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to subscribe to push notifications.';
      setError(msg);
      setIsSubscribing(false);
      return false;
    }
  }, []);

  return {
    permission,
    isSubscribing,
    isSubscribed,
    error,
    subscribeToPush,
  };
}
