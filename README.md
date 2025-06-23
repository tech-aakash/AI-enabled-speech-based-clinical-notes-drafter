Sure, here is the complete README.md content from A to Z in clean, uninterrupted Markdown format:

# AI-enabled-speech-based-clinical-notes-drafter (VoiceRX)

VoiceRX is an AI-powered clinical documentation platform that streamlines medical note generation from doctor-patient voice interactions. By combining advanced speech recognition, medical terminology mapping, and large language models, VoiceRX reduces physician workload and enhances the accuracy and standardization of healthcare records.

## Demo

Watch the project demo video: [voicerx_demo2.mp4](./voicerx%20demo.mp4)

## Features

- Speech-to-text transcription using OpenAI Whisper
- Standardized clinical terminology via SNOMED CT
- Symptom-to-diagnosis mapping with Neo4j graph database
- Automated clinical note and prescription generation using GPT-4o
- HIPAA and GDPR compliant data handling
- Streamlit web interface for patient and doctor interactions

## System Overview

VoiceRX operates as a dual-interface platform (for patients and doctors) integrated through a unified Streamlit web app. Audio inputs are processed to generate structured clinical documentation.

### Architecture Pipeline

1. Voice input is captured from patient or doctor
2. Audio preprocessing is done using `noisereduce`
3. Whisper ASR model transcribes the audio
4. Key medical terms are extracted and mapped to SNOMED CT codes via Neo4j
5. GPT-4o generates structured clinical notes and prescriptions
6. Output is displayed in a clear and compliant format

## Technologies Used

| Component                | Technology                     |
|--------------------------|--------------------------------|
| Speech Recognition       | OpenAI Whisper                 |
| Audio Preprocessing      | noisereduce (Python)           |
| Medical Term Mapping     | SNOMED CT                      |
| Database                 | Neo4j (Graph Database)         |
| Clinical Note Generation | Azure OpenAI GPT-4o            |
| Frontend Interface       | Streamlit                      |

## Example Output

### Patient Voice Input

So, I have been having a burning sensation passing urine since the last two days.

### Transcribed Text

Burning sensation while passing urine for the past two days.

### SNOMED CT Terms

- 28278009 – Passing urine
- 90673000 – Burning sensation
- 102835006 – Difficulty passing urine

### Generated Clinical Note

Chief Complaint:
Burning sensation while passing urine for the past two days.

Observations:
The patient reports discomfort during urination, possibly indicating a urinary tract infection. Symptoms began after recent travel and public restroom use.

### Prescription Output

Prescription:
No immediate medications prescribed during the consultation.

Follow-Up:
The doctor advised the patient to avoid traveling and use caution with public restrooms for the next 1–2 days. If discomfort persists after three days, the patient has been instructed to visit the hospital for further evaluation.

## Additional Example

### Patient Voice Input

So I have been having a really bad headache. I am Lavanya and I have a stomach pain and I have not been doing well since the past four days.

### SNOMED CT Terms

- 25064002 – Headache
- 271681002 – Stomach pain

### Clinical Note

Chief Complaint:
Headache (SNOMED CT: 25064002)
Stomach pain (SNOMED CT: 271681002)

Observations:
Symptoms have persisted for four days. Likely caused by fatigue and mental stress.

### Prescription

Prescription:
Advice to rest for two days. Paracetamol, once daily in the morning (SNOMED CT: 73775008).

Follow-Up:
Monitor symptoms. Return to the hospital if symptoms worsen within the next three days.

## Limitations

- Dependence on stable internet connection for cloud model inference (Whisper, GPT-4o)
- SNOMED CT requires licensing for production deployment
- Current UI built for demonstration; not yet suitable for clinical integration

## Future Improvements

- Enable offline and edge-computing capabilities
- Integrate with Electronic Health Record (EHR) systems
- Improve UI for clinical environments
- Implement authentication and encryption for enhanced security

## Contributors

- Pranav Mundhra – NMIMS, Shirpur – pranavmundhra2005@gmail.com
- Aakash Walvalkar – Michigan Technological University – aakash.muskurahat@gmail.com
- Laavanya Mishra – NMIMS, Mumbai – mishralaavanya@gmail.com
- Anushka Kumar – NMIMS, Mumbai – anushka.ayyanar@gmail.com
- Prernakumari Jha – SNDT University – jhaa3162@gmail.com
- Jayaditya Arora – NMIMS, Shirpur – jayadityaarora2007@gmail.com

## References

- OpenAI Whisper: https://openai.com/index/whisper/
- Azure GPT-4: https://azure.microsoft.com/en-us/blog/introducing-gpt4-in-azure-openai-service/
- SNOMED CT Licensing: https://www.snomed.org/licensing
- Neo4j Cypher: https://neo4j.com/docs/cypher-refcard/current/
- NoiseReduce Python Package: https://pypi.org/project/noisereduce/
