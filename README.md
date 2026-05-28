# 🧬 Secondary Structure Prediction & Q3 Accuracy Analysis

> A production-ready bioinformatics web application for protein secondary structure prediction accuracy analysis using GOR I, GOR IV, and PHD methods — built entirely with local computation, no external prediction servers.

[![Streamlit App](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://secondary-structure-prediction-7oprqwvhvzyhdexxwidtcy.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![GitHub](https://img.shields.io/badge/Repo-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/TusharParihar128/secondary-structure-prediction)

---

## 📌 Project Background

This project was originally assigned as a mini project during the **Structural Bioinformatics** course in the MSc Bioinformatics curriculum, under the guidance of **Prof. Sangeeta Sawant**. The course covered three classical secondary structure prediction methods — GOR I, GOR IV, and PHD — and the assignment was to implement these methods and evaluate their prediction accuracy against experimentally determined secondary structures.

The project was collaboratively developed:
- **Backend** — Prediction logic, DSSP preprocessing pipeline, alignment correction, and accuracy calculation
- **Frontend (initial)** — Desktop GUI using Tkinter
- **Streamlit deployment** — Later rebuilt as an interactive web application for easy online access

---

## 🌐 Live Application

👉 **[Open Web Application](https://secondary-structure-prediction-7oprqwvhvzyhdexxwidtcy.streamlit.app/)**

No installation needed. Enter a PDB ID, paste the DSSP output, select a method, and get results instantly.

---

## 🧪 Prediction Methods

### GOR I
One of the earliest information theory–based secondary structure prediction methods, developed by Garnier, Osguthorpe, and Robson. Predicts each residue as Helix (H), Beta Strand (E), or Coil (C) based on statistical propensities derived from amino acid neighbors within a fixed sequence window.

### GOR IV
An improved version of the original GOR algorithm incorporating larger sequence windows and higher-order residue pair correlations. Statistically optimized to produce better prediction accuracy than GOR I across diverse protein families.

### PHD
A neural network–based prediction method that combines evolutionary information with sequence profiles. PHD was one of the first machine-learning approaches adopted widely in structural bioinformatics and serves as a benchmark against the information-theory methods.

---

## ⚙️ Core Features

- Automatic PDB sequence fetching
- DSSP secondary structure preprocessing and cleanup
- Prediction via GOR I, GOR IV, or PHD
- Residue-level alignment between experimental (DSSP) and predicted secondary structures
- Q3 accuracy calculation
- Per-class accuracy breakdown — Helix (H), Strand (E), Coil (C)
- Interactive bar chart visualization of accuracy
- Streamlit-based web deployment — no local setup required

---

## 🧠 The Hardest Part — Alignment Preprocessing

The most technically challenging aspect of this project was getting the **residue-level alignment perfectly correct** between the raw DSSP output and the predicted sequence.

Raw DSSP output comes in a formatted layout with line numbers, spaces, gaps, and inconsistent symbol usage that cannot be directly compared residue-by-residue:

```
Sequence and secondary structure for 1HB6 chain A

1       SQAEFDKAAE EVKHLKTKPA DEEMLFIYSH YKQATVGDIN TERPGMLDFK
         HHHHHHHHH HGGG SS    HHHHHHHHHH HHHHHT S   S    TT HH
51      GKAKWDAWNE LKGTSKEDAM KAYIDKVEEL KKKYGI
        HHHHHHHHHH TTT  HHHHH HHHHHHHHHH HHHH
```

After preprocessing, the output becomes a clean, aligned format suitable for residue-wise accuracy comparison:

```
SQAEFDKAAEEVKHLKTKPADEEMLFIYSHYKQATVGDINTERPGMLDFKGKAKWDAWNELKGTSKEDAMKAYIDKVEELKKKYGI

chhhhhhhhhhgggcssccchhhhhhhhhhhhhhhccsccsccccccchhhhhhhhhhhhccccchhhhhhhhhhhhhhhhhhhcc    Absolute
chhheehhhhhehhhhehchehhhheeechehhheeceecehhcchheehchhheehechhhcechhehhhheeehehhhhhhece    Predicted
```

The preprocessing pipeline handles:

- Removing line numbers and formatting artifacts
- Stripping spacing gaps while preserving positional accuracy
- Normalizing DSSP symbols — turns, bends, and bridges mapped to standardized H/E/C states
- Reconstructing the full continuous sequence and structure strings
- Synchronizing the experimental and predicted sequences at the residue level

This entire pipeline is implemented in `preprocessing.py` and was by far the most debugging-intensive part of the project — even with assistance, getting the alignment logic right required careful iteration and testing across multiple PDB entries.

---

## 🧩 Preprocessing Pipeline — `preprocessing.py`

The preprocessing module is the backbone of the accuracy calculation system.

| Function | Purpose |
|---|---|
| `modify_secondary_structure()` | Adjusts raw DSSP structure formatting |
| `process_sequence_data()` | Generates residue-aligned sequence blocks |
| `process_dssp()` | Converts DSSP spacing and symbols into usable format |
| `remove_stars()` | Cleans unwanted formatting artifacts |
| `clean_lines()` | Removes line numbers and extra whitespace |
| `process_cleaned_data()` | Produces the final aligned sequence + structure string |
| `process_dssp_pipeline()` | Orchestrates the complete preprocessing workflow |

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python |
| Structure Preprocessing | Custom DSSP processing pipeline |
| Prediction Methods | GOR I, GOR IV, PHD (implemented locally) |
| Web Application | Streamlit |
| Initial Desktop GUI | Tkinter |
| Visualization | Matplotlib / Streamlit charts |

---

## 📂 Repository Structure

```
secondary-structure-prediction/
│
├── app.py               # Streamlit application entry point
├── main.py              # Core orchestration logic
├── preprocessing.py     # DSSP preprocessing and alignment pipeline
├── GOR_I.py             # GOR I prediction method
├── GOR_IV.py            # GOR IV prediction method
├── PHD.py               # PHD prediction method
├── PDB.py               # PDB sequence fetching utilities
├── w_plot.py            # Accuracy visualization and plotting
├── requirements.txt     # Python dependencies
└── README.md
```

---

## 📊 Application Output

For each prediction run, the application displays:

- Full sequence alignment — experimental vs predicted structure
- Q3 accuracy percentage
- Per-class counts — Helix (H), Strand (E), Coil (C), Total AA
- Bar chart visualization of structural class distribution

---

## 🚀 Running Locally

```bash
git clone https://github.com/TusharParihar128/secondary-structure-prediction.git
cd secondary-structure-prediction
pip install -r requirements.txt
streamlit run app.py
```

---

## 🤝 Acknowledgement

Special thanks to **Prof. Sangeeta Sawant** for introducing the foundational concepts of protein secondary structure prediction and for the mini project assignment that started this work.

---

## 📸 Preview

![Application Preview](https://raw.githubusercontent.com/TusharParihar128/secondary-structure-prediction/main/preview.png)

> *Built as part of MSc Bioinformatics coursework — expanded into a fully deployed web application.*
