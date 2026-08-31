import { useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';

export function useAuth() {
  const token = localStorage.getItem('samarth_token');
  let user = null;
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      user = {
        id: payload.sub,
        role: payload.role,
      };
    } catch {
      // Invalid token
    }
  }
  return { user };
}

export function useLoginMutation() {
  return useMutation({
    mutationFn: (data: unknown) => api.post('/auth/login', data),
  });
}

export function useRegisterMutation() {
  return useMutation({
    mutationFn: (data: unknown) => api.post('/auth/register', data),
  });
}
