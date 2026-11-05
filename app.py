
import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("Google Gemini API key is missing. Configure it in Render.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)


# Extract text from PDF
def extract_text_from_pdf(pdf_path):

    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        if text.strip():
            return text.strip()

    except Exception as e:
        st.warning(f"Direct PDF extraction failed: {e}")

    # OCR fallback
    try:
        images = convert_from_path(pdf_path)

        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"

    except Exception as e:
        st.error(f"OCR failed: {e}")

    return text.strip()


# Analyze resume using Gemini
def analyze_resume(resume_text, job_description=None):

    if not resume_text:
        return "Resume text is required for analysis."

    prompt = f"""
    You are an experienced technical HR professional.

    Analyze the candidate's resume for suitable roles such as:

    Data Scientist, Data Analyst, Machine Learning Engineer,
    AI Engineer, Software Developer, DevOps Engineer,
    Full Stack Developer and other relevant technical roles.

    Provide the following:

    1. Overall resume evaluation.
    2. Suitable job roles.
    3. Existing technical skills.
    4. Strengths of the candidate.
    5. Weaknesses and missing skills.
    6. Skills to improve.
    7. Recommended courses.
    8. Resume improvement suggestions.

    Resume:
    {resume_text}
    """

    if job_description:

        prompt += f"""

        Compare the resume with the following job description.

        Job Description:
        {job_description}

        Provide:

        1. Matching skills.
        2. Missing skills.
        3. Job requirements satisfied.
        4. Areas requiring improvement.
        5. Overall job suitability.

        """

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    return response.text or "No analysis generated."


# Streamlit application
st.set_page_config(
    page_title="Resume Analyzer",
    layout="wide"
)

st.title("AI Resume Analyzer")

st.write(
    "Analyze your resume and match it with job descriptions "
    "using Google Gemini AI."
)

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"]
    )

with col2:
    job_description = st.text_area(
        "Enter Job Description:",
        placeholder="Paste the job description here..."
    )


if uploaded_file is not None:

    st.success("Resume uploaded successfully!")

    if st.button("Analyze Resume"):

        with st.spinner("Analyzing your resume..."):

            try:
                # Save uploaded PDF temporarily
                with open("uploaded_resume.pdf", "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Extract resume text
                resume_text = extract_text_from_pdf(
                    "uploaded_resume.pdf"
                )

                if not resume_text:
                    st.error(
                        "Could not extract text from the PDF. "
                        "Please upload another PDF."
                    )

                else:
                    # Analyze using Gemini
                    analysis = analyze_resume(
                        resume_text,
                        job_description
                    )

                    st.success("Analysis completed!")

                    st.subheader("Resume Analysis")

                    st.markdown(analysis)

            except Exception as e:
                st.error(f"Analysis failed: {e}")

else:
    st.warning("Please upload a resume in PDF format.")


# Footer
st.markdown("---")

st.markdown(
    """
    <p style='text-align: center;'>
    Powered by <b>Streamlit</b> and <b>Google Gemini AI</b>
    </p>
    """,
    unsafe_allow_html=True
)
