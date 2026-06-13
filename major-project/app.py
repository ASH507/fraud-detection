from flask import Flask, render_template, request, send_file
import os
from generate_reports import generate_summary_pdf, generate_location_url_pdf
import process_notebook

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            # Save uploaded file
            pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(pdf_path)

            # Run processing
            process_notebook.process_pdf(pdf_path)

            # Paths to output files
            csv_filename = "upi_first60_with_location.csv"
            summary_filename = "upi_summary.pdf"
            location_filename = "upi_location_urls.pdf"

            csv_path = os.path.join(OUTPUT_FOLDER, csv_filename)
            summary_pdf = os.path.join(OUTPUT_FOLDER, summary_filename)
            location_pdf = os.path.join(OUTPUT_FOLDER, location_filename)

            # Generate PDFs
            generate_summary_pdf(csv_path, summary_pdf)
            generate_location_url_pdf(csv_path, location_pdf)

            return render_template(
                "index.html",
                csv_path=csv_filename,
                summary_path=summary_filename,
                locations_path=location_filename,
            )

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
