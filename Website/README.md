# SmartCare Copilot — Clinical AI Website

## Project Overview

SmartCare Copilot is a multimodal AI-powered clinical decision-support website developed using **Python and Streamlit**.

The website provides healthcare professionals with an interactive platform to manage patients, conduct consultations, enter clinical symptoms, and receive AI-generated differential diagnoses.

It integrates the MedRAG pipeline to retrieve relevant clinical cases and generate the top three possible diagnoses using GPT-4o-mini.

## Website Features

- **Doctor Login:** Login interface for accessing the dashboard.
- **Patient Management:** Add, edit, view, and delete patient records.
- **Consultation Management:** Create and manage patient consultations.
- **Multilingual Support:** Accepts clinical information in English and Arabic.
- **Voice Input:** Converts recorded speech into text using Faster-Whisper.
- **Symptom Selection:** Allows doctors to select symptoms through an interactive interface.
- **AI Diagnosis:** Generates three ranked differential diagnoses with explanations.
- **Clinical Recommendations:** Provides suggestions for further evaluation.
- **Doctor Profile:** Displays and allows editing of doctor information.

## Website Structure

```text
Website/
├── app.py
├── actions.py
├── config.py
├── dialogs.py
├── helpers.py
├── seed_data.py
├── state.py
├── styles.py
├── chat.py
├── model.py
├── arabic_pipeline.py
├── main_MedRAG.py
├── views/
│   ├── login.py
│   ├── dashboard.py
│   ├── patient.py
│   ├── profile.py
│   └── sidebar.py
├── components/
│   └── symptom_selector.py
├── assets/
└── README.md
```

## How the Website Works

1. The doctor logs into the website.
2. The doctor selects an existing patient or creates a new patient record.
3. The doctor starts a consultation and enters symptoms using text, voice, or the symptom selector.
4. Arabic clinical text is translated into English when necessary.
5. The clinical information is sent to the MedRAG pipeline.
6. The pipeline retrieves relevant diagnosis groups and clinical cases.
7. GPT-4o-mini generates three ranked differential diagnoses with explanations and further evaluation recommendations.
8. The results are displayed in the consultation interface.

## Technologies Used

- **Python:** Backend programming
- **Streamlit:** Website interface
- **OpenAI API:** Clinical text embeddings and GPT-4o-mini
- **Faster-Whisper:** Speech-to-text transcription
- **Deep Translator:** Arabic-to-English translation
- **NumPy:** Numerical processing
- **DDXPlus:** Clinical dataset

## Running the Website

Install the required Python dependencies and configure the OpenAI API key securely.

From the Website directory, run:

```bash
streamlit run app.py
```

The website also requires the prepared MedRAG retrieval documents and embedding cache in their configured dataset paths.

## Important Notes
- An OpenAI API key is required for diagnosis generation.

## Clinical Disclaimer

SmartCare Copilot is designed for research and clinical decision-support purposes only. AI-generated diagnoses are suggestions and must be reviewed by qualified healthcare professionals. The system does not replace medical judgment, examination, or diagnostic testing.
