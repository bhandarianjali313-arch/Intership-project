import React from 'react';
import { ContractSummary, ContractDetail } from '../types/contract';
import { RiskBadge } from '../components/RiskBadge';
import { RiskRadarChart } from '../components/RiskRadarChart';
import {
  FileText,
  ShieldAlert,
  Flame,
  Activity,
  ArrowUpRight,
  TrendingUp,
  FileSearch,
  MessageSquare,
  GitCompare,
  Download,
  Clock,
  Sparkles,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface DashboardProps {
  contracts: ContractSummary[];
  selectedDetail: ContractDetail | null;
  onSelectContract: (id: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  contracts,
  selectedDetail,
  onSelectContract,
  onNavigateTab,
}) => {
  const totalContracts = contracts.length;
  const criticalContracts = contracts.filter((c) => c.overall_risk_level === 'CRITICAL').length;
  const highRiskContracts = contracts.filter((c) => c.overall_risk_level === 'HIGH').length;
  const totalRedFlags = contracts.reduce((acc, c) => acc + c.red_flag_count, 0);
  const avgRiskScore =
    totalContracts > 0
      ? Math.round(contracts.reduce((acc, c) => acc + c.overall_risk_score, 0) / totalContracts)
      : 0;

  // Distribution chart data
  const distData = [
    {
      name: 'Low (0-25)',
      count: contracts.filter((c) => c.overall_risk_level === 'LOW').length,
      color: '#10b981',
    },
    {
      name: 'Medium (26-50)',
      count: contracts.filter((c) => c.overall_risk_level === 'MEDIUM').length,
      color: '#f59e0b',
    },
    {
      name: 'High (51-75)',
      count: contracts.filter((c) => c.overall_risk_level === 'HIGH').length,
      color: '#f97316',
    },
    {
      name: 'Critical (76-100)',
      count: contracts.filter((c) => c.overall_risk_level === 'CRITICAL').length,
      color: '#ef4444',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-indigo-950/60 via-slate-900/80 to-purple-950/50 p-6 border border-indigo-500/20 relative overflow-hidden shadow-xl">
        <div className="absolute -right-10 -bottom-10 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold text-indigo-400 bg-indigo-500/20 px-2.5 py-0.5 rounded-full border border-indigo-500/30">
                Executive Overview
              </span>
              <span className="text-xs text-slate-400 font-mono">CUAD & Legal-BERT Powered</span>
            </div>
            <h1 className="text-2xl font-black tracking-tight text-white">
              Enterprise Contract Intelligence & Risk Command Center
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-2xl">
              Real-time portfolio risk scoring, deep 14-clause NLP classification, explainable
              mitigations, and version deviation tracking.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigateTab('workspace')}
              className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-indigo-600/30 flex items-center gap-2"
            >
              <FileSearch className="w-4 h-4" />
              <span>Analyze New Contract</span>
            </button>
            <button
              onClick={() => onNavigateTab('compare')}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold transition-all border border-slate-700 flex items-center gap-2"
            >
              <GitCompare className="w-4 h-4" />
              <span>Compare Versions</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Contracts */}
        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Contracts</span>
            <FileText className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{totalContracts}</div>
          <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
            <span className="text-emerald-400 font-semibold">100% Parsed</span>
            <span>in workspace</span>
          </div>
        </div>

        {/* Average Risk Score */}
        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Mean Risk Index</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{avgRiskScore}/100</div>
          <div className="text-[11px] text-slate-400 mt-1">Portfolio Composite</div>
        </div>

        {/* Critical Alerts */}
        <div className="bg-rose-950/20 border border-rose-500/30 p-4 rounded-xl shadow-xs">
          <div className="flex items-center justify-between text-rose-300 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Critical Exposure</span>
            <Flame className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-extrabold text-rose-400">{criticalContracts}</div>
          <div className="text-[11px] text-rose-300/80 mt-1">Requires immediate remediation</div>
        </div>

        {/* High Risk Contracts */}
        <div className="bg-orange-950/20 border border-orange-500/30 p-4 rounded-xl shadow-xs">
          <div className="flex items-center justify-between text-orange-300 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">High Risk</span>
            <ShieldAlert className="w-4 h-4 text-orange-400" />
          </div>
          <div className="text-2xl font-extrabold text-orange-400">{highRiskContracts}</div>
          <div className="text-[11px] text-orange-300/80 mt-1">Elevated liability terms</div>
        </div>

        {/* Red Flags Active */}
        <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl shadow-xs">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Red Flags</span>
            <TrendingUp className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-amber-400">{totalRedFlags}</div>
          <div className="text-[11px] text-slate-400 mt-1">Actionable risk points</div>
        </div>
      </div>

      {/* Visual Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: 9-Dimension Risk Radar */}
        <div className="lg:col-span-6 bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-200">
                Multi-Factor Risk Radar (9 Dimensions)
              </h3>
              <p className="text-xs text-slate-400">
                {selectedDetail ? selectedDetail.title : 'Select a contract for granular radar'}
              </p>
            </div>
            {selectedDetail && (
              <RiskBadge level={selectedDetail.overall_risk_level} size="sm" />
            )}
          </div>
          {selectedDetail && selectedDetail.category_scores ? (
            <RiskRadarChart categories={selectedDetail.category_scores} />
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 text-xs">
              <Activity className="w-8 h-8 text-slate-600 mb-2 animate-pulse" />
              Select a contract to render full 9-dimension radar
            </div>
          )}
        </div>

        {/* Right: Portfolio Risk Distribution Chart */}
        <div className="lg:col-span-6 bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-slate-200">
                Portfolio Risk Distribution
              </h3>
              <p className="text-xs text-slate-400">Contracts segmented by risk bracket</p>
            </div>
          </div>
          <div className="w-full h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distData} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                <XAxis type="number" stroke="#64748b" fontSize={11} />
                <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={11} width={110} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-slate-900 border border-slate-700 p-2 rounded-md shadow-xl text-xs">
                          <p className="font-semibold text-slate-200">{d.name}</p>
                          <p className="text-indigo-400 font-bold">{d.count} Contract(s)</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {distData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Contract Repository Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-200">Contract Repository & Intelligence Register</h3>
            <p className="text-xs text-slate-400">Live indexed agreements ready for analysis, diffing, and export</p>
          </div>
          <span className="text-xs text-indigo-400 font-semibold bg-indigo-500/10 px-2.5 py-1 rounded-lg border border-indigo-500/20">
            {contracts.length} Available
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Contract Title</th>
                <th className="py-3 px-4">Clauses</th>
                <th className="py-3 px-4">Pages</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Risk Score</th>
                <th className="py-3 px-4">Red Flags</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {contracts.map((c) => (
                <tr
                  key={c.id}
                  onClick={() => {
                    onSelectContract(c.id);
                    onNavigateTab('workspace');
                  }}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                >
                  <td className="py-3.5 px-4">
                    <div className="font-semibold text-slate-200">{c.title}</div>
                    <div className="text-[11px] text-slate-400 font-mono">{c.file_name}</div>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-slate-300">{c.total_clauses}</td>
                  <td className="py-3.5 px-4 font-mono text-slate-300">{c.total_pages}</td>
                  <td className="py-3.5 px-4">
                    <RiskBadge level={c.overall_risk_level} size="sm" />
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="font-bold text-slate-200">{c.overall_risk_score}</span>
                    <span className="text-slate-500">/100</span>
                  </td>
                  <td className="py-3.5 px-4">
                    {c.red_flag_count > 0 ? (
                      <span className="inline-flex items-center gap-1 text-rose-400 font-bold bg-rose-500/10 px-2 py-0.5 rounded-md border border-rose-500/20">
                        <Flame className="w-3 h-3" />
                        {c.red_flag_count} Flags
                      </span>
                    ) : (
                      <span className="text-emerald-400 font-medium">None</span>
                    )}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => {
                          onSelectContract(c.id);
                          onNavigateTab('workspace');
                        }}
                        title="Inspect Clauses & XAI"
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white transition-colors"
                      >
                        <FileSearch className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          onSelectContract(c.id);
                          onNavigateTab('chat');
                        }}
                        title="AI Contract Q&A"
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-purple-600 text-slate-300 hover:text-white transition-colors"
                      >
                        <MessageSquare className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          onSelectContract(c.id);
                          onNavigateTab('reports');
                        }}
                        title="Generate Report"
                        className="p-1.5 rounded-lg bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white transition-colors"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
