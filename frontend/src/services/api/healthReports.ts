import apiClient from '@/api/client';
import type { HealthReportForm } from '@/types';

export const healthReportsApi = {
  submit: (data: HealthReportForm) => apiClient.post('/health-reports', data).then(r => r.data),
};
