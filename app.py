import gradio as gr
import os
from datetime import datetime
from fpdf import FPDF
from groq import Groq  # Groq client
import unicodedata  # ✅ For cleaning Unicode text
import tempfile

# Load Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# 🔧 Prompt builder
def build_prompt(images, client_name, location, date, report_type, notes):
    img_note = "Images of damage were uploaded." if images else "No images provided."
    if report_type == "Statement of Work":
        prompt = (
            f"You are a structural forensic engineer.\n\n"
            f"Generate a detailed {report_type} based on the following:\n"
            f"- Client Name: {client_name}\n"
            f"- Location: {location}\n"
            f"- Inspection Date: {date}\n"
            f"- Observations: {notes}\n"
            f"- {img_note}\n\n"
            f"Write in a professional tone suitable for insurance claims and contractors.\n"
            f"Organize into sections: A. Instructions, B. General Notes, C. Relevant Australian Standards, "
            f"D. Preliminaries, E. Demolition, F. Remediation and Reconstruction, G. Appendix A – Photographic Commentary."
        )
        return prompt
    else:
        prompt = (
            f"You are a structural forensic engineer.\n\n"
            f"Generate a detailed {report_type} based on the following:\n"
            f"- Client Name: {client_name}\n"
            f"- Location: {location}\n"
            f"- Inspection Date: {date}\n"
            f"- Observations: {notes}\n"
            f"- {img_note}\n\n"
            f"Write in a professional tone suitable for insurance claims and contractors.\n"
            f"Organize into sections: A. Instructions (State the commissioning entity, the purpose of the inspection, and the date of site attendance), "
            f"B. General Notes (Briefly describe the nature of the damage), C. Observations (Provide a descriptive assessment of the damage visible in the supplied photographs and the effect of this damage on the structural integritry of the structure), "
            f"D. Discussion, E. Conclusion, F. Limitations to the Report."
        )
        return prompt
# 🤖 Groq-based report generation
def generate_report(images, client_name, location, date, report_type, notes):
    if not all([client_name, location, date, report_type]):
        return "⚠️ Please fill out all fields."
    
    prompt = build_prompt(images, client_name, location, date, report_type, notes)
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a structural forensic engineering assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error generating report: {str(e)}"

# 🧼 Clean Unicode text
def clean_text(text):
    # Normalize and strip non-ASCII characters
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    
# 🧾 Export to PDF (with safe text)
def export_to_pdf(text):
    text = clean_text(text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    # ✅ Create a temporary file and return its path
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name


# 🎛️ Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# 🏚️ ForensiGen – AI Forensic Report Generator")

    with gr.Row():
        images = gr.File(label="Upload Damage Images", file_types=["image"], file_count="multiple")
        report_type = gr.Dropdown(choices=["Statement of Work", "Causation Report"], label="Report Type")

    with gr.Row():
        client_name = gr.Textbox(label="Client Name")
        location = gr.Textbox(label="Location")
        date = gr.Textbox(label="Inspection Date (e.g., 2025-05-17)")

    notes = gr.Textbox(label="Additional Observations", lines=4, placeholder="Describe what was observed on-site... (Optional)")

    generate_btn = gr.Button("🔍 Generate Report")
    report_output = gr.Textbox(label="Generated Report", lines=20)
    download_btn = gr.Button("⬇️ Export as PDF")
    file_output = gr.File(label="Download PDF",  file_types=[".pdf"])

    generate_btn.click(fn=generate_report,
                       inputs=[images, client_name, location, date, report_type, notes],
                       outputs=report_output)

    download_btn.click(fn=export_to_pdf, 
                       inputs=report_output, 
                       outputs=file_output)

demo.launch()
