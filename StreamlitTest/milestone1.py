import re
import streamlit as st

# Try imports safely (so app won't crash if not installed)
try:
    import docx2txt
except ImportError:
    docx2txt = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


# ------------------------------------------
# PAGE CONFIG
# ------------------------------------------
st.set_page_config(page_title="SkillGapAI - Milestone 1", layout="wide")

st.markdown(
    """
    <h2 style='color:white; background-color:#1E3D59; padding:15px; border-radius:10px'>
    🧠 SkillGapAI - Milestone 1: Data Ingestion & Parsing
    </h2>
    <p><b>Objective:</b> Upload resumes / job descriptions, extract & clean text,
    preview parsed content, and download the cleaned data.</p>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------
# HELPERS
# ------------------------------------------
def clean_text(text: str) -> str:
    """Normalize text by removing extra spaces and line breaks."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = text.replace("\r", " ").replace("\n", " ")
    return text.strip()


def extract_text(uploaded_file) -> str:
    """Extract plain text from PDF, DOCX, or TXT."""
    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    try:
        # ---------- PDF ----------
        if filename.endswith(".pdf"):
            if PyPDF2 is None:
                st.error("❌ PyPDF2 not installed. Run: `pip install PyPDF2`")
                return ""
            text = ""
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content + "\n"
            return clean_text(text)

        # ---------- DOCX ----------
        elif filename.endswith(".docx"):
            if docx2txt is None:
                st.error("❌ docx2txt not installed. Run: `pip install docx2txt`")
                return ""
            text = docx2txt.process(uploaded_file)
            return clean_text(text)

        # ---------- TXT ----------
        elif filename.endswith(".txt"):
            data = uploaded_file.read()
            try:
                text = data.decode("utf-8")
            except Exception:
                text = data.decode("latin1", errors="ignore")
            return clean_text(text)

        else:
            st.error("❌ Unsupported file format. Use PDF, DOCX, or TXT.")
            return ""

    except Exception as e:
        st.error(f"⚠️ Error while extracting text: {e}")
        return ""


# ------------------------------------------
# LAYOUT
# ------------------------------------------
col1, col2 = st.columns([1.1, 2])

with col1:
    st.markdown("### 📤 Upload Resume or Job Description")
    uploaded_file = st.file_uploader(
        "Choose a file (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
    )
    st.info("Supported formats: PDF • DOCX • TXT")

with col2:
    st.markdown("### 🧾 Parsed Document Preview")

    if uploaded_file is not None:
        with st.spinner("🔍 Extracting and cleaning text..."):
            extracted_text = extract_text(uploaded_file)

        if extracted_text:
            st.success(f"✅ Successfully parsed: {uploaded_file.name}")

            st.text_area(
                "Extracted & Cleaned Text",
                value=extracted_text[:4000],
                height=350,
            )
            st.caption(
                f"Characters: {len(extracted_text)} | "
                f"Words: {len(extracted_text.split())}"
            )

            # Download button
            st.download_button(
                label="💾 Download Parsed Text",
                data=extracted_text,
                file_name=f"parsed_{uploaded_file.name.split('.')[0]}.txt",
                mime="text/plain",
            )
        else:
            st.warning("No text could be extracted from this file.")
    else:
        st.warning("Upload a file to see the parsed preview here.")


# ------------------------------------------
# MANUAL JOB DESCRIPTION SECTION
# ------------------------------------------
st.markdown("---")
st.subheader("📋 Paste Job Description (Optional)")

jd_text = st.text_area("Paste Job Description here:", "", height=200)

if jd_text.strip():
    cleaned_jd = clean_text(jd_text)
    st.text_area("Cleaned Job Description Output", cleaned_jd, height=200)
    st.caption(
        f"Characters: {len(cleaned_jd)} | Words: {len(cleaned_jd.split())}"
    )

    st.download_button(
        label="💾 Download Cleaned Job Description",
        data=cleaned_jd,
        file_name="cleaned_job_description.txt",
        mime="text/plain",
    )


# ------------------------------------------
# FOOTER
# ------------------------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>Milestone 1 • Data Ingestion & Parsing • "
    "SkillGapAI Project • Developed by Suriya Varshan</p>",
    unsafe_allow_html=True,
)
