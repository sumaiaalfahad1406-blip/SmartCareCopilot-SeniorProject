"""Run flexible GPT Top-3 predictions on a configurable number of validation patients.
Accuracy is calculated separately from the saved CSV.
"""
import csv
import json
import random
from pathlib import Path

from main_MedRAG import (
    ALLOWED_DIAGNOSES,
    build_diagnosis_centroids,
    build_or_load_document_embeddings,
    generate_top3_diagnoses,
    get_query_embedding,
    load_training_documents,
    normalize_label,
    patient_to_clinical_text,
    retrieve_top3_diagnoses,
)

# Change this number whenever you want. Set to None to validate ALL patients.
NUMBER_OF_VALIDATION_PATIENTS = 5
RANDOM_SEED = 42

# Place this script beside main_MedRAG_top3.py and the dataset folder.
BASE_DIR = Path(__file__).resolve().parent
TRAIN_FOLDER = BASE_DIR / 'dataset' / 'df' / 'train' / 'retrieval_patients'
VALIDATION_FOLDER = BASE_DIR / 'dataset' / 'df' / 'validate' / 'patients'
EMBEDDINGS_PATH = BASE_DIR / 'dataset' / 'clinical_retrieval_embeddings.npy'
OUTPUT_TXT = BASE_DIR / 'top3_validation_results.txt'
OUTPUT_CSV = BASE_DIR / 'top3_validation_results.csv'


def main():
    for folder in (TRAIN_FOLDER, VALIDATION_FOLDER):
        if not folder.is_dir():
            raise FileNotFoundError(f'Missing folder: {folder}')
    if not EMBEDDINGS_PATH.is_file():
        raise FileNotFoundError(
            f'Missing saved embeddings: {EMBEDDINGS_PATH}\n'
            'Stop here rather than generating a potentially expensive new embedding bank.'
        )

    print('Loading training retrieval bank...')
    documents, document_texts, diagnoses = load_training_documents(str(TRAIN_FOLDER))
    print(f'Training/retrieval patients: {len(documents)}')
    print(f'Diagnosis groups in retrieval bank: {len(set(diagnoses))}')

    # Check cached embeddings BEFORE calling the helper, which otherwise rebuilds
    # automatically and could incur substantial API charges.
    import numpy as np
    saved = np.load(str(EMBEDDINGS_PATH), mmap_mode='r')
    if saved.shape[0] != len(documents):
        raise ValueError(
            f'Embedding count ({saved.shape[0]}) does not match retrieval '
            f'patient count ({len(documents)}). Stopping without rebuilding. '
            'Check that the original retrieval_patients folder is being used.'
        )
    document_embeddings = build_or_load_document_embeddings(
        document_texts, str(EMBEDDINGS_PATH)
    )
    centroid_labels, centroid_embeddings = build_diagnosis_centroids(
        document_embeddings, diagnoses
    )

    files = sorted(VALIDATION_FOLDER.glob('*.json'))
    if not files:
        raise ValueError(f'No validation patient JSON files found in {VALIDATION_FOLDER}')
    if NUMBER_OF_VALIDATION_PATIENTS is None:
        selected = files
    else:
        if not isinstance(NUMBER_OF_VALIDATION_PATIENTS, int) or NUMBER_OF_VALIDATION_PATIENTS < 1:
            raise ValueError('NUMBER_OF_VALIDATION_PATIENTS must be a positive integer or None.')
        if len(files) < NUMBER_OF_VALIDATION_PATIENTS:
            raise ValueError(f'Only {len(files)} validation patient files were found.')
        selected = random.Random(RANDOM_SEED).sample(files, NUMBER_OF_VALIDATION_PATIENTS)
    print(f'Total available validation patients: {len(files)}')
    print(f'Validating exactly {len(selected)} patients')

    rows = []
    report = [
        'SMARTCARE COPILOT — FLEXIBLE TOP-3 VALIDATION',
        f'Training retrieval cases: {len(documents)}',
        
        f'Validation cases: {len(selected)}',
        f'Selection: {"all validation patients" if NUMBER_OF_VALIDATION_PATIENTS is None else f"random sample, seed {RANDOM_SEED}"}',
        'Predictions are experimental, not confirmed medical diagnoses.',
        '=' * 78,
    ]

    for index, path in enumerate(selected, 1):
        with path.open('r', encoding='utf-8') as f:
            patient = json.load(f)
        query = patient_to_clinical_text(patient)
        correct = normalize_label(patient.get('Processed Diagnosis', ''))
        if not query.strip():
            raise ValueError(f'No clinical text in {path.name}')
        if correct not in ALLOWED_DIAGNOSES:
            raise ValueError(
                f'Unknown ground-truth diagnosis in {path.name}: {correct!r}. '
                'Check diagnosis normalization and the allowed-label list.'
            )

        print(f'\n[{index}/{len(selected)}] {path.name}: requesting embedding + GPT...')
        query_embedding = get_query_embedding(query)
        retrieved = retrieve_top3_diagnoses(
            query_text=query,
            query_embedding=query_embedding,
            document_embeddings=document_embeddings,
            documents=documents,
            document_texts=document_texts,
            diagnoses=diagnoses,
            centroid_labels=centroid_labels,
            centroid_embeddings=centroid_embeddings,
        )
        result = generate_top3_diagnoses(query=query, retrieval_results=retrieved)
        predictions = result['diagnoses']
        predicted_labels = [p['diagnosis'] for p in predictions]
        print(f'  Reference diagnosis: {correct}; GPT predictions saved.')

        report.extend([
            '', f'PATIENT {index} — {path.name}', '-' * 78,
            'PATIENT CASE:', query,
            '', 'CORRECT DIAGNOSIS:', correct,
            '', 'TOP 3 RETRIEVED DIAGNOSES:',
            *[f'  {i}. {r["diagnosis"]}' for i, r in enumerate(retrieved, 1)],
            '', 'GPT TOP 3 DIAGNOSES:',
            *[f'  {p["rank"]}. {p["diagnosis"]}\n     Reason: {p["explanation"]}'
              for p in predictions],
            '', 'FURTHER EVALUATION:', result.get('further_evaluation', ''),
            '=' * 78,
        ])
        rows.append({
            'patient_file': path.name,
            'patient_case': query,
            'correct_diagnosis': correct,
            'retrieval_1': retrieved[0]['diagnosis'],
            'retrieval_2': retrieved[1]['diagnosis'],
            'retrieval_3': retrieved[2]['diagnosis'],
            'gpt_1': predicted_labels[0],
            'gpt_2': predicted_labels[1],
            'gpt_3': predicted_labels[2],
            'explanation_1': predictions[0]['explanation'],
            'explanation_2': predictions[1]['explanation'],
            'explanation_3': predictions[2]['explanation'],
            'further_evaluation': result.get('further_evaluation', ''),
        })
        # Save after each successful patient, preserving partial progress if an API call fails.
        with OUTPUT_TXT.open('w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        with OUTPUT_CSV.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    print(f'\nValidation completed: {len(rows)} patients.')
    print(f'Patient reports saved to: {OUTPUT_TXT}')
    print(f'Prediction data saved to: {OUTPUT_CSV}')
    print('Run the separate accuracy script to evaluate predictions.')


if __name__ == '__main__':
    main()
