import apiClient from '@/api/client';
import type { Location } from '@/types';

export const locationsApi = {
  getAll: () => apiClient.get<Location[]>('/locations').then(r => r.data),
  getById: (id: string) => apiClient.get<Location>(`/locations/${id}`).then(r => r.data),
  getNearby: (lat: number, lng: number, radius = 5) =>
    apiClient.get<Location[]>(`/locations/nearby`, { params: { lat, lng, radius } }).then(r => r.data),
};
