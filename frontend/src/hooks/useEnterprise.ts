import { useMutation } from '@tanstack/react-query';
// import { api } from '../lib/api';

export interface EnterpriseBookingRequest {
  institution_name: string;
  services: {
    skill: string;
    quantity: number;
    schedule: 'daily' | 'weekly' | 'monthly';
  }[];
}

export interface EnterpriseBookingResponse {
  total_bookings_per_month: number;
  estimated_monthly_cost: number;
  workers_needed: number;
  welfare_fund_contribution: number;
}

export function useCreateBulkBooking() {
  return useMutation({
    mutationFn: async (data: EnterpriseBookingRequest): Promise<EnterpriseBookingResponse> => {
      // TODO: Replace with actual API call once POST /enterprise/bookings is implemented
      // return api.post('/enterprise/bookings', data);

      // Mocking the backend API response for Demo purposes
      await new Promise((resolve) => setTimeout(resolve, 800));

      let total_bookings = 0;
      let total_cost = 0;

      data.services.forEach((service) => {
        let multiplier = 1;
        if (service.schedule === 'daily') multiplier = 30;
        else if (service.schedule === 'weekly') multiplier = 4;
        else if (service.schedule === 'monthly') multiplier = 1;

        total_bookings += service.quantity * multiplier;
        total_cost += service.quantity * multiplier * 500; // Mock cost 500 INR per booking
      });

      return {
        total_bookings_per_month: total_bookings,
        estimated_monthly_cost: total_cost,
        workers_needed: Math.ceil(total_bookings / 30) || 1, // At least 1 worker if bookings exist
        welfare_fund_contribution: total_cost * 0.02, // 2% of total cost goes to Welfare Fund
      };
    },
  });
}
