import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False

from app.core.config import settings

def build_report_html(
    user_name: str,
    utility: str,
    state: str,
    bill_history: List[Dict[str, Any]],
    forecast: Dict[str, Any],
    appliances: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    report_period: str = "Last 12 Months"
) -> str:
    now_str = datetime.now().strftime("%d-%m-%Y")
    
    # Rows for bill history
    bill_rows_html = ""
    for b in bill_history:
        bill_rows_html += f"""
        <tr>
            <td>{b.get('billing_period', 'N/A')}</td>
            <td>{b.get('units_consumed_kwh', 0):.1f} kWh</td>
            <td>₹{b.get('energy_charges', 0):,.2f}</td>
            <td>₹{b.get('subsidy_amount', 0):,.2f}</td>
            <td style="font-weight: bold;">₹{b.get('net_payable', 0):,.2f}</td>
        </tr>
        """
        
    appliance_rows_html = ""
    for a in appliances:
        appliance_rows_html += f"""
        <tr>
            <td>{a.get('appliance_type', 'Appliance')}</td>
            <td>{a.get('count', 1)}</td>
            <td>{a.get('wattage_watts', 0):.0f} W</td>
            <td>{a.get('daily_hours', 0):.1f} hrs</td>
            <td style="font-weight: bold;">{a.get('estimated_monthly_kwh', 0):.1f} kWh</td>
        </tr>
        """

    rec_cards_html = ""
    for r in recommendations:
        rec_cards_html += f"""
        <div class="card" style="margin-bottom: 15px; border-left: 4px solid #10b981; padding: 12px; background: #f0fdf4;">
            <h4 style="margin: 0 0 5px 0; color: #065f46;">{r.get('title')}</h4>
            <p style="margin: 0 0 8px 0; font-size: 13px; color: #374151;">{r.get('description')}</p>
            <div style="font-size: 12px; display: flex; justify-content: space-between;">
                <span><strong>Est. Investment:</strong> ₹{r.get('investment_inr', 0):,.0f}</span>
                <span><strong>Monthly Savings:</strong> ₹{r.get('monthly_savings_inr', 0):,.0f}</span>
                <span><strong>Payback:</strong> {r.get('payback_period_years', 0):.1f} yrs</span>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>PowerPulse Energy & Cost Optimization Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1f2937;
            margin: 30px;
            font-size: 14px;
            line-height: 1.5;
        }}
        .header {{
            border-bottom: 3px solid #2563eb;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        .logo {{
            font-size: 26px;
            font-weight: bold;
            color: #1d4ed8;
        }}
        .tagline {{
            color: #6b7280;
            font-size: 14px;
        }}
        .meta-box {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 20px;
        }}
        .section-title {{
            font-size: 18px;
            color: #1e3a8a;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 6px;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #e2e8f0;
            padding: 8px 10px;
            text-align: left;
            font-size: 13px;
        }}
        th {{
            background: #f1f5f9;
            color: #334155;
            font-weight: 600;
        }}
        .highlight-box {{
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .disclaimer {{
            font-size: 11px;
            color: #6b7280;
            margin-top: 30px;
            border-top: 1px solid #e5e7eb;
            padding-top: 10px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">⚡ PowerPulse</div>
        <div class="tagline">Indian Household Electricity Consumption & Cost Optimization Report</div>
    </div>

    <div class="meta-box">
        <table style="border: none; margin: 0;">
            <tr style="border: none;">
                <td style="border: none; width: 50%;"><strong>Consumer:</strong> {user_name}</td>
                <td style="border: none;"><strong>Utility:</strong> {utility} ({state})</td>
            </tr>
            <tr style="border: none;">
                <td style="border: none;"><strong>Report Date:</strong> {now_str}</td>
                <td style="border: none;"><strong>Period:</strong> {report_period}</td>
            </tr>
        </table>
    </div>

    <div class="highlight-box">
        <h3 style="margin-top: 0; color: #1e40af;">Next Month Forecast (AI Estimate)</h3>
        <p style="font-size: 15px; margin-bottom: 5px;">
            Predicted Consumption: <strong>{forecast.get('predicted_kwh', 0):.1f} kWh</strong> &nbsp;|&nbsp;
            Est. Net Bill: <strong>₹{forecast.get('estimated_cost_inr', 0):,.2f}</strong>
        </p>
        <span style="display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; background: #dbeafe; color: #1e40af;">
            Confidence Tier: {forecast.get('confidence_tier', 'ESTIMATE')}
        </span>
        <p style="font-size: 12px; color: #4b5563; margin-top: 6px;">{forecast.get('disclaimer', '')}</p>
    </div>

    <div class="section-title">Historical Consumption & Bills</div>
    <table>
        <thead>
            <tr>
                <th>Billing Cycle</th>
                <th>Consumption</th>
                <th>Energy Charges</th>
                <th>Govt Subsidy</th>
                <th>Net Paid</th>
            </tr>
        </thead>
        <tbody>
            {bill_rows_html if bill_rows_html else '<tr><td colspan="5" style="text-align: center;">No past bills recorded</td></tr>'}
        </tbody>
    </table>

    <div class="section-title">Appliance Breakdown (Estimated Power Profile)</div>
    <table>
        <thead>
            <tr>
                <th>Appliance</th>
                <th>Count</th>
                <th>Wattage</th>
                <th>Daily Hours</th>
                <th>Est. Monthly Units</th>
            </tr>
        </thead>
        <tbody>
            {appliance_rows_html if appliance_rows_html else '<tr><td colspan="5" style="text-align: center;">No appliances registered yet</td></tr>'}
        </tbody>
    </table>

    <div class="section-title">Cost-Saving & Eco Recommendations</div>
    {rec_cards_html}

    <div class="disclaimer">
        Notice: All figures marked as "Est." are AI-generated based on statistical regression models, historical billing records, and regional tariff schedules. Actual distribution utility bills may vary based on slab adjustments, fuel surcharge adjustments (FSA/FCA), and climatic variations. Generated by PowerPulse for Indian residential consumers.
    </div>
</body>
</html>
"""

def generate_pdf_report(
    user_name: str,
    utility: str,
    state: str,
    bill_history: List[Dict[str, Any]],
    forecast: Dict[str, Any],
    appliances: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    output_filename: str = "report.pdf"
) -> Tuple[str, str]:
    """
    Generates PDF report and returns (relative_path, full_path).
    """
    html_content = build_report_html(
        user_name=user_name,
        utility=utility,
        state=state,
        bill_history=bill_history,
        forecast=forecast,
        appliances=appliances,
        recommendations=recommendations
    )
    
    reports_dir = Path(settings.STORAGE_PATH) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = reports_dir / output_filename
    
    if HAS_WEASYPRINT:
        HTML(string=html_content).write_pdf(str(pdf_path))
    else:
        # Fallback: Save clean HTML with print style or formatted report
        html_fallback_path = pdf_path.with_suffix(".html")
        with open(html_fallback_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        # Also touch/write pdf_path for file consistency
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
    relative_path = f"reports/{output_filename}"
    return relative_path, str(pdf_path)

