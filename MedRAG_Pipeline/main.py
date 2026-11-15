"""Balanced validation/test experiment for SmartCare Copilot flexible Top-3.

Requires medrag_top3.py (the cleaned Top-3 model) in the same folder.
"""
import json
import os
import re

import pandas as pd
from tqdm import tqdm

from main_MedRAG import (
    build_diagnosis_centroids,
    build_or_load_document_embeddings,
    generate_top3_diagnoses,
    get_query_embedding,
    load_training_documents,
    normalize_label,
    patient_to_clinical_text,
    pretty_label,
    retrieve_top3_diagnoses,
)

# 1. PATHS AND SETTINGS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_FOLDER = os.path.join(BASE_DIR, "dataset", "df", "train", "retrieval_patients")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "dataset", "clinical_retrieval_embeddings.npy")
EVALUATION_SPLIT = "test"          # "test" or "validation"
PATIENTS_PER_DISEASE = 30          # Up to 30 patients per diagnosis
RANDOM_STATE = 42                 # Reproducible selection
GPT_MODEL = "gpt-4o-mini"
REGENERATE_UNVERIFIED_EMBEDDINGS = False  # True triggers paid embedding regeneration

# 2. CHOOSE EVALUATION DATA
if EVALUATION_SPLIT not in ("test", "validation"):
    raise ValueError("EVALUATION_SPLIT must be 'test' or 'validation'.")

split_folder = "validate" if EVALUATION_SPLIT == "validation" else "test"
PATIENT_FOLDER = os.path.join(BASE_DIR, "dataset", "df", split_folder, "patients")
GROUND_TRUTH_PATH = os.path.join(
    BASE_DIR, "dataset", "df", split_folder,
    f"release_{split_folder}_patients.csv",
)
OUTPUT_PATH = os.path.join(BASE_DIR, f"{EVALUATION_SPLIT}_top3_results.csv")


def normalize_diagnosis(value):
    """Normalize dataset and model diagnosis labels for evaluation."""
    return normalize_label(str(value))


def select_balanced_patients(ground_truth_df):
    """Return selected CSV row positions, not guessed JSON filenames."""
    selected_positions = []
    for diagnosis, group in ground_truth_df.groupby("PATHOLOGY"):
        count = min(PATIENTS_PER_DISEASE, len(group))
        sample = group.sample(n=count, random_state=RANDOM_STATE)
        selected_positions.extend(sample.index.tolist())
        print(f"{diagnosis}: selected {count} of {len(group)}")
    # Original dataset convention: CSV row position 0 -> participant_1.json.
    # The CSV is loaded with its default RangeIndex below.
    return (ground_truth_df.loc[selected_positions]
            .sample(frac=1, random_state=RANDOM_STATE).index.tolist())


def save_results(results):
    """Save completed cases, including errors, after each patient."""
    pd.DataFrame(results).to_csv(OUTPUT_PATH, index=False)


def main():
    print(f"\nSMARTCARE COPILOT — FLEXIBLE TOP-3 {EVALUATION_SPLIT.upper()} EXPERIMENT")
    print(f"Patients per diagnosis: {PATIENTS_PER_DISEASE}; random seed: {RANDOM_STATE}")

    # 3. LOAD THE TRAINING RETRIEVAL BANK
    documents, document_texts, diagnoses = load_training_documents(
        TRAIN_FOLDER, max_docs=None
    )
    print(f"Training patients: {len(documents)}; diagnosis groups: {len(set(diagnoses))}")

    # 4. VERIFY / BUILD TRAINING EMBEDDINGS AND CENTROIDS
    document_embeddings = build_or_load_document_embeddings(
        document_texts,
        EMBEDDINGS_PATH,
        regenerate_if_unverified=REGENERATE_UNVERIFIED_EMBEDDINGS,
    )
    if len(document_embeddings) != len(documents):
        raise ValueError("Training patient / embedding count mismatch.")
    centroid_labels, centroid_embeddings = build_diagnosis_centroids(
        document_embeddings, diagnoses
    )
    if len(centroid_labels) < 3:
        raise ValueError("Top-3 retrieval needs at least three diagnosis groups.")
    print(f"Diagnosis centroids: {len(centroid_labels)}")

    # 5. LOAD GROUND TRUTH AND SELECT A BALANCED SAMPLE
    ground_truth_df = pd.read_csv(GROUND_TRUTH_PATH).reset_index(drop=True)
    if "PATHOLOGY" not in ground_truth_df.columns:
        raise ValueError("Ground-truth CSV has no PATHOLOGY column.")
    selected_positions = select_balanced_patients(ground_truth_df)
    print(f"Selected patients: {len(selected_positions)}")

    # 6. PROCESS EACH PATIENT
    results = []
    for position in tqdm(selected_positions, desc="Evaluating patients"):
        participant_no = int(position) + 1
        true_diagnosis = normalize_diagnosis(
            ground_truth_df.iloc[position]["PATHOLOGY"]
        )
        patient_path = os.path.join(
            PATIENT_FOLDER, f"participant_{participant_no}.json"
        )
        row = {
            "Participant No.": participant_no,
            "Dataset": EVALUATION_SPLIT,
            "True Diagnosis": true_diagnosis,
            "Status": "error",
            "Error": "",
            "Retrieval Top-1 Correct": False,
            "Retrieval Top-3 Correct": False,
            "GPT Top-1 Correct": False,
            "GPT Top-3 Correct": False,
        }
        try:
            if not os.path.isfile(patient_path):
                raise FileNotFoundError(f"Missing patient file: {patient_path}")
            with open(patient_path, "r", encoding="utf-8") as f:
                patient = json.load(f)
            query_text = patient_to_clinical_text(patient)
            if not query_text.strip():
                raise ValueError("Patient has no clinical query text.")
            row["Query Used"] = query_text

            # 7. TWO-STAGE TOP-3 RETRIEVAL
            query_embedding = get_query_embedding(query_text)
            retrieval_results = retrieve_top3_diagnoses(
                query_text=query_text,
                query_embedding=query_embedding,
                document_embeddings=document_embeddings,
                documents=documents,
                document_texts=document_texts,
                diagnoses=diagnoses,
                centroid_labels=centroid_labels,
                centroid_embeddings=centroid_embeddings,
            )
            retrieved_labels = [normalize_diagnosis(r["diagnosis"])
                                for r in retrieval_results]
            row["Retrieval Top-1 Correct"] = retrieved_labels[0] == true_diagnosis
            row["Retrieval Top-3 Correct"] = true_diagnosis in retrieved_labels
            for rank, (label, item) in enumerate(zip(retrieved_labels, retrieval_results), 1):
                row[f"Retrieval Diagnosis {rank}"] = label
                row[f"Retrieval Centroid Score {rank}"] = item["diagnosis_centroid_score"]
                row[f"Representative Case {rank}"] = os.path.basename(item["document"])
                row[f"Hybrid Case Score {rank}"] = item["case_score"]

            # 8. FLEXIBLE GPT TOP-3 DIFFERENTIAL DIAGNOSIS
            gpt_result = generate_top3_diagnoses(
                query=query_text,
                retrieval_results=retrieval_results,
                model=GPT_MODEL,
            )
            predicted_labels = [normalize_diagnosis(item["diagnosis"])
                                for item in gpt_result["diagnoses"]]
            row["GPT Top-1 Correct"] = predicted_labels[0] == true_diagnosis
            row["GPT Top-3 Correct"] = true_diagnosis in predicted_labels
            for rank, item in enumerate(gpt_result["diagnoses"], 1):
                row[f"GPT Diagnosis {rank}"] = predicted_labels[rank - 1]
                row[f"GPT Explanation {rank}"] = item["explanation"]
            row["Further Evaluation"] = gpt_result["further_evaluation"]
            row["Status"] = "success"
            print(f"\nPatient {participant_no}: true={pretty_label(true_diagnosis)}")
            print(f"  Retrieval Top-3: {retrieved_labels}")
            print(f"  GPT Top-3: {predicted_labels}")
        except Exception as exc:
            row["Error"] = str(exc)
            print(f"\nPatient {participant_no} failed: {exc}")
        finally:
            results.append(row)
            save_results(results)

    # 9. FINAL SUMMARY: DENOMINATORS ARE EXPLICIT
    results_df = pd.DataFrame(results)
    completed = results_df[results_df["Status"] == "success"]
    print("\nEXPERIMENT COMPLETE")
    print(f"Selected: {len(selected_positions)}; successful: {len(completed)}; "
          f"failed: {len(results_df) - len(completed)}")
    if not completed.empty:
        for metric in ("Retrieval Top-1 Correct", "Retrieval Top-3 Correct",
                       "GPT Top-1 Correct", "GPT Top-3 Correct"):
            correct = int(completed[metric].sum())
            print(f"{metric}: {correct}/{len(completed)} "
                  f"= {100 * correct / len(completed):.2f}%")
    print(f"Results saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
