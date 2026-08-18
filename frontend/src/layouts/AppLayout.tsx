import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Leaf, LayoutDashboard, Map, TrendingUp, Clock, Bell, ClipboardList, Settings, Menu, X, MapPin } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { alertsApi } from '@/services/api/alerts';
import clsx from 'clsx';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/map', label: 'Health Map', icon: Map },
  { to: '/trends', label: 'Trends', icon: TrendingUp },
  { to: '/history', label: 'History', icon: Clock },
  { to: '/report', label: 'Report', icon: ClipboardList },
  { to: '/alerts', label: 'Alerts', icon: Bell },
];

export function AppLayout({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const { pathname } = useLocation();

  const { data: alerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alertsApi.getActive(),
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
  const alertCount = (alerts || []).length;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top nav */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-7 h-7 bg-brand-600 rounded-lg flex items-center justify-center">
              <Leaf size={14} className="text-white" />
            </div>
            <span className="font-bold text-gray-900 text-sm">EnviroHealth AI</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                className={clsx(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors relative',
                  pathname === to
                    ? 'bg-gray-100 text-gray-900 font-medium'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                )}
              >
                <Icon size={14} />
                {label}
                {label === 'Alerts' && alertCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-4 h-4 text-[10px] flex items-center justify-center">
                    {alertCount > 9 ? '9+' : alertCount}
                  </span>
                )}
              </Link>
            ))}
            <Link
              to="/admin"
              className={clsx(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm transition-colors ml-2 border border-gray-200',
                pathname === '/admin' ? 'bg-gray-900 text-white' : 'text-gray-500 hover:text-gray-700'
              )}
            >
              <Settings size={14} />
              Admin
            </Link>
          </nav>

          {/* Mobile menu button */}
          <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden border-t border-gray-100 px-4 py-3 space-y-1">
            {[...NAV_ITEMS, { to: '/admin', label: 'Admin', icon: Settings }].map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={clsx(
                  'flex items-center gap-2 px-3 py-2 rounded-lg text-sm',
                  pathname === to ? 'bg-gray-100 font-medium' : 'text-gray-600'
                )}
              >
                <Icon size={16} />
                {label}
              </Link>
            ))}
          </div>
        )}
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        {children}
      </main>
    </div>
  );
}
