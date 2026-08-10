from typing import Optional
from backend.schemas.report import FinalRecommendation
from backend.schemas.evaluation import EvaluationReport
from backend.schemas.semantic_profile import SemanticProfile
from backend.schemas.mission_brief import MissionBrief


class HTMLReportGenerator:
    """Generates responsive, glassmorphism-styled HTML reports from recommendation artifacts."""

    @classmethod
    def generate_html(
        cls,
        recommendation: FinalRecommendation,
        evaluation_report: Optional[EvaluationReport] = None,
        profile: Optional[SemanticProfile] = None,
        mission: Optional[MissionBrief] = None,
    ) -> str:
        """Renders a standalone, styled HTML report."""
        winning_id = recommendation.winning_experiment_id
        model_name = recommendation.model
        summary_text = recommendation.summary

        # Build metrics HTML pills
        metrics_html = ""
        if recommendation.final_metrics:
            for k, v in recommendation.final_metrics.items():
                metrics_html += f"""
                <div class="metric-card">
                    <div class="metric-value">{v}</div>
                    <div class="metric-label">{k.upper()}</div>
                </div>
                """

        # Build ranking table HTML rows
        ranking_rows = ""
        if evaluation_report and evaluation_report.ranking:
            for item in evaluation_report.ranking:
                ranking_rows += f"""
                <tr>
                    <td><strong>#{item.rank}</strong></td>
                    <td><code>{item.experiment_id}</code></td>
                    <td>{item.model}</td>
                    <td><span class="badge">{item.score:.4f}</span></td>
                </tr>
                """

        # Build findings HTML list
        findings_html = ""
        findings_list = recommendation.key_findings or ([f.finding for f in evaluation_report.knowledge] if evaluation_report else [])
        for f in findings_list:
            findings_html += f"<li>💡 {f}</li>"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataPilot-AI Report - {winning_id}</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.1);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-color: #38bdf8;
            --success-color: #34d399;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 40px 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 8px;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        h2 {{
            color: var(--accent-color);
            margin-top: 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .metric-card {{
            background: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            border: 1px solid var(--border-color);
        }}
        .metric-value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--success-color);
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            color: var(--text-secondary);
        }}
        .badge {{
            background: rgba(56, 189, 248, 0.2);
            color: var(--accent-color);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DataPilot-AI Recommendation Report</h1>
            <p>Winning Experiment: <code>{winning_id}</code> | Model: <strong>{model_name}</strong></p>
        </div>

        <div class="card">
            <h2>Executive Summary</h2>
            <p>{summary_text}</p>
            <div class="metrics-grid">
                {metrics_html}
            </div>
        </div>

        <div class="card">
            <h2>Key Knowledge Base Findings</h2>
            <ul>
                {findings_html or '<li>Optimization completed successfully.</li>'}
            </ul>
        </div>

        <div class="card">
            <h2>Experiment Leaderboard</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Experiment ID</th>
                        <th>Model</th>
                        <th>Composite Score</th>
                    </tr>
                </thead>
                <tbody>
                    {ranking_rows or '<tr><td colspan="4">No ranking data available.</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
        return html_content
