# SmartCare Copilot — MedRAG Pipeline

## Project Overview

SmartCare Copilot is a multimodal AI-powered clinical decision-support system designed to assist healthcare professionals by generating the top three possible diagnoses based on patient symptoms and clinical information.

The system uses Retrieval-Augmented Generation (RAG), combining clinical case retrieval with GPT-4o-mini to generate differential diagnoses, explanations, and recommendations for further evaluation.

## Dataset

The project uses the publicly available **DDXPlus dataset**, which contains patient cases covering 49 diagnoses.

The dataset is used to prepare the retrieval database and evaluate the system's diagnostic performance.

## MedRAG Pipeline

The pipeline consists of the following stages:

1. **Data Preprocessing:** Convert patient records into structured clinical descriptions.
2. **Embedding Generation:** Convert clinical descriptions into numerical embeddings using OpenAI's `text-embedding-3-large`.
3. **Diagnosis Centroids:** Calculate representative embedding vectors for each diagnosis.
4. **Retrieval:** Identify the three most relevant diagnosis groups using cosine similarity.
5. **Case Selection:** Select representative patient cases using a hybrid similarity score:
   - 65% embedding similarity
   - 25% lexical similarity
   - 10% age similarity
6. **Diagnosis Generation:** Use GPT-4o-mini to generate three ranked differential diagnoses, explanations, and further evaluation recommendations.
7. **Output Validation:** Check that the generated diagnoses follow the required format and use valid diagnosis labels.

## Project Structure

```text
MedRAG_Pipeline/
├── main.py
├── main_MedRAG.py
├── authentication.py
├── Preprocessing/
│   └── preprocess_ddxplus.py
├── Training/
│   └── training.py
├── Validation/
│   ├── validation.py
│   └── validation_top3.py
└── Testing/
    ├── test.py
    ├── test_top3_10_patients.py
    └── accuracy_top3.py
```

## Evaluation

The system is evaluated using the DDXPlus dataset.

Evaluation includes:

- Top-1 diagnosis accuracy
- Top-3 diagnosis accuracy
- Retrieval performance
- GPT-generated diagnosis performance

Evaluation results should be associated with the exact code version and dataset split used.

## Technologies

- Python
- OpenAI API
- GPT-4o-mini
- OpenAI Embeddings
- NumPy
- DDXPlus Dataset

## Clinical Disclaimer

SmartCare Copilot is a research prototype intended for clinical decision support. It does not replace professional medical judgment, clinical examination, or diagnostic testing.
