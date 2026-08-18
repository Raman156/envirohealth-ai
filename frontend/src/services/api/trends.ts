import apiClient from '@/api/client';
import type { TrendsResponse } from '@/types';

export const trendsApi = {
  getForLocation: (locationId: string, periodDays = 7) =>
    apiClient.get<TrendsResponse>(`/trends/${locationId}`, { params: { period_days: periodDays } }).then(r => r.data),
};
