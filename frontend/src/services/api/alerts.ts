import apiClient from '@/api/client';
import type { Alert } from '@/types';

export const alertsApi = {
  getActive: (locationId?: string) =>
    apiClient.get<Alert[]>('/alerts', { params: locationId ? { location_id: locationId } : {} }).then(r => r.data),
};
