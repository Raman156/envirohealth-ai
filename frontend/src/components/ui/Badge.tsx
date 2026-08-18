import clsx from 'clsx';
import type { RiskLevel } from '@/types';
import { RISK_BG } from '@/utils/risk';

interface BadgeProps {
  label: string;
  level?: RiskLevel;
  className?: string;
  variant?: 'default' | 'outline';
}

export function RiskBadge({ label, level }: BadgeProps) {
  return (
    <span className={clsx(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold text-white',
      level ? RISK_BG[level] : 'bg-gray-400'
    )}>
      {label}
    </span>
  );
}

export function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    LOW: 'bg-green-100 text-green-800',
    MODERATE: 'bg-amber-100 text-amber-800',
    HIGH: 'bg-orange-100 text-orange-800',
    CRITICAL: 'bg-red-100 text-red-800',
  };
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded text-xs font-medium', colors[severity] || 'bg-gray-100 text-gray-700')}>
      {severity}
    </span>
  );
}
