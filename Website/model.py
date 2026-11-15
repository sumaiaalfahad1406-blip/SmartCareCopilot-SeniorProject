"""SmartCare flexible Top-3 MedRAG integration. No training is performed here."""
import json
import os
from datetime import date
from functools import lru_cache
import numpy as np
from arabic_pipeline import contains_arabic, correct_arabic_medical_text, translate_arabic_to_english

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_FOLDER = os.path.join(BASE_DIR, "dataset", "df", "train", "retrieval_patients")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "dataset", "clinical_retrieval_embeddings.npy")

@lru_cache(maxsize=1)
def _get_index():
    from main_MedRAG import load_training_documents, build_diagnosis_centroids
    documents, document_texts, diagnoses = load_training_documents(TRAIN_FOLDER, max_docs=None)
    if not os.path.isfile(EMBEDDINGS_PATH):
        raise FileNotFoundError("Cached embeddings missing. Copy dataset/clinical_retrieval_embeddings.npy into the project.")
    embeddings = np.load(EMBEDDINGS_PATH, allow_pickle=False)
    if len(embeddings) != len(documents):
        raise ValueError("Embedding count does not match the retrieval bank. Check your existing training bank; no automatic regeneration will occur.")
    labels, centroids = build_diagnosis_centroids(embeddings, diagnoses)
    if len(labels) < 3:
        raise ValueError("At least three diagnosis groups are needed.")
    return documents, document_texts, diagnoses, embeddings, labels, centroids

def _age_from_dob(dob):
    try:
        birth = date.fromisoformat(dob)
        today = date.today()
        return str(today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day)))
    except (TypeError, ValueError):
        return ""

def run_ai_query(query: str, patient: dict, history: list, files=None) -> str:
    """Return structured Top-3 differential diagnoses for one clinical complaint."""
    if not (query or "").strip():
        return "⚠️ Please enter clinical symptoms as text. Attachments alone cannot be analyzed."
    try:
        from main_MedRAG import (
            PRESENTATION_KEY, SYMPTOMS_KEY, patient_to_clinical_text,
            get_query_embedding, retrieve_top3_diagnoses, generate_top3_diagnoses,
        )
        original = query.strip()
        english = (translate_arabic_to_english(correct_arabic_medical_text(original))
                   if contains_arabic(original) else original)
        case = {"Age": _age_from_dob(patient.get("dob")),
                PRESENTATION_KEY: english, SYMPTOMS_KEY: ""}
        clinical_text = patient_to_clinical_text(case)
        documents, texts, diagnoses, embeddings, labels, centroids = _get_index()
        retrieved = retrieve_top3_diagnoses(
            query_text=clinical_text,
            query_embedding=get_query_embedding(clinical_text),
            document_embeddings=embeddings,
            documents=documents,
            document_texts=texts,
            diagnoses=diagnoses,
            centroid_labels=labels,
            centroid_embeddings=centroids,
        )
        result = generate_top3_diagnoses(query=clinical_text, retrieval_results=retrieved, model="gpt-4o-mini")
        if len(result.get("diagnoses", [])) != 3:
            raise ValueError("The model did not return exactly three diagnoses.")
        payload = {
            "diagnoses": result["diagnoses"],
            "further_evaluation": result.get("further_evaluation", ""),
            "translation": english if contains_arabic(original) else "",
            "retrieved": [r["diagnosis"] for r in retrieved],
        }
        return "TOP3_JSON:" + json.dumps(payload, ensure_ascii=False)
    except Exception as exc:
        return f"⚠️ Model error: {exc}"
