### specify directories ###
data_directory = "Z:/Katie/Temperature_CLIF/Temperature_Variation_Suspected_Sepsis/icu-clif_data_processed"
output_directory = "Z:/Katie/Temperature_CLIF/Temperature_Variation_Suspected_Sepsis/icu-clif_data_processed"

from clifpy.tables.hospital_diagnosis import HospitalDiagnosis
from clifpy.utils.comorbidity import calculate_cci

### load hospital diagnosis data ###
hosp_dx = HospitalDiagnosis(
	data_directory,
	output_directory,
	filetype = 'parquet',
    	timezone = 'US/Eastern'
)

# Calculate CCI Scores
cci_results = calculate_cci(hosp_dx, hierarchy = True)

# export cci_results
cci_results.to_csv(f"{output_directory}/cci_results.csv", index=False)

cci_results.to_parquet(f"{output_directory}/cci_results.parquet", index=False)
