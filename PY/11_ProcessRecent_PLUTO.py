
'''
This is the begining of an automated way to process 
new MapPluto Data

Creates a simplified file with recent-alter,... column for future filtering. 
'''
#%%
# Import
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import fiona

path = r"C:\Users\csucuogl\Desktop\DATA\NYC\MapPLUTO\MapPLUTO_21v3.gdb"

layerlist = fiona.listlayers(path)

pl = gpd.read_file(
    path,
    driver="FileGDB",
    layer = layerlist[0]
)

pd.set_option( "max_columns" , None )
pl.head()


#%%
# Adjust crs
pl = pl.set_crs("EPSG:2263")
pl.crs
#%%
# Simpler Data - Additional Columns 
#Remove unnecessary columns
pl = pl['Borough,Block,Lot,Address,BldgClass,LandUse,LotArea,UnitsRes,UnitsTotal,AssessLand,AssessTot,ExemptTot,YearBuilt,YearAlter1,YearAlter2,HistDist,Landmark,BuiltFAR,ResidFAR,CommFAR,FacilFAR,BBL,XCoord,YCoord,geometry'.split(",")].copy()

pl = pl.dropna(axis=0,subset=['LandUse'])
pl['LandUse'] = pl['LandUse'].astype(int).astype(str)
pl['LandUse'] = pl['LandUse'].str.zfill(2) 

pl['BBL'] = pl['BBL'].astype(str)
pl['BBL'] = pl['BBL'].str.split(".",0).str[0]

#FAR
pl['maxFAR'] = pl[ 'ResidFAR,CommFAR,FacilFAR'.split(',') ].max(axis=1) # Select highest of all FARs
#FAR - %
pl['availFAR_perc'] = (pl['maxFAR'] - pl['BuiltFAR']) / pl['maxFAR'] * 100
pl['availFAR_perc'] = pl['availFAR_perc'].round( 1 )

#Year Alteration
#Year Recent Change is alter
pl['YearAlter'] = pl[ ['YearAlter1','YearAlter2'] ].max( axis=1 )
pl['Year_Recent_Change'] = pl[ ['YearAlter1','YearAlter2','YearBuilt'] ].max( axis=1 )
pl['recent_alter'] = np.where(
    pl['Year_Recent_Change'] > 2012, 1, 0
)

pl['recent_built'] = np.where(
    pl['YearBuilt'] > 2012, 1, 0
)

#Imporevment
pl['AssedImprov_perc'] = ((pl['AssessTot'] - pl['AssessLand']) / pl['AssessTot']) * 100
pl['AssedImprov_perc'] = pl['AssedImprov_perc'].round(1)

pl.head()

#%%
# Remove hard to Relocate Lots
remove_bdlgs = 'Q0 Q1 T1 T2 U1 U2 U3 W1 Z5 Z8'.split( ' ' )
pl = pl[ ~pl['BldgClass'].isin(remove_bdlgs)]

# Remvoe Landmarks
pl = pl[ pl['Landmark'].isnull() ]

print( len(pl) )

# %%
# Calculate Ceqr Criteria
# 1. 5000>
# 2. %50 FAR > 
# 3. Rent St ( 1974 + 6+ Units )
# 4. Not hard to relocate -> Removed already?

pl['ceqr_big'] = np.where(
    pl['LotArea'] >= 5000 , 1,0
)

pl['ceqr_FAR'] = np.where(
    pl['availFAR_perc'] > 50 , 1,0
)

pl['ceqr_rentst'] = np.where(
    (pl['YearBuilt'] < 1974) & (pl['UnitsRes'] >= 6 ) , 0,1 #This is reverse intentionally
)

pl['is_ceqr'] = pl['ceqr_big'] + pl['ceqr_FAR'] + pl['ceqr_rentst']
pl['is_ceqr'] = np.where(
    pl['is_ceqr'] >= 3 , 1,0
)

pl[ pl['is_ceqr'] == 1 ].plot()
plt.show()

#%%
# Permit Issuance 
# Filter and Clean -> Job Type filters: DM, NB, A1
# I will add the permit data to this data to compare changes with PLUTO's alteration
perms = pd.read_csv( 
    r"C:\Users\csucuogl\Desktop\DATA\NYC\DOB_Permit_Issuance.csv",
    dtype={
        "Block":object,
        "Lot":object,
        "Bin #":object
    })
print("Permits are read!")
#%%
# Filter and Format. 
# A1 permits change the use or egress of the building.
perms = perms[perms['Job Type'].isin( ["A1","NB","DM"] )]
perms['Filing Date'] = pd.to_datetime( perms['Filing Date'] )
perms = perms[ perms['Filing Date'].dt.year > 2012 ]
perms = perms['BOROUGH,Bin #,Permit Type,Job Type,Permit Subtype,Block,Lot,Work Type,Permit Status,Filing Status,Filing Date,Issuance Date,LATITUDE,LONGITUDE'.split(",")]
perms

#%%
# Remove a few subcats
perms = perms[ perms['Permit Type'] != "PL"]
perms = perms[ perms['Permit Subtype'] != "FN"]

perms = perms[ ~perms['Permit Subtype'].isin( ["CH","SF",'SH',"SP"] ) ]
perms.groupby(by='Permit Type').size()

#%%
# Format data and prepare
# Generate BBL's
boro_dict = {
        "BROOKLYN":"3",
        "BRONX":"2",
        "STATEN ISLAND":"5",
        'MANHATTAN':"1",
        "QUEENS":"4"
    }
perms["BoroCode"] = perms['BOROUGH']
for k,v in boro_dict.items(): perms["BoroCode"] = perms["BoroCode"].str.replace(k,v)

perms = perms[(perms['Block'] != "00000") ]
perms['Lot2'] = [r[1:] if len(r)==5 else r.zfill(4) for i,r in perms['Lot'].iteritems()]
perms['BBL'] = perms['BoroCode'] + perms['Block'] + perms['Lot2']
perms[ perms['BoroCode'] == "4" ]


#%%
# If there was a permit applied for a lot, consider it changed.

permgr = perms.groupby(by='BBL',as_index=False).size()
permgr['major_alter'] = np.where( permgr['size']>0 ,1 ,0)
permgr

if 'major_alter' in pl.columns: pl=pl.drop('major_alter',axis=1)
if 'size' in pl.columns: pl=pl.drop('size',axis=1)

pl = pl.join( permgr.drop("size",axis=1).set_index("BBL"), on='BBL' )
pl['major_alter'] = np.where( pl['major_alter']==1 , 1 ,0 )

pl.head()

#%%
# Make all intergers
for _ in 'YearAlter,Year_Recent_Change,UnitsTotal,LotArea,AssessLand,AssessTot,ExemptTot,YearBuilt,YearAlter1,YearAlter2,YearAlter,Year_Recent_Change'.split(','):
    pl[_] = pl[_].astype(int)

pl.head()

#%%
temp = pl[ (pl['major_alter']==1) | (pl['recent_alter']==1) | (pl['recent_built']==1) ].copy()
temp.to_file(
    r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\SoftSites\RecentChange_2022_2.geojson",
    driver='GeoJSON', encoding='utf-8')

#%%

