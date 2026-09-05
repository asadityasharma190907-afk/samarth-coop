import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface WorkerOfferDetail {
  id: string;
  booking_id: string;
  worker_id: string;
  rank_at_offer: number;
  dispatch_score: number;
  status: string;
  expires_at: string;
  created_at: string;
  job_price: number;
  skill: string;
  lat: number;
  lng: number;
  distance_km: number;
  citizen_trust_score?: number;
  citizen_trust_level?: string | null;
}

export const useWorkerOffers = () => {
  return useQuery({
    queryKey: ['workerOffers'],
    queryFn: async () => {
      const response = (await api.get('/booking-offers/worker')) as WorkerOfferDetail[];
      return response;
    },
    refetchInterval: 3000, // Poll every 3 seconds
  });
};

export const useOfferAction = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ offerId, action }: { offerId: string; action: 'accept' | 'decline' }) => {
      const response = await api.put(`/booking-offers/${offerId}`, { action });
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workerOffers'] });
    },
  });
};
