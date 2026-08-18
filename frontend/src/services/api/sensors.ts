import apiClient from '@/api/client';
import type { Sensor, AdminStats } from '@/types';

export const sensorsApi = {
  getAll: () => apiClient.get<Sensor[]>('/sensors').then(r => r.data),
};

export const adminApi = {
  getStats: () => apiClient.get<AdminStats>('/admin/stats').then(r => r.data),
  getSensors: () => apiClient.get<Sensor[]>('/admin/sensors').then(r => r.data),
  deactivateSensor: (id: string) => apiClient.patch(`/admin/sensors/${id}/deactivate`).then(r => r.data),
};
