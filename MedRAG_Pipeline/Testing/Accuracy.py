"""Evaluate saved SmartCare Copilot flexible Top-3 predictions.

Run test_top3.py and/or validation_top3.py first. This script makes no API calls.
"""
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
# Choose "test", "validation", or "both".
EVALUATION_SPLIT = "test"

INPUT_FILES = {
    "test": BASE_DIR / "top3_test_results.csv",
    "validation": BASE_DIR / "top3_validation_results.csv",
}
REQUIRED_COLUMNS = [
    "patient_file", "correct_diagnosis",
    "retrieval_1", "retrieval_2", "retrieval_3",
    "gpt_1", "gpt_2", "gpt_3",
]


def normalize_diagnosis(value):
    if pd.isna(value):
        return ""
    value = str(value).lower().strip().replace("_", " ")
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    return " ".join(value.split())


def analyze(split):
    path = INPUT_FILES[split]
    if not path.is_file():
        print(f"\n{split.upper()}: No results file found: {path}")
        print(f"Run {'test_top3.py' if split == 'test' else 'validation_top3.py'} first.")
        return

    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name} is missing columns: {missing}")
    if df.empty:
        print(f"\n{split.upper()}: Results file has no patients.")
        return

    truth = df["correct_diagnosis"].map(normalize_diagnosis)
    if truth.eq("").any():
        raise ValueError(f"{path.name} contains missing reference diagnoses.")

    for source in ("retrieval", "gpt"):
        for rank in (1, 2, 3):
            df[f"{source}_{rank}_normalized"] = df[f"{source}_{rank}"].map(normalize_diagnosis)
        df[f"{source}_top1_correct"] = df[f"{source}_1_normalized"].eq(truth)
        df[f"{source}_top3_correct"] = (
            df[f"{source}_1_normalized"].eq(truth)
            | df[f"{source}_2_normalized"].eq(truth)
            | df[f"{source}_3_normalized"].eq(truth)
        )

    df["normalized_reference"] = truth
    n = len(df)
    print("\n" + "=" * 65)
    print(f"SMARTCARE COPILOT — {split.upper()} TOP-3 ACCURACY")
    print("=" * 65)
    print(f"Patients evaluated: {n}")
    print(f"Distinct reference diagnoses: {truth.nunique()}")
    for source, label in (("retrieval", "Retrieval"), ("gpt", "GPT")):
        for k in (1, 3):
            correct = int(df[f"{source}_top{k}_correct"].sum())
            print(f"{label} Top-{k}: {correct}/{n} ({100 * correct / n:.2f}%)")

    # Keep all original input columns, append correctness flags.
    original_columns = list(pd.read_csv(path, nrows=0).columns)
    flag_columns = [f"{source}_top{k}_correct" for source in ("retrieval", "gpt") for k in (1, 3)]
    patient_output = BASE_DIR / f"top3_{split}_accuracy_per_patient.csv"
    df[original_columns + flag_columns].to_csv(patient_output, index=False)

    summary = df.groupby("normalized_reference", sort=True).agg(
        patients=("normalized_reference", "size"),
        retrieval_top1_correct=("retrieval_top1_correct", "sum"),
        retrieval_top3_correct=("retrieval_top3_correct", "sum"),
        gpt_top1_correct=("gpt_top1_correct", "sum"),
        gpt_top3_correct=("gpt_top3_correct", "sum"),
    ).reset_index().rename(columns={"normalized_reference": "diagnosis"})
    for source in ("retrieval", "gpt"):
        for k in (1, 3):
            col = f"{source}_top{k}_correct"
            summary[f"{source}_top{k}_accuracy_percent"] = (
                100 * summary[col] / summary["patients"]
            ).round(2)
    diagnosis_output = BASE_DIR / f"top3_{split}_accuracy_by_diagnosis.csv"
    summary.to_csv(diagnosis_output, index=False)

    errors_output = BASE_DIR / f"top3_{split}_gpt_top3_errors.csv"
    df.loc[~df["gpt_top3_correct"], original_columns + flag_columns].to_csv(
        errors_output, index=False
    )
    print(f"GPT Top-3 misses: {int((~df['gpt_top3_correct']).sum())}")
    print("\nSaved:")
    print(f"  {patient_output.name}")
    print(f"  {diagnosis_output.name}")
    print(f"  {errors_output.name}")


def main():
    if EVALUATION_SPLIT not in ("test", "validation", "both"):
        raise ValueError('EVALUATION_SPLIT must be "test", "validation", or "both".')
    splits = ("test", "validation") if EVALUATION_SPLIT == "both" else (EVALUATION_SPLIT,)
    for split in splits:
        analyze(split)


if __name__ == "__main__":
    main()
