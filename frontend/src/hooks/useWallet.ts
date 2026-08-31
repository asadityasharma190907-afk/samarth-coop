import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface EarningsEntry {
  id: string;
  created_at: string;
  skill: string;
  job_price: string | number;
  platform_fee: string | number;
}

export interface WalletData {
  weekly_earnings: string | number;
  lifetime_earnings: string | number;
  entries: EarningsEntry[];
}

export function useWallet(workerId: string | undefined) {
  return useQuery<WalletData, Error>({
    queryKey: ['wallet', workerId],
    queryFn: async () => {
      if (!workerId) throw new Error('Worker ID is required');
      const { data } = await api.get(`/wallet/${workerId}`);
      return data;
    },
    enabled: !!workerId,
  });
}
