import { useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface BulkBookingItem {
  skill: string;
  quantity: number;
  schedule: 'daily' | 'weekly' | 'monthly';
  months?: number;
}

export interface EnterpriseBookingRequest {
  institution_name: string;
  bookings: BulkBookingItem[];
}

export interface BulkBookingLineItemResponse {
  skill: string;
  quantity: number;
  schedule: string;
  months: number;
  base_rate: string | number;
  schedule_multiplier: number;
  monthly_cost: string | number;
  total_cost: string | number;
  workers_needed: number;
}

export interface EnterpriseBookingResponse {
  contract_id: string;
  institution: string;
  total_bookings: number;
  estimated_monthly_cost: string | number;
  cooperative_workers_needed: number;
  welfare_fund_contribution: string | number;
  line_items: BulkBookingLineItemResponse[];
}

export function useCreateBulkBooking() {
  return useMutation<EnterpriseBookingResponse, Error, EnterpriseBookingRequest>({
    mutationFn: async (data: EnterpriseBookingRequest): Promise<EnterpriseBookingResponse> => {
      return api.post('/enterprise/bookings', data);
    },
  });
}
