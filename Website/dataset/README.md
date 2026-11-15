## Required Dataset Files

The SmartCare Copilot website integrates the MedRAG pipeline to generate the top three differential diagnoses.

Some required files are not included in the GitHub repository because of their large size.

### 1. Clinical Retrieval Embeddings

**`clinical_retrieval_embeddings.npy`**

This file contains the precomputed clinical embeddings used for diagnosis retrieval.

It is not uploaded to GitHub because of its large size.

The embeddings can be generated using the embedding-generation functionality in `main_MedRAG.py`, after preparing the retrieval patient records.

### 2. Patient Records

The website uses processed DDXPlus patient records stored in the following structure:

```text
dataset/
├── clinical_retrieval_embeddings.npy
└── df/
    ├── train/
      └── retrieval_patients/

The website's retrieval system primarily uses the training retrieval records and the precomputed embeddings.


### 3. How to Prepare the Required Files

1. Obtain the original DDXPlus dataset.
2. Run `preprocess_ddxplus.py` to prepare the clinical dataset.
3. Run the relevant preparation scripts to generate the patient JSON records.
4. Generate the clinical retrieval embeddings using `main_MedRAG.py`.
5. Place the generated files in the dataset locations expected by the website.

### Important Note

The website does not automatically regenerate missing embeddings when launched.

The retrieval database and embedding file must be prepared before running the AI diagnosis functionality.

For further information about dataset preparation, preprocessing, validation, and testing, refer to the `MedRAG_Pipeline` folder.
