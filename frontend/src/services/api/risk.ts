import apiClient from '@/api/client';
import type { RiskPrediction } from '@/types';

export const riskApi = {
  getForLocation: (locationId: string) =>
    apiClient.get<RiskPrediction>(`/risk/${locationId}`).then(r => r.data),
  recalculate: (locationId: string) =>
    apiClient.post<RiskPrediction>(`/risk/${locationId}/recalculate`).then(r => r.data),
};
