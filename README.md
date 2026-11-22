# SmartCare Copilot
### A Multimodal AI Decision-Support System for Clinical Healthcare

## Project Overview

SmartCare Copilot is an AI-powered clinical decision-support system based on the **Medical Retrieval-Augmented Generation (MedRAG)** approach.

The system combines medical information retrieval with a Large Language Model (LLM) to generate the **Top-3 most relevant diagnostic predictions** based on patient symptoms.

It supports both **Arabic and English**, allowing patients to describe their symptoms through text or voice input.

The system is designed to support preliminary clinical decision-making and is not intended to replace professional medical diagnosis.

## Key Features

- **Multilingual Support:** Accepts patient symptoms in Arabic and English.
- **Multimodal Input:** Supports text, voice, and selectable symptoms.
- **Speech Recognition:** Converts voice recordings into text using faster-whisper.
- **Translation:** Translates Arabic input into English for processing.
- **Semantic Retrieval:** Identifies relevant clinical cases using medical text embeddings.
- **Top-3 Diagnosis Prediction:** Generates three ranked diagnostic predictions.
- **Interactive Web Interface:** Provides a user-friendly interface for entering symptoms and viewing results.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| OpenAI GPT-4o-mini | Diagnostic prediction generation |
| OpenAI text-embedding-3-large | Clinical text embeddings |
| NumPy | Numerical operations |
| pandas | Dataset processing |
| scikit-learn | Similarity calculations |
| faster-whisper | Speech-to-text conversion |
| GoogleTranslator / MyMemoryTranslator | Arabic-to-English translation |
| Streamlit | Web interface |

## Dataset

The system uses the **DDXPlus dataset**, which contains simulated patient cases covering 49 diagnostic categories.

For the evaluation:

- **49 diagnostic categories**
- **11,760 training cases** used as the retrieval database (240 per diagnosis)
- **1,470 test cases** (30 per diagnosis)
- Separate training and testing cases

Each patient case contains clinical information used to identify relevant diagnoses.

## System Architecture

The SmartCare Copilot pipeline consists of the following stages:

**1. Patient Input**

The patient enters symptoms using Arabic or English text, voice, or selectable symptoms.

**2. Speech Recognition and Translation**

Voice recordings are converted into text, and Arabic input is translated into English.

**3. Clinical Text Embedding**

The processed symptoms are converted into numerical embeddings using OpenAI's `text-embedding-3-large` model.

**4. Medical Information Retrieval**

The system compares the patient's embedding with stored clinical embeddings and diagnosis centroids to identify the Top-3 most relevant diagnostic categories.

**5. LLM-Based Diagnosis Generation**

GPT-4o-mini analyzes the patient's symptoms and retrieved clinical information to generate three ranked diagnostic predictions.

**6. Results Display**

The final Top-3 predictions are displayed through the web interface.

## Evaluation

The system was evaluated using 1,470 test patients from DDXPlus, with 30 patients selected from each diagnostic category.

The evaluation measures:

- **Top-1 Accuracy:** Whether the first-ranked diagnosis matches the reference diagnosis.
- **Top-3 Accuracy:** Whether the reference diagnosis appears among the three ranked predictions.
- **Retrieval Accuracy:** Whether the retrieval stage identifies the correct diagnostic category.

The evaluation compares the generated predictions against the reference diagnoses in the dataset.

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure OpenAI API

The system requires an OpenAI API key to access the embedding and language models.

Set the environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

For Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-api-key"
```


### 5. Run the Website

From the project directory, run:

```bash
streamlit run app.py
```

The application will open in your web browser.

Ensure that the required dataset files and saved embeddings are available in their expected directories before running the system.

## Limitations

- The system is limited to the diagnostic categories available in DDXPlus.
- Speech recognition and translation errors may affect the generated results.

## Future Improvements

- Expand the supported diagnostic categories.
- Improve multilingual clinical understanding.
- Evaluate performance using additional clinical datasets.
