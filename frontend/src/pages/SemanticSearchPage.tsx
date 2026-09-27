import React, { useState } from 'react';
import { SearchResultItem } from '../types/contract';
import { searchClauses } from '../services/api';
import { RiskBadge } from '../components/RiskBadge';
import { Search, Sparkles, FileText, ArrowRight, Zap } from 'lucide-react';

interface SemanticSearchPageProps {
  onSelectContract: (id: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const SemanticSearchPage: React.FC<SemanticSearchPageProps> = ({
  onSelectContract,
  onNavigateTab,
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const sampleQueries = [
    'termination for convenience notice window',
    'unlimited liability or damages cap',
    'intellectual property transfer and AI training license',
    'automatic renewal opt-out requirement',
    'governing law in foreign or offshore jurisdiction',
    'confidentiality obligations and trade secrets',
  ];

  const handleSearch = async (term?: string) => {
    const q = (term || query).trim();
    if (!q) return;
    setIsSearching(true);
    setHasSearched(true);
    if (term) setQuery(term);
    try {
      const res = await searchClauses(q);
      setResults(res.results);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Search Hero */}
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-indigo-500/10 rounded-xl border border-indigo-500/20 text-indigo-400">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Semantic Legal Clause Search Engine</h2>
            <p className="text-xs text-slate-400">
              Query concepts in natural language across all indexed contracts (e.g. "early exit penalty")
            </p>
          </div>
        </div>

        {/* Big Search Input */}
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search concepts across all contracts (e.g., 'cancel without cause', 'IP ownership', 'liability ceiling')..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-10 pr-4 py-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-hidden focus:border-indigo-500 shadow-inner"
            />
          </div>
          <button
            onClick={() => handleSearch()}
            disabled={!query.trim() || isSearching}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-indigo-600/20 cursor-pointer"
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>

        {/* Quick Sample Queries */}
        <div className="flex items-center gap-2 flex-wrap pt-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-indigo-400" />
            <span>Try:</span>
          </span>
          {sampleQueries.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => handleSearch(sq)}
              className="text-xs px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 text-slate-300 transition-colors cursor-pointer"
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Results Header */}
      {hasSearched && (
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span>
            Found <strong className="text-white">{results.length}</strong> matching clauses for "
            <span className="text-indigo-400">{query}</span>"
          </span>
        </div>
      )}

      {/* Results Grid */}
      <div className="space-y-3">
        {results.map((r, idx) => (
          <div
            key={idx}
            onClick={() => {
              onSelectContract(r.contract_id);
              onNavigateTab('workspace');
            }}
            className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900 transition-all cursor-pointer space-y-2.5 shadow-sm group"
          >
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-bold text-slate-200">{r.contract_title}</span>
                <span className="text-[10px] text-slate-500 font-mono">
                  Sec {r.section_number} • Page {r.page_number}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded-md border border-indigo-500/20">
                  {Math.round(r.similarity_score * 100)}% Match
                </span>
                <RiskBadge level={r.risk_level} size="sm" />
              </div>
            </div>

            <div className="text-xs font-semibold text-slate-300">{r.clause_title}</div>
            <p className="text-xs font-mono text-slate-400 bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 leading-relaxed">
              {r.snippet}
            </p>

            <div className="flex items-center justify-end text-[11px] text-indigo-400 font-semibold group-hover:translate-x-1 transition-transform">
              <span>Inspect in workspace ➔</span>
            </div>
          </div>
        ))}

        {hasSearched && results.length === 0 && !isSearching && (
          <div className="text-center py-16 bg-slate-900/40 rounded-2xl border border-slate-800 text-xs text-slate-400">
            No matching clauses found for "{query}". Try a broader legal search phrase.
          </div>
        )}
      </div>
    </div>
  );
};
