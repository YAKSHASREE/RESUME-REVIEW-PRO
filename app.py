
import os
import io
import time
import streamlit as st
import pdfplumber
import pytesseract
from dotenv import load_dotenv
from pdf2image import convert_from_bytes
from google import genai
from google.genai import errors

load_dotenv()
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-3.8-flash"

if not GOOGLE_API_KEY:
    st.error("Google Gemini API key is missing. Configure GOOGLE_API_KEY in Render.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)

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
            images = convert_from_bytes(pdf_bytes)
            extracted_text = ""
            for image in images:
                extracted_text += pytesseract.image_to_string(image) + "\n"
        if not extracted_text.strip():
            raise ValueError("No readable text found in the PDF.")
        return extracted_text
    except Exception as e:
        raise Exception(f"PDF extraction failed: {str(e)}")

def analyze_resume(resume_text, job_description):
    prompt = f"""
You are an experienced technical recruiter and professional resume evaluator.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Analyze the resume against the job description and provide:

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

Be realistic and objective. Do not invent qualifications or experience.
Use clear headings and bullet points.
"""
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            if not response.text:
                raise ValueError("Gemini returned an empty response.")
            return response.text
        except errors.APIError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(5 * (2 ** attempt))
            else:
                raise
    raise Exception("Gemini could not complete the analysis. Please try again later.")

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and enter a job description to receive an AI-powered resume evaluation.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume in PDF format", type=["pdf"])

with col2:
    st.subheader("Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=250,
        placeholder="Enter the job requirements and responsibilities..."
    )

st.divider()

if st.button("🚀 Analyze Resume", use_container_width=True):
    if uploaded_file is None:
        st.warning("Please upload your resume PDF.")
    elif not job_description.strip():
        st.warning("Please enter the job description.")
    else:
        try:
            with st.spinner("Extracting resume information..."):
                resume_text = extract_resume_text(uploaded_file)
            with st.spinner("Analyzing resume using Gemini AI..."):
                analysis = analyze_resume(resume_text, job_description)
            st.success("Resume analysis completed successfully!")
            st.subheader("📊 Resume Analysis Results")
            st.markdown(analysis)
            st.download_button(
                "📥 Download Analysis",
                data=analysis,
                file_name="resume_analysis.txt",
                mime="text/plain"
            )
        except errors.APIError as e:
            if e.code == 503:
                st.error("Gemini servers are experiencing high demand. Please try again later.")
            elif e.code == 429:
                st.error("Gemini API quota or rate limit reached. Check your API usage.")
            elif e.code == 403:
                st.error("API access denied. Check your Google Cloud project status.")
            else:
                st.error(f"Gemini API Error: {e}")
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

st.divider()
st.markdown(
    "<center>Developed using Python, Streamlit and Google Gemini AI</center>",
    unsafe_allow_html=True
)
