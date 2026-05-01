# Temperature Variation in Patients with Suspected Infection

**Rationale**: Body temperature (BT) is a key vital sign in critically ill patients, with established prognostic utility. However, BT is typically evaluated statically, despite being a dynamic parameter that changes throughout hospitalization. While variation in other physiologic measures such as heart rate variability has proven clinically informative, the clinical and biological significance of temperature variation remains unexplored. 

**Objective**: To determine the clinical and biological significance of temperature variation in critically ill patients with sepsis.  

**Methods**: Perform a retrospective, observational cohort study of adult ICU patients with suspected infections within 24 hours of hospitalization. Using multivariable logistic regression models to assess the relationship between temperature variability and both 30-day mortality and culture-positive bacteremia. 

**Expected results**: An association between temperature variability on day 2 of hospitalization (24-48 hours after admission) and both 30-day mortality and culture-positive bacteremia. Expect that these associations will remain robust across various definitions of temperature variability and independent of measurement frequency or absolute temperature values (whether a patient ever mounts a fever). 

## Table of Contents

- [Overview](#overview)
- [Data Directory](#data-directory)
- [Configuration](#configuration)
- [Pipeline Details](#pipeline-details)
  - [00_renv_restore.R - Initialize R Environment](#00_renvrestoreR--initialize_R_environment)
  - [01_calc_24hr_sofa_max.py — SOFA Score Calculation](#01_calc24hrsofamaxpy--sofa-score-calculation)
  - [02_temp_var_analysis.Rmd - Cohort identification and analysis](#02_tempvaranalysisrmd--cohort-identification-and-analysis)
- [Files to Upload](#files-to-upload)

---

## Overview

This repository implements a federated analysis pipeline for a multi-site validate study of temperature variation as a predictor of patient outcomes in suspected infection. THe pipeline:

1. **Builds a cohort** of patients with suspected infection from CLIF-formatted EHR data
2. **Derives SOFA Scores** from CLIF-formatted EHR data using clifpy command in Python
3. **Defines clincal outcomes** (30-day mortality and culture-positive bacteremia)
4. **Exports figures and tables**

Each participating site runs this pipeline locally on their data. Only aggregate summary statistics are shared for pooled analysis - no patient-level data leaves the site.

### Study Design
| Element | Description |
|---------|-------------|
| **Population** | Adults (≥18 years) admitted to the ICU with suspected infection within 24 hours |
| **Exposure** | Temperature variation on day 2 of hospitalization (24-48 hours after admission) |
| **Outcome** | 30-day Mortality and culture-positive bacteremia |
| **Study Window** | Undefined|

---

## Data Directory

### Required CLIF Tables

The pipeline requires the following tables in your `data_directory`, names as `clif_<table>.<file_type>`:

| Table | Purpose |
|-------|---------|
| `clif_patient` | Demographics, death dates |
| `clif_hospitalization` | Admission dates, age |
| `clif_adt` | ADT events for ward/ICU identification |
| `clif_hospital_diagnosis` | ICD-10-CM codes for CCI calculation |
| `clif_vitals` | Temperature, map, SpO₂ |
| `clif_labs` | Absolute neutrophil count and creatinine, platelet count, WBC, arterial PO, total bilirubin for SOFA calculation |
| `clif_respiratory_support` | Device type and FiO₂ set for SOFA calculation |
| `clif_medication_admin_continuous` | Vasopressor administration |
| `clif_medication_admin_intermittent` | Administration of fever reducing drugs (e.g., Acetminophen, Ibuprofen, Aspirin), sepsis-qualifying antibiotics
| `clif_patient_assessments` | GCS scores (for SOFA calculation) |
| `microbiology_culture` | Fluid category, collection date, organism name |

### R Package Dependencies

Packages are automatically installed on first run if not present:

```r
# Data manipulation
data.table, tidyverse, lubridate

# File I/O
arrow, yaml

# Analysis
suncalc, comorbidity, tableone, broom, margins

# Visualization
patchwork

# Utilities
here, rprojroot

```

---

## Configuration

Edit `config.yaml` with your site-specific settings:

```yaml
# Site identifier
site_lowercase: "your_site"

# Input file format: parquet, csv, or fst
file_type: "parquet"

# Path to directory containing CLIF tables
data_directory: "/path/to/clif/data" 

# Output directory (project_tables/ and project_figures/ created here)
project_location: "/path/to/project/root"

#  Site location details (longitude and latitude for sun location calculations)
# specify longitude
lon <- -83.7296   (-122.6878 for OHSU)
# specify latitude
lat <- 42.2838    (45.4996 for OHSU)
```

---

## Pipeline Details

### 00_renv_restore.R

**Purpose:** Initialize the R environment

This project uses `renv` to create a reproducible, per-project R package library. The exact pacakage versions used for analysis are recorded in `renv.lock`

**Key Operations**
1. **Clone the repository** from GitHub
2. **Open `Temperature_Variation_Suspected_Infection.Rproj`** in RStudio
3. **Run the environment setup script**: `00_renv_restore.R`
   This will install `renv` if needed and restore all packages from `renv.lock`

### 01_calc_24hr_sofa_max.py — SOFA Score Calculation

**Purpose:** Use clifpy to calculate maximum SOFA score within the first 24 hours

**Key Operations**
1. **Set up clifpy** with `config.yaml`
2. **Convert dose units** from `medication_admin_continuous` to mcg/kg/min
3. **Create wide dataset** with variables necessary for SOFA calculation
4. **Get first 24hrs of each hospitalization** based on `admission_dttm` from hospitalization table
5. **Compute SOFA scores** with co.compute_sofa_scores() command in clifpy
6. **Export max SOFA scores** to .parquet file for downstream analysis

**Outputs:** `sofa_24hr.parquet` 

---

### 02_temp_var_analysis.Rmd - Cohort identification and analysis

**Purpose:** Build the analytic cohort with inclusion/exclusion criteria, derive confounding variables and outcomes of interest, and perform multivariable logistic regression analysis with multiple sensitivity tests

#### Inclusion Criteria

- Age ≥ 18 years at admission
- At least one inpatient ICU admission 
- Blood culture collected by 24 hours after admission
- Sepsis qualifying antibiotics initiated by 24 hours after admission

#### Exclusion Criteria
- Hospitalized for fewer than 48 hours
- Fewer than 2 temperature measurements 24-48 hours after admission

#### Outcome Definition

The primary outcome is **30-day mortality**

The secondary outcome is **culture-positive bacteremia** defined as a blood culture positive for Pseudomonas aeruginosa, Staphylococcus aureus, Enterococcus, Escherichia coli, or Klebsiella pneumonia

**Output Tables:**

| File | Description |
|------|-------------|
| `project_tables/table1_cat.csv` | Table 1 stratified by quartiles of temperature variation (change in temperature from patient mean) |
| `project_tables/table1_all.csv` | Table 1 for all patients in cohort|
| `project_tables/mortality_logit_results.csv` | Results from unadjusted and adjusted logistic regression models with 30-day mortality |
| `project_tables/mortality_margins.csv` | Results from marginal effects of multivariable logistic regression model with 30-day mortality |
| `project_tables/sensitivity_hospitalization_day.csv` | Sensitivity analysis with day of hospitalization |
| `project_tables/sensitivity_routine_temps.csv` | Sensitivity analysis with routine temperature measurements|
| `project_tables/sensitivity_hospitalization_day.csv` | Sensitivity analysis with day of hospitalization |
| `project_tables/sensitivity_fever.csv` | Sensitivity analysis with fever classification |
| `project_tables/bacteremia_logit_results.csv` | Results from unadjusted and adjusted logistic regression models with culture-positive bacteremia |
| `project_tables/bacteremia_margins.csv` | Results from marginal effects of multivariable logistic regression model with culture-positive bacteremia|
| `consort_flow_table ` | Numbers after inclusion and exclusion criteria are applied; used for building the consort flow diagram

**Output Figures:**

| File | Description |
|------|-------------|
| `project_figures/histogram.pdf` | Histogram of temperature variation (change in temperature from patient mean) colored by quartile |
| `project_figures/avg_temp_day.pdf` | Line plot of average temperatures measured at regular intervals (Q4 hours starting at 0:00) colored by day of hospitalization |
| `project_figures/temp_trajectory.pdf` | Trajectory of all temperature measurements over the first 6 days, colored by day of hospitalization |
| `project_figures/mortality_margins.pdf` | Forest plot from marginal effects analysis of 30-day mortality |
| `project_figures/routine_temps.pdf` | Plot of probability of temperature measurement and probability of abnormal temperature by hour of day |
| `project_figures/sensitivity_measurement_bias.pdf` | Forest plot from sensitivity analysis with routine temperature measurements |
| `project_figures/sensitivity_hospitalization_day.pdf` | Forest plot from sensitivity analysis with day of hospitalization |
| `project_figures/sensitivity_fever.pdf` | Forest plot from sensitivity analysis with fever classification |

**Output Text:**

| File | Description |
|------|-------------|
| `consort_numbers.txt` | Text printed to the console for consort diagram | 

---

## Files to Upload

After successful completion, return the contents of `project_tables` and `project_figures`. This includes all analysis artifacts, flow diagram data, figures and summary tables.
