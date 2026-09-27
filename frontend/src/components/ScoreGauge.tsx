import React from 'react';
import { RiskLevel } from '../types/contract';

interface ScoreGaugeProps {
  score: number;
  level: RiskLevel;
  size?: number;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({ score, level, size = 160 }) => {
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  // Use 270 degree arc
  const arcLength = circumference * 0.75;
  const progress = (Math.min(100, Math.max(0, score)) / 100) * arcLength;

  const colorMap = {
    LOW: { stroke: '#10b981', glow: 'rgba(16, 185, 129, 0.35)' },
    MEDIUM: { stroke: '#f59e0b', glow: 'rgba(245, 158, 11, 0.35)' },
    HIGH: { stroke: '#f97316', glow: 'rgba(249, 115, 22, 0.35)' },
    CRITICAL: { stroke: '#ef4444', glow: 'rgba(239, 68, 68, 0.45)' },
  }[level] || { stroke: '#64748b', glow: 'rgba(100, 116, 139, 0.2)' };

  return (
    <div className="flex flex-col items-center justify-center relative">
      <svg width={size} height={size} className="transform -rotate-135">
        {/* Background Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="#1e293b"
          strokeWidth={strokeWidth}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeLinecap="round"
        />
        {/* Active Progress Arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={colorMap.stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={`${progress} ${circumference}`}
          strokeDashoffset="0"
          strokeLinecap="round"
          style={{
            filter: `drop-shadow(0 0 8px ${colorMap.glow})`,
            transition: 'stroke-dasharray 1s ease-out',
          }}
        />
      </svg>
      {/* Center Value */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
        <span className="text-4xl font-extrabold tracking-tight text-white">{score}</span>
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Risk Index
        </span>
      </div>
    </div>
  );
};
