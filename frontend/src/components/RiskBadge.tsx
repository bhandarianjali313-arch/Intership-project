import React from 'react';
import { RiskLevel } from '../types/contract';
import { ShieldCheck, AlertTriangle, AlertOctagon, Flame } from 'lucide-react';

interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  level,
  size = 'md',
  showIcon = true,
}) => {
  const config = {
    LOW: {
      bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      icon: ShieldCheck,
      label: 'LOW RISK',
    },
    MEDIUM: {
      bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      icon: AlertTriangle,
      label: 'MEDIUM RISK',
    },
    HIGH: {
      bg: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
      icon: AlertOctagon,
      label: 'HIGH RISK',
    },
    CRITICAL: {
      bg: 'bg-rose-500/15 text-rose-400 border-rose-500/40 animate-pulse',
      icon: Flame,
      label: 'CRITICAL RISK',
    },
  }[level] || {
    bg: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
    icon: ShieldCheck,
    label: level,
  };

  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-semibold',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-bold',
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border ${config.bg} ${sizeClasses} shadow-sm backdrop-blur-xs`}
    >
      {showIcon && <Icon className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />}
      <span>{config.label}</span>
    </span>
  );
};
