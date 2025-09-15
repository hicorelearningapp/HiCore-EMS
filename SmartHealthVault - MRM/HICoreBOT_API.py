# -*- coding: utf-8 -*-
"""HICoreBOT_API.py
API version of HICoreBOT_ALLFeatures
"""

import os
import io
import json
import faiss
import numpy as np
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from sentence_transformers import SentenceTransformer
from langdetect import detect, DetectorFactory
from unstructured.partition.auto import partition
import pytesseract
from PIL import Image
import fitz
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from openai import AzureOpenAI

# ========== CONFIG ==========
DetectorFactory.seed = 0

os.environ["AZURE_OPENAI_API_KEY"] = "G3AKaFyet7mSiT9cDWoxol7bpTfQ9U91IrWUiD1mvgNtNL37KNfEJQQJ99BHACHYHv6XJ3w3AAAAACOGaDFv"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://hicor-megtc6ig-eastus2.cognitiveservices.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2025-01-01-preview"  # ✅ base URL only
deployment_name = "gpt-4"

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version="2025-01-01-preview"
)

# ========== GLOBAL STATE ==========
processed_text = None
text_chunks = None
text_embeddings = None
faiss_index = None
summaries = {"short": None, "detailed": None}
generated_questions = {"mcq": [], "descriptive": []}
asked_questions = []   # ✅ added
document_metadata = {"title": "N/A", "author": "N/A", "upload_date": "N/A", "language": "N/A"}

# ========== HELPERS ==========
def extract_text_with_unstructured(file_path):
    elements = partition(filename=file_path)
    return "\n".join([el.text for el in elements if el.text])

def extract_and_ocr_images_from_pdf(file_path):
    ocr_text = ""
    doc = fitz.open(file_path)
    for i, page in enumerate(doc):
        for j, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n > 4:
                pix0 = fitz.Pixmap(fitz.csGRAY, pix)
            else:
                pix0 = pix
            img_path = f"temp_{i}_{j}.png"
            pix0.save(img_path)
            ocr_text += pytesseract.image_to_string(Image.open(img_path))
            os.remove(img_path)
    return ocr_text

def detect_language_with_fallback(text):
    try:
        return detect(text) if text.strip() else "Unknown"
    except Exception:
        return "Unknown"

def call_azure_openai_api(prompt, max_tokens=512, temperature=0.7):
    response = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "system", "content": "You are a helpful assistant. Respond in JSON when asked for questions."},
                  {"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content

def safe_json_parse(output):
    try:
        return json.loads(output)
    except Exception:
        return output

# ========== FASTAPI APP ==========
app = FastAPI(title="HICoreBOT API", description="AI-powered Document Processing & QnA API")

@app.post("/process_document")
async def process_document(file: UploadFile, encoding: str = Form("Auto-Detect")):
    global processed_text, text_chunks, faiss_index, document_metadata
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        text = extract_text_with_unstructured(file_path)
        if file.filename.endswith(".pdf"):
            text += extract_and_ocr_images_from_pdf(file_path)

        processed_text = text
        detected_lang = detect_language_with_fallback(text[:2000])
        document_metadata.update({"title": file.filename, "upload_date": "Today", "language": detected_lang})

        # Chunking + embeddings
        chunk_size = 500
        text_chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        model = SentenceTransformer("all-MiniLM-L6-v2")
        text_embeddings = model.encode(text_chunks)
        faiss_index = faiss.IndexFlatL2(text_embeddings.shape[1])
        faiss_index.add(np.array(text_embeddings).astype('float32'))

        return {"status": "success", "title": file.filename, "language": detected_lang}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/summary/{summary_type}")
async def generate_summary(summary_type: str):
    if processed_text is None:
        return {"error": "Upload and process a document first"}
    prompt = f"Create a {'concise (3-5 sentences)' if summary_type=='short' else 'detailed (2-3 paragraphs)'} summary:\n{processed_text[:3000]}"
    summary = call_azure_openai_api(prompt)
    summaries[summary_type] = summary
    return {"summary_type": summary_type, "summary": summary}

@app.post("/generate_questions")
async def generate_questions(levels: str = Form("Basic-2, Intermediate-2, Advanced-1")):
    global generated_questions
    if processed_text is None:
        return {"error": "Upload and process a document first"}
    
    for part in levels.split(","):
        level, count = part.strip().split("-")
        prompt = f"Generate {count} {level} multiple-choice and descriptive questions in JSON with fields: mcq=[{{question, options, answer, explanation}}], descriptive=[{{question, answer}}]. Source:\n{processed_text[:4000]}"
        output = call_azure_openai_api(prompt)
        parsed = safe_json_parse(output)

        if isinstance(parsed, dict):
            if "mcq" in parsed:
                generated_questions["mcq"].extend(parsed["mcq"])
            if "descriptive" in parsed:
                generated_questions["descriptive"].extend(parsed["descriptive"])
        else:
            generated_questions["descriptive"].append({"question": f"{level} output", "answer": output})

    # ✅ Return updated stored questions
    return {
        "status": "questions added",
        "total_mcq": len(generated_questions["mcq"]),
        "total_descriptive": len(generated_questions["descriptive"]),
        "latest_mcq": generated_questions["mcq"][-3:],   # last 3 MCQs
        "latest_descriptive": generated_questions["descriptive"][-3:]  # last 3 descriptives
    }

@app.post("/ask")
async def ask_question(query: str = Form(...)):
    global asked_questions
    if faiss_index is None:
        return {"error": "No document processed"}
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_emb = model.encode([query])
    _, idx = faiss_index.search(np.array(query_emb).astype('float32'), 3)
    context = "\n".join([text_chunks[i] for i in idx[0]])
    prompt = f"Answer using this context only:\n{context}\nQ: {query}\nA:"
    answer = call_azure_openai_api(prompt)
    asked_questions.append({"question": query, "answer": answer})
    return {"answer": answer}

@app.get("/report")
async def get_report():
    if processed_text is None:
        return {"error": "No document processed"}

    report_path = "report.pdf"
    doc = SimpleDocTemplate(report_path, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, spaceAfter=12)
    story = [Paragraph("AI Document Processing Report", title_style)]
    story.append(Spacer(1, 12))

    # ===== Summaries =====
    if summaries.get("short"):
        story.append(Paragraph("Short Summary:", styles['Heading2']))
        story.append(Paragraph(summaries["short"], styles['Normal']))
        story.append(Spacer(1, 12))
    if summaries.get("detailed"):
        story.append(Paragraph("Detailed Summary:", styles['Heading2']))
        story.append(Paragraph(summaries["detailed"], styles['Normal']))
        story.append(Spacer(1, 12))

    # ===== Generated Questions =====
    if generated_questions["mcq"] or generated_questions["descriptive"]:
        story.append(Paragraph("Generated Questions", styles['Heading2']))

        if generated_questions["mcq"]:
            story.append(Paragraph("MCQs", styles['Heading3']))
            for i, mcq in enumerate(generated_questions["mcq"], 1):
                story.append(Paragraph(f"Q{i}: {mcq.get('question','')}", styles['Normal']))
                if mcq.get("options"):
                    story.append(ListFlowable([ListItem(Paragraph(opt, styles['Normal'])) for opt in mcq["options"]], bulletType="bullet"))
                if mcq.get("answer"):
                    story.append(Paragraph(f"Answer: {mcq['answer']}", styles['Normal']))
                if mcq.get("explanation"):
                    story.append(Paragraph(f"Explanation: {mcq['explanation']}", styles['Normal']))
                story.append(Spacer(1, 6))

        if generated_questions["descriptive"]:
            story.append(Paragraph("Descriptive Questions", styles['Heading3']))
            for i, desc in enumerate(generated_questions["descriptive"], 1):
                story.append(Paragraph(f"Q{i}: {desc.get('question','')}", styles['Normal']))
                if desc.get("answer"):
                    story.append(Paragraph(f"Answer: {desc['answer']}", styles['Normal']))
                story.append(Spacer(1, 6))

    # ===== Asked Questions =====
    if asked_questions:
        story.append(Paragraph("Asked Questions", styles['Heading2']))
        for i, qa in enumerate(asked_questions, 1):
            story.append(Paragraph(f"Q{i}: {qa['question']}", styles['Normal']))
            story.append(Paragraph(f"A: {qa['answer']}", styles['Normal']))
            story.append(Spacer(1, 6))

    doc.build(story)
    return FileResponse(report_path, filename="report.pdf", media_type="application/pdf")

@app.post("/clear")
async def clear_state():
    global processed_text, text_chunks, text_embeddings, faiss_index, summaries, generated_questions, asked_questions, document_metadata
    processed_text = None
    text_chunks = None
    text_embeddings = None
    faiss_index = None
    summaries = {"short": None, "detailed": None}
    generated_questions = {"mcq": [], "descriptive": []}
    asked_questions = []
    document_metadata = {"title": "N/A", "author": "N/A", "upload_date": "N/A", "language": "N/A"}
    return {"status": "cleared"}