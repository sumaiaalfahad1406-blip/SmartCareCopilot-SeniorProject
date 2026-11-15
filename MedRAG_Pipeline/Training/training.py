import json
import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(
    BASE_DIR,
    "dataset"
)

SOURCE_CSV = os.path.join(
    DATASET_DIR,
    "AI Data Set with Categories.csv"
)

OUTPUT_FOLDER = os.path.join(
    DATASET_DIR,
    "df",
    "train",
    "retrieval_patients"
)


# ============================================================
# TRAINING SETTINGS
# ============================================================

# Use 240 training patients from each diagnosis.
# 49 diagnoses x 240 = 11,760 training patients.

PATIENTS_PER_DIAGNOSIS = 240

# Keep the sampling reproducible.
RANDOM_STATE = 42


# ============================================================
# CLEAN VALUES
# ============================================================

def clean(value):

    if pd.isna(value):
        return ""

    return str(value)


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("CREATING BALANCED TRAINING / RETRIEVAL BANK")
    print("=" * 70)

    print(f"\nPatients per diagnosis: {PATIENTS_PER_DIAGNOSIS}")
    print(f"Random state: {RANDOM_STATE}")

    # --------------------------------------------------------
    # Load training dataset
    # --------------------------------------------------------

    df = pd.read_csv(
        SOURCE_CSV
    )

    print(
        f"\nOriginal training rows: "
        f"{len(df)}"
    )

    # --------------------------------------------------------
    # Prepare output folder
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    # Remove old retrieval JSON files.
    # This prevents old and new training banks from mixing.

    old_files_removed = 0

    for name in os.listdir(
        OUTPUT_FOLDER
    ):

        if name.endswith(".json"):

            os.remove(
                os.path.join(
                    OUTPUT_FOLDER,
                    name
                )
            )

            old_files_removed += 1

    print(
        f"Old retrieval files removed: "
        f"{old_files_removed}"
    )

    # --------------------------------------------------------
    # Clean diagnosis column
    # --------------------------------------------------------

    df[
        "Processed Diagnosis"
    ] = (

        df[
            "Processed Diagnosis"
        ]

        .fillna("")

        .astype(str)
    )

    df = df[
        df[
            "Processed Diagnosis"
        ].str.strip() != ""
    ].copy()

    # --------------------------------------------------------
    # Balanced sampling
    # --------------------------------------------------------

    balanced_parts = []

    print(
        "\nSelecting training patients "
        "for each diagnosis:\n"
    )

    for diagnosis, group in df.groupby(
        "Processed Diagnosis"
    ):

        n = min(
            PATIENTS_PER_DIAGNOSIS,
            len(group)
        )

        sampled = group.sample(
            n=n,
            random_state=RANDOM_STATE
        )

        balanced_parts.append(
            sampled
        )

        print(
            f"{diagnosis}: "
            f"selected {n} of {len(group)}"
        )

    # --------------------------------------------------------
    # Combine all diagnoses
    # --------------------------------------------------------

    balanced = pd.concat(
        balanced_parts,
        ignore_index=True
    )

    # Shuffle the final training bank.
    balanced = balanced.sample(
        frac=1,
        random_state=RANDOM_STATE
    ).reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # Save each training patient as JSON
    # --------------------------------------------------------

    print(
        "\nCreating retrieval patient files..."
    )

    for idx, row in balanced.iterrows():

        patient = {

            "Participant No.": clean(
                row.get(
                    "Participant No.",
                    idx + 1
                )
            ),

            "Age": clean(
                row.get(
                    "Age",
                    ""
                )
            ),

            "Pain Presentation and Description Areas of pain as per physiotherapy input": clean(
                row.get(
                    "Pain Presentation and Description",
                    ""
                )
            ),

            "Pain descriptions and assorted symptoms (self-report) Associated symptoms include: parasthesia, numbness, weakness, tingling, pins and needles": clean(
                row.get(
                    "Pain descriptions and assorted symptoms (self-report)",
                    ""
                )
            ),

            "Raw Evidences": clean(
                row.get(
                    "Raw Evidences",
                    ""
                )
            ),

            "Processed Diagnosis": clean(
                row.get(
                    "Processed Diagnosis",
                    ""
                )
            ),

            "Level 2": clean(
                row.get(
                    "Level 2",
                    ""
                )
            ),

            "Level 1": clean(
                row.get(
                    "Level 1",
                    ""
                )
            ),
        }

        out = os.path.join(
            OUTPUT_FOLDER,
            f"retrieval_{idx + 1}.json"
        )

        with open(
            out,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                patient,
                f,
                indent=2,
                ensure_ascii=False
            )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    diagnosis_count = (
        balanced[
            "Processed Diagnosis"
        ]
        .nunique()
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "TRAINING BANK CREATED"
    )

    print(
        "=" * 70
    )

    print(
        f"\nDiagnoses represented: "
        f"{diagnosis_count}"
    )

    print(
        f"Patients per diagnosis requested: "
        f"{PATIENTS_PER_DIAGNOSIS}"
    )

    print(
        f"Total training patients: "
        f"{len(balanced)}"
    )

    print(
        f"\nSaved to:\n"
        f"{OUTPUT_FOLDER}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()