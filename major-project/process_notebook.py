import pdfplumber
import pandas as pd
import re
from googlesearch import search
import time
import random
import os


# ==============================
# 1. DEBUG: Extract raw text
# ==============================
def extract_raw_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"\n📄 Page {i+1}:\n{text}")


# ==============================
# 2. PARSE PDF → CSV
# ==============================
def parse_phonepe_statement(pdf_path, output_csv):
    transactions = []

    print("📄 Parsing PDF:", pdf_path)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if not text:
                    continue

                lines = text.splitlines()
                i = 0

                while i < len(lines):
                    if "Paid to" in lines[i] and "DEBIT" in lines[i]:

                        line1 = lines[i]

                        match1 = re.match(
                            r"([A-Za-z]+\s\d{1,2},\s\d{4}) Paid to (.+?) DEBIT ₹?([\d,]+)",
                            line1
                        )

                        if not match1:
                            i += 1
                            continue

                        date, recipient, amount = match1.groups()
                        amount = amount.replace(",", "")

                        i += 1
                        line2 = lines[i] if i < len(lines) else ""

                        match2 = re.search(
                            r"(\d{1,2}:\d{2}\s(?:am|pm)).*?Transaction ID (\w+)",
                            line2
                        )

                        time_str, tx_id = match2.groups() if match2 else ("", "")

                        i += 1
                        line3 = lines[i] if i < len(lines) else ""

                        match3 = re.search(r"UTR No\.?\s*([\d]+)", line3)
                        utr = match3.group(1) if match3 else ""

                        transactions.append({
                            "Date": date,
                            "Time": time_str,
                            "Recipient": recipient,
                            "Type": "DEBIT",
                            "Amount": amount,
                            "Transaction ID": tx_id,
                            "UTR": utr
                        })

                    i += 1

    except Exception as e:
        print("❌ Error parsing PDF:", e)
        return

    if not transactions:
        print("❌ No transactions found! Check PDF format.")
        return

    df = pd.DataFrame(transactions)
    df.to_csv(output_csv, index=False)

    print(f"✅ Parsed {len(df)} transactions → {output_csv}")


# ==============================
# 3. CLASSIFY (Google Search)
# ==============================
def classify_first_n_recipients_via_google(csv_path, output_csv, max_rows=60):
    print("📂 Reading CSV:", csv_path)

    # ✅ Safety checks
    if not os.path.exists(csv_path):
        print("❌ CSV file not found!")
        return

    if os.stat(csv_path).st_size == 0:
        print("❌ CSV file is empty!")
        return

    try:
        df = pd.read_csv(
            csv_path,
            engine='python',
            quotechar='"',
            skipinitialspace=True
        )
    except Exception as e:
        print("❌ Error reading CSV:", e)
        return

    if df.empty:
        print("❌ DataFrame is empty!")
        return

    df = df.head(max_rows).copy()

    if "Recipient_Type" not in df.columns:
        df["Recipient_Type"] = ""

    if "Location_URL" not in df.columns:
        df["Location_URL"] = ""

    for idx, row in df.iterrows():
        recipient = str(row["Recipient"]).strip()

        print(f"\n🔍 Searching: {recipient}")

        found_location = False
        found_url = None

        try:
            results = list(search(f'"{recipient}"', num_results=5))

            for url in results:
                if any(domain in url for domain in [
                    "google.com/maps",
                    "justdial.com",
                    "zomato.com",
                    "swiggy.com",
                    "restaurant",
                    "hotel",
                    "mall"
                ]):
                    found_location = True
                    found_url = url
                    break

        except Exception as e:
            print(f"❌ Error for {recipient}: {e}")
            continue

        df.at[idx, "Recipient_Type"] = "location" if found_location else "person"
        df.at[idx, "Location_URL"] = found_url if found_location else None

        time.sleep(random.uniform(2, 4))  # faster

    df.to_csv(output_csv, index=False)

    print(f"✅ Final CSV saved → {output_csv}")


# ==============================
# 4. MAIN PIPELINE
# ==============================
def process_pdf(pdf_path):
    print("\n🚀 Starting processing...\n")

    os.makedirs("outputs", exist_ok=True)

    parsed_csv = os.path.join("outputs", "upi_parsed.csv")
    final_csv = os.path.join("outputs", "upi_first60_with_location.csv")

    # Step 1: Parse PDF
    parse_phonepe_statement(pdf_path, parsed_csv)

    # Step 2: Validate CSV
    if not os.path.exists(parsed_csv) or os.stat(parsed_csv).st_size == 0:
        print("❌ Parsing failed → CSV empty")
        return

    # Step 3: Classify
    classify_first_n_recipients_via_google(parsed_csv, final_csv)

    print("\n🎉 DONE! Check outputs folder.\n")