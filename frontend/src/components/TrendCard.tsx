import { useQuery } from '@tanstack/react-query';
import { Activity } from 'lucide-react';
import { trendsApi } from '@/services/api/trends';
import { Card, CardBody } from './ui/Card';
import { SkeletonCard } from './ui/SkeletonCard';
import { EmptyState } from './ui/EmptyState';
import { getTrendIcon, getTrendColor, formatTrendChange } from '@/utils/risk';
import clsx from 'clsx';

interface TrendCardProps {
  locationId: string;
  periodDays?: number;
}

export function TrendCard({ locationId, periodDays = 7 }: TrendCardProps) {
  const { data, isLoading } = useQuery({
    queryKey: ['trends', locationId, periodDays],
    queryFn: () => trendsApi.getForLocation(locationId, periodDays),
    staleTime: 60_000,
  });

  if (isLoading) return <SkeletonCard lines={5} />;

  return (
    <Card>
      <CardBody className="pt-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider font-medium">Trending in Your Area</p>
            <p className="text-xs text-gray-400 mt-0.5">Last {periodDays} days vs previous</p>
          </div>
          <Activity size={16} className="text-gray-300" />
        </div>

        {!data || data.trends.length === 0 ? (
          <EmptyState
            title="No health reports yet"
            description="Be the first to anonymously report how you're feeling."
          />
        ) : (
          <div className="space-y-2.5">
            {data.trends.slice(0, 6).map((trend) => (
              <div key={trend.condition} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={clsx('text-sm font-medium w-4 text-center', getTrendColor(trend.direction))}>
                    {getTrendIcon(trend.direction)}
                  </span>
                  <span className="text-sm text-gray-700 capitalize">{trend.condition.replace(/_/g, ' ')}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400">{trend.current} reports</span>
                  <span className={clsx('text-xs font-semibold', getTrendColor(trend.direction))}>
                    {formatTrendChange(trend.change_percent)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
}
