# 📊 UPI PDF Statement Analyzer

This project allows users to upload their PhonePe/UPI transaction statement in PDF format and automatically generates:

- ✅ A cleaned CSV file (`upi_first60_with_location.csv`)
- 🧾 A PDF Summary report (`upi_summary.pdf`)
- 🌐 A PDF of Recipient Location URLs (`upi_location_urls.pdf`)

---

## 🔧 How It Works

1. Upload your UPI transaction PDF via the web interface.
2. The backend (built with Flask) processes the PDF:
   - Extracts transaction info
   - Classifies top recipients by type (person/place)
   - Searches for location URLs (JustDial/Zomato/etc.)
3. Generates downloadable files:
   - Parsed CSV
   - Transaction summary PDF
   - Location URLs PDF
     
<img width="308" height="175" alt="image" src="https://github.com/user-attachments/assets/84607998-e01a-4078-8ee3-8d4473fd61bd" />


---

## 🚀 How to Use

### 1. Clone the Repo

```bash
git clone https://github.com/AdiK10/SBI_Hackathon.git
cd SBI_Hackathon
# SBI_Hackathon
2. Install Dependencies
Use pip to install required packages:

bash
Copy
Edit
pip install -r requirements.txt

python app.py
