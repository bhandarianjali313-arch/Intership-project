import React from 'react';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { RiskCategoryScore } from '../types/contract';

interface RiskRadarChartProps {
  categories: RiskCategoryScore[];
}

export const RiskRadarChart: React.FC<RiskRadarChartProps> = ({ categories }) => {
  const data = categories.map((c) => ({
    category: c.category.replace(' Risk', ''),
    score: c.score,
    fullCategory: c.category,
    riskLevel: c.risk_level,
  }));

  return (
    <div className="w-full h-72">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#334155" strokeDasharray="3 3" />
          <PolarAngleAxis
            dataKey="category"
            tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 500 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            stroke="#475569"
            tick={{ fill: '#64748b', fontSize: 9 }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                return (
                  <div className="bg-slate-900 border border-slate-700 p-2.5 rounded-lg shadow-xl text-xs">
                    <p className="font-semibold text-slate-200">{item.fullCategory}</p>
                    <p className="text-emerald-400 mt-0.5">
                      Score: <span className="font-bold">{item.score}/100</span> ({item.riskLevel})
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Radar
            name="Risk Score"
            dataKey="score"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.4}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
