import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface WelfareSummary {
  total_fees: number;
  completed_bookings: number;
  total_disbursed: number;
  remaining_balance: number;
  category_breakdown: Record<string, number>;
}

export interface WelfareDisbursementItem {
  id: string;
  amount: number;
  category: string;
  description?: string | null;
  disbursed_at: string;
}

export function useWelfareSummary() {
  return useQuery({
    queryKey: ['welfareSummary'],
    queryFn: async () => {
      const response = await api.get('/welfare-fund/summary');
      return response as WelfareSummary;
    },
    refetchInterval: 10000,
  });
}

export function useWelfareDisbursements() {
  return useQuery({
    queryKey: ['welfareDisbursements'],
    queryFn: async () => {
      const response = await api.get('/welfare-fund/disbursements');
      return response as WelfareDisbursementItem[];
    },
    refetchInterval: 10000,
  });
}
