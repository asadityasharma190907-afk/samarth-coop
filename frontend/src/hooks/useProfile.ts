import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface WorkerProfile {
  id: string;
  user_id: string;
  skill: string;
  lat: number;
  lng: number;
  rating: number | null;
  availability: boolean;
  verification_status: 'pending' | 'verified' | 'rejected';
  created_at: string;
}

export function useProfile() {
  return useQuery({
    queryKey: ['workerProfile'],
    queryFn: async () => {
      const response = await api.get('/workers/me');
      return response as WorkerProfile;
    },
  });
}
