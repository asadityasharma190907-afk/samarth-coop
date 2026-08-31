import { useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';

export function useLoginMutation() {
  return useMutation({
    mutationFn: (data: any) => api.post('/auth/login', data),
  });
}

export function useRegisterMutation() {
  return useMutation({
    mutationFn: (data: any) => api.post('/auth/register', data),
  });
}
