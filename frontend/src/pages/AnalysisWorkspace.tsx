import React, { useState, useRef } from 'react';
import { ContractDetail, ContractSummary, ClauseType, RiskLevel } from '../types/contract';
import { ScoreGauge } from '../components/ScoreGauge';
import { RiskBadge } from '../components/RiskBadge';
import { ClauseCard } from '../components/ClauseCard';
import { EntityViewer } from '../components/EntityViewer';
import { DocumentViewer } from '../components/DocumentViewer';
import { RiskRadarChart } from '../components/RiskRadarChart';
import {
  Upload,
  FileText,
  Sparkles,
  Filter,
  Layers,
  Users,
  AlertTriangle,
  Clock,
  ShieldCheck,
  CheckCircle,
  FolderOpen,
  ArrowRight,
  Flame,
} from 'lucide-react';

interface AnalysisWorkspaceProps {
  contracts: ContractSummary[];
  contract: ContractDetail | null;
  onSelectContract: (id: string) => void;
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
}

export const AnalysisWorkspace: React.FC<AnalysisWorkspaceProps> = ({
  contracts,
  contract,
  onSelectContract,
  onUpload,
  isUploading,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'clauses' | 'entities' | 'radar' | 'redflags'>('clauses');
  const [clauseFilter, setClauseFilter] = useState<string>('ALL');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [selectedClauseId, setSelectedClauseId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  const filteredClauses = contract
    ? contract.clauses.filter((cl) => {
        const matchesClause = clauseFilter === 'ALL' || cl.clause_type === clauseFilter;
        const matchesRisk = riskFilter === 'ALL' || cl.risk_level === riskFilter;
        return matchesClause && matchesRisk;
      })
    : [];

  const allClauseTypes = contract
    ? Array.from(new Set(contract.clauses.map((c) => c.clause_type)))
    : [];

  return (
    <div className="space-y-6">
      {/* Top Header & Contract Selector Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <FolderOpen className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Active Contract Workspace
            </div>
            <div className="flex items-center gap-2">
              <select
                value={contract ? contract.id : ''}
                onChange={(e) => onSelectContract(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-200 text-sm font-bold rounded-lg px-3 py-1.5 focus:outline-hidden focus:border-indigo-500 cursor-pointer max-w-xs md:max-w-md truncate"
              >
                {contracts.map((c) => (
                  <option key={c.id} value={c.id} className="bg-slate-900 text-slate-200">
                    {c.title} ({c.overall_risk_level})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Upload Button & Dropzone trigger */}
        <div className="flex items-center gap-2.5">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            onChange={handleFileInputChange}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-indigo-600/20 flex items-center gap-2 cursor-pointer"
          >
            <Upload className="w-4 h-4" />
            <span>{isUploading ? 'Analyzing Contract...' : 'Upload Contract (PDF/DOCX/TXT)'}</span>
          </button>
        </div>
      </div>

      {contract ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Pane: Interactive Document Viewer (5 cols) */}
          <div className="lg:col-span-5 h-[760px]">
            <DocumentViewer
              title={contract.title}
              rawText={contract.raw_text}
              totalPages={contract.total_pages}
            />
          </div>

          {/* Right Pane: Intelligence & Risk Analysis Panel (7 cols) */}
          <div className="lg:col-span-7 space-y-5">
            {/* Executive Risk Score Card */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl relative overflow-hidden">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <ScoreGauge score={contract.overall_risk_score} level={contract.overall_risk_level} size={130} />
                  <div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <RiskBadge level={contract.overall_risk_level} size="lg" />
                      <span className="text-xs font-mono text-slate-400">
                        {contract.total_clauses} Clauses Identified
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-slate-100">{contract.title}</h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-md line-clamp-2">
                      {contract.executive_summary}
                    </p>
                  </div>
                </div>

                {/* KPI mini stats */}
                <div className="grid grid-cols-2 gap-2 text-center shrink-0 border-l border-slate-800 pl-4">
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800/80">
                    <div className="text-lg font-bold text-rose-400">{contract.red_flags.length}</div>
                    <div className="text-[10px] text-slate-400 uppercase font-semibold">Red Flags</div>
                  </div>
                  <div className="bg-slate-950 p-2.5 rounded-xl border border-slate-800/80">
                    <div className="text-lg font-bold text-indigo-400">{contract.entities.length}</div>
                    <div className="text-[10px] text-slate-400 uppercase font-semibold">Entities</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Sub Tabs Selector */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 flex-wrap gap-2">
              <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
                <button
                  onClick={() => setActiveSubTab('clauses')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeSubTab === 'clauses'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Clauses & XAI ({contract.clauses.length})</span>
                </button>
                <button
                  onClick={() => setActiveSubTab('entities')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeSubTab === 'entities'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Users className="w-3.5 h-3.5" />
                  <span>NER Entities ({contract.entities.length})</span>
                </button>
                <button
                  onClick={() => setActiveSubTab('radar')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeSubTab === 'radar'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>9-Dimension Radar</span>
                </button>
                <button
                  onClick={() => setActiveSubTab('redflags')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    activeSubTab === 'redflags'
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Flame className="w-3.5 h-3.5" />
                  <span>Red Flags & Timeline ({contract.red_flags.length})</span>
                </button>
              </div>
            </div>

            {/* Tab 1: Clauses & Explainable AI */}
            {activeSubTab === 'clauses' && (
              <div className="space-y-4">
                {/* Filter Controls */}
                <div className="flex items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800 flex-wrap">
                  <div className="flex items-center gap-2">
                    <Filter className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-xs font-semibold text-slate-400">Clause Category:</span>
                    <select
                      value={clauseFilter}
                      onChange={(e) => setClauseFilter(e.target.value)}
                      className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg px-2.5 py-1 focus:outline-hidden"
                    >
                      <option value="ALL">All Categories ({contract.clauses.length})</option>
                      {allClauseTypes.map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-400">Risk Severity:</span>
                    <select
                      value={riskFilter}
                      onChange={(e) => setRiskFilter(e.target.value)}
                      className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg px-2.5 py-1 focus:outline-hidden"
                    >
                      <option value="ALL">All Severity Levels</option>
                      <option value="LOW">Low</option>
                      <option value="MEDIUM">Medium</option>
                      <option value="HIGH">High</option>
                      <option value="CRITICAL">Critical</option>
                    </select>
                  </div>
                </div>

                {/* Clauses list */}
                <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                  {filteredClauses.map((clause) => (
                    <ClauseCard
                      key={clause.id}
                      clause={clause}
                      isSelected={selectedClauseId === clause.id}
                      onSelect={() => setSelectedClauseId(clause.id)}
                    />
                  ))}
                  {filteredClauses.length === 0 && (
                    <div className="text-center py-12 text-slate-500 text-xs bg-slate-900/30 rounded-xl border border-slate-800">
                      No clauses match the active filter criteria.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tab 2: NER Entities */}
            {activeSubTab === 'entities' && (
              <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
                <EntityViewer entities={contract.entities} />
              </div>
            )}

            {/* Tab 3: 9-Dimension Radar */}
            {activeSubTab === 'radar' && (
              <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 space-y-4">
                <RiskRadarChart categories={contract.category_scores} />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {contract.category_scores.map((cat) => (
                    <div key={cat.category} className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-slate-200">{cat.category}</span>
                        <RiskBadge level={cat.risk_level} size="sm" />
                      </div>
                      <div className="text-lg font-black text-indigo-400 mb-1">{cat.score}/100</div>
                      <p className="text-[11px] text-slate-400">{cat.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tab 4: Red Flags & Timeline */}
            {activeSubTab === 'redflags' && (
              <div className="space-y-4">
                {/* Red flags */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                    <Flame className="w-4 h-4" />
                    <span>Critical Remediation Queue ({contract.red_flags.length})</span>
                  </h4>
                  {contract.red_flags.map((rf) => (
                    <div
                      key={rf.id}
                      className="bg-rose-950/20 border border-rose-500/30 p-4 rounded-xl space-y-2 shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-rose-300">
                          {rf.title} (Page {rf.page_number})
                        </span>
                        <RiskBadge level={rf.severity} size="sm" />
                      </div>
                      <p className="text-xs text-rose-200/90 font-medium">
                        <strong>Reason:</strong> {rf.summary}
                      </p>
                      <div className="bg-slate-950/80 p-2.5 rounded-lg text-xs text-emerald-300 border border-emerald-500/20">
                        <strong>Actionable Remedy:</strong> {rf.recommendation}
                      </div>
                    </div>
                  ))}
                  {contract.red_flags.length === 0 && (
                    <div className="text-center py-10 bg-slate-900/40 rounded-xl border border-slate-800 text-xs text-emerald-400 flex items-center justify-center gap-2">
                      <ShieldCheck className="w-5 h-5" />
                      <span>No critical red flags found in this contract.</span>
                    </div>
                  )}
                </div>

                {/* Timeline */}
                {contract.timeline_events.length > 0 && (
                  <div className="bg-slate-900/60 p-4 rounded-2xl border border-slate-800 space-y-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                      <Clock className="w-4 h-4 text-indigo-400" />
                      <span>Contract Milestone & Notice Timeline</span>
                    </h4>
                    <div className="space-y-2.5">
                      {contract.timeline_events.map((t, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-3 bg-slate-950 p-3 rounded-xl border border-slate-800"
                        >
                          <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-1 rounded-md shrink-0">
                            {t.date}
                          </span>
                          <div>
                            <div className="text-xs font-semibold text-slate-200">{t.title}</div>
                            <p className="text-[11px] text-slate-400 mt-0.5">{t.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleFileDrop}
          className="border-2 border-dashed border-slate-800 hover:border-indigo-500 rounded-3xl p-16 text-center bg-slate-900/30 transition-colors"
        >
          <Upload className="w-12 h-12 text-indigo-400 mx-auto mb-4 animate-bounce" />
          <h3 className="text-lg font-bold text-slate-200">Drag and drop your contract here</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            Supports PDF, DOCX, TXT. Our NLP engine will extract clauses, score risks, and identify red flags.
          </p>
        </div>
      )}
    </div>
  );
};
