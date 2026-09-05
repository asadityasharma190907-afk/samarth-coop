import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';

export interface PricePreviewData {
  skill: string;
  base_price: number;
  final_price: number;
  surge_surplus: number;
  is_surging: boolean;
  surge_reason?: string | null;
  urgency_multiplier: number;
  worker_earns: number;
  welfare_fund_contribution: number;
  platform_fee: number;
}

export function usePricePreview(
  skill: string | null,
  lat: number,
  lng: number,
  urgency: 'normal' | 'urgent' | 'emergency' = 'normal',
) {
  return useQuery<PricePreviewData>({
    queryKey: ['price-preview', skill, lat, lng, urgency],
    queryFn: async () => {
      if (!skill) throw new Error('Skill is required');
      const response = await api.get(
        `/bookings/price-preview?skill=${encodeURIComponent(skill)}&lat=${lat}&lng=${lng}&urgency=${urgency}`,
      );
      return response as PricePreviewData;
    },
    enabled: !!skill,
  });
}
