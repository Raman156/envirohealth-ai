import { useQuery } from '@tanstack/react-query';
import { ShieldAlert, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { riskApi } from '@/services/api/risk';
import { Card, CardBody } from './ui/Card';
import { SkeletonCard } from './ui/SkeletonCard';
import { RISK_TEXT, RISK_BG, RISK_COLORS } from '@/utils/risk';
import type { RiskLevel } from '@/types';
import clsx from 'clsx';

interface RiskCardProps {
  locationId: string;
}

export function RiskCard({ locationId }: RiskCardProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['risk', locationId],
    queryFn: () => riskApi.getForLocation(locationId),
    refetchInterval: 60_000,
    staleTime: 30_000,
  });

  if (isLoading) return <SkeletonCard lines={4} />;
  if (error || !data) return null;

  const level = data.risk_level as RiskLevel;
  const TrendIcon = data.trend === 'INCREASING' ? TrendingUp
    : data.trend === 'DECREASING' ? TrendingDown : Minus;

  return (
    <Card>
      <CardBody className="pt-5">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-1">Environmental Health Risk</p>
            <div className="flex items-end gap-2">
              <span className={clsx('text-5xl font-bold', RISK_TEXT[level])}>{data.risk_score.toFixed(0)}</span>
              <span className="text-gray-400 text-sm mb-1">/ 100</span>
            </div>
          </div>
          <div className={clsx('flex items-center gap-1 px-3 py-1.5 rounded-full text-white text-sm font-semibold', RISK_BG[level])}>
            <ShieldAlert size={14} />
            {data.risk_level}
          </div>
        </div>

        {/* Risk gauge bar */}
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden mb-4">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{ width: `${data.risk_score}%`, backgroundColor: RISK_COLORS[level] }}
          />
        </div>

        {/* Explanation */}
        {data.explanation.length > 0 && (
          <div className="space-y-1 mb-3">
            {data.explanation.slice(0, 3).map((exp, i) => (
              <p key={i} className="text-xs text-gray-500 flex items-start gap-1.5">
                <span className="text-amber-500 mt-0.5">•</span>
                {exp}
              </p>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between pt-2 border-t border-gray-50">
          <div className="flex items-center gap-1.5 text-xs text-gray-400">
            <TrendIcon size={12} className={data.trend === 'INCREASING' ? 'text-red-400' : data.trend === 'DECREASING' ? 'text-green-400' : 'text-gray-400'} />
            <span>{data.trend}</span>
          </div>
          <span className="text-xs text-gray-300">{(data.confidence * 100).toFixed(0)}% confidence</span>
        </div>
      </CardBody>
    </Card>
  );
}
