import { useQuery } from '@tanstack/react-query';
import { AlertTriangle, Wind, Droplets, Thermometer, Activity } from 'lucide-react';
import { alertsApi } from '@/services/api/alerts';
import { Card, CardBody } from './ui/Card';
import { SkeletonCard } from './ui/SkeletonCard';
import { EmptyState } from './ui/EmptyState';
import { SeverityBadge } from './ui/Badge';
import { formatDistanceToNow } from 'date-fns';
import clsx from 'clsx';

const TYPE_ICONS: Record<string, any> = {
  HEALTH_RISK: AlertTriangle,
  AIR_QUALITY: Wind,
  WATER_QUALITY: Droplets,
  WEATHER: Thermometer,
  TREND: Activity,
};

interface AlertListProps {
  locationId?: string;
  limit?: number;
}

export function AlertList({ locationId, limit = 5 }: AlertListProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['alerts', locationId],
    queryFn: () => alertsApi.getActive(locationId),
    refetchInterval: 30_000,
    staleTime: 15_000,
  });

  if (isLoading) return <SkeletonCard lines={3} />;

  const alerts = (data || []).slice(0, limit);

  return (
    <Card>
      <CardBody className="pt-5">
        <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-4">Active Alerts</p>

        {alerts.length === 0 ? (
          <EmptyState
            title="No active alerts"
            description="No environmental health alerts for this area right now."
          />
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => {
              const Icon = TYPE_ICONS[alert.type] || AlertTriangle;
              const borderColor: Record<string, string> = {
                LOW: 'border-l-green-400',
                MODERATE: 'border-l-amber-400',
                HIGH: 'border-l-orange-500',
                CRITICAL: 'border-l-red-600',
              };
              return (
                <div key={alert.id} className={clsx('border-l-4 pl-3 py-1', borderColor[alert.severity] || 'border-l-gray-300')}>
                  <div className="flex items-start gap-2">
                    <Icon size={14} className="text-gray-400 mt-0.5 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <p className="text-sm font-medium text-gray-800 leading-tight">{alert.title}</p>
                        <SeverityBadge severity={alert.severity} />
                      </div>
                      <p className="text-xs text-gray-500 line-clamp-2">{alert.message}</p>
                      <p className="text-xs text-gray-300 mt-1">
                        {formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
