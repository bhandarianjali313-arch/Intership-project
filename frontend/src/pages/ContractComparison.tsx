import React, { useState, useEffect } from 'react';
import { ContractSummary, CompareResponse } from '../types/contract';
import { compareContracts } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import {
  GitCompare,
  ArrowRight,
  TrendingUp,
  PlusCircle,
  MinusCircle,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Layers,
  ArrowDownRight,
  Flame,
} from 'lucide-react';

interface ContractComparisonProps {
  contracts: ContractSummary[];
}

export const ContractComparison: React.FC<ContractComparisonProps> = ({ contracts }) => {
  const [v1Id, setV1Id] = useState<string>(
    contracts.find((c) => c.id.includes('v1'))?.id || contracts[0]?.id || ''
  );
  const [v2Id, setV2Id] = useState<string>(
    contracts.find((c) => c.id.includes('v2'))?.id || contracts[1]?.id || ''
  );
  const [comparison, setComparison] = useState<CompareResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const runComparison = async () => {
    if (!v1Id || !v2Id || v1Id === v2Id) return;
    setIsLoading(true);
    try {
      const res = await compareContracts(v1Id, v2Id);
      setComparison(res);
    } catch (err) {
      console.error('Comparison error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (v1Id && v2Id && v1Id !== v2Id) {
      runComparison();
    }
  }, [v1Id, v2Id]);

  const filteredDiffs = comparison
    ? comparison.diffs.filter((d) => statusFilter === 'ALL' || d.status === statusFilter)
    : [];

  return (
    <div className="space-y-6">
      {/* Top Controls Header */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <GitCompare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Contract Version Comparison & Risk Delta</h2>
            <p className="text-xs text-slate-400">
              Automated redline comparison, added/removed clause analysis, and risk surge detection
            </p>
          </div>
        </div>

        {/* Version Pickers */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
          {/* Version 1 Picker */}
          <div className="md:col-span-5 bg-slate-950 p-3 rounded-xl border border-slate-800">
            <label className="text-[11px] uppercase font-bold text-slate-400 block mb-1">
              Baseline Contract (Version 1)
            </label>
            <select
              value={v1Id}
              onChange={(e) => setV1Id(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs font-semibold text-slate-200 focus:outline-hidden focus:border-indigo-500 cursor-pointer"
            >
              {contracts.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900">
                  {c.title} ({c.overall_risk_level})
                </option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2 text-center flex justify-center">
            <div className="w-10 h-10 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shadow-md">
              <ArrowRight className="w-5 h-5" />
            </div>
          </div>

          {/* Version 2 Picker */}
          <div className="md:col-span-5 bg-slate-950 p-3 rounded-xl border border-slate-800">
            <label className="text-[11px] uppercase font-bold text-slate-400 block mb-1">
              Modified Contract (Version 2)
            </label>
            <select
              value={v2Id}
              onChange={(e) => setV2Id(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs font-semibold text-slate-200 focus:outline-hidden focus:border-indigo-500 cursor-pointer"
            >
              {contracts.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900">
                  {c.title} ({c.overall_risk_level})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="text-center py-16 bg-slate-900/40 rounded-2xl border border-slate-800 text-xs text-indigo-400 animate-pulse">
          Performing semantic redline diffing across contract versions...
        </div>
      )}

      {!isLoading && comparison && (
        <div className="space-y-6">
          {/* Summary Delta Banner */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Risk Delta Metric */}
            <div
              className={`p-4 rounded-xl border ${
                comparison.risk_score_delta > 0
                  ? 'bg-rose-950/20 border-rose-500/30'
                  : 'bg-emerald-950/20 border-emerald-500/30'
              }`}
            >
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                Risk Score Delta
              </div>
              <div className="flex items-baseline gap-2">
                <span
                  className={`text-3xl font-extrabold ${
                    comparison.risk_score_delta > 0 ? 'text-rose-400' : 'text-emerald-400'
                  }`}
                >
                  {comparison.risk_score_delta > 0 ? `+${comparison.risk_score_delta}` : comparison.risk_score_delta}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  ({comparison.risk_score_v1} ➔ {comparison.risk_score_v2})
                </span>
              </div>
            </div>

            {/* Added Clauses */}
            <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl">
              <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1 mb-1">
                <PlusCircle className="w-3.5 h-3.5" />
                <span>Added Clauses</span>
              </div>
              <div className="text-2xl font-black text-white">{comparison.added_count}</div>
            </div>

            {/* Modified Clauses */}
            <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl">
              <div className="text-[11px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1 mb-1">
                <AlertCircle className="w-3.5 h-3.5" />
                <span>Modified Clauses</span>
              </div>
              <div className="text-2xl font-black text-white">{comparison.modified_count}</div>
            </div>

            {/* Removed Clauses */}
            <div className="bg-slate-900/70 border border-slate-800 p-4 rounded-xl">
              <div className="text-[11px] font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1 mb-1">
                <MinusCircle className="w-3.5 h-3.5" />
                <span>Removed Clauses</span>
              </div>
              <div className="text-2xl font-black text-white">{comparison.removed_count}</div>
            </div>
          </div>

          {/* Executive Takeaways */}
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" />
              <span>Key Redline Findings & Strategic Observations</span>
            </h3>
            <div className="space-y-2">
              {comparison.key_takeaways.map((takeaway, idx) => (
                <div
                  key={idx}
                  className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-200 font-medium"
                >
                  {takeaway}
                </div>
              ))}
            </div>
          </div>

          {/* Diff Filter Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setStatusFilter('ALL')}
              className={`text-xs px-3 py-1.5 rounded-lg border font-semibold transition-colors ${
                statusFilter === 'ALL'
                  ? 'bg-indigo-600 border-indigo-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400'
              }`}
            >
              All Changes ({comparison.diffs.length})
            </button>
            <button
              onClick={() => setStatusFilter('MODIFIED')}
              className={`text-xs px-3 py-1.5 rounded-lg border font-semibold transition-colors ${
                statusFilter === 'MODIFIED'
                  ? 'bg-amber-600 border-amber-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400'
              }`}
            >
              Modified ({comparison.modified_count})
            </button>
            <button
              onClick={() => setStatusFilter('ADDED')}
              className={`text-xs px-3 py-1.5 rounded-lg border font-semibold transition-colors ${
                statusFilter === 'ADDED'
                  ? 'bg-emerald-600 border-emerald-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400'
              }`}
            >
              Added ({comparison.added_count})
            </button>
            <button
              onClick={() => setStatusFilter('REMOVED')}
              className={`text-xs px-3 py-1.5 rounded-lg border font-semibold transition-colors ${
                statusFilter === 'REMOVED'
                  ? 'bg-rose-600 border-rose-500 text-white'
                  : 'bg-slate-900 border-slate-800 text-slate-400'
              }`}
            >
              Removed ({comparison.removed_count})
            </button>
          </div>

          {/* Side-by-Side Clause Diff Inspector */}
          <div className="space-y-4">
            {filteredDiffs.map((diff) => {
              const statusColor = {
                ADDED: 'border-emerald-500/40 bg-emerald-950/10',
                REMOVED: 'border-rose-500/40 bg-rose-950/10',
                MODIFIED: 'border-amber-500/40 bg-amber-950/10',
                UNCHANGED: 'border-slate-800 bg-slate-900/40',
              }[diff.status];

              return (
                <div key={diff.id} className={`p-4 rounded-2xl border ${statusColor} space-y-3`}>
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-slate-200">{diff.section_title}</span>
                      <span className="text-[10px] uppercase px-2 py-0.5 rounded-md font-bold bg-slate-950 border border-slate-800 text-slate-400">
                        {diff.status}
                      </span>
                    </div>
                    {diff.risk_v2 && <RiskBadge level={diff.risk_v2} size="sm" />}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Left: V1 */}
                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                      <div className="text-[10px] font-bold uppercase text-slate-500 mb-1 flex items-center justify-between">
                        <span>Version 1 (Baseline)</span>
                        {diff.risk_v1 && <RiskBadge level={diff.risk_v1} size="sm" />}
                      </div>
                      <p className="text-xs font-mono text-slate-400 leading-relaxed">
                        {diff.v1_text || <span className="italic text-slate-600">Clause did not exist in Version 1</span>}
                      </p>
                    </div>

                    {/* Right: V2 */}
                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                      <div className="text-[10px] font-bold uppercase text-slate-500 mb-1 flex items-center justify-between">
                        <span>Version 2 (Modified)</span>
                        {diff.risk_v2 && <RiskBadge level={diff.risk_v2} size="sm" />}
                      </div>
                      <p className="text-xs font-mono text-slate-300 leading-relaxed">
                        {diff.v2_text || <span className="italic text-rose-500">Clause removed in Version 2</span>}
                      </p>
                    </div>
                  </div>

                  {/* Delta note */}
                  <div className="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80 text-xs text-indigo-300 font-medium">
                    📌 <strong>Analysis:</strong> {diff.risk_delta_summary}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
