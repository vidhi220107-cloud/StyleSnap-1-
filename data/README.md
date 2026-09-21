# Dataset layout

StyleSnap uses `KrushiJethe/fashion_data` from Hugging Face. The 9,300-image,
31-class dataset is a derivative of Kaggle's Fashion Product Images Dataset. Dataset
files are intentionally ignored by Git. Keep source attribution with project reports;
the Hugging Face derivative card does not declare its own license, while the upstream
Kaggle page declares MIT.

Acquire and prepare it from the project root after installing dependencies:

```bash
python scripts/download_dataset.py --download
```

This writes a JSON verification report and CSV manifest inside the ignored `data/`
folders. It converts every exported image to RGB JPEG, keeps the full raw export for
provenance, and excludes exact duplicate copies from the derived splits to prevent
data leakage. A duplicate image with conflicting class labels stops preparation.

## Recommended layout after splitting

Create one folder per class inside each split. Folder names are the source of
truth for class names, so use the exact names supplied by the real dataset and
keep them consistent across all three splits.

```text
data/
├── raw/                         # Optional: original, unsplit dataset
│   ├── <actual-class-name>/
│   │   └── image_001.jpg
│   └── ...
├── train/
│   ├── <actual-class-name>/
│   └── ...
├── validation/
│   ├── <actual-class-name>/
│   └── ...
└── test/
    ├── <actual-class-name>/
    └── ...
```

Do not create placeholder class folders. The training code will discover the
real class names and determine the output count from `train/` when it is built.

## Split rules

- Start with each image in `raw/` exactly once.
- Produce `train/`, `validation/`, and `test/` with a fixed random seed (the
  current project setting is in `src/config.py`).
- Ensure an image appears in exactly one split; avoid near-duplicate images
  crossing splits when possible.
- Preserve the same set of class folders in every split where there are enough
  images available.

The final class names are produced only by the downloaded dataset's `articleType`
field and are recorded in `data/raw/verification_report.json`; they are never
hardcoded in model code.
