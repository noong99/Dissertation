# %%
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
df_original = pd.read_excel("../../Dissertation-report-Aug042025_all_plusStatusCollections_forProject.xlsx", header=0)
df = df_original.copy()

# %%
# extract the year from date.issued
df["year"] = (
    df["date.issued"]
    .astype(str)
    .str.extract(r"(\d{4})")   # pull 4-digit year
    .astype(float)
)

# %%
# 1. missing values - nan (4)
df[df['description.thesisdegreename'].isna()] 
# index 23360: embargo = YES -> nan
# index 25092: using collections -> Master of Fine Arts (MFA)
df.loc[25092, 'description.thesisdegreename'] = 'Master of Fine Arts (MFA)'
# index 25157: using collections -> Master of Fine Arts (MFA)
df.loc[25157, 'description.thesisdegreename'] = 'Master of Fine Arts (MFA)'
# index 30217: using identifier.uri -> Doctor of Engineering (DEng), specifically Doctor of Philosophy (Civil Engineering) # https://babel.hathitrust.org/cgi/pt?id=mdp.39015041110027&seq=7
df.loc[30217, 'description.thesisdegreename'] = 'Doctor of Engineering (DEng)'

# 2. Matching - Ed.D (1)
df.loc[30217, 'description.thesisdegreename'] = 'Doctor of Education (EdD)'

# 3. Matching - PhD (45751)
# use description.thesisdegreediscipline to match! (below)

# 4. Matching - Master's (380)
# use description.thesisdegreediscipline to match! (below)

# %% [markdown]
# ### Include fields which are related to research questions

# %%
# Handle, Collections, identifier.name-orcid, contributor.advisor, contributor.editor, contributor.author, date.issued, date.submitted, 
# identifier.uri, description.abstract, identifier.orcid, format., format.mimetype, language.iso, subject., description.thesisdegreediscipline, description.thesisdegreegrantor
# description.thesisdegreename, subject.other, description.thesisdegreename, title., contributor.affiliationum, contributor.affiliationumcampus, 
# identifier.uniqname, description.bitstreamurl, identifier.doi, language.rfc3066, contributor.authoremail, language.
cols = [
    "Handle", "collections", "identifier.name-orcid", 
    "contributor.advisor", "contributor.editor", "contributor.author",
    "date.issued", "date.submitted",
    "identifier.uri", 
    "description.abstract", "identifier.orcid",
    "format.", "format.mimetype",
    "language.iso", "subject.",
    "description.thesisdegreediscipline", "description.thesisdegreegrantor",
    "description.thesisdegreename", "subject.other",
    "title.", "contributor.affiliationum",
    "contributor.affiliationumcampus",
    "identifier.uniqname", "description.bitstreamurl",
    "identifier.doi", "language.rfc3066",
    "contributor.authoremail", "language."
]

df_rq= df[cols]

# %% [markdown]
# ### Thesisdiscipline

# %% [markdown]
# 1. drop nan values
# 2. matching to doctoral degree that are provided
# 3. matching to master degree and remain doctoral degree using kmeans and sentence-BERT Embedding

# %%
# missing thesisdegreediscipline
missing_idx = df_rq[df_rq['description.thesisdegreediscipline'].isna()].index
print(len(missing_idx), "are missing thesisdegreediscipline.")

# %%
# Drop missing values
df_rq = df_rq.dropna(subset=['description.thesisdegreediscipline'])

# %%
df_rq.columns

# %% [markdown]
# # 1. Get Master/Doctor from description.thesisdegreename

# %%
df_rq['description.thesisdegreename'].value_counts()

# %% [markdown]
# ### 1-1. (description.thesisdegreename not contain master or doctor) field -> master/doctor

# %%
# Ed.D. (description.thesisdegreename not contain master or doctor)
mask = df_rq["description.thesisdegreename"] == 'Ed.D.'
df_rq.loc[mask, "description.thesisdegreename"] = 'Doctor of Education'

# %% [markdown]
# ### 1-2. Make new column analysis.degreetype (Consider PhD = Doctor)
# 

# %%
import re

def classify_degree_regex(x):
    if pd.isna(x):
        return "Other"
    
    s = str(x).lower()

    # Doctoral group
    if re.search(r"(phd|doctor|edd|dph|dma|dap|deng|darch|sjd)", s):
        return "Doctoral"
    
    # Master group
    if re.search(r"(master|mfa|^ms|^ma)", s):
        return "Master"
    
    return "Other"

df_rq["analysis.degreetype"] = df_rq["description.thesisdegreename"].apply(classify_degree_regex)

# %%
df_rq['analysis.degreetype'].value_counts()

# %% [markdown]
# # 2. Mapping (Exact matching + clustering (fallback))

# %% [markdown]
# 1) Doctoral (analysis.degreetype == Doctoral)  
# - Ground truth: Rackham_Program_List_(Oct_2025).xlsx that provided(12/2) (Rackham official doctoral list)  
# - Steps:  
#     - exact match  
#     - Sentence-BERT embedding + KMeans cluster → nearest B.xlsx program fallback
# 2) Master (analysis.degreetype == Master)
# - Ground truth: Rackham Programs-of-Study 241 programs
# - Steps:
#     - exact match
#     - SBERT + KMeans → fallback program

# %%
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import process, fuzz
import requests
from bs4 import BeautifulSoup

# %% [markdown]
# ### 2-1. Load Rackham_Program_List_(Oct_2025).xlsx

# %%
df_original['contributor.affiliationumcampus'].value_counts()

# %% [markdown]
# #### When look into 'contributor.affiliationumcampus' field, there's no dearborn campus, remove dearborn related row in the xlsx file

# %%
doc_df = pd.read_excel("../Dataset/Rackham_Program_List_(Oct_2025).xlsx")  

# 1. School/College - Dearborn included row remove
doc_df = doc_df[~doc_df["School/College"].str.contains("Dearborn", case=False, na=False)]

# 2. Program - Dearborn included row remove
doc_df = doc_df[~doc_df["Department"].str.contains("Dearborn", case=False, na=False)]

# Must contain: Program, School/College, Department
doc_df["Program_clean"] = doc_df["Program"].astype(str).str.lower().str.strip()

doctoral_programs = doc_df["Program"].tolist()
doctoral_lower = doc_df["Program_clean"].tolist()

# %% [markdown]
# ### 2-2. Rackham study load

# %% [markdown]
# ![image.png](attachment:image.png)

# %%
url = "https://rackham.umich.edu/programs-of-study/"
html = requests.get(url).text
soup = BeautifulSoup(html, "html.parser")

rows = []
for tr in soup.select("table tbody tr"):
    cols = [td.get_text(strip=True) for td in tr.find_all("td")]
    print(cols)
    program, campus, school, degree_types = cols[:4]
    rows.append({
        "Program": program,
        "School_College": school,
        "Campus": campus,
        "Degree": degree_types
    })

rackham_df = pd.DataFrame(rows)
rackham_df["Program_clean"] = rackham_df["Program"].astype(str).str.lower().str.strip()

master_programs = rackham_df["Program"].tolist()
master_lower = rackham_df["Program_clean"].tolist()
print(len(master_programs))  # 241

# %% [markdown]
# ### 2-3. Clean discipline

# %%
df_rq["discipline_clean"] = (
    df_rq["description.thesisdegreediscipline"]
    .astype(str)
    .str.lower()
    .str.strip()
)

# %% [markdown]
# ### 2-4. Sentence BERT Embeddings

# %%
model = SentenceTransformer("all-MiniLM-L6-v2")

doctoral_emb = model.encode(doctoral_programs, convert_to_tensor=False)
master_emb = model.encode(master_programs, convert_to_tensor=False)

disc_texts = df_rq["discipline_clean"].tolist()
disc_emb = model.encode(disc_texts, convert_to_tensor=False)
df_rq["disc_emb"] = list(disc_emb)

# %% [markdown]
# ### 2-5. KMeans Clustering (Master/Doctoral)

# %%
k_doc = len(doctoral_programs)
k_mas = len(master_programs)

kmeans_doc = KMeans(n_clusters=k_doc, random_state=42).fit(disc_emb)
kmeans_mas = KMeans(n_clusters=k_mas, random_state=42).fit(disc_emb)

df_rq["cluster_doc"] = kmeans_doc.labels_
df_rq["cluster_mas"] = kmeans_mas.labels_

# %% [markdown]
# ### 2-6. Build cluster -> Program mapping

# %%
# Doctoral
cluster_centers_doc = kmeans_doc.cluster_centers_
sim_doc = cosine_similarity(cluster_centers_doc, doctoral_emb)
doc_cluster_to_prog = {i: doctoral_programs[np.argmax(sim_doc[i])] for i in range(k_doc)}


# Master
cluster_centers_mas = kmeans_mas.cluster_centers_
sim_mas = cosine_similarity(cluster_centers_mas, master_emb)
mas_cluster_to_prog = {i: master_programs[np.argmax(sim_mas[i])] for i in range(k_mas)}

# %% [markdown]
# ### 2-7. Helper functions (Exact match, Sentence-BERT nearest)

# %%
# Exact match
def exact_match(disc, programs, program_lower):
    if disc in program_lower:
        idx = program_lower.index(disc)
        return programs[idx]
    return None


# Sentence-BERT nearest
def sbert_nearest(d_emb, programs, prog_emb):
    sims = cosine_similarity([d_emb], prog_emb)[0]
    return programs[np.argmax(sims)]

# %% [markdown]
# ### 2-8. Final Hybrid Matching Function

# %%
def assign_program(row):
    disc = row["discipline_clean"]
    d_emb = row["disc_emb"]
    dtype = row["analysis.degreetype"]

    # ---------------- Doctoral ----------------
    if dtype == "Doctoral":
        # 1. Exact
        exact = exact_match(disc, doctoral_programs, doctoral_lower)
        if exact:
            program = exact
        else:
            # 2. Sentence-BERT nearest
            nearest = sbert_nearest(d_emb, doctoral_programs, doctoral_emb)
            if nearest:
                program = nearest
            else:
                # 3. KMeans fallback
                program = doc_cluster_to_prog[row["cluster_doc"]]

        # Add metadata (School, Department)
        row_prog = doc_df[doc_df["Program"] == program].iloc[0]
        return pd.Series({
            "analysis.program": program,
            "analysis.school_college": row_prog["School/College"],
            "analysis.department": row_prog["Department"]
        })

    # ---------------- Master ----------------
    else:
        # 1. Exact
        exact = exact_match(disc, master_programs, master_lower)
        if exact:
            program = exact
        else:
            # 2. SBERT nearest
            nearest = sbert_nearest(d_emb, master_programs, master_emb)
            if nearest:
                program = nearest
            else:
                # 3. KMeans fallback
                program = mas_cluster_to_prog[row["cluster_mas"]]

        # Add metadata (Rackham website has School only, no department)
        row_prog = rackham_df[rackham_df["Program"] == program].iloc[0]
        return pd.Series({
            "analysis.program": program,
            "analysis.school_college": row_prog["School_College"],
            "analysis.department": None  # No department info
        })


# %% [markdown]
# ### 2-9. Apply to rq_df (Dataframe)

# %%
mapped = df_rq.apply(assign_program, axis=1)
df_rq = pd.concat([df_rq, mapped], axis=1)

# %% [markdown]
# ### 2-10. Check assigned values (school_college, department, program)

# %% [markdown]
# We manually reviewed and resolved mismatches in school/college and program names between Master’s and Doctoral degree data to ensure consistent classification.

# %%
# Check
df_doc = df_rq[df_rq["analysis.degreetype"] == "Doctoral"]
df_mas = df_rq[df_rq["analysis.degreetype"] != "Doctoral"]

doc_programs = sorted(df_doc["analysis.program"].dropna().unique())
doc_schools = sorted(df_doc["analysis.school_college"].dropna().unique())
doc_departments = sorted(df_doc["analysis.department"].dropna().unique())

mas_programs = sorted(df_mas["analysis.program"].dropna().unique())
mas_schools = sorted(df_mas["analysis.school_college"].dropna().unique())

# Doctor summary table
doc_summary = (
    df_doc[[
        "analysis.program",
        "analysis.school_college",
        "analysis.department"
    ]]
    .drop_duplicates()
    .sort_values(
        ["analysis.school_college", "analysis.program"]
    )
    .reset_index(drop=True)
)

# Master summary table
mas_summary = (
    df_mas[[
        "analysis.program",
        "analysis.school_college"
    ]]
    .drop_duplicates()
    .sort_values(
        ["analysis.school_college", "analysis.program"]
    )
    .reset_index(drop=True)
)

print("Doctoral Programs Summary:")
print(doc_summary.to_string())
# print(doc_summary.dropna().unique())

print("\nMaster's Programs Summary:")
print(mas_summary.to_string())
# print(mas_summary.dropna().unique())

# %%
# Save unique program summaries
doc_summary.to_csv("doctoral_programs_unique.csv", index=False)
mas_summary.to_csv("master_programs_unique.csv", index=False)

# %% [markdown]
# #### As there's no department in Rackham website, Master's department -> None

# %% [markdown]
# # 3. Store new dataset

# %%
# remove columns that are not needed for analysis later
cols_to_remove = [
    "discipline_clean",
    "disc_emb",
    "cluster_doc",
    "cluster_mas"
]

df_save = df_rq.drop(columns=cols_to_remove, errors="ignore")

# %%
# csv
df_save.to_csv("Rackham_dissertation_metadata_kmeans.csv", index=False)

# xlsx
df_save.to_excel("Rackham_dissertation_metadata_kmeans.xlsx", index=False)


