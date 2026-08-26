import React, { useState, useEffect } from 'react';
import { AuditLog } from '../types/contract';
import { getAuditLogs } from '../services/api';
import { ShieldAlert, RefreshCw, Download, Filter, CheckCircle2, User, Clock } from 'lucide-react';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [actionFilter, setActionFilter] = useState('ALL');

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const data = await getAuditLogs();
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs =
    actionFilter === 'ALL'
      ? logs
      : logs.filter((l) => l.action.toLowerCase().includes(actionFilter.toLowerCase()));

  const handleExportCsv = () => {
    const headers = ['ID', 'Timestamp', 'User Role', 'User Name', 'Action', 'Target', 'Status', 'Details'];
    const rows = logs.map((l) => [
      l.id,
      l.timestamp,
      `"${l.user_role}"`,
      `"${l.user_name}"`,
      `"${l.action}"`,
      `"${l.target}"`,
      l.status,
      `"${l.details.replace(/"/g, '""')}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `lexiguard_audit_trail_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header & Filter Bar */}
      <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-rose-500/10 rounded-xl border border-rose-500/20 text-rose-400">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Compliance & Governance Audit Trail</h2>
            <p className="text-xs text-slate-400">
              Immutable logging of all contract uploads, AI queries, redline diffs, and exported reports
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          {/* Action Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="bg-slate-950 border border-slate-700 text-slate-200 text-xs font-semibold rounded-lg px-2.5 py-1.5 focus:outline-hidden focus:border-rose-500 cursor-pointer"
            >
              <option value="ALL">All Actions ({logs.length})</option>
              <option value="CONTRACT_ANALYZED">Contract Analyzed</option>
              <option value="VIEW_CONTRACT">View Contract</option>
              <option value="CONTRACT_QA">RAG Q&A</option>
              <option value="CONTRACT_COMPARE">Version Diff</option>
              <option value="SEMANTIC_SEARCH">Semantic Search</option>
              <option value="EXPORT">Report Export</option>
            </select>
          </div>

          <button
            onClick={fetchLogs}
            disabled={isLoading}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 text-xs transition-colors cursor-pointer"
            title="Refresh Logs"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={handleExportCsv}
            className="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-md shadow-indigo-600/20 flex items-center gap-1.5 cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 font-semibold uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Target Contract / Query</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4 text-slate-400 whitespace-nowrap text-[11px]">
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3 h-3 text-slate-500" />
                      <span>{new Date(log.timestamp).toLocaleString()}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <div className="font-sans font-bold text-slate-200">{log.user_name}</div>
                    <div className="text-[10px] text-slate-500 font-sans">{log.user_role}</div>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded-md text-[11px] font-bold">
                      {log.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-sans text-slate-300 font-medium max-w-xs truncate">
                    {log.target}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="inline-flex items-center gap-1 text-emerald-400 font-semibold text-[11px]">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {log.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400 text-[11px] max-w-sm truncate">
                    {log.details || '—'}
                  </td>
                </tr>
              ))}
              {filteredLogs.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500 text-xs">
                    No audit log records match the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
