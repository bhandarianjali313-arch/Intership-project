import React from 'react';
import {
  Scale,
  LayoutDashboard,
  FileSearch,
  MessageSquare,
  GitCompare,
  Search,
  FileCheck,
  ShieldAlert,
  UserCheck,
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  userRole: string;
  setUserRole: (role: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  userRole,
  setUserRole,
}) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'workspace', label: 'Contract Analysis', icon: FileSearch },
    { id: 'chat', label: 'AI Contract Chat', icon: MessageSquare },
    { id: 'compare', label: 'Version Diff', icon: GitCompare },
    { id: 'search', label: 'Semantic Search', icon: Search },
    { id: 'reports', label: 'Report Generator', icon: FileCheck },
    { id: 'audit', label: 'Audit Trail', icon: ShieldAlert },
  ];

  const roles = ['Legal Counsel', 'Compliance Officer', 'Risk Manager', 'Viewer'];

  return (
    <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Name */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-base font-extrabold tracking-tight text-white">
                  LEXIGUARD
                </span>
                <span className="text-xs font-bold px-1.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                  AI 2.0
                </span>
              </div>
              <p className="text-[10px] font-medium text-slate-400 tracking-wider">
                CONTRACT INTELLIGENCE & RISK SCORING
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex items-center gap-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 shadow-xs'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Role Selector & Online Indicator */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 bg-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-800">
              <UserCheck className="w-3.5 h-3.5 text-indigo-400" />
              <select
                value={userRole}
                onChange={(e) => setUserRole(e.target.value)}
                className="bg-transparent text-xs text-slate-300 font-medium focus:outline-hidden cursor-pointer"
              >
                {roles.map((r) => (
                  <option key={r} value={r} className="bg-slate-900 text-slate-200">
                    {r}
                  </option>
                ))}
              </select>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span className="font-semibold text-[11px]">Engine Live</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
