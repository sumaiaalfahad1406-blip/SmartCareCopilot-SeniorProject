import json
import hashlib
import os
import re
from collections import defaultdict

import numpy as np
import openai
from sklearn.metrics.pairwise import cosine_similarity

from authentication import api_key


# ============================================================
# OPENAI CLIENT
# ============================================================

client = openai.OpenAI(api_key=api_key)


# ============================================================
# ALLOWED DIAGNOSES
# ============================================================

ALLOWED_DIAGNOSES = [
    "acute copd exacerbation infection",
    "bronchiectasis",
    "bronchiolitis",
    "bronchitis",
    "bronchospasm acute asthma exacerbation",
    "pulmonary embolism",
    "pulmonary neoplasm",
    "spontaneous pneumothorax",
    "urti",
    "viral pharyngitis",
    "whooping cough",
    "acute laryngitis",
    "acute pulmonary edema",
    "croup",
    "larygospasm",
    "epiglottitis",
    "pneumonia",
    "atrial fibrillation",
    "myocarditis",
    "pericarditis",
    "psvt",
    "possible nstemi stemi",
    "stable angina",
    "unstable angina",
    "gerd",
    "boerhaave syndrome",
    "pancreatic neoplasm",
    "scombroid food poisoning",
    "inguinal hernia",
    "tuberculosis",
    "hiv initial infection",
    "ebola",
    "influenza",
    "chagas",
    "acute otitis media",
    "acute rhinosinusitis",
    "allergic sinusitis",
    "chronic rhinosinusitis",
    "myasthenia gravis",
    "guillain barre syndrome",
    "cluster headache",
    "acute dystonic reactions",
    "sle",
    "sarcoidosis",
    "anaphylaxis",
    "panic attack",
    "spontaneous rib fracture",
    "anemia",
]


# ============================================================
# PATIENT JSON KEYS
# ============================================================

PRESENTATION_KEY = (
    "Pain Presentation and Description Areas of pain as per physiotherapy input"
)

SYMPTOMS_KEY = (
    "Pain descriptions and assorted symptoms (self-report) Associated symptoms include: "
    "parasthesia, numbness, weakness, tingling, pins and needles"
)


# ============================================================
# TEXT / LABEL NORMALIZATION
# ============================================================

def normalize_text(text):
    return str(text).lower().strip()


def normalize_label(pred):
    """
    Convert model/training diagnosis text to one of the allowed labels
    whenever possible.
    """

    pred = normalize_text(pred)
    pred = pred.replace("**", "").strip()
    pred = pred.replace("diagnosis:", "").replace("diagnoses:", "").strip()

    pred = pred.replace("_", " ")
    pred = pred.replace("-", " ")
    pred = pred.replace("/", " ")
    pred = pred.replace("(", " ").replace(")", " ")
    pred = re.sub(r"[^a-z0-9\s]", " ", pred)

    pred = " ".join(pred.split())

    aliases = {
        "boerhaave": "boerhaave syndrome",
        "hiv initial infection": "hiv initial infection",
        "acute copd exacerbation infection":
            "acute copd exacerbation infection",
        "bronchospasm acute asthma exacerbation":
            "bronchospasm acute asthma exacerbation",
        "possible nstemi stemi":
            "possible nstemi stemi",
        "guillain barre syndrome":
            "guillain barre syndrome",
    }

    if pred in aliases:
        return aliases[pred]

    for label in ALLOWED_DIAGNOSES:
        if pred == label:
            return label

    for label in sorted(
        ALLOWED_DIAGNOSES,
        key=len,
        reverse=True
    ):
        if label in pred:
            return label

    return pred


def pretty_label(label):
    label = str(label).replace("_", " ").strip()

    return " ".join(
        word.capitalize()
        for word in label.split()
    )


# ============================================================
# EMBEDDINGS
# ============================================================

def get_embeddings(
    texts,
    batch_size=100
):

    if not texts:
        return np.array(
            [],
            dtype=np.float32
        )

    all_embeddings = []

    for i in range(
        0,
        len(texts),
        batch_size
    ):

        batch = [
            str(t)
            if t is not None
            else ""
            for t in texts[
                i:i + batch_size
            ]
        ]

        response = (
            client.embeddings.create(
                input=batch,
                model="text-embedding-3-large",
            )
        )

        all_embeddings.extend(
            item.embedding
            for item in response.data
        )

    return np.array(
        all_embeddings,
        dtype=np.float32
    )


def get_query_embedding(
    query
):

    result = get_embeddings(
        [query]
    )

    if len(result) == 0:

        raise ValueError(
            "Failed to generate query embedding."
        )

    return result[0]


# ============================================================
# CLINICAL-ONLY PATIENT TEXT
# ============================================================

def patient_to_clinical_text(
    patient
):

    """
    Create the SAME clinical representation
    for train, validation and test patients.

    Diagnosis fields are NOT included here.
    """

    parts = []

    age = str(
        patient.get(
            "Age",
            ""
        )
    ).strip()

    presentation = str(
        patient.get(
            PRESENTATION_KEY,
            ""
        )
    ).strip()

    symptoms = str(
        patient.get(
            SYMPTOMS_KEY,
            ""
        )
    ).strip()

    if age:

        parts.append(
            f"Age: {age}"
        )

    if presentation:

        parts.append(
            f"Presentation: {presentation}"
        )

    if symptoms:

        parts.append(
            f"Symptoms: {symptoms}"
        )

    return "\n".join(
        parts
    )


# ============================================================
# LOAD TRAINING DOCUMENTS
# ============================================================

def load_training_documents(
    train_folder,
    max_docs=None
):

    documents = []
    document_texts = []
    diagnoses = []

    if not os.path.exists(
        train_folder
    ):

        raise FileNotFoundError(
            f"Training folder not found: "
            f"{train_folder}"
        )

    for file_name in sorted(
        os.listdir(
            train_folder
        )
    ):

        if not file_name.endswith(
            ".json"
        ):
            continue

        path = os.path.join(
            train_folder,
            file_name
        )

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                patient = json.load(
                    f
                )

        except Exception as e:

            print(
                f"Could not load "
                f"{file_name}: {e}"
            )

            continue

        clinical_text = (
            patient_to_clinical_text(
                patient
            )
        )

        diagnosis = (
            normalize_label(
                patient.get(
                    "Processed Diagnosis",
                    ""
                )
            )
        )

        if (
            not clinical_text
            or not diagnosis
        ):
            continue

        documents.append(
            path
        )

        document_texts.append(
            clinical_text
        )

        diagnoses.append(
            diagnosis
        )

        if (
            max_docs is not None
            and len(documents) >= max_docs
        ):
            break

    if not documents:

        raise ValueError(
            "No training JSON files were loaded."
        )

    return (
        documents,
        document_texts,
        diagnoses
    )


# ============================================================
# SAVE / LOAD DOCUMENT EMBEDDINGS
# ============================================================

def save_document_embeddings(
    embeddings,
    embeddings_path
):

    folder = os.path.dirname(
        embeddings_path
    )

    if folder:

        os.makedirs(
            folder,
            exist_ok=True
        )

    np.save(
        embeddings_path,
        embeddings
    )


def build_or_load_document_embeddings(
    document_texts,
    embeddings_path,
    regenerate_if_unverified=False
):
    import os
    import numpy as np

    if os.path.exists(embeddings_path):
        print("Loading existing training embeddings...")

        embeddings = np.load(embeddings_path)

        if len(embeddings) != len(document_texts):
            raise ValueError(
                "Number of saved embeddings does not match "
                "the number of training documents."
            )

        print("Existing embeddings loaded successfully.")
        return embeddings

    print("No saved embeddings found. Generating embeddings...")

    embeddings = np.asarray(get_embeddings(document_texts))

    np.save(embeddings_path, embeddings)

    print("Embeddings generated and saved successfully.")
    return embeddings

# ============================================================
# DIAGNOSIS CENTROIDS
# ============================================================

def build_diagnosis_centroids(
    document_embeddings,
    diagnoses
):

    grouped = defaultdict(
        list
    )

    for embedding, diagnosis in zip(
        document_embeddings,
        diagnoses
    ):

        grouped[
            diagnosis
        ].append(
            embedding
        )

    labels = []
    centroids = []

    for diagnosis in sorted(
        grouped
    ):

        labels.append(
            diagnosis
        )

        centroid = np.mean(
            np.vstack(
                grouped[
                    diagnosis
                ]
            ),
            axis=0
        )

        centroid = (
            centroid
            /
            (
                np.linalg.norm(
                    centroid
                )
                + 1e-12
            )
        )

        centroids.append(
            centroid
        )

    return (
        labels,
        np.vstack(
            centroids
        ).astype(
            np.float32
        )
    )


# ============================================================
# HYBRID CASE MATCHING HELPERS
# ============================================================

def extract_terms(
    text
):

    text = normalize_text(
        text
    )

    words = re.findall(
        r"[a-z0-9]+",
        text
    )

    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "is",
        "are",
        "was",
        "were",
        "do",
        "does",
        "did",
        "you",
        "your",
        "have",
        "has",
        "had",
        "with",
        "for",
        "from",
        "age",
        "presentation",
        "symptoms",
        "patient",
        "feel",
        "experiencing",
        "any",
        "within",
    }

    return {
        word
        for word in words
        if (
            len(word) > 2
            and word not in stop
        )
    }


def lexical_overlap(
    query_text,
    candidate_text
):

    query_terms = extract_terms(
        query_text
    )

    candidate_terms = extract_terms(
        candidate_text
    )

    if (
        not query_terms
        or not candidate_terms
    ):

        return 0.0

    return (
        len(
            query_terms
            &
            candidate_terms
        )
        /
        len(
            query_terms
            |
            candidate_terms
        )
    )


def age_similarity(
    query_text,
    candidate_text
):

    query_age = re.search(
        r"Age:\s*(\d+)",
        query_text,
        flags=re.IGNORECASE
    )

    candidate_age = re.search(
        r"Age:\s*(\d+)",
        candidate_text,
        flags=re.IGNORECASE
    )

    if (
        not query_age
        or not candidate_age
    ):

        return 0.5

    difference = abs(
        int(
            query_age.group(1)
        )
        -
        int(
            candidate_age.group(1)
        )
    )

    return max(
        0.0,
        1.0
        -
        min(
            difference,
            50
        )
        /
        50.0
    )



# ============================================================
# RETRIEVE TOP 3 DIAGNOSES
# ============================================================

def retrieve_top3_diagnoses(
    query_text,
    query_embedding,
    document_embeddings,
    documents,
    document_texts,
    diagnoses,
    centroid_labels,
    centroid_embeddings,
):

    # Stage 1: Rank diagnosis centroids
    centroid_scores = cosine_similarity(
        [query_embedding],
        centroid_embeddings
    )[0]

    top_indices = np.argsort(
        centroid_scores
    )[::-1][:3]

    results = []

    # Stage 2: Find best case for each diagnosis
    for idx in top_indices:

        diagnosis = centroid_labels[int(idx)]

        candidate_indices = [
            i for i, label in enumerate(diagnoses)
            if label == diagnosis
        ]

        if not candidate_indices:
            continue

        candidate_embeddings = document_embeddings[
            candidate_indices
        ]

        dense_scores = cosine_similarity(
            [query_embedding],
            candidate_embeddings
        )[0]

        best_index = None
        best_score = float("-inf")
        best_parts = None

        for local_i, global_i in enumerate(candidate_indices):

            dense = float(dense_scores[local_i])

            lexical = lexical_overlap(
                query_text,
                document_texts[global_i]
            )

            age = age_similarity(
                query_text,
                document_texts[global_i]
            )

            final_score = (
                0.65 * dense
                + 0.25 * lexical
                + 0.10 * age
            )

            if final_score > best_score:

                best_score = final_score
                best_index = global_i

                best_parts = {
                    "dense_similarity": dense,
                    "lexical_overlap": lexical,
                    "age_similarity": age,
                    "hybrid_score": final_score,
                }

        results.append({
            "diagnosis": diagnosis,
            "diagnosis_centroid_score": float(
                centroid_scores[int(idx)]
            ),
            "document": documents[best_index],
            "document_text": document_texts[best_index],
            "case_score": best_score,
            "score_parts": best_parts,
        })

    if len(results) != 3:
        raise ValueError(
            "Could not retrieve three distinct diagnoses."
        )

    return results

# ============================================================
# GENERATE TOP 3 GPT DIAGNOSES
# ============================================================

def generate_top3_diagnoses(
    query,
    retrieval_results,
    model="gpt-4o-mini",
):
    """Rank three differential diagnoses from all allowed labels.

    The retrieved top three are evidence, not a hard restriction.
    """
    if len(retrieval_results) != 3:
        raise ValueError("Exactly 3 retrieval results are required.")

    candidates = []
    for rank, result in enumerate(retrieval_results, start=1):
        diagnosis = normalize_label(result["diagnosis"])
        if diagnosis not in ALLOWED_DIAGNOSES:
            raise ValueError(f"Unknown retrieval diagnosis: {diagnosis}")

        with open(result["document"], "r", encoding="utf-8") as f:
            case = json.load(f)

        candidates.append({
            "retrieval_rank": rank,
            "diagnosis": diagnosis,
            "centroid_similarity": float(result["diagnosis_centroid_score"]),
            "representative_case": patient_to_clinical_text(case),
        })

    if len({item["diagnosis"] for item in candidates}) != 3:
        raise ValueError("Retrieved diagnoses must be distinct.")

    system_prompt = f"""
You are a clinical decision-support assistant for a research prototype.
Rank the three most plausible differential diagnoses for the CURRENT patient.

Rules:
- Consider ALL diagnoses in the allowed list, not only retrieved candidates.
- The three retrieved diagnoses and training cases are supporting evidence,
  NOT mandatory selections or confirmed diagnoses.
- Prioritize the CURRENT patient's symptoms, age, and presentation.
- You MAY replace any or all retrieved diagnoses with other allowed labels
  when the current patient's evidence supports them better.
- Return EXACTLY three DISTINCT diagnosis labels, ordered from most
  to least plausible, using exact labels from the allowed list.
- Do not invent labels, assert certainty, or fabricate findings.
- Briefly explain each choice using the current patient's evidence.
- Recommend appropriate clinical assessment and urgent evaluation for
  potentially dangerous symptoms; do not prescribe treatment.
- Return JSON only in this structure:
{{
  "diagnoses": [
    {{"rank": 1, "diagnosis": "exact allowed label", "explanation": "brief reason"}},
    {{"rank": 2, "diagnosis": "exact allowed label", "explanation": "brief reason"}},
    {{"rank": 3, "diagnosis": "exact allowed label", "explanation": "brief reason"}}
  ],
  "further_evaluation": "brief follow-up guidance"
}}

Allowed diagnosis labels:
{json.dumps(ALLOWED_DIAGNOSES)}
""".strip()

    user_prompt = (
        "CURRENT PATIENT:\n" + str(query)
        + "\n\nTOP THREE RETRIEVED CANDIDATES (supporting evidence):\n"
        + json.dumps(candidates, ensure_ascii=False)
    )

    # Retry a limited number of times if GPT violates the allowed-label rules.
    # Never silently accept or replace an out-of-dataset diagnosis.
    last_error = None
    for attempt in range(1, 4):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        if last_error is not None:
            messages.append({
                "role": "user",
                "content": (
                    "Your previous output failed validation: " + str(last_error)
                    + "\nRegenerate the complete JSON response. "
                    "Use ONLY exact labels from the allowed diagnosis list, "
                    "with three distinct diagnoses ranked 1, 2, 3."
                ),
            })

        response = client.chat.completions.create(
            model=model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=messages,
        )
        try:
            content = response.choices[0].message.content
            if not content:
                raise ValueError("GPT returned an empty response.")
            result = json.loads(content)
            ranked = result.get("diagnoses")
            if not isinstance(ranked, list) or len(ranked) != 3:
                raise ValueError("GPT did not return exactly three diagnoses.")

            labels = []
            for expected_rank, item in enumerate(ranked, start=1):
                if not isinstance(item, dict) or item.get("rank") != expected_rank:
                    raise ValueError("GPT returned invalid diagnosis ranks.")
                label = normalize_label(item.get("diagnosis", ""))
                if label not in ALLOWED_DIAGNOSES:
                    raise ValueError(f"GPT returned an unknown diagnosis: {label}")
                if (not isinstance(item.get("explanation"), str)
                        or not item["explanation"].strip()):
                    raise ValueError("GPT omitted a diagnosis explanation.")
                item["diagnosis"] = label
                labels.append(label)

            if len(set(labels)) != 3:
                raise ValueError("GPT returned duplicate diagnoses.")
            if not isinstance(result.get("further_evaluation"), str):
                raise ValueError("GPT omitted further evaluation guidance.")
            return result
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            last_error = exc
            print(f"GPT Top-3 validation failed (attempt {attempt}/3): {exc}")

    raise ValueError(f"GPT Top-3 failed after 3 attempts: {last_error}")
