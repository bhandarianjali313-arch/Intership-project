import React, { useState } from 'react';
import { ClauseItem } from '../types/contract';
import { RiskBadge } from './RiskBadge';
import {
  ChevronDown,
  ChevronUp,
  Sparkles,
  AlertCircle,
  TrendingDown,
  Compass,
  FileText,
  Copy,
  Check,
} from 'lucide-react';

interface ClauseCardProps {
  clause: ClauseItem;
  isSelected?: boolean;
  onSelect?: () => void;
}

export const ClauseCard: React.FC<ClauseCardProps> = ({
  clause,
  isSelected,
  onSelect,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(clause.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      onClick={onSelect}
      className={`rounded-xl border transition-all duration-200 cursor-pointer overflow-hidden ${
        isSelected
          ? 'border-indigo-500 bg-indigo-950/20 shadow-lg shadow-indigo-500/10'
          : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/90'
      }`}
    >
      {/* Header Bar */}
      <div className="p-4 flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">
              Sec {clause.section_number}
            </span>
            <span className="text-xs text-slate-400 font-medium truncate">
              {clause.clause_type}
            </span>
            <span className="text-[10px] text-slate-500">Page {clause.page_number}</span>
          </div>
          <h4 className="text-sm font-semibold text-slate-200 truncate">{clause.title}</h4>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <RiskBadge level={clause.risk_level} size="sm" />
          <button
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
            className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800"
          >
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Snippet preview */}
      <div className="px-4 pb-3">
        <p className="text-xs text-slate-400 font-mono line-clamp-2 bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/80">
          {clause.text}
        </p>
      </div>

      {/* Expandable Explainable AI Drawer */}
      {expanded && (
        <div className="px-4 pb-4 pt-2 border-t border-slate-800/80 bg-slate-950/40 space-y-3">
          {/* XAI Reasoning & Impact Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs">
            {/* Reason */}
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              <div className="flex items-center gap-1.5 font-semibold text-amber-400 mb-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>Explainability Reason</span>
              </div>
              <p className="text-slate-300 leading-relaxed">{clause.reason}</p>
            </div>

            {/* Impact */}
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800">
              <div className="flex items-center gap-1.5 font-semibold text-rose-400 mb-1">
                <TrendingDown className="w-3.5 h-3.5 shrink-0" />
                <span>Business & Legal Impact</span>
              </div>
              <p className="text-slate-300 leading-relaxed">{clause.impact}</p>
            </div>
          </div>

          {/* Actionable Recommendation */}
          <div className="bg-emerald-950/20 border border-emerald-500/30 p-3 rounded-lg text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-emerald-400 mb-1">
              <Compass className="w-3.5 h-3.5 shrink-0" />
              <span>Actionable Strategic Recommendation</span>
            </div>
            <p className="text-emerald-200 leading-relaxed">{clause.recommendation}</p>
          </div>

          {/* Evidence Citation Reference */}
          <div className="flex items-center justify-between pt-1 text-[11px] text-slate-500">
            <div className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5" />
              <span>
                Evidence Reference: Page {clause.page_number} • Match Confidence:{' '}
                {Math.round(clause.confidence * 100)}%
              </span>
            </div>
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 text-slate-400 hover:text-slate-200 transition-colors"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
              <span>{copied ? 'Copied' : 'Copy Clause'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
