import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { locationsApi } from '@/services/api/locations';
import { historyApi } from '@/services/api/history';
import { Card, CardBody } from '@/components/ui/Card';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from 'recharts';

const PERIODS = ['24h', '7d', '30d', '90d', '180d', '1y'];

export function HistoryPage() {
  const [period, setPeriod] = useState('30d');
  const [locationId, setLocationId] = useState('');

  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: locationsApi.getAll,
    staleTime: 5 * 60_000,
  });

  useEffect(() => {
    if (locations && locations.length > 0 && !locationId) {
      setLocationId(locations[0].id);
    }
  }, [locations, locationId]);

  const selectedId = locationId || (locations?.[0]?.id ?? '');

  const { data: history, isLoading } = useQuery({
    queryKey: ['history', selectedId, period],
    queryFn: () => historyApi.getForLocation(selectedId, period),
    enabled: !!selectedId,
    staleTime: 60_000,
  });

  const envSeries = history?.environment_series || {};

  const aqiData = (envSeries['aqi'] || []).map(d => ({ date: d.timestamp, aqi: d.value }));
  const tempData = (envSeries['temperature'] || []).map(d => ({ date: d.timestamp, temp: d.value }));

  const topSymptoms = Object.entries(history?.health || {})
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Historical Records</h1>
          <p className="text-sm text-gray-500 mt-0.5">Environmental and health activity over time</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <select
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white text-gray-600"
            value={selectedId}
            onChange={(e) => setLocationId(e.target.value)}
          >
            {(locations || []).map((l) => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </select>
          <div className="flex gap-1">
            {PERIODS.map(p => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`text-xs px-2.5 py-1.5 rounded-lg border transition-all ${
                  period === p
                    ? 'bg-gray-900 text-white border-gray-900'
                    : 'border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <SkeletonCard lines={4} /><SkeletonCard lines={4} />
        </div>
      )}

      {history && (
        <>
          {/* Symptom summary */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {topSymptoms.map(([symptom, count]) => (
              <Card key={symptom}>
                <CardBody className="pt-3 pb-3">
                  <p className="text-xs text-gray-400 capitalize mb-0.5">{symptom.replace(/_/g, ' ')}</p>
                  <p className="text-xl font-bold text-gray-800">{count}</p>
                  <p className="text-xs text-gray-400">reports</p>
                </CardBody>
              </Card>
            ))}
          </div>

          {aqiData.length > 1 && (
            <Card>
              <CardBody className="pt-5">
                <p className="text-sm font-medium text-gray-700 mb-4">Air Quality Index (AQI)</p>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={aqiData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={v => v.slice(5)} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ fontSize: 12 }} />
                    <Line type="monotone" dataKey="aqi" stroke="#f97316" strokeWidth={2} dot={false} name="AQI" />
                  </LineChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>
          )}

          {tempData.length > 1 && (
            <Card>
              <CardBody className="pt-5">
                <p className="text-sm font-medium text-gray-700 mb-4">Temperature (°C)</p>
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={tempData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={v => v.slice(5)} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ fontSize: 12 }} />
                    <Line type="monotone" dataKey="temp" stroke="#3b82f6" strokeWidth={2} dot={false} name="Temp °C" />
                  </LineChart>
                </ResponsiveContainer>
              </CardBody>
            </Card>
          )}

          <Card>
            <CardBody className="pt-5">
              <p className="text-sm font-medium text-gray-700 mb-4">Environment Summary — {period}</p>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {Object.entries(history.environment)
                  .filter(([, v]) => v != null && v !== 0)
                  .map(([key, val]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-400 mb-1 capitalize">{key.replace(/_/g, ' ')}</p>
                      <p className="text-base font-semibold text-gray-700">{(val as number).toFixed(1)}</p>
                    </div>
                  ))}
              </div>
            </CardBody>
          </Card>
        </>
      )}
    </div>
  );
}
