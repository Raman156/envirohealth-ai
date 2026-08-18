import { HealthMap } from '@/components/HealthMap';

export function MapPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-gray-900">Environmental Health Map</h1>
        <p className="text-sm text-gray-500 mt-0.5">Click any location to view detailed risk data. Use the layer controls to switch between views.</p>
      </div>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden" style={{ height: 'calc(100vh - 180px)' }}>
        <HealthMap />
      </div>
    </div>
  );
}
