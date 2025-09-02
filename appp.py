import streamlit as st
import re
import io
from reportlab.pdfgen import canvas
import fitz  # PyMuPDF
import easyocr

# --- Streamlit page setup ---
st.set_page_config(page_title="MediCloak", page_icon="🛡")
st.title("🛡 MediCloak - AI Privacy Protector")
st.markdown("""
MediCloak detects and hides private details in medical text.  
Upload a PDF or Image, and it will redact sensitive info like *names, phone numbers, emails, IDs, dates, addresses, insurance details, MRNs, and emergency contacts*.
""")

# --- Extra keywords for address & names ---
ADDRESS_KEYWORDS = [
    "street", "road", "nagar", "colony", "hospital", 
    "clinic", "avenue", "lane", "block", "chennai", "delhi", "bangalore", "mumbai"
]

NAME_KEYWORDS = [
    "ramesh", "kumar", "sujatha", "raj", "anita", "arun"
]

# --- Dictionary-based redaction ---
def dictionary_redact(t: str) -> str:
    for word in ADDRESS_KEYWORDS:
        t = re.sub(rf"\b{word}\b", "[REDACTED ADDRESS]", t, flags=re.IGNORECASE)
    for word in NAME_KEYWORDS:
        t = re.sub(rf"\b{word}\b", "[REDACTED NAME]", t, flags=re.IGNORECASE)
    return t

# --- Regex redaction for structured PII ---
def regex_redact(t: str) -> str:
    if not t:
        return t

    t = re.sub(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', "[REDACTED EMAIL]", t)
    t = re.sub(r'\b(?:\+91[-\s]?|0)?\d{10}\b', "[REDACTED PHONE]", t)
    t = re.sub(r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', "[REDACTED PHONE]", t)
    t = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', "[REDACTED AADHAAR]", t)
    t = re.sub(r'\b[A-Z]{5}\d{4}[A-Z]\b', "[REDACTED PAN]", t)
    t = re.sub(r'\b\d{6}\b', "[REDACTED PIN]", t)
    t = re.sub(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', "[REDACTED DATE]", t)
    t = re.sub(r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b', "[REDACTED DATE]", t)
    t = re.sub(r'\b(?:\+91[-\s]?|0)?\d{5,10}\b', "[REDACTED PHONE]", t)
    t = re.sub(r'\bINS\d+\b', "[REDACTED INSURANCE ID]", t, flags=re.IGNORECASE)
    t = re.sub(r'\bMRN[-]?\d+\b', "[REDACTED MRN]", t, flags=re.IGNORECASE)
    return t

# --- Combined redaction ---
def redact(t: str) -> str:
    t = regex_redact(t)
    t = dictionary_redact(t)
    return t

# --- Extract text from PDF ---
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- Extract text from Image ---
reader = easyocr.Reader(['en'])
def extract_text_from_image(image_file):
    result = reader.readtext(image_file.read(), detail=0)
    return "\n".join(result)

# --- Create downloadable PDF ---
def create_pdf(text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    for i, line in enumerate(text.split('\n')):
        c.drawString(50, 800 - 15*i, line)
    c.save()
    buffer.seek(0)
    return buffer

# --- File uploader ---
uploaded_file = st.file_uploader("📂 Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    # Extract text
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    else:
        extracted_text = extract_text_from_image(uploaded_file)

    # Redact
    redacted_text = redact(extracted_text)

    st.subheader("🔹 Extracted Text")
    st.write(extracted_text)

    st.subheader("🔹 Redacted Text")
    st.success(redacted_text)

    # Download options
    st.download_button(
        label="📥 Download Redacted Text",
        data=redacted_text,
        file_name="redacted.txt",
        mime="text/plain"
    )

    pdf_buffer = create_pdf(redacted_text)
    st.download_button(
        label="📥 Download Redacted PDF",
        data=pdf_buffer,
        file_name="redacted.pdf",
        mime="application/pdf"
    )

# Footer
st.markdown("---")
st.caption("Made with ❤ by Team MediCloak | Hackathon Prototype")