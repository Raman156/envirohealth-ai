import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { locationsApi } from '@/services/api/locations';
import { trendsApi } from '@/services/api/trends';
import { TrendCard } from '@/components/TrendCard';
import { Card, CardBody } from '@/components/ui/Card';
import { getTrendColor, getTrendIcon, formatTrendChange } from '@/utils/risk';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import clsx from 'clsx';

const PERIOD_OPTIONS = [
  { value: 7, label: '7 days' },
  { value: 14, label: '14 days' },
  { value: 30, label: '30 days' },
];

export function TrendsPage() {
  const [periodDays, setPeriodDays] = useState(7);
  const [locationId, setLocationId] = useState<string>('');

  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: locationsApi.getAll,
    staleTime: 5 * 60_000,
  });

  // Set default location once loaded
  useEffect(() => {
    if (locations && locations.length > 0 && !locationId) {
      setLocationId(locations[0].id);
    }
  }, [locations, locationId]);

  const selectedLocation = locationId || (locations?.[0]?.id ?? '');

  const { data: trends } = useQuery({
    queryKey: ['trends', selectedLocation, periodDays],
    queryFn: () => trendsApi.getForLocation(selectedLocation, periodDays),
    enabled: !!selectedLocation,
    staleTime: 60_000,
  });

  const chartData = (trends?.trends || []).map(t => ({
    name: t.condition.replace(/_/g, ' '),
    current: t.current,
    previous: t.previous,
    change: t.change_percent,
    direction: t.direction,
  }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Local Trends</h1>
          <p className="text-sm text-gray-500 mt-0.5">Community health activity compared to the previous period</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <select
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-600"
            value={selectedLocation}
            onChange={(e) => setLocationId(e.target.value)}
          >
            {(locations || []).map((l) => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </select>
          {PERIOD_OPTIONS.map(opt => (
            <button
              key={opt.value}
              onClick={() => setPeriodDays(opt.value)}
              className={clsx(
                'text-sm px-3 py-1.5 rounded-lg border transition-all',
                periodDays === opt.value
                  ? 'bg-gray-900 text-white border-gray-900'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300'
              )}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {selectedLocation && <TrendCard locationId={selectedLocation} periodDays={periodDays} />}

        <Card>
          <CardBody className="pt-5">
            <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-4">
              Symptom Volume — Current vs Previous
            </p>
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData} layout="vertical">
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(val: number, name: string) => [val, name === 'current' ? 'Current' : 'Previous']}
                    contentStyle={{ fontSize: 12 }}
                  />
                  <Bar dataKey="previous" fill="#e5e7eb" name="previous" radius={[0, 2, 2, 0]} />
                  <Bar dataKey="current" name="current" radius={[0, 2, 2, 0]}>
                    {chartData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={
                          entry.direction === 'INCREASING' ? '#f97316'
                          : entry.direction === 'DECREASING' ? '#22c55e'
                          : '#94a3b8'
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400 text-center py-8">No trend data available</p>
            )}
          </CardBody>
        </Card>
      </div>

      {(trends?.trends || []).length > 0 && (
        <Card>
          <CardBody className="pt-5">
            <p className="text-xs text-gray-500 uppercase tracking-wider font-medium mb-4">All Symptoms</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-gray-400 border-b border-gray-100">
                    <th className="pb-2 font-medium">Symptom</th>
                    <th className="pb-2 font-medium text-right">Current</th>
                    <th className="pb-2 font-medium text-right">Previous</th>
                    <th className="pb-2 font-medium text-right">Change</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {trends!.trends.map(t => (
                    <tr key={t.condition}>
                      <td className="py-2 text-gray-700 capitalize">{t.condition.replace(/_/g, ' ')}</td>
                      <td className="py-2 text-right text-gray-600">{t.current}</td>
                      <td className="py-2 text-right text-gray-400">{t.previous}</td>
                      <td className={clsx('py-2 text-right font-medium', getTrendColor(t.direction))}>
                        {getTrendIcon(t.direction)} {formatTrendChange(t.change_percent)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  );
}
