# %%
import pandas as pd
import geopandas as gpd # geodataframe panda
import numpy as np # math


# %%
import os
from pandas.core.indexes.api import get_objs_combined_axis 
from pandas.core.arrays import categorical

# %%#
## create sample maps and charts for TASC wireframes and mock ups
## PLUTO 2021; 
# 1. calculate available FAR
# 2. create column with categories:
#       Lots greater than 5000 sf
#       Lots with more than 50% FAR available
# to find if available FAR is 50% or higher: Available FAR / max FAR

# 3. Create coloumn for comparison map based on Recomended CEQR thresholds
#       Lots > 1200 sf
#       Lots > 0 FAR
# 
# 4. Separate column: 
#   - recently developed, meets above CEQR criteria
#   - recently developed, Does not meet above criteria 
#   - 
#   - 
gdf["PerAvailFAR"] = (gdf['AvailFAR']/gdf['MaxFAR']*100)
gdf.head()
#%%
#read in shapefile of pluto
#%%
# open Shapefile NYC PLUTO 2021
#folder='/Users/saraeichner/Dropbox/TASC_Sara/Data/nyc_mappluto_21v4_shp'
# print(folder)
gdf= gpd.read_file('/Users/saraeichner/Dropbox/TASC_Sara/Data/nyc_mappluto_21v4_shp/MapPLUTO.shp', low_memory=False)
gdf.head()

 #%%%
#%%
gdf.columns
#%%
# find max FAR, max value of 'ResidFAR', 'CommFAR', 'FacilFAR'
gdf['MaxFAR2'] = np.nanmax(gdf[['ResidFAR', 'CommFAR', 'FacilFAR']], axis=1)
# gdf['AvailFAR']= (gdf['builtFAR']
#%%
gdf.head()
#%%

gdf['PerAvFAR'] = (gdf['AvFAR']/gdf['MaxFAR2'])*100
gdf.head()
# %%

gdf.plot(column='PerAvFAR', cmap='OrRd', scheme='quantiles', figsize=(12, 12),
legend=True, 
ax.set_axis_off(););

# %%
QN = gdf[gdf.Borough=='QN']
QN.head(20)

# %%
(QN['BuiltFAR'].head(40))

# %%
print(list(gdf.columns))
# %%
