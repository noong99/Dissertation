# Rackham Dissertation Metadata Analysis: Programs, Authors, and Faculty Roles

## Project Overview

This project is part of the Deep Blue Dissertation Research Project, a collaborative initiative with
the Rackham Graduate School in celebration of its 150th anniversary. 

Using more than a century of dissertation and master’s thesis metadata from the University of Michigan (1909–2025), this Author_Faculty_Staff files investigates questions about authorship, mentorship, and faculty involvement in graduate research.

In particular, the analysis focuses on two research questions:

**- RQ2: Which alumnus wrote the most dissertations?**
This question examines author-level productivity by constructing and disambiguating author identities using institutional identifiers (e.g., uniqname, ORCID) and name-based signals, and then ranking alumni by the number of dissertations authored.

**- RQ5: What role do faculty and staff play in dissertation authorship and mentorship?**
This question explores faculty and staff involvement through advisor and committee member metadata.
While the current analysis relies on internal metadata, the workflow is designed to be extensible to future matching against external faculty and staff reference lists.

To address these questions, the analysis combines:
- large-scale metadata cleaning and normalization,
- identifier-based and name-based disambiguation methods, and
- interpretable aggregation and trend analysis.

By systematically resolving ambiguous author records and examining faculty participation, this analyses provide a clearer view of how individual alumni contributions and faculty mentorship have shaped the university’s scholarly output over time.


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

- **Dissertation_research_subset.xlsx** 
  A curated subset of the primary dissertation metadata file, filtered and cleaned for research analysis. Includes only variables relevant to the research questions, excludes zero-coverage fields, and standardizes column naming (pdf_filename → filename).


## Project Structure

```text
Final/
├── Dataset/
│   ├── Dissertation-report-Aug042025_all_plusStatusCollections_forProject.xlsx
│   ├── DissMatchedExport.xlsx
│   ├── Rackham_Program_List_(Oct_2025).xlsx
│   ├── build_dissertation_research_subset.py
│   └── Dissertation_research_subset.xlsx
│
├── Author_Faculty_Staff/
│   ├── author_dissertation_count_after_metadata_merge.ipynb / author_dissertation_count_after_metadata_merge.py
│   │   → Counts dissertations per author after metadata integration (DissMatchedExport.xlsx)
│   │
│   ├── author_dissertation_ranking_confidence.ipynb / author_dissertation_ranking_confidence.py
│   │   → Identity resolution and confidence-based author ranking
│   │
│   ├── faculty_and_staff_dissertation_analysis.ipynb / faculty_and_staff_dissertation_analysis.py
│   │   → Analysis of dissertations authored by faculty and staff
│   │
│   ├── author_dissertation_ranking_confidence_framework.pdf
│   │   → Methodological overview of identity resolution and confidence scoring
│   │
│   ├── Analysis_Outputs/
│   │   ├── advisor_dissertation_counts.csv
│   │   │   →Yearly counts of unique dissertation advisors
│   │   ├── author_handle_pairs.csv
│   │   │   → Author names mapped to resolved identity keys (handle-based)
│   │   ├── merged_exploded_author.csv
│   │   │   → Exploded author-name–level records (one author name per row per dissertation)
│   │   ├── merged_exploded_uniq.csv
│   │   │   → Exploded uniqname-level records (one uniqname per row per dissertation)
│   │   ├── merged_without_explode.csv
│   │   │   → Enriched dissertation metadata prior to author/identifier explosion
│   │   └── top5_advisors_summary_by_year.csv
│   │       → Longitudinal summary of the top five advisors by dissertation activity
│   │
│   └── README.md
│       → Overview, methodology, and file descriptions

```

## Analysis Workflow

**Author identity resolution and confidence-based ranking**
Author names are normalized and disambiguated using a confidence-aware identity resolution framework:
- ORCID- or uniqname-based identifiers are treated as high-confidence matches
- Name-based composites are treated as lower-confidence matches
Unique dissertation handles are then used to count dissertations per individual, ensuring reliable aggregation even in the presence of duplicated or ambiguous names. Ranking prioritizes dissertation count first, followed by confidence level to favor unambiguous identifications.
Confidence scoring and author identity resolution logic are documented in detail in
author_dissertation_ranking_confidence_framework.pdf,
which describes the construction of identity keys, confidence levels, and ranking rules used in this analysis.

## Notebook Descriptions
#### 1. `author_dissertation_ranking_confidence.ipynb` / `author_dissertation_ranking_confidence.py`  
**Author-level disambiguation and confidence-based dissertation ranking (RQ2)**

This notebook addresses Research Question 2: Which alumnus wrote the most dissertations?

Using the cleaned dissertation metadata subset, the analysis performs author-level identity resolution by combining:
- Identifier-based matching (uniqname, ORCID) when available
- Name-based heuristics supplemented with degree, discipline, year, and affiliation metadata
Unique dissertations are aggregated per resolved author using dissertation handles, and authors are ranked by dissertation count.
Each author identity is assigned a confidence level reflecting the reliability of the identification.
> **Note:** Details of the confidence scoring logic, identity key construction, and ranking rules are documented in
> author_dissertation_ranking_confidence_framework.pdf.

**Outputs**
- `author_handle_pairs.csv`
  → Mapping between normalized author names and resolved identity keys used in ranking

---

#### 2. `author_dissertation_count_after_metadata_merge.ipynb` / `author_dissertation_count_after_metadata_merge.py`  
**Metadata enrichment and author-level aggregation preparation (RQ2)**

This notebook supports Research Question 2 by preparing enriched, analysis-ready dissertation metadata for author-level aggregation.

The analysis:
- Incorporates a supplemental identifier dataset (DissMatchedExport.xlsx) to fill missing uniqnames
- Aligns and merges metadata across sources
- Applies manual corrections for records with multiple or inconsistent uniqnames
- Expands multi-valued author identifiers to support flexible aggregation strategies
Both uniqname-based and name-based representations are produced to balance high-confidence attribution and broad historical coverage.

**Outputs**
- `merged_without_explode.xlsx` 
  → Enriched dissertation metadata prior to author/identifier explosion
- `merged_exploded_uniq.xlsx` 
  → One uniqname per row per dissertation (identifier-based aggregation)
- `merged_exploded_author.xlsx` 
  → One author name per row per dissertation (name-based aggregation)
  
These outputs serve as reusable intermediate layers for reproducible author-level analysis and future re-disambiguation.

---

#### 3. `faculty_and_staff_dissertation_analysis.ipynb` / `faculty_and_staff_dissertation_analysis.py`  
**Faculty and staff involvement in dissertations**

This script analyzes faculty and staff participation in dissertations using advisor, committee, and campus-level metadata.

The analysis:
- Normalizes advisor names
- Aggregates advisor activity across time
- Produces longitudinal summaries suitable for workload and mentorship analysis
The design is extensible, allowing future integration of richer faculty–staff identifiers or cross-role matching.

**Outputs**
- `advisor_dissertation_counts.csv` 
  → Yearly counts of unique dissertation advisors
- `top5_advisors_summary_by_year.csv` 
  → Longitudinal summary of the top five advisors, including total dissertations advised, active years, and advising span


## Reproducibility

Python scripts mirror notebook logic for batch execution if needed.

