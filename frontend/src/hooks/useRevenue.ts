import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface RevenueStream {
  name: string;
  amount: number;
  percentage: number;
}

export interface RevenueAnalyticsResponse {
  gmv: number;
  platform_revenue: number;
  welfare_fund: number;

  avg_order_value: number;
  blended_fee_percentage: number;
  net_margin_per_booking: number;

  breakeven_target_bookings: number;
  current_bookings: number;
  breakeven_percentage: number;

  revenue_streams: RevenueStream[];
}

export function useRevenue() {
  return useQuery({
    queryKey: ['revenueAnalytics'],
    queryFn: async () => {
      const response = await api.get('/analytics/revenue');
      return response as RevenueAnalyticsResponse;
    },
    refetchInterval: 10000,
  });
}
