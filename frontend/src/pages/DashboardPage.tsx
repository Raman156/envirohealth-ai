import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapPin } from 'lucide-react';
import { useNearestLocation } from '@/hooks/useNearestLocation';
import { RiskCard } from '@/components/RiskCard';
import { TrendCard } from '@/components/TrendCard';
import { AlertList } from '@/components/AlertList';
import { HealthMap } from '@/components/HealthMap';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { Card, CardBody } from '@/components/ui/Card';
import { historyApi } from '@/services/api/history';
import { locationsApi } from '@/services/api/locations';
import { getAQICategory } from '@/utils/risk';
import { Link } from 'react-router-dom';
import type { Location } from '@/types';

function EnvStat({ label, value, sub, color }: { label: string; value: string; sub?: string; color?: string }) {
  return (
    <Card>
      <CardBody className="pt-4 pb-4">
        <p className="text-xs text-gray-400 mb-1">{label}</p>
        <p className="text-2xl font-bold" style={color ? { color } : undefined}>{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
      </CardBody>
    </Card>
  );
}

export function DashboardPage() {
  const { data: nearestLocation, isLoading: locationLoading } = useNearestLocation();
  const [selectedLocationId, setSelectedLocationId] = useState<string>('');

  const { data: allLocations } = useQuery({
    queryKey: ['locations'],
    queryFn: locationsApi.getAll,
    staleTime: 5 * 60_000,
  });

  // Use nearest location by default, allow manual override
  const location: Location | null = selectedLocationId
    ? (allLocations?.find(l => l.id === selectedLocationId) ?? nearestLocation ?? null)
    : (nearestLocation ?? (allLocations?.[0] ?? null));

  const { data: history } = useQuery({
    queryKey: ['history', location?.id, '24h'],
    queryFn: () => historyApi.getForLocation(location!.id, '24h'),
    enabled: !!location,
    staleTime: 30_000,
  });

  const aqi = history?.environment?.average_aqi || 0;
  const aqiCat = getAQICategory(aqi);
  const temp = history?.environment?.average_temperature;
  const humidity = history?.environment?.average_humidity;
  const ph = history?.environment?.average_water_ph;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Dashboard</h1>
          {location && (
            <div className="flex items-center gap-1.5 mt-1 text-sm text-gray-500">
              <MapPin size={13} />
              <span>{location.name}, {location.city}</span>
            </div>
          )}
        </div>
        {allLocations && (
          <select
            className="text-sm border border-gray-200 rounded-lg px-3 py-1.5 text-gray-600 bg-white"
            value={location?.id ?? ''}
            onChange={(e) => setSelectedLocationId(e.target.value)}
          >
            {allLocations.map(l => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </select>
        )}
      </div>

      {locationLoading && !allLocations && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <SkeletonCard /><SkeletonCard /><SkeletonCard />
        </div>
      )}

      {location && (
        <>
          {/* Risk + env stats */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            <div className="lg:col-span-1">
              <RiskCard locationId={location.id} />
            </div>
            <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4 content-start">
              <EnvStat
                label="Air Quality (AQI)"
                value={aqi > 0 ? aqi.toFixed(0) : '—'}
                sub={aqi > 0 ? aqiCat.label : 'No data'}
                color={aqi > 0 ? aqiCat.color : undefined}
              />
              <EnvStat
                label="Temperature"
                value={temp ? `${temp.toFixed(1)}°C` : '—'}
                sub={humidity ? `Humidity ${humidity.toFixed(0)}%` : undefined}
              />
              <EnvStat
                label="Water Quality"
                value={ph ? `pH ${ph.toFixed(1)}` : '—'}
                sub={ph
                  ? (ph > 6.5 && ph < 8.5 ? 'Acceptable range' : 'Outside normal range')
                  : undefined}
              />
            </div>
          </div>

          {/* Trends + Alerts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <TrendCard locationId={location.id} />
            <AlertList locationId={location.id} />
          </div>

          {/* Map preview */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
            <div className="px-5 pt-4 pb-3 flex items-center justify-between">
              <p className="text-sm font-medium text-gray-700">Environmental Health Map</p>
              <Link to="/map" className="text-xs text-brand-600 hover:text-brand-700">Full map →</Link>
            </div>
            <div style={{ height: '360px' }}>
              <HealthMap initialLocation={{ lat: location.latitude, lng: location.longitude }} />
            </div>
          </div>
        </>
      )}

      <p className="text-xs text-gray-400 text-center pb-2">
        EnviroHealth AI detects community-level risk patterns — not a medical diagnosis tool.
      </p>
    </div>
  );
}
