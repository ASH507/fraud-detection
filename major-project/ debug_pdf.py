import pdfplumber
import os

for f in os.listdir("uploads"):
    if f.endswith(".pdf"):
        print(f"Reading: {f}")
        with pdfplumber.open(f"uploads/{f}") as pdf:
            for i, page in enumerate(pdf.pages[:2]):
                text = page.extract_text()
                print(f"\n--- PAGE {i+1} ---")
                if text:
                    for j, line in enumerate(text.splitlines()[:40]):
                        print(f"{j}: {line}")
                else:
                    print("(no text)")
        break