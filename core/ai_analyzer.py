import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_resource
def load_model():
    """
    Load the sentence-transformer model once per Streamlit server session.
    Streamlit reuses the cached model on later reruns.
    """
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model


def split_text(text, chunk_size=150):
    """
    Split long text into smaller chunks so that the model can compare
    different parts of a resume and job description.
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def calculate_similarity(resume_text, job_description):
    """
    Calculate semantic alignment from the job description's perspective.

    Each job-description chunk is compared with all resume chunks.
    We take the best resume match for each job-description chunk, then
    average those best matches.

    The returned value is a semantic similarity indicator, not a hiring
    probability or a validated measure of job suitability.
    """

    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    # 1. Load the sentence-transformer model.
    model = load_model()

    # 2. Divide both documents into smaller chunks.
    resume_chunks = split_text(resume_text)
    job_chunks = split_text(job_description)

    if not resume_chunks or not job_chunks:
        raise ValueError("Unable to create text chunks for comparison.")

    # 3. Convert each chunk into a numerical embedding.
    resume_embeddings = model.encode(resume_chunks)
    job_embeddings = model.encode(job_chunks)

    # 4. Compare every job-description chunk with every resume chunk.
    similarity_matrix = cosine_similarity(
        job_embeddings,
        resume_embeddings
    )

    # 5. Find the strongest resume match for each job-description chunk.
    best_matches = similarity_matrix.max(axis=1)

    # 6. Average the best matches to get the overall semantic score.
    similarity = best_matches.mean()

    # Convert to a percentage-style indicator for display.
    score = similarity * 100

    return round(float(score), 2)
