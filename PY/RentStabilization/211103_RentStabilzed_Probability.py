
#%% IMPORT DATA

#Pluto 19v1 , NYS Rent St Buildings, Chris W Rent St Buildings
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pl = pd.read_csv( r"C:\Users\csucuogl\Desktop\WORK\TASC_Repo\T_Pluto\nyc_pluto_19v1_csv\pluto_19v1.csv" )
r18 = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\rentstab_counts_for_pluto_19v1_bbls.csv")
rst = pd.read_csv(r"C:\Users\csucuogl\Desktop\WORK\TASC_Repo\BuildingList\NY_RentSt_Buildings_Rd.csv")

r18['ucbbl'] = r18['ucbbl'].astype(str)
rst['bbl'] = rst['bbl'].astype(str)

display( r18.head(5) )
display( rst.head(5) )

#%% Get a Longer of unique BBL's 

print( "{} Rent Stabilized BBLS in 2018 Data from C.Whong".format(len(r18['ucbbl'].unique()) ) ) 
print( "{} Rent Stabilized BBLS in 2018 Data from NYS".format(len(rst['bbl'].unique())) )

# Merge Lists and Remove Duplicates
bbls = r18['ucbbl'].tolist() + rst['bbl'].tolist()
bbls = list(set(bbls))

print( "When Combined {} BBLS are in the list".format( len(bbls) ) )


# %% Merge with Pluto -> Add a Rent_St Columns as Y/N Field for BBLS
pl['bbl'] = pl['bbl'].astype(str)
pl['Rent_St'] = "N"
pl.loc[ pl['bbl'].isin(bbls) , "Rent_St" ] = "Y"

pl.sample(10)

#%% Bring in PUMAS -> Spatial Join
#This Takes a While
import geopandas as gpd

pumas = gpd.read_file( r"C:\Users\csucuogl\Downloads\PUMA_NYC.geojson" )
pumas = pumas.to_crs( epsg=2263 )
pumas = pumas[['PUMACE10','NAMELSAD10','geometry']]

pl = pl[ ~pl['xcoord'].isnull() ]
gpl = gpd.GeoDataFrame( pl , geometry = gpd.points_from_xy( x = pl['xcoord'], y = pl['ycoord'], crs=2263) )

gpl = gpd.sjoin(gpl , pumas , how='inner', op="intersects")
pl = pl.join( gpl[['PUMACE10','NAMELSAD10']] )

pl.head()

#%% Clean PLUTO.
# 1. Remove BBL's with no housing
# 2. Remove unnecessary columns
pd.set_option( 'max_columns', None )

pl['yearalter'] = pl[["yearalter1", "yearalter2"]].max(axis=1)

cols = [ 
    'PUMACE10',
    'bbl',
    'cd',
    'zipcode',
    'zonedist1',
    #'zonedist2',
    #'zonedist3',
    #'zonedist4',
    'overlay1',
    #'overlay2',
    'spdist1',
    #'spdist2',
    #'spdist3',
    #'splitzone',
    'bldgclass',
    'landuse',
    #'easements',
    'lotarea',
    'bldgarea',
    #'comarea',
    'resarea',
    #'officearea',
    #'retailarea',
    #'garagearea',
    #'strgearea',
    #'factryarea',
    #'otherarea',
    'unitsres',
    'unitstotal',
    'yearbuilt',
    'yearalter',
    #'yearalter1',
    #'yearalter2',
    'borocode',
    'Rent_St']


col_str = ['cd','zipcode','landuse']
col_int = [ 'unitsres' , 'yearbuilt','yearalter']

#Simplify
pl = pl[ cols]

#Only That has housing units
pl = pl[ pl['unitsres'] > 0 ]

#Formatting - Strings
for _ in col_str:
    pl[_] = pl[_].astype(str)
    pl[_] = pl[_].str.split(".").str[0]

#Formatting - integers
for _ in col_int: pl[_] = pl[_].astype(int)    

#Format Landusefor sorting
pl['landuse'] = pl['landuse'].str.zfill(2)
pl

#%% initial Tree
#Scikit Learn Tree for tests

from sklearn import tree
import matplotlib.pyplot as plt
import numpy as np


to_conv = ['landuse','zonedist1','bldgclass','overlay1','spdist1'] #Categorical Fields Here
test_cols = ['yearbuilt','unitsres','bldgarea','resarea'] # Numeric Fields Here

spumas = pumas.sample(1)
boroc = spumas['PUMACE10'].values[0]

pl1 = pl[ pl['PUMACE10'] == boroc ].copy()
pl1 = pl1[ pl1['resarea'] < 13211398 ]
pl1 = pl1[ pl1['yearbuilt'] > 1600 ] #Remove wrong enteries
#pl1 = pl1.sample( 5000 ) #Reduce Samples

#Convert Rent St availability to 0 & 1
pl1['Rent_St'] = np.where( pl1['Rent_St']=="N" , 1 , 0)

#Convert categorical to dummies
for t in to_conv:
    temp = pl1[ t ]
    temp = pd.get_dummies( temp )
    temp.columns = ["{}_{}".format(t,i) for i in temp.columns]
    pl1 = pl1.join( temp )

#Remove categorical fields
pl1 = pl1.drop( to_conv , axis = 1 )
test_cols = test_cols + temp.columns.tolist()

#training data , target
X,y = pl1[ test_cols ].values , pl1['Rent_St'].values

print( "Here we go!" )
clf = tree.DecisionTreeClassifier( max_leaf_nodes=9 , random_state=1 )
clf = clf.fit(X, y)

#Plot the Tree
plt.figure( figsize= (8,12) )
tree.plot_tree(
    clf, 
    filled=True,
    feature_names= test_cols,
    rounded= True , precision= 2 )
plt.title( 'Rent Stabilization Decision Tree for\n {}'.format(str(spumas['NAMELSAD10'].values[0])))
plt.show()

# %% ------------- Year Built ------------- 

import plotly.express as px

fig = px.histogram( pl[pl['yearbuilt']>1890], x="yearbuilt", 
    color="Rent_St",nbins=20 , 
    color_discrete_sequence=px.colors.qualitative.D3)

#1978
fig.add_shape(type="line",
    x0=1978, y0=0, x1=1978, y1=200000,
    line=dict(
        color="LightSeaGreen",
        width=4,
        dash="dashdot",
    )
)

fig.update_layout(
    autosize=False,width=800,height=400,
    title={
        'text': "Number of Rent St BBL's per Year",
        'y':0.95,'x':0.075},
    margin=dict(
        l=50,
        r=50,
        b=50,
        t=50,
        pad=4
    )
    )
fig.show()

# %% UnitRes - And other Units
# ------------- LANDUSE ------------- 
# Pivot -> Sum -> Percentage
def pivot_perc(df,ind, col , thr):
    gr = pd.pivot_table( data = df[[col,ind]] , index=col,columns=ind,aggfunc=len)
    gr = gr.fillna( 0 )
    gr = gr.reset_index()
    gr = gr.sort_values(by=col)

    gr['sum'] = gr['Y'] + gr["N"]
    gr = gr[ gr['sum'] > thr ] #Remove not residential like landuses

    gr['perc_Y'] = (gr['Y'] / gr['sum']) * 100
    gr['perc_Y']  = gr['perc_Y'] .astype(int)
    gr['perc_N'] = (gr['N'] / gr['sum']) * 100
    gr = gr[ gr['sum'] > thr ]
    gr['perc_N'] = gr['perc_N'].astype( int )

    gr = gr.sort_values( by='perc_Y' , ascending=False)

    plt.figure(figsize=(16,8))
    plt.grid( axis='x' , color='grey', alpha=0.5)
    sns.barplot( data = gr[ gr['perc_Y'] > 5 ], x = col , y ='perc_Y' , color = 'black')
    plt.xticks( rotation = 90 )

    plt.show()
    return gr


u6 = pl[ pl['unitsres'] > 5 ]

#pivot_perc(u6,'Rent_St','spdist1' , 20)
#pivot_perc(pl,'Rent_St','landuse',100)
pivot_perc(u6,'Rent_St','zonedist1',20)


# %%  _-_-_-_-_-_- LOT AREA _-_-_-_-_-_-
q = 8
u6['lotarea2'] = pd.qcut( u6['lotarea'] , q , labels=[i for i in range(q) ] )
pivot_perc(u6,'Rent_St','lotarea2',10)


# %%

q = 8
u6['bldgarea2'] = pd.qcut( u6['bldgarea'] , q , labels=[i for i in range(q) ] )
pivot_perc(u6,'Rent_St','bldgarea2',10)


# %% RENT ST STATS AGAIN
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn

df = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\RentSt_AllYears_Filled.csv")
pl = pd.read_csv( r"C:\Users\csucuogl\Desktop\WORK\TASC_Repo\T_Pluto\nyc_pluto_19v1_csv\pluto_19v1.csv" )

display( df.head() )
display( pl.head() )


#%%

pl = pl[[ 'yearbuilt','yearalter1','unitsres','bbl','borough']]
pl = pl.join( df.set_index('bbl') , on='bbl')

#With Rent Stabilized Units
plr = pl[ pl['st_2018'] > 0 ]
plr.head()

#%%
plr = plr[ plr['yearbuilt'] > 1850 ]

plr['yearbuilt'].hist(bins = 20 )
plt.title('Year Built')
plt.show()

plr = plr[ plr['unitsres'] > 0 ]

np.log(plr['unitsres']).hist(bins = 20 )
plt.title('Units Res')
plt.show()

#%%
plr['pass'] = np.where( (plr['yearbuilt'] < 1974) & (plr['unitsres'] >= 6) , "Assumed to have Rent St", "Assumed NOT to have Rent St" )

p1,p2 = plr[['pass']].groupby(by='pass').size().values
print( round(p2*100 / (p1+p2)) )

#%%
plr['unitsres_log'] = plr["unitsres"]**0.1
sns.jointplot( 
    x= plr["unitsres_log"],
    y=plr["yearbuilt"],
    hue=plr['pass'],
    joint_kws={'s': 1,'alpha':0.5},
    ylim=(1875,2022)
    )
plt.show()

#%%
gr = plr[['pass','borough']].groupby(by=['borough','pass'],as_index=False).size()
gr.pivot(columns='borough')

#%%
pt = pd.pivot_table(
    data = plr[['pass','borough']],
    index = 'borough',
    columns = 'pass',
    aggfunc=len
).reset_index()

pt['total'] = pt['Assumed NOT to have Rent St'] + pt['Assumed to have Rent St']
pt['perc Proxy'] = (pt['Assumed to have Rent St']*100 / pt['total']).round()
pt['perc Proxy'] = pt['perc Proxy'].astype(str)

#%%

import plotly.graph_objects as go

fig = go.Figure(data=[go.Table(
    header=dict(values=pt.columns),
    cells=dict(values=pt.transpose().values))
                     ])
fig.show()

#%%
