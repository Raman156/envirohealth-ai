import { Link } from 'react-router-dom';
import { Leaf, Map, ClipboardList, ShieldAlert, Wind, Droplets, Activity, ChevronRight } from 'lucide-react';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-emerald-950">
      {/* Nav */}
      <nav className="px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-500 rounded-xl flex items-center justify-center">
            <Leaf size={16} className="text-white" />
          </div>
          <span className="text-white font-bold">EnviroHealth AI</span>
        </div>
        <div className="flex gap-3">
          <Link to="/dashboard" className="text-gray-400 hover:text-white text-sm transition-colors">Dashboard</Link>
          <Link to="/report" className="bg-brand-600 hover:bg-brand-500 text-white text-sm px-4 py-1.5 rounded-full transition-colors">
            Report Symptoms
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <div className="max-w-6xl mx-auto px-6 pt-20 pb-16">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-brand-900/40 border border-brand-700/30 rounded-full px-3 py-1 mb-6">
            <span className="w-1.5 h-1.5 bg-brand-400 rounded-full animate-pulse" />
            <span className="text-brand-400 text-xs font-medium">Live environmental monitoring</span>
          </div>

          <h1 className="text-5xl font-bold text-white leading-tight mb-6">
            Know the health risks around you{' '}
            <span className="text-brand-400">before they become bigger problems.</span>
          </h1>
          <p className="text-gray-400 text-lg mb-8 leading-relaxed">
            EnviroHealth AI combines community health reports, air quality, water quality, and weather data to detect emerging environmental health risks in your area — early.
          </p>

          <div className="flex flex-wrap gap-3">
            <Link to="/map" className="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white px-6 py-3 rounded-xl font-medium transition-all">
              <Map size={18} />
              Explore Health Map
              <ChevronRight size={16} />
            </Link>
            <Link to="/report" className="flex items-center gap-2 border border-gray-600 hover:border-gray-400 text-gray-300 hover:text-white px-6 py-3 rounded-xl font-medium transition-all">
              <ClipboardList size={18} />
              Report Anonymously
            </Link>
          </div>
        </div>
      </div>

      {/* How it works */}
      <div className="max-w-6xl mx-auto px-6 pb-16">
        <p className="text-gray-500 text-xs uppercase tracking-widest mb-6">How it works</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { icon: ClipboardList, label: 'Community Reports', desc: 'Anonymous symptom reports from your neighbors' },
            { icon: Wind, label: 'Air & Weather', desc: 'Live AQI, PM2.5, temperature, humidity data' },
            { icon: Droplets, label: 'Water Quality', desc: 'pH, TDS, turbidity from monitoring stations' },
            { icon: ShieldAlert, label: 'AI Risk Engine', desc: 'Transparent risk scoring with explainability' },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-4">
              <Icon size={20} className="text-brand-400 mb-3" />
              <p className="text-white text-sm font-medium mb-1">{label}</p>
              <p className="text-gray-500 text-xs leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="max-w-6xl mx-auto px-6 pb-10">
        <p className="text-gray-600 text-xs text-center">
          EnviroHealth AI identifies environmental health risk patterns. It does not diagnose medical conditions.
          Always consult a healthcare professional for personal health concerns.
        </p>
      </div>
    </div>
  );
}
