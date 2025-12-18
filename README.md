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

Final/
├── Dataset/
│   ├── Dissertation-report-Aug042025_all_plusStatusCollections_*.xlsx
│   ├── DissMatchedExport.xlsx
│   └── Rackham_Program_List_(Oct_2025).xlsx
│
├── Programs_Department_College/
│   ├── 1_kmeans_data.ipynb / .py
│   │   → Text preprocessing and embedding generation for program names
│   │
│   ├── 2_kmeans_data_mapping.ipynb / .py
│   │   → KMeans clustering and program mapping
│   │
│   ├── 3_data_analysis.ipynb / .py
│   │   → Downstream analysis and visualization
│   │
│   ├── doctoral_programs_unique.csv
│   ├── master_programs_unique.csv
│   │   → Unique program name lists by degree level
│   │
│   ├── Rackham_dissertation_metadata_kmeans.csv
│   ├── Rackham_dissertation_metadata_kmeans_mapping.csv
│   │   → Output datasets with cluster labels and mapped metadata
│   │
│   └── Analysis Figures/
│       → Generated figures used in analysis and reporting



RQ1
Use .... variables for data analysis.

kmeans_bert_data: Rackham_dissertation_metadata_kmeans.csv (.xlsx), doctoral_programs_unique.csv, master_programs_unique.csv
kmeans_bert_data_mapping: Rackham_dissertation_metadata_kmeans_mapping.csv (.xlsx)

Department- not exist for masters

[Mapping]
- school/college: 
- programs: 
