import { useState, useCallback } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import { useQuery } from '@tanstack/react-query';
import { Wind, Droplets, ShieldAlert, MapPin } from 'lucide-react';
import { heatmapApi } from '@/services/api/heatmap';
import { sensorsApi } from '@/services/api/sensors';
import { RISK_COLORS, getAQICategory } from '@/utils/risk';
import type { HeatmapPoint, RiskLevel } from '@/types';
import clsx from 'clsx';

type MapLayer = 'risk' | 'air' | 'water' | 'sensors';

const LAYER_CONFIG: Record<MapLayer, { label: string; icon: any; query: any }> = {
  risk: { label: 'Health Risk', icon: ShieldAlert, query: heatmapApi.getRisk },
  air: { label: 'Air Quality', icon: Wind, query: heatmapApi.getAir },
  water: { label: 'Water Quality', icon: Droplets, query: heatmapApi.getWater },
  sensors: { label: 'Sensors', icon: MapPin, query: sensorsApi.getAll },
};

function getPointColor(layer: MapLayer, point: HeatmapPoint): string {
  if (layer === 'risk') return RISK_COLORS[point.risk_level as RiskLevel] || '#94a3b8';
  if (layer === 'air') {
    const aqi = point.value || 0;
    return getAQICategory(aqi).color;
  }
  return RISK_COLORS[point.risk_level as RiskLevel] || '#94a3b8';
}

interface LocationPanelProps {
  point: HeatmapPoint | null;
  onClose: () => void;
}

function LocationPanel({ point, onClose }: LocationPanelProps) {
  if (!point) return null;
  return (
    <div className="absolute bottom-6 left-4 right-4 md:left-auto md:right-4 md:w-72 bg-white rounded-xl shadow-xl border border-gray-100 z-[1000] p-4">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="font-semibold text-gray-800">{point.location_name}</h3>
          <p className="text-xs text-gray-400">{point.grid_id}</p>
        </div>
        <button onClick={onClose} className="text-gray-300 hover:text-gray-500 text-lg leading-none">×</button>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-xs text-gray-500">Risk Score</span>
          <span className="text-xs font-semibold" style={{ color: RISK_COLORS[point.risk_level as RiskLevel] }}>
            {point.risk_score.toFixed(0)} — {point.risk_level}
          </span>
        </div>
        {point.value != null && (
          <div className="flex justify-between">
            <span className="text-xs text-gray-500">{point.label?.split(':')[0]}</span>
            <span className="text-xs font-medium text-gray-700">{point.value.toFixed(0)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export function HealthMap({ initialLocation }: { initialLocation?: { lat: number; lng: number } }) {
  const [layer, setLayer] = useState<MapLayer>('risk');
  const [selected, setSelected] = useState<HeatmapPoint | null>(null);
  const center = initialLocation || { lat: 22.5, lng: 78.96 }; // India center

  const { data: heatmapData } = useQuery({
    queryKey: ['heatmap', layer],
    queryFn: LAYER_CONFIG[layer as 'risk' | 'air' | 'water'].query,
    enabled: layer !== 'sensors',
    staleTime: 60_000,
  });

  const { data: sensorData } = useQuery({
    queryKey: ['sensors-map'],
    queryFn: sensorsApi.getAll,
    staleTime: 60_000,
  });

  const points: HeatmapPoint[] = (heatmapData as any)?.points || [];

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden">
      {/* Layer selector */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 z-[1000] flex gap-1 bg-white/90 backdrop-blur-sm rounded-full p-1 shadow-md">
        {(Object.entries(LAYER_CONFIG) as [MapLayer, typeof LAYER_CONFIG[MapLayer]][]).map(([key, cfg]) => {
          const Icon = cfg.icon;
          return (
            <button
              key={key}
              onClick={() => setLayer(key)}
              className={clsx(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all',
                layer === key ? 'bg-gray-800 text-white' : 'text-gray-600 hover:bg-gray-100'
              )}
            >
              <Icon size={12} />
              {cfg.label}
            </button>
          );
        })}
      </div>

      <MapContainer
        center={[center.lat, center.lng]}
        zoom={5}
        style={{ height: '100%', width: '100%' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />

        {/* Heatmap points */}
        {layer !== 'sensors' && points.map((point) => (
          <CircleMarker
            key={point.location_id}
            center={[point.latitude, point.longitude]}
            radius={14}
            pathOptions={{
              fillColor: getPointColor(layer, point),
              fillOpacity: 0.75,
              color: getPointColor(layer, point),
              weight: 1,
            }}
            eventHandlers={{ click: () => setSelected(point) }}
          >
            <Popup>
              <div className="text-sm">
                <strong>{point.location_name}</strong>
                <br />
                Risk: {point.risk_score.toFixed(0)} — {point.risk_level}
                {point.label && <><br />{point.label}</>}
              </div>
            </Popup>
          </CircleMarker>
        ))}

        {/* Sensor markers */}
        {(layer === 'sensors' || layer === 'risk') && (sensorData || []).map((sensor: any) => (
          <CircleMarker
            key={sensor.id}
            center={[sensor.latitude, sensor.longitude]}
            radius={5}
            pathOptions={{
              fillColor: sensor.status === 'ONLINE' ? '#22c55e' : sensor.status === 'WARNING' ? '#f59e0b' : '#ef4444',
              fillOpacity: 1,
              color: '#fff',
              weight: 1.5,
            }}
          >
            <Popup>
              <div className="text-xs">
                <strong>{sensor.sensor_code}</strong>
                <br />
                {sensor.type} · {sensor.status}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg shadow p-2 z-[1000]">
        <p className="text-xs font-medium text-gray-500 mb-1.5">Risk Level</p>
        <div className="flex flex-col gap-1">
          {(['LOW', 'MODERATE', 'ELEVATED', 'HIGH', 'VERY HIGH'] as RiskLevel[]).map(level => (
            <div key={level} className="flex items-center gap-1.5">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: RISK_COLORS[level] }} />
              <span className="text-xs text-gray-500">{level}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Location detail panel */}
      <LocationPanel point={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
