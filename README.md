# AI-enabled-speech-based-clinical-notes-drafter

[![Demo Video](#demo)](#demo)  
*AI-powered, speech-based clinical notes drafter leveraging Whisper, Neo4j, GPT-4o, and SNOMED CT for next-gen medical documentation.*

---

## Table of Contents

- [Overview](#overview)
- [Demo](#demo)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Methodology](#methodology)
- [Example Outputs](#example-outputs)
- [Installation](#installation)
- [Usage](#usage)
- [Authors](#authors)
- [License](#license)
- [References](#references)

---

## Overview

**AI-enabled-speech-based-clinical-notes-drafter** is an all-in-one healthcare documentation platform that harnesses advanced AI technologies to streamline clinical note-taking and prescription management.

The platform uses patient and doctor voice inputs to generate standardized clinical notes, map medical concepts to SNOMED CT codes, and produce clear, structured documentation. It leverages:

- **OpenAI Whisper:** Robust, multilingual speech-to-text.
- **Neo4j:** Medical graph database for clinical coding and relationships.
- **GPT-4o:** Generation of clinically accurate and standardized documentation.
- **SNOMED CT:** Uniform medical terminology.
- **Streamlit:** Interactive web application interface.

This solution is designed to reduce administrative burdens, improve accuracy, and ensure compliance with data privacy regulations (HIPAA/GDPR).

---

## Demo

https://github.com/tech-aakash/AI-enabled-speech-based-clinical-notes-drafter.git/voicerx_demo2.mp4

Or download/view the demo video directly:  
[▶️ Click here for video demo (voicerx_demo2.mp4)](voicerx_demo2.mp4)

---

## Features

- 🎤 **Speech-to-Text:** Transcribe patient and physician speech using OpenAI Whisper.
- 🩺 **Medical Concept Mapping:** Map symptoms and prescriptions to SNOMED CT codes using Neo4j.
- 📝 **Automated Clinical Notes:** Generate structured, standardized clinical notes with GPT-4o.
- 🏥 **Prescription Management:** Extract and structure doctor’s prescriptions.
- 🔒 **Compliance:** Designed for HIPAA & GDPR adherence.
- 🌎 **Multilingual Support:** Handles varied accents and languages.
- ⚡ **Noise Reduction:** Uses Python’s `noisereduce` for clear transcription.
- 🔗 **Extensible Architecture:** Ready for EHR integration and expansion.

---

## System Architecture

```mermaid
flowchart LR
  Patient & Doctor -->|Voice Input| Whisper
  Whisper -->|Transcription| Neo4j
  Neo4j -->|Medical Coding| GPT-4o
  GPT-4o -->|Clinical Note| StreamlitApp
  StreamlitApp -->|User Interface| Patient & Doctor
