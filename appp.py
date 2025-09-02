import streamlit as st
from fpdf import FPDF
import os

# Function to create PDF with text and optional image
def create_pdf(text, image_file=None, filename="output.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add text
    pdf.multi_cell(0, 10, text)

    # Add image if uploaded
    if image_file:
        image_path = "temp_image.png"
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())
        pdf.image(image_path, x=10, y=pdf.get_y() + 10, w=100)
        os.remove(image_path)

    pdf.output(filename)
    return filename

# Streamlit app
st.title("📄 PDF Generator App")

user_text = st.text_area("✍ Enter text for the PDF:")

uploaded_image = st.file_uploader("📷 Upload an image (optional)", type=["png", "jpg", "jpeg"])

if st.button("Generate PDF"):
    if user_text.strip():
        pdf_file = create_pdf(user_text, uploaded_image, "generated.pdf")
        with open(pdf_file, "rb") as f:
            st.download_button("⬇ Download PDF", f, file_name="generated.pdf")
    else:
        st.warning("⚠ Please enter some text before generating the PDF.")