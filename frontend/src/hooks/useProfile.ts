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
  name?: string;
  phone?: string;
  experience_years?: number;
  languages_spoken?: string;
  local_address?: string;
  completed_jobs_count: number;
  lifetime_welfare_fund_contribution: number;
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
