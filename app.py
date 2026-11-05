
import os
import io
import streamlit as st
import pdfplumber
import pytesseract
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
from google import genai
from google.genai import types, errors

# Configuration
load_dotenv()
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3.8-flash"

if not GOOGLE_API_KEY:
    st.error("Gemini API key is missing. Configure GOOGLE_API_KEY in Render.")
    st.stop()

# Gemini client
client = genai.Client(
    api_key=GOOGLE_API_KEY,
    http_options=types.HttpOptions(timeout=60000)
)

# Extract text from PDF
def extract_resume_text(pdf_file):
    pdf_bytes = pdf_file.getvalue()
    extracted_text = ""

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"

        if len(extracted_text.strip()) < 50:
            st.info("Scanned PDF detected. Performing OCR...")
            images = convert_from_bytes(pdf_bytes, dpi=150)
            extracted_text = ""

            for image in images:
                extracted_text += pytesseract.image_to_string(image) + "\n"

        if not extracted_text.strip():
            raise ValueError("No readable text found in the PDF.")

        return extracted_text

    except Exception as e:
        raise Exception(f"PDF extraction failed: {e}")

# Analyze resume using Gemini
def analyze_resume(resume_text, job_description):
    prompt = f"""
You are an experienced technical recruiter and professional resume evaluator.

Analyze the candidate's resume against the job description.

RESUME:
{resume_text[:20000]}

JOB DESCRIPTION:
{job_description[:10000]}

Provide the following analysis:

1. Resume Summary
2. Job Match Percentage with explanation
3. Matching Technical and Soft Skills
4. Missing Skills
5. Candidate Strengths
6. Weaknesses and Improvement Areas
7. Project Evaluation
8. Education and Experience Evaluation
9. Specific Resume Improvement Suggestions
10. Ten Relevant Technical and HR Interview Questions

Instructions:
- Be realistic and objective.
- Do not invent qualifications or experience.
- Identify missing skills accurately.
- Use clear headings and bullet points.
- Keep the analysis detailed but concise.
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=3000
            )
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return response.text

    except errors.APIError as e:
        if e.code == 503:
            raise Exception("Gemini is currently experiencing high demand. Please try again later.")
        elif e.code == 429:
            raise Exception("API quota or rate limit reached. Check your Gemini API usage.")
        elif e.code == 403:
            raise Exception("API access denied. Check your Google Cloud project status.")
        elif e.code == 404:
            raise Exception("Model not found or unavailable. Check the model name in AI Studio.")
        else:
            raise Exception(f"Gemini API error ({e.code}): {e.message}")

# Application interface
st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and enter a job description to receive an AI-powered resume evaluation.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume in PDF format",
        type=["pdf"]
    )

with col2:
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Enter the job requirements and responsibilities..."
    )

st.divider()

# Analyze button
if st.button("🚀 Analyze Resume", use_container_width=True):
    if uploaded_file is None:
        st.warning("Please upload your resume PDF.")

    elif not job_description.strip():
        st.warning("Please enter the job description.")

    else:
        try:
            with st.status("Processing your resume...", expanded=True) as status:
                st.write("Step 1: Extracting resume information...")
                resume_text = extract_resume_text(uploaded_file)

                st.write("Step 2: Preparing resume and job description...")
                st.write("Step 3: Sending request to Gemini AI...")

                analysis = analyze_resume(resume_text, job_description)

                status.update(
                    label="Resume analysis completed!",
                    state="complete",
                    expanded=False
                )

            st.success("Analysis completed successfully!")
            st.subheader("📊 Resume Analysis Results")
            st.markdown(analysis)

            st.download_button(
                label="📥 Download Analysis",
                data=analysis,
                file_name="resume_analysis.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

# Footer
st.divider()
st.markdown(
    "<center>Developed using Python, Streamlit and Google Gemini AI</center>",
    unsafe_allow_html=True
)
