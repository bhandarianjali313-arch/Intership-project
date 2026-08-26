import React, { useState, useEffect } from 'react';
import { ContractSummary, ContractDetail } from './types/contract';
import { getContracts, getContract, uploadContract } from './services/api';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { AnalysisWorkspace } from './pages/AnalysisWorkspace';
import { ContractChat } from './pages/ContractChat';
import { ContractComparison } from './pages/ContractComparison';
import { SemanticSearchPage } from './pages/SemanticSearchPage';
import { ReportsPage } from './pages/ReportsPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { Scale, CheckCircle, AlertCircle } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [userRole, setUserRole] = useState<string>('Legal Counsel');
  const [contracts, setContracts] = useState<ContractSummary[]>([]);
  const [selectedContractId, setSelectedContractId] = useState<string>('');
  const [selectedDetail, setSelectedDetail] = useState<ContractDetail | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  const showToast = (text: string, type: 'success' | 'error' = 'success') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 3500);
  };

  const loadContracts = async (preferredId?: string) => {
    try {
      const data = await getContracts();
      setContracts(data);
      if (data.length > 0) {
        const idToSelect = preferredId || selectedContractId || data[0].id;
        setSelectedContractId(idToSelect);
        const detail = await getContract(idToSelect);
        setSelectedDetail(detail);
      }
    } catch (err) {
      console.error('Failed to load contracts:', err);
    }
  };

  useEffect(() => {
    loadContracts();
  }, []);

  const handleSelectContract = async (id: string) => {
    setSelectedContractId(id);
    try {
      const detail = await getContract(id);
      setSelectedDetail(detail);
    } catch (err) {
      console.error('Failed to load contract details:', err);
    }
  };

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const newContract = await uploadContract(file);
      showToast(`'${file.name}' analyzed successfully with ${newContract.clauses.length} clauses!`, 'success');
      await loadContracts(newContract.id);
      setActiveTab('workspace');
    } catch (err) {
      console.error('Upload failed:', err);
      showToast('Failed to analyze document. Please ensure valid PDF, DOCX, or TXT format.', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        userRole={userRole}
        setUserRole={setUserRole}
      />

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 animate-slide-up flex items-center gap-2.5 px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 shadow-2xl text-xs font-semibold">
          {toastMessage.type === 'success' ? (
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400" />
          )}
          <span className={toastMessage.type === 'success' ? 'text-emerald-300' : 'text-rose-300'}>
            {toastMessage.text}
          </span>
        </div>
      )}

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'dashboard' && (
          <Dashboard
            contracts={contracts}
            selectedDetail={selectedDetail}
            onSelectContract={handleSelectContract}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'workspace' && (
          <AnalysisWorkspace
            contracts={contracts}
            contract={selectedDetail}
            onSelectContract={handleSelectContract}
            onUpload={handleUpload}
            isUploading={isUploading}
          />
        )}

        {activeTab === 'chat' && (
          <ContractChat
            contracts={contracts}
            selectedContractId={selectedContractId}
            onSelectContract={handleSelectContract}
          />
        )}

        {activeTab === 'compare' && (
          <ContractComparison contracts={contracts} />
        )}

        {activeTab === 'search' && (
          <SemanticSearchPage
            onSelectContract={handleSelectContract}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'reports' && (
          <ReportsPage
            contracts={contracts}
            contract={selectedDetail}
            onSelectContract={handleSelectContract}
          />
        )}

        {activeTab === 'audit' && <AuditLogsPage />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-indigo-400" />
            <span className="font-bold text-slate-400">LexiGuard AI Platform</span>
            <span>— Contract Intelligence, CUAD NLP & Risk Scoring</span>
          </div>
          <div>Enterprise LegalTech System • Powered by Deep Learning & Explainable AI (XAI)</div>
        </div>
      </footer>
    </div>
  );
}

export default App;
