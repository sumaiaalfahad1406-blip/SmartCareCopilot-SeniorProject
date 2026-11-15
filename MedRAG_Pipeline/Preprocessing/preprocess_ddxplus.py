import ast
import json
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
TRAIN_CSV = os.path.join(DATASET_DIR, "df", "train", "release_train_patients.csv")
EVIDENCES_PATH = os.path.join(DATASET_DIR, "release_evidences.json")
CONDITIONS_PATH = os.path.join(DATASET_DIR, "release_conditions.json")
OUTPUT_CSV = os.path.join(DATASET_DIR, "AI Data Set with Categories.csv")


def normalize_diagnosis(text):
    if pd.isna(text):
        return ""
    return "_".join(str(text).strip().lower().replace("-", " ").split())


def parse_evidence_list(raw):
    if isinstance(raw, list):
        return raw
    if pd.isna(raw):
        return []
    try:
        return ast.literal_eval(str(raw))
    except Exception:
        try:
            return json.loads(str(raw).replace("'", '"'))
        except Exception:
            return []


def split_evidence(evidence):
    evidence = str(evidence)
    if "_@_" in evidence:
        base, value = evidence.split("_@_", 1)
        return base, value
    return evidence, ""


def decode_value(meta, value_code):
    if not value_code:
        return ""

    # DDXPlus versions differ slightly. Try common containers safely.
    for key in ["value_meaning", "value-meaning", "values", "possible-values", "possible_values"]:
        container = meta.get(key)

        if isinstance(container, dict):
            if value_code in container:
                value = container[value_code]
                if isinstance(value, dict):
                    for k in ["en", "name", "label", "meaning", "value"]:
                        if k in value:
                            return str(value[k])
                return str(value)

        if isinstance(container, list):
            for item in container:
                if isinstance(item, dict):
                    code = str(item.get("id", item.get("code", item.get("value", ""))))
                    if code == value_code:
                        for k in ["name", "label", "meaning", "en", "value"]:
                            if k in item:
                                return str(item[k])
                elif str(item) == value_code:
                    return str(item)

    return value_code.replace("_", " ")


def evidence_to_text(evidence, evidences_info):
    base, value_code = split_evidence(evidence)
    meta = evidences_info.get(base, {})
    question = meta.get("question_en", base)
    decoded = decode_value(meta, value_code)

    if decoded:
        return f"{question} Answer: {decoded}"
    return str(question)


def main():
    print("Loading DDXPlus training data...")
    df = pd.read_csv(TRAIN_CSV)
    print(f"Loaded {len(df)} patients")

    with open(EVIDENCES_PATH, "r", encoding="utf-8") as f:
        evidences_info = json.load(f)

    with open(CONDITIONS_PATH, "r", encoding="utf-8") as f:
        conditions_info = json.load(f)

    rows = []

    for idx, row in df.iterrows():
        pathology = row.get("PATHOLOGY", "")
        diagnosis = normalize_diagnosis(pathology)
        evidence_list = parse_evidence_list(row.get("EVIDENCES", "[]"))

        # IMPORTANT: keep ALL evidences, not only [:10].
        readable = [
            evidence_to_text(ev, evidences_info)
            for ev in evidence_list
        ]
        readable = [x for x in readable if x]

        initial_raw = row.get("INITIAL_EVIDENCE", "")
        initial_text = ""
        if pd.notna(initial_raw) and str(initial_raw).strip():
            initial_text = evidence_to_text(initial_raw, evidences_info)

        level1 = diagnosis
        level2 = diagnosis
        if pd.notna(pathology) and pathology in conditions_info:
            condition = conditions_info[pathology]
            condition_name = condition.get("cond-name-eng", pathology)
            level1 = normalize_diagnosis(condition_name)
            level2 = normalize_diagnosis(condition_name)

        rows.append({
            "Participant No.": str(idx + 1),
            "Age": row.get("AGE", ""),
            "Pain Presentation and Description": initial_text,
            "Pain descriptions and assorted symptoms (self-report)": "; ".join(readable),
            "Raw Evidences": json.dumps(evidence_list, ensure_ascii=False),
            "Processed Diagnosis": diagnosis,
            "Level 2": level2,
            "Level 1": level1,
        })

        if (idx + 1) % 100000 == 0:
            print(f"Processed {idx + 1}/{len(df)}")

    output_df = pd.DataFrame(rows)
    output_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"Saved {len(output_df)} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
