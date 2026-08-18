import apiClient from '@/api/client';
import type { HistoryResponse } from '@/types';

export const historyApi = {
  getForLocation: (locationId: string, period = '30d') =>
    apiClient.get<HistoryResponse>(`/history/${locationId}`, { params: { period } }).then(r => r.data),
};
