import streamlit as st
import os
from datetime import datetime
from openai import AzureOpenAI
from typing import List, Dict, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Config ---
st.set_page_config(
    page_title="VoiceRx",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Create directories
os.makedirs("voice_recordings", exist_ok=True)
os.makedirs("doctors_recordings", exist_ok=True)

# Custom CSS matching ABHA profile style
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        background: white;
        padding: 20px 40px;
        border-bottom: 2px solid #e5e7eb;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .welcome-section {
        flex: 1;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 5px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .welcome-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin: 0;
    }
    
    .header-controls {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    /* User Info */
    .user-info {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 12px 20px;
        border-radius: 25px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Main Container */
    .profile-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    /* Recording Section Cards */
    .recording-section {
        background: white;
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recording-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        transition: height 0.3s ease;
    }
    
    .recording-section:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
    }
    
    .recording-section:hover::before {
        height: 8px;
    }
    
    /* Language Detection Badge */
    .language-badge {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        display: inline-block;
        margin: 5px 0;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f3f4f6;
    }
    
    .section-icon {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        color: white;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
        transition: all 0.3s ease;
    }
    
    .section-header:hover .section-icon {
        transform: scale(1.1);
        box-shadow: 0 12px 35px rgba(99, 102, 241, 0.4);
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0;
    }
    
    .section-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin: 5px 0 0 0;
    }
    
    /* Audio Input Container */
    .audio-container {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    
    .audio-container:hover {
        border-color: #6366f1;
        background: #f8faff;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.3);
        width: 100%;
        height: 45px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(99, 102, 241, 0.4);
        background: linear-gradient(135deg, #5855eb 0%, #7c3aed 100%);
        color: #fde047;
    }
    
    /* Status Messages */
    .success-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 3px 10px rgba(16, 185, 129, 0.3);
    }
    
    .processing-message {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 15px 0;
        font-weight: 500;
        box-shadow: 0 3px 10px rgba(245, 158, 11, 0.3);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Content Display Boxes */
    .content-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        border-left: 4px solid #6366f1;
    }
    
    .transcript-box {
        font-family: 'Georgia', serif;
        line-height: 1.6;
        color: #374151;
        font-size: 15px;
    }
    
    .diseases-box {
        background: #f0fdf4;
        border-left-color: #10b981;
    }
    
    .disease-tag {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        margin: 4px;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    /* SNOMED Results */
    .snomed-container {
        background: #fefefe;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin: 15px 0;
        overflow: hidden;
    }
    
    .snomed-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 12px 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .snomed-content {
        padding: 20px;
    }
    
    .snomed-term {
        background: #f8faff;
        border: 1px solid #e0e7ff;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .snomed-term-title {
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
        text-transform: capitalize;
    }
    
    .snomed-match {
        background: white;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 8px 12px;
        margin: 4px 0;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .concept-id {
        font-weight: 600;
        color: #6366f1;
    }
    
    /* Clinical Note */
    .clinical-note-container {
        background: white;
        border: 2px solid #6366f1;
        border-radius: 16px;
        margin: 30px 0;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.2);
    }
    
    .clinical-note-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 20px;
        text-align: center;
    }
    
    .clinical-note-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
    }
    
    .clinical-note-content {
        padding: 30px;
        font-family: 'Georgia', serif;
        line-height: 1.8;
        color: #374151;
    }
    
    .clinical-note-content h4 {
        color: #6366f1;
        border-bottom: 2px solid #e0e7ff;
        padding-bottom: 8px;
        margin: 20px 0 15px 0;
        font-weight: 600;
    }
    
    /* Step Indicators */
    .step-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin: 20px 0;
        padding: 15px;
        background: #f8faff;
        border-radius: 12px;
        border: 1px solid #e0e7ff;
    }
    
    .step-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #d1d5db;
        transition: all 0.3s ease;
    }
    
    .step-dot.active {
        background: #6366f1;
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.6);
        transform: scale(1.3);
    }
    
    .step-dot.completed {
        background: #10b981;
        transform: scale(1.2);
    }
    
    .step-line {
        width: 30px;
        height: 2px;
        background: #d1d5db;
        transition: all 0.3s ease;
    }
    
    .step-line.active {
        background: #6366f1;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            flex-direction: column;
            gap: 15px;
            padding: 20px;
        }
        
        .welcome-title {
            font-size: 1.5rem;
        }
        
        .recording-section {
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .section-header {
            flex-direction: column;
            text-align: center;
            gap: 10px;
        }
    }
    
    /* Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .recording-section {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Spinner customization */
    .stSpinner > div {
        border-color: #6366f1 transparent #6366f1 transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def save_audio_file(audio_file, username: str, folder: str) -> str:
    """Save uploaded audio file with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{username}_{timestamp}.wav"
    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as f:
        f.write(audio_file.getbuffer())
    return filepath

def check_azure_credentials() -> dict:
    """Check if Azure credentials are properly configured"""
    credentials = {
        'whisper_api_key': os.getenv("AZURE_OPENAI_API_KEY"),
        'whisper_endpoint': os.getenv("AZURE_OPENAI_ENDPOINT"),
        'chat_api_key': os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
        'chat_endpoint': os.getenv("AZURE_OPENAI_CHAT_ENDPOINT")
    }
    
    missing = [key for key, value in credentials.items() if not value]
    return {
        'valid': len(missing) == 0,
        'missing': missing,
        'credentials': credentials
    }

def transcribe_audio_multilingual(filepath: str) -> dict:
    """
    Enhanced transcribe audio using Azure OpenAI Whisper with multilingual support
    Returns both original and English translation if needed
    """
    creds_check = check_azure_credentials()
    if not creds_check['valid']:
        raise ValueError(f"Missing Azure OpenAI credentials: {', '.join(creds_check['missing'])}")
    
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-06-01",  # Latest Whisper API version
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        with open(filepath, "rb") as audio:
            # First transcription - detect language and transcribe in original language
            result = client.audio.transcriptions.create(
                file=audio,
                model="whisper",
                response_format="verbose_json",  # Get detailed response with language detection
                temperature=0.1  # Lower temperature for more consistent results
            )
            
            original_text = result.text
            detected_language = result.language if hasattr(result, 'language') else 'unknown'
            
            # If not English, translate to English using Whisper's translation feature
            english_text = original_text
            if detected_language != 'en' and detected_language != 'english':
                logger.info(f"Detected non-English language: {detected_language}. Translating to English...")
                
                # Reset file pointer for translation
                with open(filepath, "rb") as audio_translate:
                    translation_result = client.audio.translations.create(
                        file=audio_translate,
                        model="whisper",
                        response_format="text",
                        temperature=0.1
                    )
                    english_text = translation_result
            
            return {
                'original_text': original_text,
                'english_text': english_text,
                'detected_language': detected_language,
                'translated': detected_language != 'en' and detected_language != 'english'
            }
            
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        st.error(f"Transcription failed: {str(e)}")
        return {
            'original_text': "Transcription failed. Please check your Azure OpenAI configuration.",
            'english_text': "Transcription failed. Please check your Azure OpenAI configuration.",
            'detected_language': 'unknown',
            'translated': False
        }

def extract_diseases_enhanced(transcript: str) -> dict:
    """
    Enhanced disease extraction using latest GPT-4o with structured output
    """
    creds_check = check_azure_credentials()
    if not creds_check['valid']:
        st.error(f"Missing Azure OpenAI credentials: {', '.join(creds_check['missing'])}")
        return {'diseases': [], 'symptoms': [], 'severity': 'unknown'}
    
    try:
        client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
            api_version="2025-01-01-preview"  # Latest API version for GPT-4o
        )
        
        # Enhanced system prompt for better medical extraction
        system_prompt = """You are an expert medical AI assistant specializing in clinical documentation.
        
        Analyze the medical transcript and extract:
        1. Diseases/Conditions mentioned
        2. Symptoms reported
        3. Overall severity assessment (mild, moderate, severe, critical)
        
        Return your response as a valid JSON object with this exact structure:
        {
            "diseases": ["list of medical conditions/diseases"],
            "symptoms": ["list of symptoms"],
            "severity": "mild|moderate|severe|critical",
            "urgency": "low|medium|high|emergency"
        }
        
        Be precise and use standard medical terminology. If no clear diseases are mentioned, return empty arrays."""
        
        response = client.chat.completions.create(
            model="gpt-4o",  # Latest GPT-4o model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Medical transcript to analyze: {transcript}"}
            ],
            temperature=0.1,  # Low temperature for consistent medical analysis
            max_tokens=1000,
            response_format={"type": "json_object"}  # Structured JSON response
        )
        
        result = json.loads(response.choices[0].message.content.strip())
        
        # Validate the response structure
        expected_keys = ['diseases', 'symptoms', 'severity', 'urgency']
        for key in expected_keys:
            if key not in result:
                result[key] = [] if key in ['diseases', 'symptoms'] else 'unknown'
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        # Fallback to simple list extraction
        return extract_diseases_fallback(transcript)
    except Exception as e:
        logger.error(f"Disease extraction failed: {str(e)}")
        st.error(f"Disease extraction failed: {str(e)}")
        return {'diseases': [], 'symptoms': [], 'severity': 'unknown', 'urgency': 'unknown'}

def extract_diseases_fallback(transcript: str) -> dict:
    """Fallback method for disease extraction"""
    try:
        client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
            api_version="2025-01-01-preview"
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Extract medical conditions and symptoms from the transcript. Reply only with a Python list like: ['fever', 'headache', 'cold']."
                },
                {"role": "user", "content": transcript}
            ],
            temperature=0.1
        )
        
        diseases_list = eval(response.choices[0].message.content.strip())
        return {
            'diseases': diseases_list,
            'symptoms': diseases_list,  # Fallback: treat as both
            'severity': 'unknown',
            'urgency': 'unknown'
        }
    except Exception:
        return {'diseases': [], 'symptoms': [], 'severity': 'unknown', 'urgency': 'unknown'}

def search_snomed_terms(term_list: List[str]) -> dict:
    """Enhanced SNOMED CT search with better error handling"""
    try:
        uri = "bolt://localhost:7687"
        username = "neo4j"
        password = "aakash@123"
        driver = GraphDatabase.driver(uri, auth=(username, password))
        results_by_keyword = {}
        
        # Enhanced query with better scoring and fuzzy matching
        query = """
        CALL db.index.fulltext.queryNodes('termIndex', $keyword + '~') YIELD node, score
        WHERE score > 0.3
        RETURN node.conceptId AS conceptId, node.term AS term, 
               node.semanticTag AS semanticTag, score
        ORDER BY score DESC
        LIMIT 10
        """
        
        with driver.session() as session:
            for keyword in term_list:
                try:
                    matches = session.execute_read(
                        lambda tx: tx.run(query, keyword=keyword.strip().lower()).data()
                    )
                    results_by_keyword[keyword] = [
                        (r["conceptId"], r["term"], r.get("semanticTag", ""), r["score"]) 
                        for r in matches
                    ]
                except Exception as e:
                    logger.warning(f"SNOMED search failed for term '{keyword}': {str(e)}")
                    results_by_keyword[keyword] = []
                    
        driver.close()
        return results_by_keyword
        
    except Exception as e:
        logger.error(f"SNOMED database connection failed: {str(e)}")
        st.error(f"SNOMED search failed: {str(e)}")
        return {term: [] for term in term_list}

def generate_clinical_note_enhanced(
    patient_transcript: str, 
    patient_analysis: dict, 
    doctor_transcript: str, 
    doctor_snomed: dict,
    patient_lang_info: dict,
    doctor_lang_info: dict
) -> str:
    """
    Enhanced clinical note generation with latest GPT-4o capabilities
    """
    try:
        client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
            api_version="2025-01-01-preview"
        )

        # Prepare enhanced context
        patient_context = f"""
Patient Communication:
- Original Language: {patient_lang_info.get('detected_language', 'English')}
- Transcript: {patient_transcript}
- Diseases/Conditions: {', '.join(patient_analysis.get('diseases', []))}
- Symptoms: {', '.join(patient_analysis.get('symptoms', []))}
- Severity Assessment: {patient_analysis.get('severity', 'Not assessed')}
- Urgency Level: {patient_analysis.get('urgency', 'Not assessed')}
"""

        doctor_context = f"""
Doctor's Assessment:
- Original Language: {doctor_lang_info.get('detected_language', 'English')}
- Transcript: {doctor_transcript}
"""

        # Enhanced system prompt for clinical documentation
        system_prompt = """You are an expert clinical documentation specialist with deep knowledge of medical terminology, clinical workflows, and healthcare standards.

Create a comprehensive, structured clinical note that follows standard medical documentation practices. The note should be:
- Clinically accurate and professionally formatted
- Include relevant SNOMED CT codes where applicable
- Follow SOAP (Subjective, Objective, Assessment, Plan) structure when appropriate
- Be suitable for electronic health records (EHR)
- Include severity and urgency assessments
- Account for any language translation notes if applicable

Format the output with clear headers and bullet points for readability."""

        prompt = f"""
Generate a detailed clinical note using the following information:

{patient_context}

{doctor_context}

SNOMED CT Terminology References:
{json.dumps(doctor_snomed, indent=2)}

Please structure the clinical note with the following sections:
1. Patient Presentation & Chief Complaint
2. Clinical Findings & Symptoms
3. Assessment & Diagnosis
4. Treatment Plan & Recommendations
5. Medications & Dosage (if prescribed)
6. Follow-up Instructions
7. Clinical Codes & References

Include severity indicators and any urgent care recommendations based on the assessment.
"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Low temperature for clinical accuracy
            max_tokens=2000
        )
        
        clinical_note = response.choices[0].message.content.strip()
        
        # Add metadata footer
        metadata = f"""

---
**Documentation Metadata:**
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Patient Language: {patient_lang_info.get('detected_language', 'English')}
- Doctor Language: {doctor_lang_info.get('detected_language', 'English')}
- AI Assistant: GPT-4o Clinical Documentation
- Translation Applied: {'Yes' if patient_lang_info.get('translated', False) or doctor_lang_info.get('translated', False) else 'No'}
"""
        
        return clinical_note + metadata
        
    except Exception as e:
        logger.error(f"Clinical note generation failed: {str(e)}")
        st.error(f"Clinical note generation failed: {str(e)}")
        return "Clinical note generation failed. Please check your configuration."

# --- MAIN APPLICATION ---

# Set default user as user104 (always signed in)
username = "user104"

# Main Header with user info
st.markdown(f"""
    <div class="main-header">
        <div class="welcome-section">
            <h1 class="welcome-title">🎤 VoiceRx - AI Clinical Notes</h1>
            <p class="welcome-subtitle">Multi-language voice recordings to structured clinical documentation</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main container
st.markdown('<div class="profile-container">', unsafe_allow_html=True)

# Create two columns for patient and doctor sections
col1, col2 = st.columns(2, gap="large")

# --- PATIENT SIDE ---
with col1:
    with st.container():
        st.markdown("""
        <div class="recording-section">
            <div class="section-header">
                <div class="section-icon">👨‍🏫</div>
                <div>
                    <div class="section-title">Patient Portal</div>
                    <div class="section-subtitle">Record your symptoms in any language</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Audio input container
        st.markdown("""
        <div class="audio-container">
            <h4 style="margin: 0 0 10px 0; color: #374151;">🎙️ Record symptoms in any language</h4>
            <p style="margin: 0; color: #6b7280; font-size: 14px;">Speak naturally in your preferred language - we'll handle the translation automatically</p>
        </div>
        """, unsafe_allow_html=True)
        
        patient_audio = st.audio_input("Record Patient Symptoms", key="patient_audio")

        # Only process patient audio if it's new
        if patient_audio and (not hasattr(st.session_state, 'patient_audio_processed') or 
                            st.session_state.get('patient_audio_hash') != hash(patient_audio.getbuffer().tobytes())):
            
            # Mark this audio as being processed and store its hash
            st.session_state.patient_audio_processed = True
            st.session_state.patient_audio_hash = hash(patient_audio.getbuffer().tobytes())
            
            filepath = save_audio_file(patient_audio, username, "voice_recordings")
            st.markdown(f'<div class="success-message">✅ Audio saved as <code>{os.path.basename(filepath)}</code></div>', unsafe_allow_html=True)

            # Step indicators
            st.markdown("""
            <div class="step-indicator">
                <div class="step-dot active"></div>
                <div class="step-line active"></div>
                <div class="step-dot"></div>
                <div class="step-line"></div>
                <div class="step-dot"></div>
            </div>
            """, unsafe_allow_html=True)
            
            # Step 1: Enhanced Transcription with Language Detection
            st.markdown('<div class="processing-message">🔄 Converting speech to text with language detection...</div>', unsafe_allow_html=True)
            
            with st.spinner("Transcribing and translating audio..."):
                transcription_result = transcribe_audio_multilingual(filepath)
                st.session_state.patient_transcription = transcription_result
            
            # Display language detection and transcription results
            lang_name = transcription_result['detected_language'].title()
            if transcription_result['translated']:
                st.markdown(f'<span class="language-badge">🌐 Detected: {lang_name} → Translated to English</span>', unsafe_allow_html=True)
                
                if transcription_result['original_text'] != transcription_result['english_text']:
                    st.markdown("**📝 Original Transcript:**")
                    st.markdown(f'<div class="content-box transcript-box" style="border-left-color: #f59e0b;">{transcription_result["original_text"]}</div>', unsafe_allow_html=True)
                
                st.markdown("**📝 English Translation:**")
                st.markdown(f'<div class="content-box transcript-box">{transcription_result["english_text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="language-badge">🇺🇸 Detected: English</span>', unsafe_allow_html=True)
                st.markdown("**📝 Patient Transcript:**")
                st.markdown(f'<div class="content-box transcript-box">{transcription_result["english_text"]}</div>', unsafe_allow_html=True)

            # Step 2: Enhanced Disease and Symptom Analysis
            st.markdown("""
            <div class="step-indicator">
                <div class="step-dot completed"></div>
                <div class="step-line active"></div>
                <div class="step-dot active"></div>
                <div class="step-line active"></div>
                <div class="step-dot"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="processing-message">🔍 Advanced analysis of symptoms and medical conditions...</div>', unsafe_allow_html=True)
            
            with st.spinner("Extracting medical terms with AI analysis..."):
                medical_analysis = extract_diseases_enhanced(transcription_result['english_text'])
                st.session_state.patient_analysis = medical_analysis

            # Display enhanced medical analysis
            col_diseases, col_symptoms = st.columns(2)
            
            with col_diseases:
                st.markdown("**🏥 Medical Conditions:**")
                if medical_analysis['diseases']:
                    diseases_html = '<div class="content-box diseases-box">'
                    for disease in medical_analysis['diseases']:
                        diseases_html += f'<span class="disease-tag">{disease.title()}</span>'
                    diseases_html += '</div>'
                    st.markdown(diseases_html, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="content-box" style="border-left-color: #6b7280;"><em>No specific conditions identified</em></div>', unsafe_allow_html=True)
            
            with col_symptoms:
                st.markdown("**🩺 Symptoms Reported:**")
                if medical_analysis['symptoms']:
                    symptoms_html = '<div class="content-box" style="border-left-color: #f59e0b; background: #fffbeb;">'
                    for symptom in medical_analysis['symptoms']:
                        symptoms_html += f'<span class="disease-tag" style="background: linear-gradient(135deg, #f59e0b, #d97706);">{symptom.title()}</span>'
                    symptoms_html += '</div>'
                    st.markdown(symptoms_html, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="content-box" style="border-left-color: #6b7280;"><em>No specific symptoms identified</em></div>', unsafe_allow_html=True)

            # Display severity and urgency assessment
            severity_color = {
                'mild': '#10b981', 'moderate': '#f59e0b', 
                'severe': '#ef4444', 'critical': '#dc2626'
            }.get(medical_analysis.get('severity', 'unknown'), '#6b7280')
            
            urgency_color = {
                'low': '#10b981', 'medium': '#f59e0b', 
                'high': '#ef4444', 'emergency': '#dc2626'
            }.get(medical_analysis.get('urgency', 'unknown'), '#6b7280')

            col_sev, col_urg = st.columns(2)
            with col_sev:
                st.markdown(f"""
                <div class="content-box" style="border-left-color: {severity_color};">
                    <strong>⚕️ Severity:</strong> <span style="color: {severity_color}; font-weight: 600;">{medical_analysis.get('severity', 'Unknown').title()}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_urg:
                st.markdown(f"""
                <div class="content-box" style="border-left-color: {urgency_color};">
                    <strong>🚨 Urgency:</strong> <span style="color: {urgency_color}; font-weight: 600;">{medical_analysis.get('urgency', 'Unknown').title()}</span>
                </div>
                """, unsafe_allow_html=True)

            # Step 3: Enhanced SNOMED Matching
            st.markdown("""
            <div class="step-indicator">
                <div class="step-dot completed"></div>
                <div class="step-line active"></div>
                <div class="step-dot completed"></div>
                <div class="step-line active"></div>
                <div class="step-dot active"></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="processing-message">🔬 Matching SNOMED CT medical terminology...</div>', unsafe_allow_html=True)
            
            with st.spinner("Searching comprehensive medical database..."):
                # Combine all terms for SNOMED search
                all_terms = medical_analysis['diseases'] + medical_analysis['symptoms']
                patient_snomed = search_snomed_terms(all_terms) if all_terms else {}
                st.session_state.patient_snomed = patient_snomed

            # Display Enhanced SNOMED results
            if patient_snomed:
                st.markdown("""
                <div class="snomed-container">
                    <div class="snomed-header">📚 SNOMED CT Medical Terminology Matches</div>
                    <div class="snomed-content">
                """, unsafe_allow_html=True)
                
                for term, matches in patient_snomed.items():
                    if matches:  # Only show terms with matches
                        st.markdown(f'<div class="snomed-term"><div class="snomed-term-title">🔍 {term.title()}</div>', unsafe_allow_html=True)
                        for cid, label, semantic_tag, score in matches[:5]:  # Show top 3 matches
                            confidence = "High" if score > 0.8 else "Medium" if score > 0.5 else "Low"
                            st.markdown(f"""
                            <div class="snomed-match">
                                <span>
                                    <span class="concept-id">{cid}</span> - {label}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div></div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="content-box" style="border-left-color: #6b7280;">
                    <em>No SNOMED CT matches found or no specific medical terms identified</em>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="success-message">✅ Patient analysis completed successfully</div>', unsafe_allow_html=True)

        # Display previously processed patient data if it exists
        elif hasattr(st.session_state, 'patient_transcription'):
            transcription_result = st.session_state.patient_transcription
            lang_name = transcription_result['detected_language'].title()
            
            if transcription_result['translated']:
                st.markdown(f'<span class="language-badge">🌐 Detected: {lang_name} → Translated to English</span>', unsafe_allow_html=True)
                
                if transcription_result['original_text'] != transcription_result['english_text']:
                    st.markdown("**📝 Original Transcript:**")
                    st.markdown(f'<div class="content-box transcript-box" style="border-left-color: #f59e0b;">{transcription_result["original_text"]}</div>', unsafe_allow_html=True)
                
                st.markdown("**📝 English Translation:**")
                st.markdown(f'<div class="content-box transcript-box">{transcription_result["english_text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="language-badge">🇺🇸 Detected: English</span>', unsafe_allow_html=True)
                st.markdown("**📝 Patient Transcript:**")
                st.markdown(f'<div class="content-box transcript-box">{transcription_result["english_text"]}</div>', unsafe_allow_html=True)
            
            if hasattr(st.session_state, 'patient_analysis'):
                medical_analysis = st.session_state.patient_analysis
                
                # Display medical analysis
                col_diseases, col_symptoms = st.columns(2)
                
                with col_diseases:
                    st.markdown("**🏥 Medical Conditions:**")
                    if medical_analysis['diseases']:
                        diseases_html = '<div class="content-box diseases-box">'
                        for disease in medical_analysis['diseases']:
                            diseases_html += f'<span class="disease-tag">{disease.title()}</span>'
                        diseases_html += '</div>'
                        st.markdown(diseases_html, unsafe_allow_html=True)
                
                with col_symptoms:
                    st.markdown("**🩺 Symptoms Reported:**")
                    if medical_analysis['symptoms']:
                        symptoms_html = '<div class="content-box" style="border-left-color: #f59e0b; background: #fffbeb;">'
                        for symptom in medical_analysis['symptoms']:
                            symptoms_html += f'<span class="disease-tag" style="background: linear-gradient(135deg, #f59e0b, #d97706);">{symptom.title()}</span>'
                        symptoms_html += '</div>'
                        st.markdown(symptoms_html, unsafe_allow_html=True)
                
                # Show severity and urgency
                severity_color = {
                    'mild': '#10b981', 'moderate': '#f59e0b', 
                    'severe': '#ef4444', 'critical': '#dc2626'
                }.get(medical_analysis.get('severity', 'unknown'), '#6b7280')
                
                urgency_color = {
                    'low': '#10b981', 'medium': '#f59e0b', 
                    'high': '#ef4444', 'emergency': '#dc2626'
                }.get(medical_analysis.get('urgency', 'unknown'), '#6b7280')

                col_sev, col_urg = st.columns(2)
                with col_sev:
                    st.markdown(f"""
                    <div class="content-box" style="border-left-color: {severity_color};">
                        <strong>⚕️ Severity:</strong> <span style="color: {severity_color}; font-weight: 600;">{medical_analysis.get('severity', 'Unknown').title()}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_urg:
                    st.markdown(f"""
                    <div class="content-box" style="border-left-color: {urgency_color};">
                        <strong>🚨 Urgency:</strong> <span style="color: {urgency_color}; font-weight: 600;">{medical_analysis.get('urgency', 'Unknown').title()}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            if hasattr(st.session_state, 'patient_snomed') and st.session_state.patient_snomed:
                st.markdown("""
                <div class="snomed-container">
                    <div class="snomed-header">📚 SNOMED CT Medical Terminology Matches</div>
                    <div class="snomed-content">
                """, unsafe_allow_html=True)
                
                for term, matches in st.session_state.patient_snomed.items():
                    if matches:
                        st.markdown(f'<div class="snomed-term"><div class="snomed-term-title">🔍 {term.title()}</div>', unsafe_allow_html=True)
                        for match_data in matches[:5]:
                            if len(match_data) >= 4:
                                cid, label, semantic_tag, score = match_data
                                confidence = "High" if score > 0.8 else "Medium" if score > 0.5 else "Low"
                                st.markdown(f"""
                                <div class="snomed-match">
                                    <span>
                                        <span class="concept-id">{cid}</span> - {label}
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                # Fallback for old format
                                cid, label = match_data[:2]
                                st.markdown(f'<div class="snomed-match"><span class="concept-id">{cid}</span><span>{label}</span></div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div></div>', unsafe_allow_html=True)
                st.markdown('<div class="success-message">✅ Patient analysis completed successfully</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

# --- DOCTOR SIDE ---
with col2:
    with st.container():
        st.markdown("""
        <div class="recording-section">
            <div class="section-header">
                <div class="section-icon">👨‍⚕️</div>
                <div>
                    <div class="section-title">Doctor Portal</div>
                    <div class="section-subtitle">Record diagnosis in any language</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Audio input container
        st.markdown("""
        <div class="audio-container">
            <h4 style="margin: 0 0 10px 0; color: #374151;">🎙️ Record diagnosis & prescription</h4>
            <p style="margin: 0; color: #6b7280; font-size: 14px;">Provide medical assessment in your preferred language - automatic translation included</p>
        </div>
        """, unsafe_allow_html=True)
        
        doctor_audio = st.audio_input("Record Doctor Notes", key="doctor_audio")

        # Only process doctor audio if it's new
        if doctor_audio and (not hasattr(st.session_state, 'doctor_audio_processed') or 
                            st.session_state.get('doctor_audio_hash') != hash(doctor_audio.getbuffer().tobytes())):
            
            # Mark this audio as being processed and store its hash
            st.session_state.doctor_audio_processed = True
            st.session_state.doctor_audio_hash = hash(doctor_audio.getbuffer().tobytes())
            
            filepath = save_audio_file(doctor_audio, username + "_doctor", "doctors_recordings")
            st.markdown(f'<div class="success-message">✅ Doctor audio saved as <code>{os.path.basename(filepath)}</code></div>', unsafe_allow_html=True)

            # Enhanced Transcription for Doctor
            st.markdown('<div class="processing-message">🔄 Converting doctor notes to text with language detection...</div>', unsafe_allow_html=True)
            with st.spinner("Transcribing and translating doctor's assessment..."):
                doctor_transcription = transcribe_audio_multilingual(filepath)
                st.session_state.doctor_transcription = doctor_transcription

            # Display doctor language detection and transcription
            lang_name = doctor_transcription['detected_language'].title()
            if doctor_transcription['translated']:
                st.markdown(f'<span class="language-badge">🌐 Detected: {lang_name} → Translated to English</span>', unsafe_allow_html=True)
                
                if doctor_transcription['original_text'] != doctor_transcription['english_text']:
                    st.markdown("**📝 Original Assessment:**")
                    st.markdown(f'<div class="content-box transcript-box" style="border-left-color: #f59e0b;">{doctor_transcription["original_text"]}</div>', unsafe_allow_html=True)
                
                st.markdown("**📝 English Translation:**")
                st.markdown(f'<div class="content-box transcript-box">{doctor_transcription["english_text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="language-badge">🇺🇸 Detected: English</span>', unsafe_allow_html=True)
                st.markdown("**📝 Doctor's Assessment:**")
                st.markdown(f'<div class="content-box transcript-box">{doctor_transcription["english_text"]}</div>', unsafe_allow_html=True)

            # SNOMED Matching for treatments
            st.markdown('<div class="processing-message">🔬 Processing treatment terminology...</div>', unsafe_allow_html=True)
            with st.spinner("Analyzing treatment codes..."):
                # Extract treatment terms from doctor's transcript
                treatment_terms = [doctor_transcription['english_text']]
                doctor_snomed = search_snomed_terms(treatment_terms)
                st.session_state.doctor_snomed = doctor_snomed

            # Generate Enhanced Clinical Note
            if hasattr(st.session_state, 'patient_transcription'):
                st.markdown('<div class="processing-message">📋 Generating comprehensive clinical note with AI...</div>', unsafe_allow_html=True)
                with st.spinner("Creating enhanced clinical documentation..."):
                    note = generate_clinical_note_enhanced(
                        st.session_state.patient_transcription['english_text'],
                        st.session_state.patient_analysis,
                        st.session_state.doctor_transcription['english_text'],
                        st.session_state.doctor_snomed,
                        st.session_state.patient_transcription,
                        st.session_state.doctor_transcription
                    )
                    st.session_state.clinical_note = note
                
                # Display enhanced clinical note
                st.markdown("""
                <div class="clinical-note-container">
                    <div class="clinical-note-header">
                        <div class="clinical-note-title">📋 Enhanced Clinical Documentation</div>
                    </div>
                    <div class="clinical-note-content">
                """, unsafe_allow_html=True)
                
                st.markdown(note)
                
                st.markdown("""
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="success-message">✅ Enhanced clinical note generated successfully</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="content-box" style="border-left-color: #f59e0b; background: #fffbeb;">
                    <p style="margin: 0; color: #92400e;">ℹ️ Please complete patient recording first to generate the comprehensive clinical note.</p>
                </div>
                """, unsafe_allow_html=True)

        # Display previously processed doctor data if it exists
        elif hasattr(st.session_state, 'doctor_transcription'):
            doctor_transcription = st.session_state.doctor_transcription
            lang_name = doctor_transcription['detected_language'].title()
            
            if doctor_transcription['translated']:
                st.markdown(f'<span class="language-badge">🌐 Detected: {lang_name} → Translated to English</span>', unsafe_allow_html=True)
                
                if doctor_transcription['original_text'] != doctor_transcription['english_text']:
                    st.markdown("**📝 Original Assessment:**")
                    st.markdown(f'<div class="content-box transcript-box" style="border-left-color: #f59e0b;">{doctor_transcription["original_text"]}</div>', unsafe_allow_html=True)
                
                st.markdown("**📝 English Translation:**")
                st.markdown(f'<div class="content-box transcript-box">{doctor_transcription["english_text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="language-badge">🇺🇸 Detected: English</span>', unsafe_allow_html=True)
                st.markdown("**📝 Doctor's Assessment:**")
                st.markdown(f'<div class="content-box transcript-box">{doctor_transcription["english_text"]}</div>', unsafe_allow_html=True)
            
            # Show clinical note if it exists
            if hasattr(st.session_state, 'clinical_note'):
                st.markdown("""
                <div class="clinical-note-container">
                    <div class="clinical-note-header">
                        <div class="clinical-note-title">📋 Enhanced Clinical Documentation</div>
                    </div>
                    <div class="clinical-note-content">
                """, unsafe_allow_html=True)
                
                st.markdown(st.session_state.clinical_note)
                
                st.markdown("""
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="success-message">✅ Enhanced clinical note generated successfully</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Footer with new features
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding: 30px; background: white; border-radius: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
    <h4 style="margin: 0 0 10px 0; color: #374151;">🏥 VoiceRx </h4>
    <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">AI-Powered Multi-Language Healthcare Documentation</p>
    <p style="margin: 5px 0 0 0; color: #9ca3af; font-size: 12px;">Powered by Azure OpenAI GPT-4o & Advanced Medical Terminology</p>
</div>
""", unsafe_allow_html=True)