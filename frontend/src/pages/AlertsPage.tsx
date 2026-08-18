import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '@/services/api/alerts';
import { locationsApi } from '@/services/api/locations';
import { Card, CardBody } from '@/components/ui/Card';
import { SeverityBadge } from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { Bell, AlertTriangle, Wind, Droplets, Activity, Thermometer } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

const ICONS: Record<string, any> = {
  HEALTH_RISK: AlertTriangle,
  AIR_QUALITY: Wind,
  WATER_QUALITY: Droplets,
  WEATHER: Thermometer,
  TREND: Activity,
};

export function AlertsPage() {
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['all-alerts'],
    queryFn: () => alertsApi.getActive(),
    refetchInterval: 30_000,
    staleTime: 15_000,
  });

  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: locationsApi.getAll,
    staleTime: 5 * 60_000,
  });

  const locationMap = Object.fromEntries((locations || []).map(l => [l.id, l.name]));

  if (isLoading) return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-gray-900">Active Alerts</h1>
      <SkeletonCard lines={4} /><SkeletonCard lines={4} />
    </div>
  );

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Active Alerts</h1>
        <span className="text-sm text-gray-400">{(alerts || []).length} active</span>
      </div>

      {(alerts || []).length === 0 ? (
        <Card>
          <CardBody className="py-12">
            <EmptyState
              icon={<Bell size={40} />}
              title="No active alerts"
              description="No environmental health alerts at this time. The system monitors continuously."
            />
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-3">
          {(alerts || []).map((alert) => {
            const Icon = ICONS[alert.type] || AlertTriangle;
            return (
              <Card key={alert.id}>
                <CardBody className="py-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-gray-50 rounded-lg flex items-center justify-center shrink-0">
                      <Icon size={16} className="text-gray-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-gray-800 text-sm">{alert.title}</p>
                        <SeverityBadge severity={alert.severity} />
                      </div>
                      <p className="text-sm text-gray-500 mb-2">{alert.message}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-400">
                        {alert.location_id && <span>📍 {locationMap[alert.location_id] || 'Unknown area'}</span>}
                        {alert.risk_score != null && <span>Risk: {alert.risk_score.toFixed(0)}/100</span>}
                        <span>{formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}</span>
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
