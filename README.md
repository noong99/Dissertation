# Rackham Dissertation Program Mapping and Analysis

## Project Overview

This project is part of the Deep Blue Dissertation Research Project, a collaborative initiative with
the Rackham Graduate School in celebration of its 150th anniversary. Using over a century of
dissertation and master’s thesis metadata from the University of Michigan, the project examines
how academic fields, degree programs, and research themes have evolved over time.

To address questions about long-term disciplinary development, the analysis combines metadata
cleaning and normalization with embedding-based semantic clustering and trend visualization.
By aligning inconsistent historical discipline labels with modern program structures, this project
provides a more coherent view of how the university’s scholarly landscape has expanded,
diversified, and transformed across generations of graduate students.


## Data Sources
- **Dissertation-report-Aug042025_all_plusStatusCollections_forProject.xlsx** 
  Primary dataset containing 53,048 dissertation and master’s thesis records (1909–2025),
  including degree information, discipline labels, authorship metadata, and publication years.

- **Rackham_Program_List_(Oct_2025).xlsx**
  Official Rackham reference list of doctoral programs and discipline labels, used to validate and
  standardize doctoral program mappings.

- **Rackham Programs of Study website**  
  Rackham’s official listing of 241 graduate programs, used as the canonical reference for
  mapping master’s-level programs.
  
- **DissMatchedExport.xlsx**  
  Supplemental reference dataset providing campus IDs (campusid), employee IDs (emplid),
  and uniqnames, used to improve identifier completeness and resolve ambiguous author records.


## Project Structure

```text
Final/
├── Dataset/
│   ├── Dissertation-report-Aug042025_all_plusStatusCollections_*.xlsx
│   ├── DissMatchedExport.xlsx
│   └── Rackham_Program_List_(Oct_2025).xlsx
│
├── Programs_Department_College/
│   ├── 1_kmeans_data.ipynb / 1_kmeans_data.py
│   ├── 2_kmeans_data_mapping.ipynb / 2_kmeans_data_mapping.py
│   ├── 3_data_analysis.ipynb / 3_data_analysis.py
│   │
│   ├── doctoral_programs_unique.csv
│   ├── master_programs_unique.csv
│   │ 
│   ├── Rackham_dissertation_metadata_kmeans.csv / Rackham_dissertation_metadata_kmeans.xlsx
│   ├── Rackham_dissertation_metadata_kmeans_mapping.csv / Rackham_dissertation_metadata_kmeans_mapping.xslx
│   │
│   └── Analysis Figures/
│       → Generated figures used in analysis
```

## Analysis Workflow

1. Metadata preprocessing and degree classification
  Dissertation records are cleaned and classified into Doctoral or Master categories based on degree name patterns.
2. Program mapping and standardization
  Discipline labels are aligned with official Rackham program lists using a hybrid approach combining exact matching, Sentence-BERT semantic similarity, and KMeans clustering as a fallback.
3. Manual refinement
  Remaining inconsistencies in program and school/college names are manually resolved, and abbreviations are expanded to full names for clarity.
4. Downstream analysis and visualization
   Long-term trends are analyzed and visualized by degree level, school/college, department (Doctoral only), program, and dissertation title content.

## Notebook Descriptions
### 1. `1_kmeans_data.ipynb` / `1_kmeans_data.py`  
**Metadata preprocessing and initial program mapping**

This notebook performs the core preprocessing and automated program-mapping steps.

- Loads raw dissertation and master’s thesis metadata from Deep Blue
- Cleans and normalizes degree names and discipline labels
- Classifies records into **Doctoral** and **Master** degree types using rule-based patterns
- Applies a hybrid program-mapping pipeline:
  - Exact string matching against official Rackham program lists
  - Sentence-BERT semantic similarity matching
  - KMeans clustering as a fallback for noisy or ambiguous labels
- Uses:
  - *Rackham Program List (Oct. 2025)* as the ground truth for Doctoral programs
  - *Rackham Programs of Study* website as the reference for Master’s programs

**Outputs**
- `Rackham_dissertation_metadata_kmeans.csv` / `.xlsx`  
  → Dissertation metadata with assigned program, school/college, and (for Doctoral only) department
- `doctoral_programs_unique.csv`  
  → Unique Doctoral program–school–department combinations
- `master_programs_unique.csv`  
  → Unique Master’s program–school combinations

> **Note:** Department-level information is not available for Master’s programs in the Rackham
> Programs of Study data and is therefore not included at this stage.

---

### 2. `2_kmeans_data_mapping.ipynb` / `2_kmeans_data_mapping.py`  
**Manual refinement and standardization**

This notebook refines the automated mapping results to improve consistency across sources.

- Manually resolves remaining inconsistencies in:
  - School/college names
  - Program labels
- Expands abbreviations to their full names for clarity
- Aligns naming conventions between Doctoral and Master’s data sources
- Retains original program names when a definitive canonical standard cannot be established

**Outputs**
- `Rackham_dissertation_metadata_kmeans_mapping.csv` / `.xlsx`  
  → Final standardized dataset used for downstream analysis

---

### 3. `3_data_analysis.ipynb` / `3_data_analysis.py`  
**Trend analysis and topic modeling**

This notebook conducts the main analytical tasks and generates figures and tables.

- Analyzes long-term trends by:
  - Degree level (Doctoral vs Master)
  - School/college
  - Department (Doctoral only)
  - Program
- Produces time-series visualizations and summary tables
- Includes **title-based analyses**, such as:
  - Keyword frequency analysis
  - TF-IDF–based topic modeling
  - LDA topic extraction by decade
  - Sentence-BERT–based semantic clustering of dissertation titles
- Excludes 2025–2026 data in selected analyses to avoid bias from embargo-related incompleteness

**Outputs**
- Figures and tables saved in `Analysis Figures/`
- Results used in the final blog post and reporting


## Reproducibility

The analysis notebooks are numbered in execution order.
Running the notebooks sequentially reproduces the full preprocessing, mapping, and analysis workflow.
Python scripts mirror notebook logic for batch execution if needed.

