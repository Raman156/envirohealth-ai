import apiClient from '@/api/client';
import type { HeatmapResponse } from '@/types';

export const heatmapApi = {
  getRisk: () => apiClient.get<HeatmapResponse>('/heatmap/risk').then(r => r.data),
  getAir: () => apiClient.get<HeatmapResponse>('/heatmap/air').then(r => r.data),
  getWater: () => apiClient.get<HeatmapResponse>('/heatmap/water').then(r => r.data),
};
