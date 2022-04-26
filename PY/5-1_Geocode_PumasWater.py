
#%% IMPORT ALL BORO PLUTOS

import pandas as pd
import geopandas as gpd
import os

from pandas.core.arrays import categorical

path = r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\T_Pluto\nyc_pluto_07c'
files = [i for i in os.listdir( path ) if i.split('.')[1] == 'TXT' or i.split('.')[1] == 'csv']

df = pd.DataFrame()
for f in files:
    file_path = os.path.join(path,f)
    print( f, file_path )
    temp = pd.read_csv( file_path )
    df = df.append( temp )

df

# %% CLEAN AND FORMAT

df = df[['BBL','XCoord','YCoord']]
df['XCoord'] = df['XCoord'].str.strip()
df['YCoord'] = df['YCoord'].str.strip()


df = df[ ~df['XCoord'].isnull() ]
df = df[ df['XCoord'] != "" ]

df['BBL'] = df['BBL'].astype( str )
df['BBL'] = df['BBL'].str.split('.').str[0]

df = df.sort_values("BBL")
df

#%% Make GeoDF
import matplotlib.pyplot as plt

gdf = gpd.GeoDataFrame(
    df,
    geometry= gpd.points_from_xy( df['XCoord'],df['YCoord'] ),
    crs = 2263
)

gdf.sample( 1000 ).plot()
plt.show()
# %% IMPORT PUMAS

path = r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Boundaries\2010 Public Use Microdata Areas (PUMAs).geojson"
puma = gpd.read_file( path )

puma = puma.to_crs( epsg = 2263 )
puma.plot()
plt.show()

#%% SJOIN PUMAS

gdf1 = gpd.sjoin( gdf , puma , op='intersects' )
gdf1 = gdf1[ 'BBL XCoord YCoord geometry puma'.split(" ") ]
gdf1.sample(10)

#%% Import water rev Plans
# import and join

czb = gpd.read_file( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Boundaries\NYCWRP Shapefiles\NYCZB_2002.shp" )
smia = gpd.read_file( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Boundaries\NYCWRP Shapefiles\SMIA_2002.shp" )

czb['czb'] = 'czb'
gdf2 = gpd.sjoin( gdf , czb , op='intersects' )
gdf2 = gdf2[ 'BBL czb'.split(" ") ]

gdf3 = gpd.sjoin( gdf , smia , op='intersects' )
gdf3 = gdf3[ 'BBL Name'.split(" ") ]
gdf3

#%%

gdf2a = gdf1.join( gdf2.set_index('BBL') , on="BBL" )
gdf2a = gdf2a.join( gdf3.set_index('BBL') , on="BBL" )

#%%

gdf2a.head()

#%%

gdf2a.sample(1000).plot( column="puma" , categorical=True)
plt.show()

#%%
gdf2a.to_file( 
    r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Boundaries\BLL_boundaries.geojson',
    driver = "GeoJSON",
    encoding = 'utf-8'
    )