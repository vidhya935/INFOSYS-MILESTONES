# ==========================================
# SkillGapAI - Milestone 3 (Debugged Version)
# Skill Gap Analysis & Similarity Matching
# ==========================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sentence_transformers import SentenceTransformer, util

# ------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------
st.set_page_config(page_title="SkillGapAI - Milestone 3", layout="wide")

st.markdown(
    """
    <h2 style='color:white; background-color:#5B2C6F; padding:15px; border-radius:10px'>
    🧠 SkillGapAI - Milestone 3: Skill Gap Analysis & Similarity Matching
    </h2>
    <p><b>Objective:</b> Compare candidate and job skills using BERT embeddings using cosine similarity.
    </p>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------
# LOAD MODEL
# ------------------------------------------
@st.cache_resource
def load_model():
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        st.error(f"Model loading failed: {e}")
        return None

model = load_model()


# ------------------------------------------
# SKILL INPUTS
# ------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👨‍💻 Resume Skills")
    resume_skills_input = st.text_area(
        "Enter resume skills (comma-separated):",
        "Python, SQL, Machine Learning, Tableau"
    )

with col2:
    st.markdown("### 🏢 Job Description Skills")
    jd_skills_input = st.text_area(
        "Enter job skills (comma-separated):",
        "Python, Data Visualization, Deep Learning, Communication, AWS"
    )

resume_skills = [s.strip() for s in resume_skills_input.split(",") if s.strip()]
jd_skills = [s.strip() for s in jd_skills_input.split(",") if s.strip()]

# Stop if model did not load
if model is None:
    st.stop()


# ------------------------------------------
# SIMILARITY COMPUTATION
# ------------------------------------------
if resume_skills and jd_skills:

    st.markdown("---")
    st.header("🔍 Skill Gap Analysis")

    # Encode text
    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)

    # Cosine similarity matrix
    similarity_matrix = util.cos_sim(resume_embeddings, jd_embeddings).cpu().numpy()

    # Convert matrix to DF
    sim_df = pd.DataFrame(similarity_matrix, index=resume_skills, columns=jd_skills)

    # --------------------------------------
    # CLASSIFY SKILLS
    # --------------------------------------
    matched_skills = []
    partial_skills = []
    missing_skills = []

    for skill in jd_skills:
        max_sim = sim_df[skill].max()

        if max_sim >= 0.80:
            matched_skills.append(skill)
        elif max_sim >= 0.50:
            partial_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Calculate match %
    overall_match = (
        (len(matched_skills) + 0.5 * len(partial_skills))
        / len(jd_skills)
    ) * 100

    # --------------------------------------
    # VISUALS
    # --------------------------------------
    colA, colB = st.columns([2, 1])

    with colA:
        st.subheader("📈 Skill Similarity Heatmap")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(sim_df, annot=True, fmt=".2f", cmap="YlGnBu", cbar=True)
        st.pyplot(fig)

    with colB:
        st.subheader("📊 Summary")
        st.metric("Matched Skills", len(matched_skills))
        st.metric("Partial Skills", len(partial_skills))
        st.metric("Missing Skills", len(missing_skills))
        st.metric("Overall Match", f"{overall_match:.2f}%")

        # Pie chart
        labels = ["Matched", "Partial", "Missing"]
        sizes = [len(matched_skills), len(partial_skills), len(missing_skills)]

        fig2, ax2 = plt.subplots(figsize=(3, 3))
        ax2.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax2.axis("equal")
        st.pyplot(fig2)

    # Missing Skills
    st.markdown("---")
    st.subheader("❌ Missing Skills")
    if missing_skills:
        for s in missing_skills:
            st.error("🚫 " + s)
    else:
        st.success("✨ No missing skills")

    # Detailed comparison table
    results = []
    for jd_skill in jd_skills:
        max_sim = sim_df[jd_skill].max()
        best_match = sim_df[jd_skill].idxmax()
        results.append({
            "Job Skill": jd_skill,
            "Closest Resume Skill": best_match,
            "Similarity (%)": round(max_sim * 100, 2)
        })

    st.markdown("---")
    st.subheader("📋 Detailed Table")
    st.dataframe(pd.DataFrame(results))


else:
    st.info("Please enter Resume & JD skills to start analysis.")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:gray;'>Milestone 3 – Skill Gap Analysis • SkillGapAI</p>",
    unsafe_allow_html=True
)
