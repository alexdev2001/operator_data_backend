import textwrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
import pandas as pd
import matplotlib.pyplot as plt
from app.services.analysis_service import generate_time_series_chart, generate_seasonality_chart, generate_forecast_chart

UPLOAD_DIR = "app/uploads"
PLOTS_DIR = "app/plots"
REPORT_DIR = "app/reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def draw_wrapped_text(c: canvas.Canvas, text: str, x: float, y: float, width: float, leading: float = 14):
    """
    Draws text wrapped within the specified width.
    """
    lines = textwrap.wrap(text, width=int(width / 6))  # Approx chars per line; adjust as needed
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y

def generate_full_report(file_name: str, sheet_names: list[str]):
    report_path = os.path.join(REPORT_DIR, f"full_report.pdf")
    c = canvas.Canvas(report_path, pagesize=A4)
    width, height = A4
    margin = 50

    # ------------------- COVER PAGE -------------------
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width / 2, height - 120, "GGR Analysis Report")

    c.setFont("Helvetica", 13)
    c.drawCentredString(width / 2, height - 160, "Comprehensive Performance Analysis by Operator")
    c.drawCentredString(width / 2, height - 190, f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}")

    c.setFont("Helvetica", 11)
    intro_text = (
        "This report provides a comprehensive overview of Gross Gaming Revenue (GGR) trends, seasonality, and forecasts "
        "across all registered operators. It is designed for decision-makers who may not be familiar with data analytics, "
        "and provides clear explanations for each chart and metric to help interpret performance and identify patterns."
    )
    y = height - 250
    y = draw_wrapped_text(c, intro_text, x=margin, y=y, width=width - 2*margin)
    c.showPage()

    # ------------------- PER-OPERATOR SECTIONS -------------------
    operator_summaries = []

    for sheet in sheet_names:
        print(f"Processing operator sheet: {sheet}")

        ts_path = generate_time_series_chart(file_name, sheet_name=sheet)
        season_path = generate_seasonality_chart(file_name, sheet_name=sheet)
        forecast_path = generate_forecast_chart(file_name, sheet_name=sheet)

        df = pd.read_excel(os.path.join(UPLOAD_DIR, file_name), sheet_name=sheet, header=1)

        # Ensure Date column is datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Clean numeric columns
        numeric_columns = ['Bets Closed', 'Closed Bets Wagered Amount', 'Total Winnings', 'GGR']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                           .replace({',': '', '\xa0': '', ' ': ''}, regex=True)
                           .replace('nan', 0)
                )
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Compute metrics
        total_bets = df['Bets Closed'].sum()
        total_wagered = df['Closed Bets Wagered Amount'].sum()
        total_winnings = df['Total Winnings'].sum()
        total_ggr = df['GGR'].sum()
        avg_ggr = df['GGR'].mean()
        operator_summaries.append((sheet, total_ggr))

        highest_day = df.loc[df['GGR'].idxmax()] if not df.empty else None
        lowest_day = df.loc[df['GGR'].idxmin()] if not df.empty else None

        def safe_date_format(value):
            if isinstance(value, pd.Timestamp):
                return value.strftime('%Y-%m-%d')
            return str(value)

        weekly_change = (
            ((df['GGR'].iloc[-7:].mean() - df['GGR'].iloc[-14:-7].mean()) / df['GGR'].iloc[-14:-7].mean() * 100)
            if len(df) >= 14 else None
        )

        # ---------------- HEADER & SUMMARY ----------------
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, height - 50, f"Operator: {sheet}")

        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin, height - 80, "Key Performance Summary:")

        c.setFont("Helvetica", 11)
        y = height - 110
        summary_data = [
            ["Total Bets Closed", f"{total_bets:,.0f}"],
            ["Total Wagered Amount", f"{total_wagered:,.2f}"],
            ["Total Winnings", f"{total_winnings:,.2f}"],
            ["Total GGR", f"{total_ggr:,.2f}"],
            ["Average Daily GGR", f"{avg_ggr:,.2f}"],
        ]
        if highest_day is not None:
            summary_data.append(["Highest GGR Day", f"{safe_date_format(highest_day.get('Date'))} ({highest_day['GGR']:,.2f})"])
        if lowest_day is not None:
            summary_data.append(["Lowest GGR Day", f"{safe_date_format(lowest_day.get('Date'))} ({lowest_day['GGR']:,.2f})"])
        if weekly_change is not None:
            summary_data.append(["Weekly % Change", f"{weekly_change:.2f}%"])

        for metric, value in summary_data:
            c.drawString(margin, y, f"{metric}:")
            c.drawString(margin + 250, y, str(value))
            y -= 18

        c.showPage()

        # ---------------- CHARTS ----------------
        chart_texts = [
            ("GGR Trend Over Time",
             "This chart shows daily GGR over time, helping visualize performance fluctuations and long-term trends for the operator.",
             ts_path),
            ("Seasonality Analysis",
             "This chart decomposes the GGR data into trend, seasonality, and residual components, highlighting recurring weekly/monthly patterns.",
             season_path),
            ("Forecasting Future GGR",
             "Using the Prophet forecasting model, this chart predicts future GGR for the next 30 days and provides confidence intervals.",
             forecast_path)
        ]

        for title, desc, path in chart_texts:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margin, height - 70, title)
            c.setFont("Helvetica", 11)
            draw_wrapped_text(c, desc, x=margin, y=height - 90, width=width - 2*margin)
            c.drawImage(path, margin, height - 500, width=500, height=300)
            c.showPage()

    # ------------------- FINAL PAGE: RANKING -------------------
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 50, "Operator Ranking by Total GGR")
    c.setFont("Helvetica", 12)

    sorted_operators = sorted(operator_summaries, key=lambda x: x[1], reverse=True)
    y = height - 100
    for rank, (operator, ggr) in enumerate(sorted_operators, start=1):
        c.drawString(margin, y, f"{rank}. {operator}")
        c.drawString(margin + 250, y, f"Total GGR: {ggr:,.2f}")
        y -= 20
        if y < margin:
            c.showPage()
            y = height - 50

    c.showPage()
    c.save()
    return report_path