export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type ClauseType =
  | 'Termination'
  | 'Liability'
  | 'Payment'
  | 'Confidentiality'
  | 'Privacy'
  | 'Intellectual Property'
  | 'Indemnification'
  | 'Warranty'
  | 'Renewal'
  | 'Governing Law'
  | 'Dispute Resolution'
  | 'Non-compete'
  | 'Data Protection'
  | 'Force Majeure'
  | 'General Provisions';

export type EntityType =
  | 'Person'
  | 'Organization'
  | 'Date'
  | 'Monetary Value'
  | 'Location'
  | 'Jurisdiction'
  | 'Contract Duration'
  | 'Renewal Date'
  | 'Payment Term';

export interface ClauseItem {
  id: string;
  clause_type: ClauseType;
  title: string;
  text: string;
  page_number: number;
  section_number: string;
  risk_level: RiskLevel;
  confidence: number;
  reason: string;
  impact: string;
  recommendation: string;
  evidence_quote: string;
}

export interface EntityItem {
  id: string;
  entity_type: EntityType;
  text: string;
  context: string;
  page_number: number;
}

export interface RiskCategoryScore {
  category: string;
  score: number;
  risk_level: RiskLevel;
  description: string;
  key_findings: string[];
}

export interface RedFlagItem {
  id: string;
  title: string;
  severity: RiskLevel;
  category: string;
  clause_title: string;
  page_number: number;
  summary: string;
  recommendation: string;
}

export interface TimelineEvent {
  date: string;
  title: string;
  description: string;
  clause_ref: string;
}

export interface ContractSummary {
  id: string;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  upload_time: string;
  total_pages: number;
  total_clauses: number;
  overall_risk_score: number;
  overall_risk_level: RiskLevel;
  executive_summary: string;
  red_flag_count: number;
}

export interface ContractDetail {
  id: string;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  upload_time: string;
  total_pages: number;
  total_clauses: number;
  overall_risk_score: number;
  overall_risk_level: RiskLevel;
  executive_summary: string;
  clauses: ClauseItem[];
  entities: EntityItem[];
  category_scores: RiskCategoryScore[];
  red_flags: RedFlagItem[];
  timeline_events: TimelineEvent[];
  raw_text?: string;
}

export interface Citation {
  page_number: number;
  section_number: string;
  section_title: string;
  quote: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  confidence?: number;
  timestamp?: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
  has_sufficient_evidence: boolean;
}

export interface ClauseDiff {
  id: string;
  section_title: string;
  clause_type: ClauseType;
  status: 'ADDED' | 'REMOVED' | 'MODIFIED' | 'UNCHANGED';
  v1_text?: string | null;
  v2_text?: string | null;
  risk_v1?: RiskLevel | null;
  risk_v2?: RiskLevel | null;
  risk_delta_summary: string;
  risk_changed: boolean;
}

export interface CompareResponse {
  contract_v1_id: string;
  contract_v2_id: string;
  contract_v1_title: string;
  contract_v2_title: string;
  risk_score_v1: number;
  risk_score_v2: number;
  risk_score_delta: number;
  diffs: ClauseDiff[];
  added_count: number;
  removed_count: number;
  modified_count: number;
  unchanged_count: number;
  key_takeaways: string[];
}

export interface SearchResultItem {
  contract_id: string;
  contract_title: string;
  clause_id: string;
  clause_title: string;
  clause_type: ClauseType;
  page_number: number;
  section_number: string;
  snippet: string;
  similarity_score: number;
  risk_level: RiskLevel;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  user_role: string;
  user_name: string;
  action: string;
  target: string;
  status: string;
  details: string;
}
