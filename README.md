# RESUME-REVIEW-PRO
Resume Review Pro is an AI-powered tool designed to automate and enhance the resume evaluation process. Using Google Gemini AI and Natural Language Processing (NLP), the system allows job seekers to upload resumes in PDF format and receive an AI-driven analysis. The tool extracts key information such as skills, experience, and education from resumes, provides recommendations for improvement, and compares the resume against a provided job description to help job seekers better align their profiles with specific job roles.

Features
Text Extraction:

Supports text-based PDFs and image-based PDFs (using OCR technology via pytesseract) for text extraction.

AI-Powered Evaluation:

Identifies skills present in the resume and suggests additional ones to enhance the profile.

Provides insights into strengths and weaknesses based on the resume’s content.

Compares the resume against an optional job description to assess alignment.

Job Seeker Support:

Recommends courses to improve missing skills.

Offers actionable suggestions for resume enhancement.

Recruiter Efficiency:

Automates initial resume screening, reducing manual review time.

Ensures an objective and unbiased evaluation of resumes.

Technologies Used
Google Gemini AI: For resume analysis, skill identification, and job description comparison.

Streamlit: A user-friendly framework for building the web interface.

PDFPlumber: Extracts text from text-based PDFs.

PyTesseract & pdf2image: For OCR to handle image-based PDFs.

Python-dotenv: Loads environment variables securely.
