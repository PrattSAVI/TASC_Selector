#%% Import Master Pluto and make geodf
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

pl = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv" , dtype={'bbl': object})
display( pl.head() )


gpl = gpd.GeoDataFrame(
    pl[['bbl','XCoord',"YCoord"]],
    geometry = gpd.points_from_xy( pl['XCoord'],pl['YCoord'] ),
    crs = 2263
)

#Plot sample of it
gpl.sample(100).plot()
plt.show()

#%% Import rezonings SHP file

rez = gpd.read_file( r"C:\Users\csucuogl\Downloads\nyzma\geo_export_a3cc145d-0440-4f26-859e-15490ec98833.shp" )
rez = rez.drop(['time_effec','shape_leng','shape_area'] , axis = 1)
rez['date_effec'] = pd.to_datetime( rez['date_effec'] )
rez = rez[ rez['date_effec'].dt.year < 2018  ] # Before 2017
rez = rez[ rez['status'] == "Adopted" ] # Only adopted ones
rez = rez.to_crs( 2263 ) # to state plane

#PLot rezoning and sample points
ax = gpl.sample(100).plot( markersize=0.2 , color = 'red')
rez.plot( ax = ax , alpha = 0.35 )
plt.show()

#%% Spatial Join

gpl = gpl[ ~gpl['XCoord'].isnull()] #If only has x,y
sample = gpl.copy()
sample = sample[['bbl','geometry']] #
jj = gpd.sjoin( #Spatial join
    sample,
    rez[['project_na','geometry']]
)

#Some points inersect with more than 1 boundary, 4 at max
gr = jj.groupby(by='bbl', as_index = False).agg(
    lambda x: ', '.join(x)
    )
#Show some
gr[ gr['project_na'].str.contains(', ')]
#%% Join with master Pluto

pl1 =pl.join( gr.set_index('bbl'),on='bbl')
pl1.head()

#%% Clean the data

pl1 = pl1.drop(['Unnamed: 0'],axis = 1)
pl1.columns.str.replace('project_na','in_rezoning')

pl1.head()

#%% Export

pl1.to_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv')
