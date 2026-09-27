import json
from datetime import datetime
from typing import Dict, Any
from app.models.schemas import ContractDetail

def generate_json_report(contract: ContractDetail) -> Dict[str, Any]:
    return {
        "report_metadata": {
            "platform": "LexiGuard AI - LegalTech Contract Intelligence",
            "generated_at": datetime.now().isoformat(),
            "contract_id": contract.id,
            "contract_title": contract.title,
            "file_name": contract.file_name,
            "overall_risk_score": contract.overall_risk_score,
            "overall_risk_level": contract.overall_risk_level.value
        },
        "executive_summary": contract.executive_summary,
        "category_breakdown": [c.model_dump() for c in contract.category_scores],
        "red_flags": [r.model_dump() for r in contract.red_flags],
        "clauses_analyzed": [cl.model_dump() for cl in contract.clauses],
        "extracted_entities": [e.model_dump() for e in contract.entities],
        "timeline_events": [t.model_dump() for t in contract.timeline_events]
    }

def generate_html_printable_report(contract: ContractDetail) -> str:
    risk_colors = {
        "LOW": "#10b981",
        "MEDIUM": "#f59e0b",
        "HIGH": "#f97316",
        "CRITICAL": "#ef4444"
    }
    risk_color = risk_colors.get(contract.overall_risk_level.value, "#64748b")

    rf_list = []
    for rf in contract.red_flags:
        rf_list.append(
            f"<div style='background:#fef2f2; border-left:4px solid #ef4444; padding:12px; margin-bottom:10px; border-radius:4px;'>"
            f"<div style='display:flex; justify-content:space-between; font-weight:bold; color:#991b1b;'>"
            f"<span>{rf.title} (Page {rf.page_number})</span>"
            f"<span style='background:#fee2e2; padding:2px 8px; border-radius:4px;'>{rf.severity.value}</span>"
            f"</div>"
            f"<p style='margin:6px 0; color:#450a0a;'><strong>Reason:</strong> {rf.summary}</p>"
            f"<p style='margin:4px 0; color:#065f46; font-size:13px;'><strong>Recommendation:</strong> {rf.recommendation}</p>"
            f"</div>"
        )
    rf_html = "".join(rf_list) if rf_list else "<p style='color:#10b981;'>No critical red flags identified.</p>"

    cl_list = []
    for cl in contract.clauses:
        bg = "#fee2e2" if cl.risk_level.value in ["HIGH", "CRITICAL"] else "#ecfdf5"
        fg = "#991b1b" if cl.risk_level.value in ["HIGH", "CRITICAL"] else "#065f46"
        cl_list.append(
            f"<div style='border:1px solid #e2e8f0; border-radius:6px; padding:12px; margin-bottom:12px; background:#fafafa;'>"
            f"<div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #cbd5e1; padding-bottom:6px;'>"
            f"<strong style='color:#0f172a;'>Section {cl.section_number}: {cl.title}</strong>"
            f"<span style='background:{bg}; color:{fg}; padding:2px 8px; border-radius:10px; font-weight:bold; font-size:12px;'>{cl.risk_level.value}</span>"
            f"</div>"
            f"<p style='font-family:monospace; background:#fff; border:1px solid #e2e8f0; padding:8px; border-radius:4px; font-size:12px; margin:8px 0;'>{cl.text}</p>"
            f"<div style='font-size:13px; color:#1e293b;'>"
            f"<p><strong>Reason:</strong> {cl.reason}</p>"
            f"<p><strong>Impact:</strong> {cl.impact}</p>"
            f"<p style='color:#047857;'><strong>Recommendation:</strong> {cl.recommendation}</p>"
            f"<p style='color:#64748b; font-size:11px;'>Page {cl.page_number} | Confidence {int(cl.confidence*100)}%</p>"
            f"</div>"
            f"</div>"
        )
    cl_html = "".join(cl_list)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Risk Report - {contract.title}</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; color: #1e293b; padding: 30px; max-width: 900px; margin: 0 auto; }}
        .header {{ border-bottom: 2px solid #0f172a; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; color: #fff; font-weight: bold; background-color: {risk_color}; }}
        .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 20px 0; }}
        .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; text-align: center; }}
        .val {{ font-size: 22px; font-weight: bold; color: #0f172a; }}
        .lbl {{ font-size: 11px; color: #64748b; text-transform: uppercase; }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0; font-size:24px;">LexiGuard AI Risk Report</h1>
            <p style="margin:4px 0; color:#64748b;">{contract.title}</p>
        </div>
        <div style="text-align:right;">
            <span class="badge">{contract.overall_risk_level.value} RISK</span>
            <div style="font-size:26px; font-weight:bold; color:{risk_color};">{contract.overall_risk_score}/100</div>
        </div>
    </div>
    <div class="grid">
        <div class="card"><div class="val">{contract.total_pages}</div><div class="lbl">Pages</div></div>
        <div class="card"><div class="val">{contract.total_clauses}</div><div class="lbl">Clauses</div></div>
        <div class="card"><div class="val" style="color:#ef4444;">{len(contract.red_flags)}</div><div class="lbl">Red Flags</div></div>
        <div class="card"><div class="val">{len(contract.entities)}</div><div class="lbl">Entities</div></div>
    </div>
    <h2>Executive Summary</h2>
    <p style="background:#f1f5f9; padding:12px; border-radius:6px;">{contract.executive_summary}</p>
    <h2>Critical Red Flags</h2>
    {rf_html}
    <h2>Clause Intelligence</h2>
    {cl_html}
    <div style="margin-top:40px; padding-top:20px; border-top:1px solid #cbd5e1; font-size:12px; color:#94a3b8; text-align:center;">
        Generated by LexiGuard AI Contract Intelligence Platform
    </div>
</body>
</html>"""
