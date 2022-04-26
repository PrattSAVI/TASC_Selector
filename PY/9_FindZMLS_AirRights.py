
#%% -------------- IMPORT PLUTO FROM 07 and 17
from distutils.util import change_root
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd

# - Where are the folders
folder07 = r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\T_Pluto\nyc_pluto_07c'
folder17 = r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\T_Pluto\nyc_pluto_17v1'

# - Merge folders
def mergePL(folder):
    files = [i for i in os.listdir(folder) if i.split(".")[1] != "pdf"]
    df = pd.DataFrame()
    for f in files:
        temp = pd.read_csv( os.path.join(folder,f) )
        df = df.append( temp )
    return df

pl07 = mergePL(folder07)
pl17 = mergePL(folder17)

pl17.head()

#%% ---- Lots that dissapeared 
# --- List all plots in 17. If these are not available in 07, 
# It has dissappered

pd.set_option('max_columns',None)

# - Format BBL
pl07['BBL'] = pl07['BBL'].astype(str).str.split(".").str[0]
pl17['BBL'] = pl17['BBL'].astype(str).str.split(".").str[0]

# - If is lot in 07 not available in 17
lots_d = pl07[ ~pl07['BBL'].isin( pl17['BBL'].tolist() ) ]
lots_d = lots_d[lots_d['Lot']  != 9999 ]
lots_d = lots_d[ lots_d['CT2000'] != '       ']

# - Format Lat/Lon
lots_d['XCoord'] = lots_d['XCoord'].str.strip()
lots_d['YCoord'] = lots_d['YCoord'].str.strip()
lots_d = lots_d[lots_d['XCoord']  != '' ]
lots_d = lots_d[~lots_d['XCoord'].isnull() ]
lots_d['XCoord'] = lots_d['XCoord'].astype(int)
lots_d['YCoord'] = lots_d['YCoord'].astype(int)

# - Make GeoData & Plot
gdf = gpd.GeoDataFrame(
    lots_d,
    geometry=gpd.points_from_xy( lots_d['XCoord'] , lots_d['YCoord'])
    )

# These are the dissappeared lots. 
gdf.plot(markersize=1)
plt.show()

#%% ---- Group by BORO & BLOCK

# - Format
lots_d['Block'] = lots_d['Block'].astype(str)
lots_d['Block'] = lots_d['Block'].str.split('.').str[0]
lots_d['BB'] = [r['Borough']+r['Block'] for i,r in lots_d.iterrows()]

# How many are merged per block
blocks = lots_d.groupby( by=['Borough','Block'] , as_index=False).agg(
    {'BBL': len,
        'XCoord': 'first',
        "YCoord":'first'}
    )
blocks = blocks[ blocks['BBL']>1 ] #These are lot number changes
blocks.columns = ['Borough	Block	Disp_Count	XCoord	YCoord'.split('\t')]

# - Make a new BB column. I'll use this to filter lot number chages. 
blocks['BB'] = [r['Borough']+r['Block'] for i,r in blocks.iterrows()]
blocks.head()


#%%

# - Single lots that were probably merged. 
lots_2 = lots_d[ lots_d['BB'].isin( [i[0] for i in blocks['BB'].values] )]
display( lots_2.head() )


#%% --- Condos have a 75XX Lot number, this filters them
lots_3 = lots_2.copy()
lots_3['Lot'] = lots_3[ ~lots_3['Lot'].isnull() ]
lots_3['Lot'] = lots_3['Lot'].astype(str).str.split('.').str[0]
lots_3 = lots_3[ ~((lots_3['Lot'].apply(len) == 4) & (lots_3['Lot'].str[:1] == "7")) ]
lots_3 = lots_3[['BBL','Lot','Block',"XCoord","YCoord",'CondoNo']]
lots_3

gdf1 = gpd.GeoDataFrame(
    lots_3,
    geometry=gpd.points_from_xy(lots_3['XCoord'],lots_3['YCoord']),
    crs=2263
)

# These are the dissappeared lots. 
gdf1.plot(markersize=1)
plt.show()

#%% Export 

# - Possible mergers without the Condo conversions. 
file_loc = r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\LotMergers\Merged_lots_Check.csv'
lots_3.to_csv(file_loc)



#%% ---------------- ZLDA's Start Here ------------------------
# ------- ACRIS Docs are here!

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd

pd.set_option("max_columns",None)

folder = r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\LotMergers\ZLM_Zelda"
files = os.listdir( folder )

legal = pd.read_csv( os.path.join(folder,files[1]))
master = pd.read_csv( os.path.join(folder,files[2]))
master['date'] = pd.to_datetime( master['RECORDED / FILED'])

print( "---------- LEGAL ------------" )
# Legal has BBL
display( legal.head() )

print( "---------- MASTER ------------" )
# This has Doc ID
display( master.head() )

#%% -- FORMAT
# - Make BBL for Legal
# P=partial E=entire

legal['BLOCK'] = legal['BLOCK'].astype(str)
legal['BOROUGH'] = legal['BOROUGH'].astype(str)
legal['LOT'] = legal['LOT'].astype(str)

legal['bbl'] = legal['BOROUGH'] + legal['BLOCK'].astype(str).str.zfill(5) + legal['LOT'].astype(str).str.zfill(4)
legal.head()

#%% 
# --- Join Propoerty Types into the dataset
# Properties Class is recorded in another CSV

prot = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\LotMergers\ZLM_Zelda\ACRIS_-_Property_Types_Codes.csv" )
legal = legal.join(prot.drop("RECORD TYPE",axis=1).set_index("PROPERTY TYPE"),on='PROPERTY TYPE',rsuffix='_long')
legal.head()
#%% 
# Filter Data
legal_ar = legal[ legal['AIR RIGHTS'] == "Y" ]
legal_ar['gt_date'] = pd.to_datetime( legal_ar['GOOD THROUGH DATE'])
legal_ar.head()

# %% 
# Join masters and legal data
allpr = legal_ar.join( master.set_index("DOCUMENT ID") , on="DOCUMENT ID" , rsuffix="_m")
allpr

#%% Filter by Time. 
# Only Keep [2007 to 2017]
allpr2 = allpr[ (allpr['date'].dt.year > 2006) & (allpr['date'].dt.year < 2018)]
allpr2

#%% 
# -- Count Air Right transfer agreements in the dataset
gr = allpr2.groupby( by='bbl',as_index=False).size()
gr['bbl'] = gr['bbl'].astype(str)
gr.columns = ['bbl','airright_trans']
gr.sort_values(by='airright_trans')

#%% 
# Import Master Pluto
pl = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv' , dtype={'bbl':object})
pl.head()

#%% 
# Join Air rights

pl1 = pl.join(gr.set_index('bbl'),on='bbl')
pl1.sort_values(by='airright_trans',ascending=False).head()

#%% 
# Assign 1/ Y to merged lots. I'll fill 0 later on.
lots_3['merged'] = 1
lots_3 = lots_3[['BBL','merged']]\
# Join in
pl2 = pl1.join( lots_3.set_index("BBL") , on='bbl' )
pl2

#%%
# Fill NaN's to empty rows. 
pl2['merged'] = pl2['merged'].fillna(0)
pl2['airright_trans'] = pl2['airright_trans'].fillna(0)

#%%
# Clean merged Data
pl2['merged'] = pl2['merged'].astype(int)
pl2['airright_trans'] = pl2['airright_trans'].astype(int)

#%%

# --------------------- How to consider Appearing and Dissapearing Lots.

pl = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv' , dtype={'bbl':object})
pl.head()

#%%
import numpy as np
#Lot area is available in 07 but not in 17
pl['has_disappered'] = np.where(
    (~pl['LotArea_07'].isnull()) & (pl['LotArea_17'].isnull()),1,0
)

# Lots 
pl['has_appered'] = np.where(
    (~pl['LotArea_17'].isnull()) & (pl['LotArea_07'].isnull()),1,0
)

#Make sure not to inlucde minor changes
pl['has_lotincreased'] = np.where(
    (~pl['LotArea_07'].isnull()) & (~pl['LotArea_17'].isnull()) & (pl['LotArea_07'] != pl['LotArea_17']) & (pl['LotArea_07'] < pl['LotArea_17'])   & ( ~(pl['LotArea_07']/pl['LotArea_17']).between(0.90, 1.1, inclusive=False) ),1,0
)

pl['has_lotdecreased'] = np.where(
    (~pl['LotArea_07'].isnull()) & (~pl['LotArea_17'].isnull()) & (pl['LotArea_07'] != pl['LotArea_17']) & (pl['LotArea_07'] > pl['LotArea_17'])   & ( ~(pl['LotArea_07']/pl['LotArea_17']).between(0.90, 1.1, inclusive=False) ),1,0
)

# is the begning with 75
pl['lot'] = pl['bbl'].str[-4:]
pl['is_condoconv'] = np.where(
    (pl['has_appered'] == 1) & (pl['lot'].str[:2].isin(['70','75'])),1,0
)

pl['is_built'] = np.where(
    pl['YearBuilt_17'] >= 2007 , 1,0
)

pl.loc[ pl['is_condoconv']==1 , 'has_appered' ] = 0
pl = pl.drop('lot', axis=1 )


#%%
# Get previous lot bbl for condo converted. Not all are here, some are missed. 

#Find what they become
conv = pl[ pl['is_condoconv']==1].copy()
conv['lot2'] = conv['bbl'].str[-2:]
conv['lot2'] = conv['lot2'].str.zfill(4)
conv['bbl2'] = conv['bbl'].str[:-4] + conv['lot2'] 

# Match with previous similar values. 
pl['before_condo'] = None
for r in pl[ pl['bbl'].isin( conv['bbl2'].tolist()) ]['bbl'].tolist():
    if r in conv['bbl2'].tolist():
        pl.loc[ pl['bbl'] == r , 'before_condo' ] = conv[ conv['bbl2'] == r ]['bbl'].values[0]

pl[~pl['before_condo'].isnull()][['is_condoconv','before_condo','bbl']]

#%%

col = ['puma','is_built','bbl','has_disappered','has_appered','has_lotincreased','has_lotdecreased','is_condoconv'] 

gr = pl[col].groupby(by='puma').sum()
gr = gr.join( pl.groupby(by='puma',as_index=False).size().set_index('puma') )
gr.index = gr.index.astype(int)
gr.columns = gr.columns.str.replace('size','total_lots')
gr

#%%

pl.to_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv" )

#%%
# To get all altered lots that can be soft sites
# Recently built, 
# and lots that had dissappered 
# lots that had convered to condos -> How to know where they started from? 
# If lot dissappered, is there a similar BB and a L with 75XX or 70XX added? 

# This should be the filter for the Final VIZ's. 

plb = pl[
    (pl['YearBuilt_17'] >= 2007) |
    (pl['has_disappered'] == 1) |
    (pl['has_lotincreased'] == 1)
].copy()

plb = plb[ ~plb['LotArea_07'].isnull() ] # Has area in 2007
plb = plb[ ~plb['puma'].isnull() ] # Has Puma by location

# Reduce to meaningful values. 
plb = plb[ (plb['LotArea_07'] > 0.01) & (plb['LotArea_07'] < plb['LotArea_07'].quantile(0.99)) ]
plb = plb[ (plb['availFAR_perc_07'] > -100 ) & (plb['availFAR_perc_07'] <= 100) ]

#%%

col = 'LotArea_07'

x1 = plb[ plb['has_disappered']==1 ][col]
x2 = plb[ plb['YearBuilt_17'] >= 2007 ][col]

plt.hist( [x1 , x2] ,bins=200, stacked=True, color = ['r','g'])
plt.xlim(0, plb[col].quantile(0.9) )
plt.show()
#%%
