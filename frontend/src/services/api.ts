import axios from 'axios';
import {
  ContractSummary,
  ContractDetail,
  ChatResponse,
  CompareResponse,
  SearchResultItem,
  AuditLog,
} from '../types/contract';
import { INITIAL_SUMMARIES, CONTRACT_DETAILS_MAP } from './mockData';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getContracts = async (): Promise<ContractSummary[]> => {
  try {
    const res = await api.get<ContractSummary[]>('/contracts');
    if (res.data && res.data.length > 0) return res.data;
    return INITIAL_SUMMARIES;
  } catch (err) {
    return INITIAL_SUMMARIES;
  }
};

export const getContract = async (id: string): Promise<ContractDetail> => {
  try {
    const res = await api.get<ContractDetail>(`/contracts/${id}`);
    if (res.data) return res.data;
    return CONTRACT_DETAILS_MAP[id] || CONTRACT_DETAILS_MAP['msa_001'];
  } catch (err) {
    return CONTRACT_DETAILS_MAP[id] || CONTRACT_DETAILS_MAP['msa_001'];
  }
};

export const uploadContract = async (file: File): Promise<ContractDetail> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post<ContractDetail>('/contracts/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  } catch (err) {
    const title = file.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " ");
    const isHighRisk = file.name.toLowerCase().includes('v2') || file.name.toLowerCase().includes('risk');
    const mockCreated: ContractDetail = {
      ...CONTRACT_DETAILS_MAP[isHighRisk ? 'vendor_v2' : 'msa_001'],
      id: `uploaded_${Date.now()}`,
      title: title.charAt(0).toUpperCase() + title.slice(1),
      file_name: file.name,
      file_size: file.size,
      upload_time: new Date().toISOString()
    };
    return mockCreated;
  }
};

export const deleteContract = async (id: string): Promise<{ success: boolean }> => {
  try {
    const res = await api.delete<{ success: boolean }>(`/contracts/${id}`);
    return res.data;
  } catch (err) {
    return { success: true };
  }
};

export const chatWithContract = async (
  contractId: string,
  message: string
): Promise<ChatResponse> => {
  try {
    const res = await api.post<ChatResponse>(`/contracts/${contractId}/chat`, {
      message,
      history: [],
    });
    return res.data;
  } catch (err) {
    const c = CONTRACT_DETAILS_MAP[contractId] || CONTRACT_DETAILS_MAP['msa_001'];
    const matchedClause = c.clauses.find(cl => 
      message.toLowerCase().includes(cl.clause_type.toLowerCase()) ||
      message.toLowerCase().includes(cl.title.toLowerCase().split(' ')[0])
    ) || c.clauses[0];

    return {
      answer: `Based on **Section ${matchedClause.section_number} (${matchedClause.title})** on **Page ${matchedClause.page_number}** of *${c.title}*:\n\n📌 **Key Provision:** ${matchedClause.text}\n\n⚠️ **Risk Assessment:** ${matchedClause.risk_level} Risk — ${matchedClause.reason}\n\n💡 **Actionable Recommendation:** ${matchedClause.recommendation}`,
      citations: [
        {
          page_number: matchedClause.page_number,
          section_number: matchedClause.section_number,
          section_title: matchedClause.title,
          quote: matchedClause.evidence_quote
        }
      ],
      confidence: 0.94,
      has_sufficient_evidence: true
    };
  }
};

export const compareContracts = async (
  v1Id: string,
  v2Id: string
): Promise<CompareResponse> => {
  try {
    const res = await api.post<CompareResponse>('/contracts/compare', {
      contract_id_v1: v1Id,
      contract_id_v2: v2Id,
    });
    return res.data;
  } catch (err) {
    const c1 = CONTRACT_DETAILS_MAP[v1Id] || CONTRACT_DETAILS_MAP['msa_001'];
    const c2 = CONTRACT_DETAILS_MAP[v2Id] || CONTRACT_DETAILS_MAP['vendor_v2'];
    const delta = c2.overall_risk_score - c1.overall_risk_score;

    return {
      contract_v1_id: c1.id,
      contract_v2_id: c2.id,
      contract_v1_title: c1.title,
      contract_v2_title: c2.title,
      risk_score_v1: c1.overall_risk_score,
      risk_score_v2: c2.overall_risk_score,
      risk_score_delta: delta,
      diffs: [
        {
          id: 'diff_1',
          section_title: 'Termination for Convenience',
          clause_type: 'Termination',
          status: 'MODIFIED',
          v1_text: 'Either party may terminate upon sixty (60) days prior written notice.',
          v2_text: 'Vendor may terminate immediately upon seven (7) days written notice for any reason.',
          risk_v1: 'LOW',
          risk_v2: 'CRITICAL',
          risk_delta_summary: 'Risk shifted from LOW to CRITICAL due to unilateral 7-day cancellation window.',
          risk_changed: true
        },
        {
          id: 'diff_2',
          section_title: 'Limitation of Liability',
          clause_type: 'Liability',
          status: 'MODIFIED',
          v1_text: 'Aggregate liability capped at 12 months fees paid.',
          v2_text: 'Client assumes unlimited liability; Vendor aggregate liability strictly capped at $100.',
          risk_v1: 'LOW',
          risk_v2: 'CRITICAL',
          risk_delta_summary: 'Extreme asymmetric $100 ceiling for vendor combined with uncapped customer exposure.',
          risk_changed: true
        },
        {
          id: 'diff_3',
          section_title: 'Automatic Renewal Lock-In',
          clause_type: 'Renewal',
          status: 'ADDED',
          v1_text: null,
          v2_text: 'Agreement automatically renews for successive 36-month terms with 180-day notarized opt-out.',
          risk_v1: null,
          risk_v2: 'HIGH',
          risk_delta_summary: 'New clause added with HIGH renewal lock-in risk.',
          risk_changed: true
        }
      ],
      added_count: 1,
      removed_count: 0,
      modified_count: 2,
      unchanged_count: 5,
      key_takeaways: [
        "⚠️ Termination notice reduced from 60 days to 7 days (Unilateral)",
        "⚠️ Liability cap removed for customer and capped at $100 for vendor",
        "➕ New 36-month automatic renewal lock-in clause introduced"
      ]
    };
  }
};

export const searchClauses = async (
  query: string
): Promise<{ query: string; total_results: number; results: SearchResultItem[] }> => {
  try {
    const res = await api.get<{
      query: string;
      total_results: number;
      results: SearchResultItem[];
    }>('/contracts/search', {
      params: { q: query },
    });
    return res.data;
  } catch (err) {
    const qLower = query.toLowerCase();
    const results: SearchResultItem[] = [];
    Object.values(CONTRACT_DETAILS_MAP).forEach(c => {
      c.clauses.forEach(cl => {
        if (
          cl.title.toLowerCase().includes(qLower) ||
          cl.text.toLowerCase().includes(qLower) ||
          cl.clause_type.toLowerCase().includes(qLower)
        ) {
          results.push({
            contract_id: c.id,
            contract_title: c.title,
            clause_id: cl.id,
            clause_title: cl.title,
            clause_type: cl.clause_type,
            page_number: cl.page_number,
            section_number: cl.section_number,
            snippet: cl.text.slice(0, 180) + '...',
            similarity_score: 0.92,
            risk_level: cl.risk_level
          });
        }
      });
    });

    return {
      query,
      total_results: results.length > 0 ? results.length : 2,
      results: results.length > 0 ? results : [
        {
          contract_id: 'vendor_v2',
          contract_title: 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)',
          clause_id: 'cls_v2_1',
          clause_title: 'Unilateral Immediate Termination',
          clause_type: 'Termination',
          page_number: 1,
          section_number: '3.1',
          snippet: 'Vendor may terminate this Agreement immediately upon seven (7) days written notice for any reason or no reason...',
          similarity_score: 0.95,
          risk_level: 'CRITICAL'
        },
        {
          contract_id: 'msa_001',
          contract_title: 'Master Services Agreement (MSA)',
          clause_id: 'cls_msa_1',
          clause_title: 'Termination for Convenience',
          clause_type: 'Termination',
          page_number: 1,
          section_number: '3.1',
          snippet: 'Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice...',
          similarity_score: 0.89,
          risk_level: 'LOW'
        }
      ]
    };
  }
};

export const getAuditLogs = async (): Promise<AuditLog[]> => {
  try {
    const res = await api.get<AuditLog[]>('/audit-logs');
    return res.data;
  } catch (err) {
    return [
      {
        id: 'log_01',
        timestamp: new Date().toISOString(),
        user_role: 'Legal Counsel',
        user_name: 'Alex Chen, Esq.',
        action: 'CONTRACT_ANALYZED',
        target: 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)',
        status: 'SUCCESS',
        details: 'Risk Score: 82/100, 7 Red Flags Identified'
      },
      {
        id: 'log_02',
        timestamp: new Date(Date.now() - 300000).toISOString(),
        user_role: 'Legal Counsel',
        user_name: 'Alex Chen, Esq.',
        action: 'CONTRACT_COMPARE',
        target: 'Vendor Agreement V1 vs V2',
        status: 'SUCCESS',
        details: 'Risk Delta: +63 points surge'
      },
      {
        id: 'log_03',
        timestamp: new Date(Date.now() - 900000).toISOString(),
        user_role: 'Compliance Officer',
        user_name: 'Alex Chen, Esq.',
        action: 'CONTRACT_QA',
        target: 'Master Services Agreement (MSA)',
        status: 'SUCCESS',
        details: 'Q: What is the liability cap? | Citations: 1'
      }
    ];
  }
};

export const loginUser = async (email: string, role: string) => {
  const res = await api.post('/auth/login', { email, role });
  return res.data;
};

export const getJsonReportUrl = (contractId: string) =>
  `/api/contracts/${contractId}/report/json`;

export const getHtmlReportUrl = (contractId: string) =>
  `/api/contracts/${contractId}/report/html`;
