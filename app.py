import gradio as gr
from huggingface_hub import InferenceClient
from fpdf import FPDF
import os
from datetime import datetime

hf_token = os.getenv("HF_TOKEN")
client = InferenceClient(model="mistralai/Mixtral-8x7B-Instruct-v0.1", token=hf_token)

def build_prompt(images, client_name, location, date, report_type, notes):
    img_note = "Images of damage were uploaded." if images else "No images provided."
    prompt = (
        f"<s>[INST] You are a structural forensic engineer.\n\n"
        f"Generate a detailed {report_type} based on the following:\n"
        f"- Client Name: {client_name}\n"
        f"- Location: {location}\n"
        f"- Inspection Date: {date}\n"
        f"- Observations: {notes}\n"
        f"- {img_note}\n\n"
        f"Write in a professional tone suitable for insurance claims and contractors.\n"
        f"Organize into sections: Summary, Observations, Damage Assessment, Reference to Building Codes and Recommendations."
        f" [/INST]"
    )
    return prompt

def generate_report(images, client_name, location, date, report_type, notes):
    if not all([client_name, location, date, report_type]):
        return "Please fill out all fields."
    prompt = build_prompt(images, client_name, location, date, report_type, notes)
    response = client.text_generation(prompt, max_new_tokens=1024, temperature=0.4)
    return response.strip()

def export_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)
    filename = f"forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

with gr.Blocks() as demo:
    gr.Markdown("# 🏚️ GenAI Forensic Report Generator")

    with gr.Row():
        images = gr.File(label="Upload Damage Images", file_types=["image"], file_count="multiple")
        report_type = gr.Dropdown(choices=["Statement of Work", "Causation Report"],
                                  label="Report Type")
    with gr.Row():
        client_name = gr.Textbox(label="Client Name")
        location = gr.Textbox(label="Location")
        date = gr.Textbox(label="Inspection Date (e.g., 2025-05-16)")

    notes = gr.Textbox(label="Additional Observations", lines=4, placeholder="Describe what was observed on-site...")

    generate_btn = gr.Button("🔍 Generate Report")
    report_output = gr.Textbox(label="Generated Report", lines=20)
    download_btn = gr.Button("⬇️ Export as PDF")
    file_output = gr.File(label="Download PDF")

    generate_btn.click(fn=generate_report,
                       inputs=[images, client_name, location, date, report_type, notes],
                       outputs=report_output)

    download_btn.click(fn=export_to_pdf, inputs=report_output, outputs=file_output)

demo.launch()
