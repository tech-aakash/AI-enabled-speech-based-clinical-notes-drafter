import streamlit as st
import os
from datetime import datetime
from openai import AzureOpenAI
from typing import List
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Config ---
st.set_page_config(page_title="VoiceRx", page_icon="🎤", layout="wide")
st.title(":microphone: VoiceRx - AI based clinical notes drafter")
os.makedirs("voice_recordings", exist_ok=True)
os.makedirs("doctors_recordings", exist_ok=True)

# --- Helper Functions ---
def save_audio_file(audio_file, user_tag: str, folder: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_tag}_{timestamp}.wav"
    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as f:
        f.write(audio_file.getbuffer())
    return filepath

def transcribe_audio(filepath: str) -> str:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    with open(filepath, "rb") as audio:
        result = client.audio.transcriptions.create(file=audio, model="whisper")
    return result.text

def extract_diseases(transcript: str) -> List[str]:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT")
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a medical assistant for a doctor. Extract only the diseases or clinical complaints mentioned in the transcript. Reply only with a valid Python list like: ['fever', 'cold'].If the patient reveals any PII (personally identifiable information like name, address, phone number or anything else related, make sure to ignore.)"
            },
            {"role": "user", "content": transcript}
        ]
    )
    try:
        return eval(response.choices[0].message.content.strip())
    except:
        return []

def search_snomed_terms(term_list):
    uri = "neo4j://127.0.0.1:7687"
    username = "neo4j"
    password = "YOUR PASSWORD HERE"  # Update if needed
    driver = GraphDatabase.driver(uri, auth=(username, password))

    results_by_keyword = {}
    query = """
    CALL db.index.fulltext.queryNodes('termIndex', $keyword) YIELD node, score
    WHERE score > 0.5
    RETURN node.conceptId AS conceptId, node.term AS term, score
    ORDER BY score DESC
    LIMIT 5
    """
    with driver.session() as session:
        for keyword in term_list:
            matches = session.execute_read(lambda tx: tx.run(query, keyword=keyword.strip().lower()).data())
            results_by_keyword[keyword] = [(r["conceptId"], r["term"]) for r in matches]
    driver.close()
    return results_by_keyword

def generate_clinical_note(patient_transcript: str, patient_snomed: dict, doctor_transcript: str, doctor_snomed: dict) -> str:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT")
    )

    snomed_summary = ""
    for label, entries in [("Patient", patient_snomed), ("Doctor", doctor_snomed)]:
        snomed_summary += f"{label} SNOMED CT Matches:\n"
        for term, results in entries.items():
            top_match = results[0] if results else ("N/A", "No match")
            snomed_summary += f"- {term}: {top_match[0]} - {top_match[1]}\n"

    prompt = f"""
Draft a structured clinical note using the following information:

Patient Transcript:
{patient_transcript}

Doctor's Transcript:
{doctor_transcript}

{snomed_summary}

Return the final note in this format:
Chief Complaint
Observations
Prescription
Any pathological or radiology test if ordered
Medicines and dosage (if any)
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a clinical assistant generating structured notes for doctors. Make sure to keep follow up section separate if mentioned. Remove personal information like name, address etc if revealed."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# --- UI Layout ---
col1, col2 = st.columns(2)

# --- PATIENT SIDE ---
with col1:
    st.subheader("👨‍🏫 Patient - Record your complaint")
    patient_audio = st.audio_input("Record your symptoms", key="patient_audio")

    if patient_audio:
        filepath = save_audio_file(patient_audio, "patient", "voice_recordings")
        st.success(f"Saved as `{os.path.basename(filepath)}`")

        with st.spinner("Transcribing..."):
            transcript = transcribe_audio(filepath)
            st.session_state.patient_transcript = transcript
            st.write(transcript)

        with st.spinner("Extracting diseases..."):
            diseases = extract_diseases(transcript)
            st.session_state.extracted_diseases = diseases
            st.code(diseases)

        with st.spinner("Searching SNOMED CT for complaints..."):
            patient_snomed = search_snomed_terms(diseases)
            st.session_state.patient_snomed = patient_snomed
            for term, matches in patient_snomed.items():
                st.markdown(f"**{term.title()}**")
                for cid, label in matches:
                    st.markdown(f"- `{cid}` - {label}")

# --- DOCTOR SIDE ---
with col2:
    st.subheader("👨‍⚕️ Doctor - Record your plan")
    doctor_audio = st.audio_input("Record diagnosis and prescription", key="doctor_audio")

    if doctor_audio:
        filepath = save_audio_file(doctor_audio, "doctor", "doctors_recordings")
        st.success(f"Doctor note saved as `{os.path.basename(filepath)}`")

        with st.spinner("Transcribing doctor's plan..."):
            doc_transcript = transcribe_audio(filepath)
            st.session_state.doctor_transcript = doc_transcript
            st.write(doc_transcript)

        with st.spinner("Searching SNOMED CT for treatments..."):
            treatment_terms = [doc_transcript]  # Optional: extract keywords using NLP
            doctor_snomed = search_snomed_terms(treatment_terms)
            st.session_state.doctor_snomed = doctor_snomed

        with st.spinner("Generating final clinical note..."):
            note = generate_clinical_note(
                st.session_state.patient_transcript,
                st.session_state.patient_snomed,
                st.session_state.doctor_transcript,
                st.session_state.doctor_snomed,
            )
            st.subheader("📋 Final Clinical Note")
            st.markdown(note)
