### TACS - CEQR Evaluation  
This repo contains codes used for creating a comprehensive lot scale data/viz set for NYC. Codes in the PY folder creates a temporal mapPLUTO and formats the created dataset. 
Many additional information is added to the dataset by using the additional codes in the folder as well.  

Codes include:
**Data:**
* Combining multiple Pluto datasets / formatting
* PUMA and SMA's
* Rezonings applied to lot
* Number of permits applied(A1,DM,NB)
* Lot mergers and air-right transfers (based on pluto and ACRIS)

**Analysis:**
* Exploratory Visualizations
* Transformation of datasets for determining thresholds
* Visualizations (Some are available in Charts folder)
* Feature importance calculations for selected fields

At the root of the repo is a html file, which is a simple visualization of the distribution of the dataset. This is created using D3 in Svelte. 

The analysis in progress can be viewed [here](https://docs.google.com/presentation/d/1yfW8YtFwiSTX19jY6uFw8F0U_hoSpedANLKzy8S011s/edit?usp=sharing). 

