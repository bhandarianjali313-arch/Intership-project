import { ContractDetail, ContractSummary } from '../types/contract';

export const INITIAL_SUMMARIES: ContractSummary[] = [
  {
    id: 'msa_001',
    title: 'Master Services Agreement (MSA)',
    file_name: 'sample_msa.txt',
    file_type: '.txt',
    file_size: 14200,
    upload_time: '2026-08-26T10:00:00.000Z',
    total_pages: 5,
    total_clauses: 20,
    overall_risk_score: 12,
    overall_risk_level: 'LOW',
    executive_summary: "Analyzed 'Master Services Agreement (MSA)' comprising 20 clauses across 5 pages. Standard commercial risk parameters with well-balanced mutual protections.",
    red_flag_count: 0
  },
  {
    id: 'vendor_v2',
    title: 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)',
    file_name: 'sample_vendor_v2.txt',
    file_type: '.txt',
    file_size: 7900,
    upload_time: '2026-08-26T11:15:00.000Z',
    total_pages: 3,
    total_clauses: 9,
    overall_risk_score: 82,
    overall_risk_level: 'CRITICAL',
    executive_summary: "CRITICAL RISK: Aggressive redlines detected including 7-day unilateral cancellation, unlimited customer liability, $100 vendor ceiling, and 100% price escalation.",
    red_flag_count: 7
  },
  {
    id: 'vendor_v1',
    title: 'Cloud Infrastructure Vendor Agreement (V1.0 - Baseline)',
    file_name: 'sample_vendor_v1.txt',
    file_type: '.txt',
    file_size: 6100,
    upload_time: '2026-08-26T09:30:00.000Z',
    total_pages: 3,
    total_clauses: 8,
    overall_risk_score: 19,
    overall_risk_level: 'LOW',
    executive_summary: "Baseline cloud vendor agreement with standard 12-month liability cap and 60-day mutual notice protections.",
    red_flag_count: 0
  },
  {
    id: 'nda_001',
    title: 'Mutual Non-Disclosure Agreement (NDA)',
    file_name: 'sample_nda.txt',
    file_type: '.txt',
    file_size: 7800,
    upload_time: '2026-08-26T08:45:00.000Z',
    total_pages: 3,
    total_clauses: 11,
    overall_risk_score: 13,
    overall_risk_level: 'LOW',
    executive_summary: "Analyzed 'Mutual Non-Disclosure Agreement (NDA)'. High confidentiality protections with customary carveouts and standard 5-year term.",
    red_flag_count: 0
  }
];

export const CONTRACT_DETAILS_MAP: Record<string, ContractDetail> = {
  msa_001: {
    id: 'msa_001',
    title: 'Master Services Agreement (MSA)',
    file_name: 'sample_msa.txt',
    file_type: '.txt',
    file_size: 14200,
    upload_time: '2026-08-26T10:00:00.000Z',
    total_pages: 5,
    total_clauses: 20,
    overall_risk_score: 12,
    overall_risk_level: 'LOW',
    executive_summary: "Analyzed 'Master Services Agreement (MSA)' comprising 20 clauses across 5 pages. Standard commercial risk parameters with well-balanced mutual protections.",
    clauses: [
      {
        id: 'cls_msa_1',
        clause_type: 'Termination',
        title: 'Termination for Convenience',
        text: 'Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice to the other party.',
        page_number: 1,
        section_number: '3.1',
        risk_level: 'LOW',
        confidence: 0.95,
        reason: 'Standard mutual 60-day termination notice period ensures sufficient transition time.',
        impact: 'Low operational disruption under customary commercial practice.',
        recommendation: 'Maintain clause as currently drafted.',
        evidence_quote: 'Either party may terminate this Agreement for convenience upon sixty (60) days...'
      },
      {
        id: 'cls_msa_2',
        clause_type: 'Liability',
        title: 'Limitation of Liability',
        text: 'In no event shall either party aggregate liability arising out of or related to this Agreement exceed the total amount paid by Client hereunder in the twelve (12) months preceding the incident.',
        page_number: 2,
        section_number: '8.2',
        risk_level: 'LOW',
        confidence: 0.96,
        reason: 'Standard 12-month mutual fee cap aligns with market best practice.',
        impact: 'Controlled financial exposure tied directly to annual contract value.',
        recommendation: 'Clause acceptable.',
        evidence_quote: 'In no event shall either party aggregate liability exceed the total amount paid...'
      },
      {
        id: 'cls_msa_3',
        clause_type: 'Payment',
        title: 'Payment Terms & Invoicing',
        text: 'Client agrees to pay all undisputed invoices within thirty (30) days of receipt (Net 30). Late payments accrue interest at 1.0% per month.',
        page_number: 2,
        section_number: '4.1',
        risk_level: 'LOW',
        confidence: 0.94,
        reason: 'Standard Net 30 payment terms with customary statutory late fee.',
        impact: 'Predictable cash flow cycle.',
        recommendation: 'Standard terms accepted.',
        evidence_quote: 'Client agrees to pay all undisputed invoices within thirty (30) days...'
      },
      {
        id: 'cls_msa_4',
        clause_type: 'Intellectual Property',
        title: 'Ownership of Deliverables & Background IP',
        text: 'All custom deliverables created specifically for Client shall be deemed works made for hire and owned exclusively by Client upon payment. Vendor retains background IP.',
        page_number: 3,
        section_number: '6.1',
        risk_level: 'LOW',
        confidence: 0.93,
        reason: 'Express Work Made for Hire assignment protects Client core proprietary assets.',
        impact: 'Total IP ownership secured for custom development.',
        recommendation: 'Maintain Work Made for Hire vesting.',
        evidence_quote: 'All custom deliverables created specifically for Client shall be deemed works made for hire...'
      },
      {
        id: 'cls_msa_5',
        clause_type: 'Confidentiality',
        title: 'Confidentiality Obligations',
        text: 'Each party agrees to hold the other party Proprietary Information in strict confidence for a period of five (5) years from the date of disclosure.',
        page_number: 3,
        section_number: '7.1',
        risk_level: 'LOW',
        confidence: 0.97,
        reason: 'Standard 5-year confidentiality obligation with customary trade secret exclusions.',
        impact: 'Robust trade secret protection.',
        recommendation: 'Terms accepted.',
        evidence_quote: 'Each party agrees to hold the other party Proprietary Information in strict confidence...'
      },
      {
        id: 'cls_msa_6',
        clause_type: 'Data Protection',
        title: 'Data Security Safeguards',
        text: 'Vendor shall implement technical and administrative safeguards compliant with SOC 2 Type II and ISO 27001 standards. In event of breach, vendor shall notify Client within 48 hours.',
        page_number: 4,
        section_number: '9.3',
        risk_level: 'LOW',
        confidence: 0.95,
        reason: 'Mandatory SOC 2 / ISO compliance with prompt 48-hour security breach notification.',
        impact: 'High regulatory adherence under GDPR and CCPA.',
        recommendation: 'Ensure annual SOC 2 audit reports are delivered.',
        evidence_quote: 'Vendor shall implement technical and administrative safeguards compliant with SOC 2 Type II...'
      },
      {
        id: 'cls_msa_7',
        clause_type: 'Governing Law',
        title: 'Governing Law and Venue',
        text: 'This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflicts of law principles.',
        page_number: 5,
        section_number: '12.1',
        risk_level: 'LOW',
        confidence: 0.98,
        reason: 'Delaware governing law is the gold standard for commercial stability.',
        impact: 'Predictable judicial precedents.',
        recommendation: 'Delaware jurisdiction approved.',
        evidence_quote: 'This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware...'
      }
    ],
    entities: [
      { id: 'e1', entity_type: 'Organization', text: 'Apex Cloud Solutions LLC', context: 'Agreement by and between Apex Cloud Solutions LLC and Client Enterprises', page_number: 1 },
      { id: 'e2', entity_type: 'Organization', text: 'Client Enterprises Inc.', context: 'Agreement by and between Apex Cloud Solutions LLC and Client Enterprises', page_number: 1 },
      { id: 'e3', entity_type: 'Jurisdiction', text: 'State of Delaware', context: 'Governed by the laws of the State of Delaware', page_number: 5 },
      { id: 'e4', entity_type: 'Monetary Value', text: '$500,000.00', context: 'Annual services commitment value', page_number: 2 },
      { id: 'e5', entity_type: 'Date', text: 'January 15, 2026', context: 'Effective execution date', page_number: 1 },
      { id: 'e6', entity_type: 'Payment Term', text: 'Net 30', context: 'Invoices payable within 30 days of receipt', page_number: 2 },
      { id: 'e7', entity_type: 'Contract Duration', text: 'twenty-four (24) months', context: 'Initial term shall be 24 months', page_number: 1 },
      { id: 'e8', entity_type: 'Person', text: 'Sarah Jenkins, Esq.', context: 'Signed by: Sarah Jenkins, General Counsel', page_number: 5 }
    ],
    category_scores: [
      { category: 'Financial Risk', score: 12, risk_level: 'LOW', description: 'Net 30 terms with standard late payment safeguards', key_findings: ['Standard Net 30 accepted'] },
      { category: 'Liability Risk', score: 14, risk_level: 'LOW', description: 'Mutual 12-month liability ceiling', key_findings: ['Mutual 12-month cap in place'] },
      { category: 'Termination Risk', score: 10, risk_level: 'LOW', description: '60-day mutual termination notice window', key_findings: ['Balanced exit rights'] },
      { category: 'Privacy Risk', score: 12, risk_level: 'LOW', description: 'SOC 2 Type II safeguards & 48h breach notice', key_findings: ['GDPR compliant'] },
      { category: 'IP Risk', score: 15, risk_level: 'LOW', description: 'Work Made for Hire vests in Client', key_findings: ['Client owns custom deliverables'] },
      { category: 'Compliance Risk', score: 11, risk_level: 'LOW', description: 'Standard commercial warranties', key_findings: ['Standard warranties'] },
      { category: 'Confidentiality Risk', score: 10, risk_level: 'LOW', description: '5-year non-disclosure covenant', key_findings: ['5-year term'] },
      { category: 'Renewal Risk', score: 12, risk_level: 'LOW', description: 'Annual renewal with 30-day opt-out', key_findings: ['Annual cycle'] },
      { category: 'Jurisdiction Risk', score: 10, risk_level: 'LOW', description: 'State of Delaware courts', key_findings: ['Delaware venue'] }
    ],
    red_flags: [],
    timeline_events: [
      { date: '60 days', title: 'Termination Notice Window', description: 'Notice required prior to effective date', clause_ref: '3.1' },
      { date: '30 days', title: 'Payment Due Window', description: 'Net 30 invoice settlement', clause_ref: '4.1' },
      { date: '48 hours', title: 'Security Breach Notice', description: 'Mandatory breach reporting window', clause_ref: '9.3' }
    ],
    raw_text: `MASTER SERVICES AGREEMENT (MSA)

1. ENGAGEMENT AND SERVICES
This Master Services Agreement is entered into between Apex Cloud Solutions LLC ("Vendor") and Client Enterprises Inc. ("Client").

3.1 TERMINATION FOR CONVENIENCE
Either party may terminate this Agreement for convenience upon sixty (60) days prior written notice to the other party.

4.1 PAYMENT TERMS
Client agrees to pay all undisputed invoices within thirty (30) days of receipt (Net 30). Late payments accrue interest at 1.0% per month.

6.1 INTELLECTUAL PROPERTY & DELIVERABLES
All custom deliverables created specifically for Client shall be deemed works made for hire and owned exclusively by Client upon payment. Vendor retains background IP.

7.1 CONFIDENTIALITY
Each party agrees to hold the other party Proprietary Information in strict confidence for a period of five (5) years from the date of disclosure.

8.2 LIMITATION OF LIABILITY
In no event shall either party aggregate liability arising out of or related to this Agreement exceed the total amount paid by Client hereunder in the twelve (12) months preceding the incident.

9.3 DATA PROTECTION & SECURITY
Vendor shall implement technical and administrative safeguards compliant with SOC 2 Type II and ISO 27001 standards. In event of breach, vendor shall notify Client within 48 hours.

12.1 GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.`
  },

  vendor_v2: {
    id: 'vendor_v2',
    title: 'Cloud Infrastructure Vendor Agreement (V2.0 - Redlined High Risk)',
    file_name: 'sample_vendor_v2.txt',
    file_type: '.txt',
    file_size: 7900,
    upload_time: '2026-08-26T11:15:00.000Z',
    total_pages: 3,
    total_clauses: 9,
    overall_risk_score: 82,
    overall_risk_level: 'CRITICAL',
    executive_summary: "CRITICAL RISK: Aggressive redlines detected including 7-day unilateral cancellation, unlimited customer liability, $100 vendor ceiling, and 100% price escalation.",
    clauses: [
      {
        id: 'cls_v2_1',
        clause_type: 'Termination',
        title: 'Unilateral Immediate Termination',
        text: 'Vendor may terminate this Agreement immediately upon seven (7) days written notice for any reason or no reason. Client is prohibited from terminating prior to the end of the initial 36-month term.',
        page_number: 1,
        section_number: '3.1',
        risk_level: 'CRITICAL',
        confidence: 0.96,
        reason: 'Unilateral 7-day termination creates sudden service disruption vulnerability while locking client in for 36 months.',
        impact: 'Severe operational lock-in and acute service interruption risk.',
        recommendation: 'Mandate mutual 30 to 60 days notice and remove one-sided customer lock-in.',
        evidence_quote: 'Vendor may terminate this Agreement immediately upon seven (7) days written notice...'
      },
      {
        id: 'cls_v2_2',
        clause_type: 'Liability',
        title: 'Unlimited Customer Liability & $100 Ceiling for Vendor',
        text: 'Client assumes unlimited liability for any and all direct, indirect, special, and consequential damages. Vendor total aggregate liability is strictly capped at $100.00.',
        page_number: 2,
        section_number: '8.2',
        risk_level: 'CRITICAL',
        confidence: 0.98,
        reason: 'Egregious asymmetric ceiling: Vendor caps exposure at $100 while Client assumes open-ended consequential damages.',
        impact: 'Catastrophic financial and litigation liability exposure.',
        recommendation: 'Strike the $100 cap; establish a mutual liability cap equal to 12 months fees paid.',
        evidence_quote: 'Client assumes unlimited liability... Vendor total aggregate liability is strictly capped at $100.00.'
      },
      {
        id: 'cls_v2_3',
        clause_type: 'Payment',
        title: 'Aggressive Payment & 100% Price Escalation',
        text: 'Invoices are due upon receipt (Net 7). Late payments accrue penalty interest of 10% daily. Vendor reserves right to increase fees up to 100% annually without notice.',
        page_number: 2,
        section_number: '4.1',
        risk_level: 'CRITICAL',
        confidence: 0.95,
        reason: 'Punitive Net 7 payment terms, usurious 10% daily penalty, and uncontrolled 100% annual price escalations.',
        impact: 'Unpredictable budget escalation and acute cash flow risk.',
        recommendation: 'Standardize to Net 30, cap late interest at 1.5%/month, and limit fee increases to CPI (max 3-5%).',
        evidence_quote: 'Invoices are due upon receipt (Net 7). Late payments accrue penalty interest of 10% daily...'
      },
      {
        id: 'cls_v2_4',
        clause_type: 'Intellectual Property',
        title: 'IP Transfer & AI Model Training License',
        text: 'Client grants Vendor a perpetual, irrevocable, worldwide, royalty-free license to ingest, modify, and train proprietary AI models on all Client confidential data.',
        page_number: 2,
        section_number: '6.2',
        risk_level: 'CRITICAL',
        confidence: 0.97,
        reason: 'Forfeiture of proprietary intellectual property and confidential data to train vendor third-party AI models.',
        impact: 'Complete loss of trade secrets and potential third-party IP leakage.',
        recommendation: 'Strictly prohibit AI model training on customer data; restrict license to temporary operational processing.',
        evidence_quote: 'Client grants Vendor a perpetual, irrevocable, worldwide, royalty-free license to ingest and train AI models...'
      },
      {
        id: 'cls_v2_5',
        clause_type: 'Data Protection',
        title: 'Total Disclaimer of Data Breach Liability',
        text: 'Vendor makes no representations or warranties regarding data security or confidentiality and disclaims all liability for data breaches, loss of data, or cyber incidents.',
        page_number: 3,
        section_number: '9.1',
        risk_level: 'CRITICAL',
        confidence: 0.95,
        reason: 'Total disclaimer of data security obligations violates GDPR, CCPA, and standard enterprise compliance.',
        impact: 'Massive regulatory non-compliance exposure with zero vendor indemnity.',
        recommendation: 'Mandate ISO 27001 / SOC 2 certification and prompt 48h breach notification.',
        evidence_quote: 'Vendor makes no representations or warranties regarding data security... disclaims all liability for data breaches.'
      },
      {
        id: 'cls_v2_6',
        clause_type: 'Renewal',
        title: '36-Month Auto-Renewal with 180-Day Notarized Opt-Out',
        text: 'This Agreement shall automatically renew for successive thirty-six (36) month terms unless Client provides notarized written notice 180 days prior to expiration.',
        page_number: 3,
        section_number: '11.2',
        risk_level: 'HIGH',
        confidence: 0.92,
        reason: 'Burdensome 3-year evergreen renewal with unrealistic 180-day notarized notice trap.',
        impact: 'Inability to terminate underperforming vendor without heavy early exit penalties.',
        recommendation: 'Change to 1-year renewal with standard 30-day written email opt-out.',
        evidence_quote: 'Agreement shall automatically renew for successive thirty-six (36) month terms unless notarized notice...'
      },
      {
        id: 'cls_v2_7',
        clause_type: 'Governing Law',
        title: 'Offshore Jurisdiction & Dispute Venue',
        text: 'This Agreement is governed by the laws of the Republic of Seychelles, and all disputes must be arbitrated in Seychelles at Client sole expense.',
        page_number: 3,
        section_number: '14.1',
        risk_level: 'HIGH',
        confidence: 0.94,
        reason: 'Offshore foreign jurisdiction designed to make legal enforcement cost-prohibitive.',
        impact: 'Prohibitive legal costs to defend rights or resolve disputes.',
        recommendation: 'Change governing law and venue back to Delaware or New York.',
        evidence_quote: 'This Agreement is governed by the laws of the Republic of Seychelles at Client sole expense.'
      }
    ],
    entities: [
      { id: 'ev2_1', entity_type: 'Organization', text: 'Titan Cloud Infrastructure Corp.', context: 'Vendor entity in redlined agreement', page_number: 1 },
      { id: 'ev2_2', entity_type: 'Jurisdiction', text: 'Republic of Seychelles', context: 'Governed by the laws of the Republic of Seychelles', page_number: 3 },
      { id: 'ev2_3', entity_type: 'Monetary Value', text: '$100.00', context: 'Vendor aggregate liability ceiling', page_number: 2 },
      { id: 'ev2_4', entity_type: 'Payment Term', text: 'Net 7', context: 'Invoices due upon receipt (Net 7)', page_number: 2 },
      { id: 'ev2_5', entity_type: 'Contract Duration', text: 'thirty-six (36) months', context: 'Lock-in renewal term of 36 months', page_number: 3 }
    ],
    category_scores: [
      { category: 'Financial Risk', score: 88, risk_level: 'CRITICAL', description: 'Net 7 payment, 10% daily penalty, 100% price hikes', key_findings: ['Punitive price escalation', 'Usurious late penalties'] },
      { category: 'Liability Risk', score: 95, risk_level: 'CRITICAL', description: 'Asymmetric $100 vendor cap and uncapped client liability', key_findings: ['Uncapped client liability', '$100 vendor ceiling'] },
      { category: 'Termination Risk', score: 90, risk_level: 'CRITICAL', description: 'Unilateral 7-day termination by vendor', key_findings: ['7-day sudden cancellation'] },
      { category: 'Privacy Risk', score: 85, risk_level: 'CRITICAL', description: 'Total disclaimer of breach responsibility', key_findings: ['Zero data security warranty'] },
      { category: 'IP Risk', score: 92, risk_level: 'CRITICAL', description: 'Perpetual AI model training license on client data', key_findings: ['AI data mining over proprietary data'] },
      { category: 'Compliance Risk', score: 70, risk_level: 'HIGH', description: 'Disclaimer of standard commercial warranties', key_findings: ['Warranties disclaimed'] },
      { category: 'Confidentiality Risk', score: 65, risk_level: 'HIGH', description: 'Weak trade secret safeguards', key_findings: ['Trade secret exceptions'] },
      { category: 'Renewal Risk', score: 80, risk_level: 'HIGH', description: '36-month lock-in with 180-day notarized opt-out', key_findings: ['3-year evergreen lock-in'] },
      { category: 'Jurisdiction Risk', score: 78, risk_level: 'HIGH', description: 'Seychelles offshore arbitration at client expense', key_findings: ['Offshore Seychelles venue'] }
    ],
    red_flags: [
      { id: 'rf_v2_1', title: 'Unilateral 7-Day Termination Window', severity: 'CRITICAL', category: 'Termination Risk', clause_title: 'Termination for Convenience', page_number: 1, summary: 'Vendor can terminate unilaterally on 7 days notice without cause.', recommendation: 'Require mutual 30 to 60 days notice.' },
      { id: 'rf_v2_2', title: 'Asymmetric $100 Liability Ceiling', severity: 'CRITICAL', category: 'Liability Risk', clause_title: 'Limitation of Liability', page_number: 2, summary: 'Vendor liability is capped at $100 while client assumes unlimited liability.', recommendation: 'Establish mutual 12-month fees paid cap.' },
      { id: 'rf_v2_3', title: 'Perpetual AI Training License on Client Data', severity: 'CRITICAL', category: 'IP Risk', clause_title: 'IP Transfer & AI License', page_number: 2, summary: 'Grants vendor perpetual rights to train proprietary AI models on client confidential data.', recommendation: 'Strictly prohibit AI model training on customer data.' },
      { id: 'rf_v2_4', title: 'Total Disclaimer of Data Breach Liability', severity: 'CRITICAL', category: 'Privacy Risk', clause_title: 'Data Security Safeguards', page_number: 3, summary: 'Vendor disclaims all security and regulatory breach obligations.', recommendation: 'Mandate SOC 2 Type II compliance and 48h breach notice.' },
      { id: 'rf_v2_5', title: '100% Unilateral Price Escalation', severity: 'CRITICAL', category: 'Financial Risk', clause_title: 'Payment Terms & Invoicing', page_number: 2, summary: 'Vendor reserves right to double pricing annually without notice.', recommendation: 'Cap price increases to CPI (max 3-5% per year).' },
      { id: 'rf_v2_6', title: '36-Month Auto-Renewal Trap', severity: 'HIGH', category: 'Renewal Risk', clause_title: 'Automatic Renewal', page_number: 3, summary: 'Requires 180-day notarized opt-out or locks into 36 months.', recommendation: 'Change to 1-year renewal with 30-day email opt-out.' },
      { id: 'rf_v2_7', title: 'Offshore Seychelles Jurisdiction', severity: 'HIGH', category: 'Jurisdiction Risk', clause_title: 'Governing Law', page_number: 3, summary: 'Arbitration in Seychelles at client sole expense.', recommendation: 'Return governing law to Delaware or New York.' }
    ],
    timeline_events: [
      { date: '7 days', title: 'Unilateral Termination Notice', description: 'Vendor sudden cancellation window', clause_ref: '3.1' },
      { date: '7 days', title: 'Net 7 Payment Due', description: 'Immediate invoice settlement requirement', clause_ref: '4.1' },
      { date: '180 days', title: 'Notarized Opt-Out Window', description: 'Mandatory deadline to prevent 3-year auto-renewal', clause_ref: '11.2' }
    ],
    raw_text: `MASTER CLOUD SERVICES AGREEMENT (V2.0 REDLINED - HIGH RISK)

3.1 TERMINATION
Vendor may terminate this Agreement immediately upon seven (7) days written notice for any reason or no reason. Client is prohibited from terminating prior to the end of the initial 36-month term.

4.1 PAYMENT TERMS
Invoices are due upon receipt (Net 7). Late payments accrue penalty interest of 10% daily. Vendor reserves right to increase fees up to 100% annually without notice.

6.2 INTELLECTUAL PROPERTY & AI TRAINING
Client grants Vendor a perpetual, irrevocable, worldwide, royalty-free license to ingest, modify, and train proprietary AI models on all Client confidential data.

8.2 LIMITATION OF LIABILITY
Client assumes unlimited liability for any and all direct, indirect, special, and consequential damages. Vendor total aggregate liability is strictly capped at $100.00.

9.1 DATA PROTECTION DISCLAIMER
Vendor makes no representations or warranties regarding data security or confidentiality and disclaims all liability for data breaches, loss of data, or cyber incidents.

11.2 AUTOMATIC RENEWAL
This Agreement shall automatically renew for successive thirty-six (36) month terms unless Client provides notarized written notice 180 days prior to expiration.

14.1 GOVERNING LAW & JURISDICTION
This Agreement is governed by the laws of the Republic of Seychelles, and all disputes must be arbitrated in Seychelles at Client sole expense.`
  }
};
