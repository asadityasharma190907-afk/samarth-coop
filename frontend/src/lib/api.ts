const BASE_URL = 'http://localhost:8000';

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('samarth_token');
  const headers = new Headers(options.headers || {});

  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    let message = 'An unexpected error occurred';
    if (errorData) {
      if (typeof errorData.detail === 'string') {
        message = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        message = errorData.detail
          .map((item: { msg?: string }) => item.msg || JSON.stringify(item))
          .join('; ');
      } else if (typeof errorData.message === 'string') {
        message = errorData.message;
      }
    }
    throw new Error(message);
  }

  return response.json();
}

export const api = {
  get: (url: string) => fetchWithAuth(url),
  post: (url: string, data: unknown) =>
    fetchWithAuth(url, { method: 'POST', body: JSON.stringify(data) }),
  put: (url: string, data: unknown) =>
    fetchWithAuth(url, { method: 'PUT', body: JSON.stringify(data) }),
  patch: (url: string, data: unknown) =>
    fetchWithAuth(url, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (url: string) => fetchWithAuth(url, { method: 'DELETE' }),
};
