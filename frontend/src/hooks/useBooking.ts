import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface AssignedWorkerDetail {
  id: string;
  name: string;
  skill: string;
  rating: number | null;
  verified?: boolean;
  verification_status?: 'pending' | 'verified' | 'rejected';
  distance_km: number;
}

export interface Booking {
  booking_id: string;
  status: string;
  job_price: number;
  platform_fee: number;
  skill: string;
  lat: number;
  lng: number;
  description?: string;
  created_at: string;
  assigned_worker?: AssignedWorkerDetail;
  rating?: number | null;
  dispute_reason?: string | null;
}

export interface CreateBookingPayload {
  skill: string;
  lat: number;
  lng: number;
  description?: string;
  urgency?: 'normal' | 'urgent' | 'emergency';
  gender_preference?: 'any' | 'female' | 'male';
}

export const useCreateBooking = () => {
  return useMutation({
    mutationFn: async (payload: CreateBookingPayload) => {
      const response = (await api.post('/bookings', payload)) as Booking;
      return response;
    },
  });
};

export const useBooking = (bookingId: string | undefined) => {
  return useQuery({
    queryKey: ['booking', bookingId],
    queryFn: async () => {
      const response = (await api.get(`/bookings/${bookingId}`)) as Booking;
      return response;
    },
    enabled: !!bookingId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'pending' || status === 'assigned' ? 3000 : false;
    },
  });
};

export const useDisputeBooking = (bookingId: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (reason: string) => {
      const response = await api.post(`/bookings/${bookingId}/dispute`, { reason });
      return response;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['booking', bookingId] });
    },
  });
};

export const useBookings = () => {
  return useQuery({
    queryKey: ['bookings'],
    queryFn: async () => {
      const response = (await api.get('/bookings')) as Booking[];
      return response;
    },
  });
};
