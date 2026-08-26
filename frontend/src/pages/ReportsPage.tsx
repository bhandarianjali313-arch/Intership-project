import React, { useState } from 'react';
import { ContractDetail, ContractSummary } from '../types/contract';
import { RiskBadge } from '../components/RiskBadge';
import { ScoreGauge } from '../components/ScoreGauge';
import {
  FileCheck,
  Download,
  Printer,
  FileCode,
  ShieldCheck,
  Flame,
  CheckCircle2,
  ExternalLink,
} from 'lucide-react';
import { getHtmlReportUrl, getJsonReportUrl } from '../services/api';

interface ReportsPageProps {
  contracts: ContractSummary[];
  contract: ContractDetail | null;
  onSelectContract: (id: string) => void;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({
  contracts,
  contract,
  onSelectContract,
}) => {
  const [reportFormat, setReportFormat] = useState<'HTML' | 'JSON'>('HTML');

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJson = () => {
    if (!contract) return;
    const url = getJsonReportUrl(contract.id);
    window.open(url, '_blank');
  };

  const handleOpenHtml = () => {
    if (!contract) return;
    const url = getHtmlReportUrl(contract.id);
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Header & Export Toolbar */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-emerald-500/10 rounded-xl border border-emerald-500/20 text-emerald-400">
            <FileCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Executive Contract Risk Report Generator</h2>
            <p className="text-xs text-slate-400">
              Download institutional audit reports with Executive Summary, 14-clause scorecard, and XAI findings
            </p>
          </div>
        </div>

        {/* Contract Picker & Action Buttons */}
        <div className="flex items-center gap-3 flex-wrap">
          <select
            value={contract ? contract.id : ''}
            onChange={(e) => onSelectContract(e.target.value)}
            className="bg-slate-950 border border-slate-700 text-slate-200 text-xs font-bold rounded-lg px-3 py-2 focus:outline-hidden focus:border-emerald-500 cursor-pointer max-w-xs truncate"
          >
            {contracts.map((c) => (
              <option key={c.id} value={c.id} className="bg-slate-900">
                {c.title} ({c.overall_risk_level})
              </option>
            ))}
          </select>

          <button
            onClick={handlePrint}
            className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-bold transition-all border border-slate-700 flex items-center gap-1.5 cursor-pointer"
          >
            <Printer className="w-4 h-4 text-slate-400" />
            <span>Print / Save PDF</span>
          </button>

          <button
            onClick={handleDownloadJson}
            className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-indigo-600/20 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={handleOpenHtml}
            className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-emerald-600/20 cursor-pointer"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Open Standalone HTML</span>
          </button>
        </div>
      </div>

      {/* Live Printable Report Preview Sheet */}
      {contract ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 max-w-4xl mx-auto shadow-2xl space-y-8 bg-gradient-to-b from-slate-900/60 to-slate-950">
          {/* Report Top Header */}
          <div className="border-b border-slate-800 pb-6 flex items-start justify-between gap-4">
            <div>
              <div className="text-xs font-bold text-indigo-400 tracking-wider uppercase mb-1">
                LexiGuard AI • LegalTech Audit Certificate
              </div>
              <h1 className="text-2xl font-black text-white">{contract.title}</h1>
              <p className="text-xs text-slate-400 mt-1">
                Analyzed on {new Date(contract.upload_time).toLocaleDateString()} • File:{' '}
                <span className="font-mono text-slate-300">{contract.file_name}</span>
              </p>
            </div>
            <div className="flex flex-col items-end gap-1 shrink-0">
              <RiskBadge level={contract.overall_risk_level} size="lg" />
              <div className="text-3xl font-black text-white mt-1">
                {contract.overall_risk_score}
                <span className="text-sm font-normal text-slate-500">/100</span>
              </div>
            </div>
          </div>

          {/* Quick Metrics Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <div className="text-xl font-bold text-white">{contract.total_pages}</div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Pages</div>
            </div>
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <div className="text-xl font-bold text-white">{contract.total_clauses}</div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Clauses Segmented</div>
            </div>
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <div className="text-xl font-bold text-rose-400">{contract.red_flags.length}</div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Red Flags Identified</div>
            </div>
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
              <div className="text-xl font-bold text-indigo-400">{contract.entities.length}</div>
              <div className="text-[10px] text-slate-400 uppercase font-semibold">Entities Extracted</div>
            </div>
          </div>

          {/* Executive Summary */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              1. Executive Risk Summary
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800 font-serif">
              {contract.executive_summary}
            </p>
          </div>

          {/* Critical Red Flags */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
              <Flame className="w-4 h-4" />
              <span>2. Critical Red Flags & Recommended Mitigation</span>
            </h3>
            {contract.red_flags.map((rf) => (
              <div
                key={rf.id}
                className="bg-rose-950/20 border border-rose-500/30 p-4 rounded-xl space-y-2"
              >
                <div className="flex items-center justify-between text-xs font-bold text-rose-300">
                  <span>
                    {rf.title} (Page {rf.page_number})
                  </span>
                  <RiskBadge level={rf.severity} size="sm" />
                </div>
                <p className="text-xs text-rose-200/90 font-medium">
                  <strong>Risk:</strong> {rf.summary}
                </p>
                <div className="bg-slate-950 p-2.5 rounded-lg text-xs text-emerald-300 border border-emerald-500/20">
                  <strong>Remediation:</strong> {rf.recommendation}
                </div>
              </div>
            ))}
            {contract.red_flags.length === 0 && (
              <p className="text-xs text-emerald-400 bg-emerald-950/20 p-3 rounded-xl border border-emerald-500/20">
                No high or critical red flags found in this contract. Customary commercial standards met.
              </p>
            )}
          </div>

          {/* 9-Dimension Breakdown Table */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              3. Category Risk Scorecard (9 Dimensions)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {contract.category_scores.map((cat) => (
                <div key={cat.category} className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <div className="flex items-center justify-between text-xs font-bold text-slate-200 mb-1">
                    <span>{cat.category}</span>
                    <RiskBadge level={cat.risk_level} size="sm" />
                  </div>
                  <div className="text-lg font-black text-indigo-400">{cat.score}/100</div>
                  <p className="text-[11px] text-slate-400 mt-1">{cat.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Clause Inventory */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
              4. Clause Intelligence Register
            </h3>
            <div className="space-y-3">
              {contract.clauses.map((cl) => (
                <div
                  key={cl.id}
                  className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
                    <span className="font-bold text-slate-200">
                      Section {cl.section_number}: {cl.title}
                    </span>
                    <RiskBadge level={cl.risk_level} size="sm" />
                  </div>
                  <p className="font-mono text-[11px] text-slate-400 bg-slate-900/60 p-2 rounded-md">
                    {cl.text}
                  </p>
                  <div className="text-slate-300 space-y-1 pt-1">
                    <p>
                      <strong>Reason:</strong> {cl.reason}
                    </p>
                    <p className="text-emerald-400">
                      <strong>Recommendation:</strong> {cl.recommendation}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Footer Note */}
          <div className="text-center text-[11px] text-slate-500 pt-6 border-t border-slate-800">
            Generated by LexiGuard AI Contract Intelligence Platform • Informational LegalTech Analysis
          </div>
        </div>
      ) : (
        <div className="text-center py-16 bg-slate-900/40 rounded-2xl border border-slate-800 text-xs text-slate-400">
          Select a contract to generate and preview its risk report.
        </div>
      )}
    </div>
  );
};
