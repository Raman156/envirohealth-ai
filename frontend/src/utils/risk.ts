import type { RiskLevel } from '@/types';

export const RISK_COLORS: Record<RiskLevel, string> = {
  'LOW': '#22c55e',
  'MODERATE': '#84cc16',
  'ELEVATED': '#f59e0b',
  'HIGH': '#f97316',
  'VERY HIGH': '#ef4444',
};

export const RISK_BG: Record<RiskLevel, string> = {
  'LOW': 'bg-green-500',
  'MODERATE': 'bg-lime-500',
  'ELEVATED': 'bg-amber-500',
  'HIGH': 'bg-orange-500',
  'VERY HIGH': 'bg-red-500',
};

export const RISK_TEXT: Record<RiskLevel, string> = {
  'LOW': 'text-green-600',
  'MODERATE': 'text-lime-600',
  'ELEVATED': 'text-amber-600',
  'HIGH': 'text-orange-600',
  'VERY HIGH': 'text-red-600',
};

export const RISK_BORDER: Record<RiskLevel, string> = {
  'LOW': 'border-green-200',
  'MODERATE': 'border-lime-200',
  'ELEVATED': 'border-amber-200',
  'HIGH': 'border-orange-200',
  'VERY HIGH': 'border-red-200',
};

export function getRiskLevel(score: number): RiskLevel {
  if (score <= 20) return 'LOW';
  if (score <= 40) return 'MODERATE';
  if (score <= 60) return 'ELEVATED';
  if (score <= 80) return 'HIGH';
  return 'VERY HIGH';
}

export function getAQICategory(aqi: number): { label: string; color: string } {
  if (aqi <= 50) return { label: 'Good', color: '#22c55e' };
  if (aqi <= 100) return { label: 'Moderate', color: '#f59e0b' };
  if (aqi <= 150) return { label: 'Unhealthy for Sensitive', color: '#f97316' };
  if (aqi <= 200) return { label: 'Unhealthy', color: '#ef4444' };
  if (aqi <= 300) return { label: 'Very Unhealthy', color: '#a855f7' };
  return { label: 'Hazardous', color: '#7f1d1d' };
}

export function formatTrendChange(change: number): string {
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toFixed(0)}%`;
}

export function getTrendIcon(direction: string): string {
  if (direction === 'INCREASING') return '↑';
  if (direction === 'DECREASING') return '↓';
  return '→';
}

export function getTrendColor(direction: string): string {
  if (direction === 'INCREASING') return 'text-red-500';
  if (direction === 'DECREASING') return 'text-green-500';
  return 'text-gray-500';
}
