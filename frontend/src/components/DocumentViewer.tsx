import React, { useState } from 'react';
import { Search, ChevronLeft, ChevronRight, FileText } from 'lucide-react';

interface DocumentViewerProps {
  title: string;
  rawText?: string;
  totalPages: number;
  highlightQuery?: string;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  title,
  rawText = '',
  totalPages,
  highlightQuery = '',
}) => {
  const [searchTerm, setSearchTerm] = useState(highlightQuery);
  const [currentPage, setCurrentPage] = useState(1);

  // Split raw text into simulated pages
  const pages = React.useMemo(() => {
    if (!rawText) return ['No document content available.'];
    const parts = rawText.split(/--- PAGE \d+ ---/i).filter((p) => p.trim());
    if (parts.length > 0) return parts;
    // Fallback: chunk into ~300 words
    const words = rawText.split(/\s+/);
    const result = [];
    const perPage = 300;
    for (let i = 0; i < words.length; i += perPage) {
      result.push(words.slice(i, i + perPage).join(' '));
    }
    return result.length > 0 ? result : [rawText];
  }, [rawText]);

  const activePageText = pages[Math.min(currentPage - 1, pages.length - 1)] || '';

  const renderHighlightedText = (text: string) => {
    if (!searchTerm.trim()) return text;
    const regex = new RegExp(`(${searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-amber-400/30 text-amber-200 px-1 rounded-xs font-semibold">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-900/40 rounded-xl border border-slate-800 overflow-hidden">
      {/* Top Document Toolbar */}
      <div className="p-3 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2 min-w-0">
          <FileText className="w-4 h-4 text-indigo-400 shrink-0" />
          <span className="text-xs font-semibold text-slate-200 truncate">{title}</span>
        </div>

        <div className="flex items-center gap-3">
          {/* Search inside Document */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search in text..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg pl-8 pr-3 py-1 text-xs text-slate-200 placeholder-slate-500 focus:outline-hidden focus:border-indigo-500 w-36 md:w-48"
            />
          </div>

          {/* Page Pagination */}
          <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-slate-950 px-2 py-1 rounded-lg border border-slate-800">
            <button
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              className="p-0.5 rounded-sm hover:text-slate-200 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono font-medium text-slate-300">
              Page {currentPage} of {Math.max(totalPages, pages.length)}
            </span>
            <button
              disabled={currentPage >= Math.max(totalPages, pages.length)}
              onClick={() => setCurrentPage((p) => Math.min(Math.max(totalPages, pages.length), p + 1))}
              className="p-0.5 rounded-sm hover:text-slate-200 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Document Content Pane */}
      <div className="flex-1 p-5 overflow-y-auto font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap selection:bg-indigo-500 selection:text-white bg-slate-950/60">
        {renderHighlightedText(activePageText)}
      </div>
    </div>
  );
};
