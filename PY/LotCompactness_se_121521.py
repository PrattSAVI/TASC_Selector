
# control + enter runs cell 
# shift + enter runs cell + adds new one or jumps to next one

# %%
import pandas as pd
import geopandas as gpd # geodataframe panda
import numpy as np # math


# %%
import os
from pandas.core.indexes.api import get_objs_combined_axis 


#%%
folder='/Users/saraeichner/Dropbox/TASC_Sara/Data/MapPLUTO_07C'
print(folder)
boros = ['Bronx', 'Staten_Island', 'Manhattan', 'Brooklyn', 'Queens']


#%%
path2 = []
# for all the boros, join boro name to path

for b in boros:
    path1 = os.path.join(folder,b)
    
    files = os.listdir(path1)
# for all the files, find files and split them on the . if they = shp
# if the nubmer of elements in line split by . is 2, and shp, 
# then append path 1 and the file name to create path2

    for f in files: 
        if f.split('.')[1] == 'shp':
            if len( f.split('.') )== 2:
                    path2.append( os.path.join(path1,f) )
path2



# %%
# merge all the Map Pluto shapefiles into one dataframe

# make an empty dataframe: 
mp = gpd.GeoDataFrame()

for path in path2:
    print( path ) #print the path and file name being read into python
    temp = gpd.read_file( path ) # read the file
    mp = mp.append( temp ) # append to mp geodataframe which will merge into one gdf
mp.head()



# %%
# check number of rows in the geodataframe to make sure it merged
mp.shape[1]
mp.shape[0]
# check that all boros are in the geodataframe
mp['Borough'].unique()
mp['Shape_area'].min()

#%%
#import pi and square root functions from Math to run the Polsby Popper calculation
from math import pi, sqrt


#%%
# calculate compactness of each tax lot using the Polsby Popper formula

def pp_compactness(geom): # Polsby-Popper
    p = geom.length
    a = geom.area    
    return (4*pi*a)/(p*p)
    
# def s_compactness(geom): # Schwartzberg
  #  p = geom.length
  #  a = geom.area    
  #  return 1/(p/(2*pi*sqrt(a/pi)))

gdf = mp
gdf["Polsby_Popper"] = gdf.geometry.apply(pp_compactness)
# gdf["Schwartzberg"] = gdf.geometry.apply(s_compactness)
gdf.head()



#%%
# convert numeric BBLs to strings
gdf['BBL2'] = gdf['BBL'].astype(str)
gdf['BBL2'] = gdf['BBL2'].str.split('.').str[0] 
gdf.head()


#%%
# save MapPLUTO with Compact Score and geometry 
gdf.to_file(
    '/Users/saraeichner/Dropbox/TASC_Sara/Data/MapPLUTO_07C/MapPLUTO_07_merged.geojson)',
    driver = 'GeoJSON',
    encoding = 'utf-8'
)



#%%
# create a csv of just BBLs and Compact score to be joined to temporal pluto
# from gdf, extract the BBLs and the compactness score 

compact = gdf[['BBL2', 'Polsby_Popper']]
compact.head()


#%%
compact.to_csv(
    '/Users/saraeichner/Dropbox/TASC_Sara/Data/MapPLUTO_07C/MapPLUTO_CompactScores.csv)',
    encoding = 'utf-8',
    index = False
)

# %%
