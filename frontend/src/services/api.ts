import axios from 'axios';
import {
  ContractSummary,
  ContractDetail,
  ChatResponse,
  CompareResponse,
  SearchResultItem,
  AuditLog,
} from '../types/contract';

const API_BASE = '/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getContracts = async (): Promise<ContractSummary[]> => {
  const res = await api.get<ContractSummary[]>('/contracts');
  return res.data;
};

export const getContract = async (id: string): Promise<ContractDetail> => {
  const res = await api.get<ContractDetail>(`/contracts/${id}`);
  return res.data;
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
  const res = await api.post<ChatResponse>(`/contracts/${contractId}/chat`, {
    message,
    history: [],
  });
  return res.data;
};

export const compareContracts = async (
  v1Id: string,
  v2Id: string
): Promise<CompareResponse> => {
  const res = await api.post<CompareResponse>('/contracts/compare', {
    contract_id_v1: v1Id,
    contract_id_v2: v2Id,
  });
  return res.data;
};

export const searchClauses = async (
  query: string
): Promise<{ query: string; total_results: number; results: SearchResultItem[] }> => {
  const res = await api.get<{
    query: string;
    total_results: number;
    results: SearchResultItem[];
  }>('/contracts/search', {
    params: { q: query },
  });
  return res.data;
};

export const getAuditLogs = async (): Promise<AuditLog[]> => {
  const res = await api.get<AuditLog[]>('/audit-logs');
  return res.data;
};

export const loginUser = async (email: string, role: string) => {
  const res = await api.post('/auth/login', { email, role });
  return res.data;
};

export const getJsonReportUrl = (contractId: string) =>
  `/api/contracts/${contractId}/report/json`;

export const getHtmlReportUrl = (contractId: string) =>
  `/api/contracts/${contractId}/report/html`;
