import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminApi } from '@/services/api/sensors';
import { Card, CardBody } from '@/components/ui/Card';
import { SkeletonCard } from '@/components/ui/SkeletonCard';
import { Users, Activity, Wifi, WifiOff, Database, Bell, PowerOff } from 'lucide-react';
import clsx from 'clsx';

function StatBox({ icon: Icon, label, value, color }: any) {
  return (
    <Card>
      <CardBody className="pt-4 pb-4">
        <div className="flex items-center gap-3">
          <div className={clsx('w-9 h-9 rounded-lg flex items-center justify-center', color)}>
            <Icon size={16} className="text-white" />
          </div>
          <div>
            <p className="text-xs text-gray-400">{label}</p>
            <p className="text-xl font-bold text-gray-800">{value?.toLocaleString() ?? '—'}</p>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}

export function AdminPage() {
  const [loginState, setLoginState] = useState<'prompt' | 'authed'>('prompt');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const qc = useQueryClient();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || 'Login failed');
      localStorage.setItem('auth_token', data.access_token);
      setLoginState('authed');
    } catch (err: any) {
      setLoginError(err.message);
    }
  };

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: adminApi.getStats,
    enabled: loginState === 'authed',
    staleTime: 30_000,
  });

  const { data: sensors, isLoading: sensorsLoading } = useQuery({
    queryKey: ['admin-sensors'],
    queryFn: adminApi.getSensors,
    enabled: loginState === 'authed',
    staleTime: 30_000,
  });

  const deactivateMutation = useMutation({
    mutationFn: adminApi.deactivateSensor,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-sensors'] }),
  });

  if (loginState === 'prompt') {
    return (
      <div className="max-w-sm mx-auto pt-12">
        <h1 className="text-xl font-bold text-gray-900 mb-6">Admin Login</h1>
        <Card>
          <CardBody className="pt-6">
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="text-sm text-gray-600 block mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  placeholder="admin@envirohealth.ai"
                />
              </div>
              <div>
                <label className="text-sm text-gray-600 block mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                />
              </div>
              {loginError && <p className="text-red-500 text-xs">{loginError}</p>}
              <button type="submit" className="w-full bg-gray-900 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-gray-800">
                Sign In
              </button>
              <p className="text-xs text-gray-400 text-center">Demo: admin@envirohealth.ai / Admin@1234</p>
            </form>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Admin Dashboard</h1>
        <button
          onClick={() => { localStorage.removeItem('auth_token'); setLoginState('prompt'); }}
          className="text-xs text-gray-400 hover:text-gray-600"
        >
          Sign out
        </button>
      </div>

      {statsLoading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1,2,3,4].map(i => <SkeletonCard key={i} lines={2} />)}
        </div>
      ) : stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatBox icon={Users} label="Total Users" value={stats.total_users} color="bg-blue-500" />
          <StatBox icon={Activity} label="Health Reports" value={stats.total_health_reports} color="bg-brand-500" />
          <StatBox icon={Wifi} label="Online Sensors" value={stats.online_sensors} color="bg-green-500" />
          <StatBox icon={WifiOff} label="Offline Sensors" value={stats.offline_sensors} color="bg-red-400" />
          <StatBox icon={Database} label="Env Readings" value={stats.total_env_readings} color="bg-purple-500" />
          <StatBox icon={Bell} label="Active Alerts" value={stats.active_alerts} color="bg-amber-500" />
        </div>
      )}

      {/* Sensor management */}
      <Card>
        <CardBody className="pt-5">
          <p className="text-sm font-medium text-gray-700 mb-4">Sensor Health</p>
          {sensorsLoading ? <SkeletonCard lines={5} /> : (
            <div className="space-y-2">
              {(sensors || []).map((sensor: any) => (
                <div key={sensor.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                  <div className="flex items-center gap-3">
                    <div className={clsx('w-2 h-2 rounded-full', {
                      'bg-green-500': sensor.status === 'ONLINE',
                      'bg-red-500': sensor.status === 'OFFLINE',
                      'bg-amber-500': sensor.status === 'WARNING',
                    })} />
                    <div>
                      <p className="text-sm font-medium text-gray-700">{sensor.sensor_code}</p>
                      <p className="text-xs text-gray-400">{sensor.type} · {sensor.status}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">
                      {sensor.last_seen ? new Date(sensor.last_seen).toLocaleTimeString() : 'Never'}
                    </span>
                    {sensor.status === 'ONLINE' && (
                      <button
                        onClick={() => deactivateMutation.mutate(sensor.id)}
                        className="text-xs text-red-400 hover:text-red-600 flex items-center gap-1"
                        title="Deactivate sensor"
                      >
                        <PowerOff size={12} />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
