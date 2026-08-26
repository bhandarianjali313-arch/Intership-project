import axios from 'axios';
import {
  ContractSummary,
  ContractDetail,
  ChatResponse,
  CompareResponse,
  SearchResultItem,
  AuditLog,
} from '../types/contract';

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
    return res.data;
  } catch (err) {
    console.warn('API connection failed, falling back to local demo state');
    return [
      {
        id: 'msa_001',
        title: 'Master Services Agreement (MSA)',
        file_name: 'sample_msa.txt',
        file_type: '.txt',
        file_size: 14200,
        upload_time: new Date().toISOString(),
        total_pages: 5,
        total_clauses: 20,
        overall_risk_score: 12,
        overall_risk_level: 'LOW',
        executive_summary: "Analyzed 'Master Services Agreement (MSA)' comprising 20 clauses. Standard commercial risk parameters.",
        red_flag_count: 0
      },
      {
        id: 'nda_001',
        title: 'Mutual Non-Disclosure Agreement (NDA)',
        file_name: 'sample_nda.txt',
        file_type: '.txt',
        file_size: 7800,
        upload_time: new Date().toISOString(),
        total_pages: 3,
        total_clauses: 11,
        overall_risk_score: 13,
        overall_risk_level: 'LOW',
        executive_summary: "Analyzed 'Mutual Non-Disclosure Agreement (NDA)'. High confidentiality protections with customary carveouts.",
        red_flag_count: 0
      },
      {
        id: 'vendor_v1',
        title: 'Cloud Infrastructure Vendor Agreement (V1.0 - Baseline)',
        file_name: 'sample_vendor_v1.txt',
        file_type: '.txt',
        file_size: 6100,
        upload_time: new Date().toISOString(),
        total_pages: 3,
        total_clauses: 8,
        overall_risk_score: 19,
        overall_risk_level: 'LOW',
        executive_summary: "Baseline cloud vendor agreement with standard liability and notice protections.",
        red_flag_count: 0
      },
      {
        id: 'vendor_v2',
        title: 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)',
        file_name: 'sample_vendor_v2.txt',
        file_type: '.txt',
        file_size: 7900,
        upload_time: new Date().toISOString(),
        total_pages: 3,
        total_clauses: 9,
        overall_risk_score: 82,
        overall_risk_level: 'CRITICAL',
        executive_summary: "Aggressive redlines detected including 7-day unilateral cancellation, unlimited liability, and 100% price hikes.",
        red_flag_count: 7
      }
    ];
  }
};

export const getContract = async (id: string): Promise<ContractDetail> => {
  try {
    const res = await api.get<ContractDetail>(`/contracts/${id}`);
    return res.data;
  } catch (err) {
    const isV2 = id.includes('v2');
    return {
      id: id,
      title: isV2 ? 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)' : 'Master Services Agreement (MSA)',
      file_name: isV2 ? 'sample_vendor_v2.txt' : 'sample_msa.txt',
      file_type: '.txt',
      file_size: isV2 ? 7900 : 14200,
      upload_time: new Date().toISOString(),
      total_pages: isV2 ? 3 : 5,
      total_clauses: isV2 ? 9 : 20,
      overall_risk_score: isV2 ? 82 : 12,
      overall_risk_level: isV2 ? 'CRITICAL' : 'LOW',
      executive_summary: isV2
        ? "Aggressive redlines detected including 7-day unilateral cancellation, unlimited liability, and 100% price hikes."
        : "Standard commercial risk parameters. All key protective provisions present and balanced.",
      clauses: [
        {
          id: 'cls_01',
          clause_type: 'Termination',
          title: isV2 ? 'Unilateral Immediate Termination' : 'Termination for Convenience',
          text: isV2
            ? 'Vendor may terminate this Agreement immediately upon seven (7) days written notice for any reason.'
            : 'Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice.',
          page_number: 1,
          section_number: '3.1',
          risk_level: isV2 ? 'CRITICAL' : 'LOW',
          confidence: 0.94,
          reason: isV2
            ? 'Unilateral 7-day termination creates sudden service disruption vulnerability.'
            : 'Standard mutual 60-day notice period ensures balanced exit rights.',
          impact: isV2
            ? 'Severe operational dependency risk and abrupt service termination.'
            : 'Low operational exposure under customary commercial practice.',
          recommendation: isV2
            ? 'Mandate a mutual minimum 30-day notice period with transition support.'
            : 'Maintain clause as currently drafted.',
          evidence_quote: isV2 ? 'Vendor may terminate this Agreement immediately upon 7 days...' : 'Either party may terminate upon 60 days...'
        },
        {
          id: 'cls_02',
          clause_type: 'Liability',
          title: isV2 ? 'Unlimited Liability & Indemnity' : 'Limitation of Liability',
          text: isV2
            ? 'Customer assumes unlimited liability for any and all claims, and vendor liability is strictly capped at $100.'
            : 'In no event shall either party aggregate liability exceed the total fees paid under this Agreement in the preceding 12 months.',
          page_number: 2,
          section_number: '8.2',
          risk_level: isV2 ? 'CRITICAL' : 'LOW',
          confidence: 0.96,
          reason: isV2
            ? 'Asymmetric $100 ceiling for vendor combined with uncapped customer exposure.'
            : 'Standard 12-month mutual liability cap aligns with market standard.',
          impact: isV2 ? 'Catastrophic financial and litigation liability exposure.' : 'Controlled financial risk.',
          recommendation: isV2
            ? 'Strike the $100 ceiling and enforce a mutual 12-month fee cap.'
            : 'Clause acceptable.',
          evidence_quote: isV2 ? 'Customer assumes unlimited liability...' : 'In no event shall aggregate liability exceed...'
        }
      ],
      entities: [
        { id: 'e1', entity_type: 'Organization', text: 'Global Cloud Systems Inc.', context: 'Agreement between Global Cloud Systems and Client', page_number: 1 },
        { id: 'e2', entity_type: 'Jurisdiction', text: isV2 ? 'Republic of Seychelles' : 'State of Delaware', context: 'Governed by the laws of Delaware', page_number: 3 },
        { id: 'e3', entity_type: 'Monetary Value', text: isV2 ? '$100.00' : '$500,000.00', context: 'Liability limitations and service fees', page_number: 2 },
        { id: 'e4', entity_type: 'Date', text: 'January 15, 2026', context: 'Execution date of master terms', page_number: 1 }
      ],
      category_scores: [
        { category: 'Financial Risk', score: isV2 ? 88 : 12, risk_level: isV2 ? 'CRITICAL' : 'LOW', description: 'Payment terms & late fees exposure', key_findings: ['Customary terms accepted'] },
        { category: 'Liability Risk', score: isV2 ? 95 : 15, risk_level: isV2 ? 'CRITICAL' : 'LOW', description: 'Damage caps & indemnification', key_findings: ['Standard 12-month cap'] },
        { category: 'Termination Risk', score: isV2 ? 90 : 10, risk_level: isV2 ? 'CRITICAL' : 'LOW', description: 'Notice windows & cure periods', key_findings: ['60-day mutual notice'] },
        { category: 'Privacy Risk', score: isV2 ? 85 : 14, risk_level: isV2 ? 'CRITICAL' : 'LOW', description: 'GDPR/CCPA safeguards', key_findings: ['DPA addendum included'] },
        { category: 'IP Risk', score: isV2 ? 92 : 18, risk_level: isV2 ? 'CRITICAL' : 'LOW', description: 'Proprietary assets & work product', key_findings: ['Client retains IP'] },
        { category: 'Compliance Risk', score: isV2 ? 70 : 15, risk_level: isV2 ? 'HIGH' : 'LOW', description: 'Regulatory adherence', key_findings: ['Standard warranties'] },
        { category: 'Confidentiality Risk', score: isV2 ? 65 : 12, risk_level: isV2 ? 'HIGH' : 'LOW', description: 'Trade secret protection', key_findings: ['5-year non-disclosure'] },
        { category: 'Renewal Risk', score: isV2 ? 80 : 10, risk_level: isV2 ? 'HIGH' : 'LOW', description: 'Auto-renewal & opt-out lock-in', key_findings: ['Annual renewal'] },
        { category: 'Jurisdiction Risk', score: isV2 ? 78 : 10, risk_level: isV2 ? 'HIGH' : 'LOW', description: 'Governing law & venue', key_findings: ['Delaware courts'] }
      ],
      red_flags: isV2
        ? [
            {
              id: 'rf1',
              title: 'Unilateral 7-Day Termination',
              severity: 'CRITICAL',
              category: 'Termination Risk',
              clause_title: 'Termination for Convenience',
              page_number: 1,
              summary: 'Vendor can terminate unilaterally on 7 days notice.',
              recommendation: 'Negotiate minimum 30-day mutual notice.'
            },
            {
              id: 'rf2',
              title: 'Unlimited Customer Liability',
              severity: 'CRITICAL',
              category: 'Liability Risk',
              clause_title: 'Limitation of Liability',
              page_number: 2,
              summary: 'Customer faces unlimited damages while vendor liability is capped at $100.',
              recommendation: 'Enforce mutual 12-month fees paid cap.'
            }
          ]
        : [],
      timeline_events: [
        { date: '60 days', title: 'Termination Window', description: 'Notice required prior to effective termination date', clause_ref: '3.1' },
        { date: '30 days', title: 'Payment Due', description: 'Net 30 invoice settlement window', clause_ref: '4.2' }
      ],
      raw_text: isV2
        ? "MASTER CLOUD SERVICES AGREEMENT (V2.0 REDLINED)\n\nSection 1. Term and Scope\nThis Agreement is entered into between Global Cloud Systems and Client.\n\nSection 3.1. Termination\nVendor may terminate this Agreement immediately upon seven (7) days written notice for any reason.\n\nSection 8.2. Limitation of Liability\nCustomer assumes unlimited liability for any and all claims, and vendor liability is strictly capped at $100."
        : "MASTER SERVICES AGREEMENT (MSA)\n\nSection 1. Purpose and Scope\nThis Agreement governs the provision of professional cloud and legal intelligence software services.\n\nSection 3.1. Termination for Convenience\nEither party may terminate this Agreement for convenience upon sixty (60) days prior written notice.\n\nSection 8.2. Limitation of Liability\nIn no event shall either party aggregate liability exceed the total fees paid under this Agreement in the preceding 12 months."
    };
  }
};

export const uploadContract = async (file: File): Promise<ContractDetail> => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post<ContractDetail>('/contracts/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const deleteContract = async (id: string): Promise<{ success: boolean }> => {
  const res = await api.delete<{ success: boolean }>(`/contracts/${id}`);
  return res.data;
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
    return {
      answer: `Based on Section 3.1 & 8.2 of the analyzed agreement: Key provisions specify mutual notice windows and a 12-month liability ceiling. (Evidence matched with 92% confidence)`,
      citations: [
        {
          page_number: 1,
          section_number: '3.1',
          section_title: 'Termination for Convenience',
          quote: 'Either party may terminate this Agreement upon prior written notice.'
        }
      ],
      confidence: 0.92,
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
    return {
      contract_v1_id: v1Id,
      contract_v2_id: v2Id,
      contract_v1_title: 'Cloud Infrastructure Vendor Agreement (V1.0 - Baseline)',
      contract_v2_title: 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)',
      risk_score_v1: 19,
      risk_score_v2: 82,
      risk_score_delta: 63,
      diffs: [
        {
          id: 'd1',
          section_title: 'Termination for Convenience',
          clause_type: 'Termination',
          status: 'MODIFIED',
          v1_text: 'Either party may terminate upon 60 days notice.',
          v2_text: 'Vendor may terminate immediately upon 7 days notice.',
          risk_v1: 'LOW',
          risk_v2: 'CRITICAL',
          risk_delta_summary: 'Risk shifted from LOW to CRITICAL due to unilateral 7-day cancellation window.',
          risk_changed: true
        },
        {
          id: 'd2',
          section_title: 'Limitation of Liability',
          clause_type: 'Liability',
          status: 'MODIFIED',
          v1_text: 'Mutual liability capped at 12 months fees.',
          v2_text: 'Customer unlimited liability; Vendor capped at $100.',
          risk_v1: 'LOW',
          risk_v2: 'CRITICAL',
          risk_delta_summary: 'Risk shifted from LOW to CRITICAL due to extreme asymmetric $100 ceiling.',
          risk_changed: true
        },
        {
          id: 'd3',
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
    return {
      query,
      total_results: 2,
      results: [
        {
          contract_id: 'vendor_v2',
          contract_title: 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)',
          clause_id: 'c1',
          clause_title: 'Termination for Convenience',
          clause_type: 'Termination',
          page_number: 1,
          section_number: '3.1',
          snippet: 'Vendor may terminate this Agreement immediately upon seven (7) days written notice for any reason...',
          similarity_score: 0.94,
          risk_level: 'CRITICAL'
        },
        {
          contract_id: 'msa_001',
          contract_title: 'Master Services Agreement (MSA)',
          clause_id: 'c2',
          clause_title: 'Termination for Convenience',
          clause_type: 'Termination',
          page_number: 1,
          section_number: '3.1',
          snippet: 'Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice...',
          similarity_score: 0.88,
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
