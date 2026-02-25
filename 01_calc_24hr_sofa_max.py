### specify config.yaml path ###
config_path = "Z:/Katie/Temperature_CLIF/Temperature_Variation_Suspected_Sepsis/config.yaml"

import yaml

# Load the YAML config as a dictionary
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

data_dir = config['data_directory']
output_dir = config['output_directory']

import clifpy
import pandas as pd
from clifpy.clif_orchestrator import ClifOrchestrator

# Set up CLIFpy
co = ClifOrchestrator(config_path=config_path)

# Convert dose units
co.convert_dose_units_for_continuous_meds(
    preferred_units={
        "norepinephrine": "mcg/kg/min",
        "epinephrine": "mcg/kg/min",
        "dopamine": "mcg/kg/min",
        "dobutamine": "mcg/kg/min"
    }
)

# Create wide dataset (with vars necessary for SOFA calculation)
co.create_wide_dataset(
    tables_to_load=['vitals', 'labs', 'medication_admin_continuous', 'respiratory_support'],
    category_filters={
        'vitals': ['spo2', 'map'],
        'labs': ['platelet_count', 'bilirubin_total', 'creatinine', 'po2_arterial'],
	'patient_assessments': ['gcs_total'], 
        'medication_admin_continuous': ['norepinephrine', 'dopamine', 'epinephrine', 'dobutamine'],
        'respiratory_support': ['fio2_set', 'device_category']
    }
)
wide_df = co.wide_df

# Load admission times from clif_hospitalization
clif_hosp = pd.read_parquet(f"{data_dir}/clif_hospitalization.parquet")
clif_hosp['admission_dttm'] = pd.to_datetime(clif_hosp['admission_dttm']).dt.tz_localize('US/Eastern', ambiguous='NaT')

# Ensure time column is datetime and match on hospitalization_id
wide_df['event_time'] = pd.to_datetime(wide_df['event_time']) 
wide_df = wide_df.merge(
    clif_hosp[['hospitalization_id', 'admission_dttm']],
    on='hospitalization_id',
    how='left'
)

# Filter events to the first 24 hours of each hospitalization
within_24hr = wide_df[
    (wide_df['event_time'] >= wide_df['admission_dttm']) &
    (wide_df['event_time'] < wide_df['admission_dttm'] + pd.Timedelta(hours=24))
]

# Compute SOFA scores on these events
sofa_24hr = co.compute_sofa_scores(wide_df=within_24hr, id_name='hospitalization_id', extremal_type='worst')

# export sofa_24hr
sofa_24hr.to_csv(f"{output_directory}/sofa_24hr.csv", index=False)
sofa_24hr.to_parquet(f"{output_directory}/sofa_24hr.parquet", index=False)

