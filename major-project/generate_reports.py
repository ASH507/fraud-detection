import pandas as pd
from fpdf import FPDF
import os

def generate_summary_pdf(csv_path, output_path):
    df = pd.read_csv(csv_path)

    # Summary calculations
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.to_period("M")
    monthly_summary = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)

    top_recipients = df["Recipient"].value_counts().head(10)
    top_by_amount = df.groupby("Recipient")["Amount"].sum().sort_values(ascending=False).head(10)

    largest_debit = df[df["Type"] == "DEBIT"].sort_values("Amount", ascending=False).head(1)
    largest_credit = df[df["Type"] == "CREDIT"].sort_values("Amount", ascending=False).head(1)

    day_counts = df["Date"].dt.date.value_counts().sort_values(ascending=False).head(1)
    df["Hour"] = df["Date"].dt.hour
    hour_counts = df["Hour"].value_counts().sort_index()

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    def add_section(title, content):
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=title, ln=True)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 6, content)
        pdf.ln(4)

    add_section("Monthly Summary (Debits and Credits):", monthly_summary.to_string())
    add_section("Top 10 Most Frequent Recipients:", top_recipients.to_string())
    add_section("Top Recipients by Total Amount:", top_by_amount.to_string())
    add_section("Largest Single Debit:", largest_debit[["Date", "Recipient", "Amount"]].to_string(index=False))
    add_section("Largest Single Credit:", largest_credit[["Date", "Recipient", "Amount"]].to_string(index=False))
    add_section("Day with Most Transactions:", day_counts.to_string())
    add_section("Most Active Hours:", hour_counts.to_string())

    pdf.output(output_path)
    print(f"Saved summary PDF to {output_path}")

def generate_location_url_pdf(csv_path, output_path):
    df = pd.read_csv(csv_path)
    location_df = df[df["Recipient_Type"] == "location"]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, "Location URLs for Recipients Detected as Locations\n\n")

    for i, row in location_df.iterrows():
        line = f"{row['Recipient']} --> {row.get('Location_URL', '')}"
        pdf.multi_cell(0, 6, line)

    pdf.output(output_path)
    print(f"Saved location URL PDF to {output_path}")
