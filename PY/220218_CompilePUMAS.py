
#%%
# Import Dependencies

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd

pd.set_option( "max_columns",None)

#%%
# Import Puma geometry

acs07 = gpd.read_file( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\CensusDataIndicators_PUMAs\ACS_Indicators_2007-2009_PUMA00.geojson')
acs10 = gpd.read_file( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\CensusDataIndicators_PUMAs\ACS_Indicators_2010-2017_PUMA10.geojson')
display( acs07.head() )
display( acs10.head() )

#%%
# Import Master Pluto

pl = pd.read_csv( 
    r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv',
    dtype={'bbl': object,'puma':object})
pl['puma'] = pl['puma'].str.split('.').str[0]
display( pl.head() )

gdf = gpd.GeoDataFrame(
    pl,
    geometry=gpd.points_from_xy( pl['XCoord'],pl['YCoord']),
    crs=2263
)

gdf.plot(markersize=0.1)
plt.show()

#%%
# Merge 2007 and 2017 geo with housing, see the housing number is the same

gdf = gdf[ ~gdf['XCoord'].isnull() ]
gdf = gdf[ ~gdf['YCoord'].isnull() ]

s1 = gpd.sjoin( gdf[['UnitsRes_07','bbl','geometry']] , acs07 )
gr1 = s1[['UnitsRes_07','geometry','PUMA5CE00']].groupby('PUMA5CE00').sum()

acs10 = acs10.to_crs( 2263 )
s2 = gpd.sjoin( gdf[['UnitsRes_07','bbl','geometry']] , acs10 )

gr2 = s2[['UnitsRes_07','geometry','PUMACE10']].groupby('PUMACE10').sum()

grt = gr1.join( gr2 , rsuffix='_10' )
grt['dif'] = grt['UnitsRes_07'] - grt['UnitsRes_07_10']
grt['pdif'] = (grt['dif'] * 100 / grt['UnitsRes_07']).round(2)

#Show percentage of differene in the number of Res Units
grt.sort_values(by='pdif')

#%%
# Join 07 to 17 dataset
# Format PUMA ACS
acs = acs07.drop("geometry",axis=1).join( acs10.set_index('PUMACE10') , on='PUMA5CE00'  )

acs.drop(
    ['STATEFP10','GEOID10','NAMELSAD10','MTFCC10','STATEFP00','PUMA5ID00','NAMELSAD00','MTFCC00','FUNCSTAT00','ALAND00','AWATER00','INTPTLAT00','INTPTLON00'],
    axis = 1
)

acs.head()

#%%
# Count Everything per puma
import numpy as np

#not compact ~ 0.4
pl['not_Compact'] = np.where(
    pl['Compact_07'] < pl['Compact_07'].quantile(0.1),
    0,1
) 

#Assed Land/Improve Ratio Increased
pl['asses_ratio_inc'] = np.where(
    pl['AssedImprov_perc_07'] <  pl['AssedImprov_perc_17'],
    1,0
)

pl['puma'] = pl['puma'].astype(str).str.zfill(5)
pl = pl[ pl['puma'] != '00nan' ] # These are the tiny tiny lots by east queens and BK

# Aggregate columns together
gr = pl.groupby( by='puma').agg(
    {
        'bbl': len,
        'airright_trans':sum,
        'merged':sum,
        'OwnerName_07':'nunique', # number of unique
        'UnitsRes_Increased':sum,
        'was_Landmark':sum,
        'st_2007':sum,
        'st_2017':sum,
        'permits_07':sum,
        'permits_17':sum,
        'recent_alter':sum,
        'not_Compact':sum,
        'asses_ratio_inc':sum,
        "UnitsRes_07":sum,
        "UnitsRes_17":sum
    }
)

# Correct Columns Names
gr.columns = gr.columns.str.replace('bbl','NU_lots')
gr.columns = gr.columns.str.replace('airright_trans','NU_airRightTrans')
gr.columns = gr.columns.str.replace('merged','NU_mergedLots')
gr.columns = gr.columns.str.replace('OwnerName_07','NU_uniqueOwners')
gr.columns = gr.columns.str.replace('UnitsRes_Increased','NU_unitResInc')
gr.columns = gr.columns.str.replace('was_Landmark','NU_landmark')
gr.columns = gr.columns.str.replace('st_2007','NU_rentSt_07')
gr.columns = gr.columns.str.replace('st_2017','NU_rentSt_17')
gr.columns = gr.columns.str.replace('permits_07','NU_permits_07')
gr.columns = gr.columns.str.replace('permits_17','NU_permits_17')

#Correct Tyoes
gr['NU_permits_07'] = gr['NU_permits_07'].astype(int)
gr['NU_permits_17'] = gr['NU_permits_17'].astype(int)
gr['NU_rentSt_07'] = gr['NU_rentSt_07'].astype(int)
gr['NU_rentSt_17'] = gr['NU_rentSt_17'].astype(int)

#Calculate percentages
gr['PERC_unitResInc'] = (gr['NU_unitResInc'] / gr['NU_lots']).round(2) * 100
gr['PERC_landmark'] = (gr['NU_landmark'] / gr['NU_lots']).round(2) * 100
gr['PERC_rentSt_07'] = (gr['NU_rentSt_07'] / gr['UnitsRes_07']).round(2) * 100
gr['PERC_rentSt_17'] = (gr['NU_rentSt_17'] / gr['UnitsRes_17']).round(2) * 100
gr['PERC_recentAlter'] = (gr['recent_alter'] / gr['NU_lots']).round(2) * 100 
gr['PERC_notCompact'] = (gr['not_Compact'] / gr['NU_lots']).round(2) * 100 
gr['PERC_assesedRatioInc'] = (gr['asses_ratio_inc'] / gr['NU_lots']).round(2) * 100 

gr = gr.drop( ['recent_alter','not_Compact','asses_ratio_inc','UnitsRes_07','UnitsRes_17'] , axis = 1 )
gr.head(12)

#%%
# Format and clean up
acs1 = acs.drop( 'STATEFP00 PUMA5ID00 NAMELSAD00 MTFCC00 FUNCSTAT00 ALAND00 AWATER00 INTPTLAT00 INTPTLON00'.split(" "),axis=1)
acs1 = acs1.drop('Area_1 STATEFP10 GEOID10 NAMELSAD10 MTFCC10'.split(' '),axis = 1)

acs1.columns = acs1.columns.str.replace('PUMA5CE00','puma')
acs1.head()
#add grouped values to acs files
acs1 = acs1.join( gr , on='puma')

#Remvoe the tiny polygons in the east
acs1['area'] = acs1.to_crs(2263).area
acs1 = acs1[ acs1['area'] > 90000 ]

acs1.plot( column = 'PERC_notCompact' , legend = True )
plt.show() 

#%%
# Merge with previous PUMA file
puma = puma['puma screen_failed screen_passed tot_lot_count screen_failed_perc dev_trends_permit dev_trends_lots_altered_perc dev_trends_constrcution'.split(' ')]

acs2 = acs1.join( puma.set_index('puma') , on='puma' )
acs2.head()

#%%
# Reorder columns in Master PUMA
cols = ['TotPop_07',
 'TotHH_07',
 'TotHUnit_07',
 'PercOcc_07',
 'PercVac_07',
 'PerRentOcc_07',
 'PerOwnOcc_07',
 'PerHHBelowPov_07',
 'LimELP_07',
 'EA_GrdPf_07',
 'TotPop_08',
 'TotHH_08',
 'TotHUnit_08',
 'PercOcc_08',
 'PercVac_08',
 'PerRentOcc_08',
 'PerOwnOcc_08',
 'PerHHBelowPov_08',
 'LimELP_08',
 'EA_GrdPf_08',
 'TotPop_09',
 'TotHH_09',
 'TotHUnit_09',
 'PercOcc_09',
 'PercVac_09',
 'PerRentOcc_09',
 'PerOwnOcc_09',
 'PerHHBelowPov_09',
 'LimELP_09',
 'EA_GrdPf_09',
 'GRAPI>30_07',
 'GRAPI>30_08',
 'GRAPI>30_09',
 'SMOCAPI>30_07',
 'SMOCAPI>30_08',
 'SMOCAPI>30_09',
 'GRAPI>30_10',
 'GRAPI>30_11',
 'GRAPI>30_12',
 'GRAPI>30_13',
 'GRAPI>30_14',
 'GRAPI>30_15',
 'GRAPI>30_16',
 'GRAPI>30_17',
 'SMOCAPI>30_10',
 'SMOCAPI>30_11',
 'SMOCAPI>30_12',
 'SMOCAPI>30_13',
 'SMOCAPI>30_14',
 'SMOCAPI>30_15',
 'SMOCAPI>30_16',
 'SMOCAPI>30_17',
 'TotPop_10',
 'TotHH_10',
 'TotHUnit_10',
 'PercOcc_10',
 'PercVac_10',
 'PerRentOcc_10',
 'PerOwnOcc_10',
 'PerHHBelowPov_10',
 'LimELP_10',
 'EA_GrdPfD_10',
 'TotPop_11',
 'TotHH_11',
 'TotHUnit_11',
 'PercOcc_11',
 'PercVac_11',
 'PerRentOcc_11',
 'PerOwnOcc_11',
 'PerHHBelowPov_11',
 'LimELP_11',
 'EA_GrdPf_11',
 'TotPop_12',
 'TotHH_12',
 'TotHUnit_12',
 'PercOcc_12',
 'PercVac_12',
 'PerRentOcc_12',
 'PerOwnOcc_12',
 'PerHHBelowPov_12',
 'LimELP_12',
 'EA_GrdPf_12',
 'TotPop_13',
 'TotHH_13',
 'TotHUnit_13',
 'PercOcc_13',
 'PercVac_13',
 'PerRentOcc_13',
 'PerOwnOcc_13',
 'PerHHBelowPov_13',
 'LimELP_13',
 'EA_GrdPf_13',
 'TotPop_14',
 'TotHH_14',
 'TotHUnit_14',
 'PercOcc_14',
 'PercVac_14',
 'PerRentOcc_14',
 'PerOwnOcc_14',
 'PerHHBelowPov_14',
 'LimELP_14',
 'EA_GrdPf_14',
 'TotPop_15',
 'TotHH_15',
 'TotHUnit_15',
 'PercOcc_15',
 'PercVac_15',
 'PerRentOcc_15',
 'PerOwnOcc_15',
 'PerHHBelowPov_15',
 'LimELP_15',
 'EA_GrdPf_15',
 'TotPop_16',
 'TotHH_16',
 'TotHUnit_16',
 'PercOcc_16',
 'PercVac_16',
 'PerRentOcc_16',
 'PerOwnOcc_16',
 'PerHHBelowPov_16',
 'LimELP_16',
 'EA_GrdPf_16',
 'TotPop_17',
 'TotHH_17',
 'TotHUnit_17',
 'PercOcc_17',
 'PercVac_17',
 'PerRentOcc_17',
 'PerOwnOcc_17',
 'PerHHBelowPov_17',
 'LimELP_17',
 'EA_GrdPf_17']

#Make a DF with columns names
df = pd.DataFrame(
    data = cols,
)

df.columns = ['col']
# Seperate year and values
df['year'] = df['col'].str.split("_").str[1]
df['val'] = df['col'].str.split("_").str[0]
# Save new sorted values
acs_cols = df.sort_values(['val','year'])['col'].tolist()
#Remvoe the  to be sorted, sort and re-add
acs3 = acs2[ acs2.columns[ ~acs2.columns.isin( acs_cols) ].tolist() + acs_cols ]

acs3.head()

#%%
# Export 
acs3 = acs3.set_crs(4326,allow_override=True)
acs3.to_file(
    r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_PUMA.geojson",
    driver="GeoJSON",
    encoding = 'utf-8'
)


# %% ------------- START HERE -------------------
# Import Master PUMA
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

puma = gpd.read_file(r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_PUMA.geojson")
puma.head()

#%%
# Get 07 Data
cols = [
    'TotPop_07',
 'TotHH_07',
 'TotHUnit_07',
 'PercOcc_07',
 'PercVac_07',
 'PerRentOcc_07',
 'PerOwnOcc_07',
 'PerHHBelowPov_07',
 'LimELP_07',
 'EA_GrdPf_07',
 'TotPop_08',
 'TotHH_08',
 'TotHUnit_08',
 'PercOcc_08',
 'PercVac_08',
 'PerRentOcc_08',
 'PerOwnOcc_08',
 'PerHHBelowPov_08',
 'LimELP_08',
 'EA_GrdPf_08',
 'TotPop_09',
 'TotHH_09',
 'TotHUnit_09',
 'PercOcc_09',
 'PercVac_09',
 'PerRentOcc_09',
 'PerOwnOcc_09',
 'PerHHBelowPov_09',
 'LimELP_09',
 'EA_GrdPf_09',
 'GRAPI>30_07',
 'GRAPI>30_08',
 'GRAPI>30_09',
 'SMOCAPI>30_07',
 'SMOCAPI>30_08',
 'SMOCAPI>30_09',
 'GRAPI>30_10',
 'GRAPI>30_11',
 'GRAPI>30_12',
 'GRAPI>30_13',
 'GRAPI>30_14',
 'GRAPI>30_15',
 'GRAPI>30_16',
 'GRAPI>30_17',
 'SMOCAPI>30_10',
 'SMOCAPI>30_11',
 'SMOCAPI>30_12',
 'SMOCAPI>30_13',
 'SMOCAPI>30_14',
 'SMOCAPI>30_15',
 'SMOCAPI>30_16',
 'SMOCAPI>30_17',
 'TotPop_10',
 'TotHH_10',
 'TotHUnit_10',
 'PercOcc_10',
 'PercVac_10',
 'PerRentOcc_10',
 'PerOwnOcc_10',
 'PerHHBelowPov_10',
 'LimELP_10',
 'EA_GrdPfD_10',
 'TotPop_11',
 'TotHH_11',
 'TotHUnit_11',
 'PercOcc_11',
 'PercVac_11',
 'PerRentOcc_11',
 'PerOwnOcc_11',
 'PerHHBelowPov_11',
 'LimELP_11',
 'EA_GrdPf_11',
 'TotPop_12',
 'TotHH_12',
 'TotHUnit_12',
 'PercOcc_12',
 'PercVac_12',
 'PerRentOcc_12',
 'PerOwnOcc_12',
 'PerHHBelowPov_12',
 'LimELP_12',
 'EA_GrdPf_12',
 'TotPop_13',
 'TotHH_13',
 'TotHUnit_13',
 'PercOcc_13',
 'PercVac_13',
 'PerRentOcc_13',
 'PerOwnOcc_13',
 'PerHHBelowPov_13',
 'LimELP_13',
 'EA_GrdPf_13',
 'TotPop_14',
 'TotHH_14',
 'TotHUnit_14',
 'PercOcc_14',
 'PercVac_14',
 'PerRentOcc_14',
 'PerOwnOcc_14',
 'PerHHBelowPov_14',
 'LimELP_14',
 'EA_GrdPf_14',
 'TotPop_15',
 'TotHH_15',
 'TotHUnit_15',
 'PercOcc_15',
 'PercVac_15',
 'PerRentOcc_15',
 'PerOwnOcc_15',
 'PerHHBelowPov_15',
 'LimELP_15',
 'EA_GrdPf_15',
 'TotPop_16',
 'TotHH_16',
 'TotHUnit_16',
 'PercOcc_16',
 'PercVac_16',
 'PerRentOcc_16',
 'PerOwnOcc_16',
 'PerHHBelowPov_16',
 'LimELP_16',
 'EA_GrdPf_16',
 'TotPop_17',
 'TotHH_17',
 'TotHUnit_17',
 'PercOcc_17',
 'PercVac_17',
 'PerRentOcc_17',
 'PerOwnOcc_17',
 'PerHHBelowPov_17',
 'LimELP_17',
 'EA_GrdPf_17']

a = []
for i in cols:
    if i.rsplit("_",1)[1] == "07":
        print(i)
        a.append( i )
pacs = puma[ ['puma'] + a + ['geometry'] ]
pacs = pacs.set_index( 'puma' )
pacs.plot( column = cols[8] , cmap='OrRd' , legend=True) # Limited English
plt.title("Limited English Profficiency")
plt.show()

#%% Displacement INDEX
# Create Ranks
a = ['PercOcc_07', # Percent Occupied Housing Units BAD 
    'EA_GrdPf_07', # Educational GOOD
    'SMOCAPI>30_07', # Owners Cost BAD
    'PerRentOcc_07', # Percent Renter Occupied Housing Units BAD
    'PerHHBelowPov_07', # Percent Households Below Poverty BAD 
    'LimELP_07', # Limited Eng BAD
    'GRAPI>30_07' # Gross Rent as Percent of Income > 30% BAD
]
pacs['EA_GrdPf_07'] = pacs['EA_GrdPf_07'] * -1
divs = 10
for col in a:
    pacs["{}_rank".format(col) ] = pd.qcut( 
        pacs[col] , 
        q = [i/10 for i in range(divs+1)] , 
        labels = [i+1 for i in range(divs)]
        )

pacs.plot( column = 'EA_GrdPf_07' , categorical = False , cmap = 'OrRd' , legend=True)
plt.show()

#%%
# Ranks for 
ranks = pacs[ [ i+"_rank" for i in a ] ].copy()
ranks['Overall'] = ranks.mean(axis=1)
ranks.sample(12)

pacs = pacs.join( ranks['Overall'] )
pacs.head()

#%%

pacs.to_crs(2263).plot( column = "Overall" , cmap='OrRd' , legend=True, figsize=(15,15))
plt.title( "Overall Vulnerability Index")
sns.despine(top=True,left=True,right=True,bottom=True)
plt.tick_params(left=False,bottom=False,labelleft=False,labelbottom=False)
plt.savefig(r"C:\Users\csucuogl\Dropbox\TASC Application\Charts\OverAllVuln.png")
plt.show()

#%%
for i in pacs.columns[ pacs.columns.str.contains("_rank") ].tolist():
    pacs[i] = pacs[i].astype(str) 

pacs.to_file(
    r"C:\Users\csucuogl\Downloads\Master_PUMA.geojson",
    driver="GeoJSON",
    encoding = 'utf-8'
)

#%% 

for i in pacs.columns[ pacs.columns.str.contains("_rank") ].tolist():
    pacs[i] = pacs[i].astype(str) 