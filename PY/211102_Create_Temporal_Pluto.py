
"""
This Code iteratively builds the final lot scale dataset for the RPA/MAS project
Aim is to merge MapPluto in to a Temporal dataset. Each necessary field is represented as Field_Year(YY)

Large and complcated dataset were merged outise
1. Permits data from DOB
2. ZLM and Airright transfers
"""
#%% Dependencies and Link
from numpy import subtract
import pandas as pd
import os
import numpy as np
pd.set_option('max_columns',None)

#All Pluto Files are Here
#Iterate over all folders and files to find the csv and txt files and add them to a df
folder_path = r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\T_Pluto' #SAVI PC
#folder_path = r'D:\DROPBOX\Dropbox\TASC Application\DATA\T_Pluto' #HOME PC
folders = os.listdir( folder_path )

#List all files and paths
all_files = []
for i in folders:
    files = os.listdir( os.path.join( folder_path,i ) ) 
    for f in files: all_files.append( [i,f] )

#Create a dataframe of pluto files.
all_files = pd.DataFrame( data = all_files , columns = ['version','files'])
all_files['format'] = [r.split('.')[1] for i,r in all_files['files'].iteritems()]

#filter out pdfs (data dictionaries)
all_files = all_files[ all_files['format'].isin( ['csv','txt','TXT'] ) ].copy()
#Format and Create full paths
all_files['year'] = [r.split('_')[2][:2] for i,r in all_files['version'].iteritems()]
all_files['path'] = [os.path.join(folder_path,r['version'],r['files']) for i,r in all_files.iterrows()]
all_files.head(3)

# %% _-_-_-_- OPEN All PLUTO and MERGE _-_-_-_-
#07 SI Pluto has problematic lines and symbols.

def create_Pluto(single_year):

    #Which columns to keep in PLUTO
    cols = [ 
        'BBL','BoroCode','Block','Lot',
        'BldgClass','LandUse','OwnerName',
        'LotArea','BldgArea', 'ComArea','ResArea','OfficeArea','RetailArea',
        'NumBldgs','UnitsRes','UnitsTotal','LotFront','LotDepth',
        'AssessLand','AssessTot','YearBuilt','YearAlter1','YearAlter2',
        'HistDist','Landmark','CondoNo'
        ]

    # Each Boro is in a seperate file. So this for loop merges them in to one.
    # -------- Merge All Boros Here --------------------   
    df = pd.DataFrame() #Empty DataFrame
    for i,r in single_year.iterrows():
        print( r['files'])
        temp = pd.read_csv( r['path'] , encoding='utf-8' , low_memory=False).dropna(subset=['Block'] , axis=0 )
        temp = temp.drop_duplicates( keep='first')
        temp['year'] = r['year']
        
        #Remove Unnecessary Cols
        #Include every column that has FAR in its name. 
        cols1 = cols +  list(set(temp.columns[ temp.columns.str.contains("FAR") ].tolist())) 
        temp = temp[ cols1 ]

        df = df.append( temp )
    print( r['year'] )
    # -------- Format Columns After Here --------------------
    # 1. Landuse
    # Fill NaN, " " values with "0"
    # Convert "2" to "02" for sorting purposes
    df['LandUse'] = df['LandUse'].fillna("0")
    df.loc[ df['LandUse'].isnull() , "LandUse" ] = "0"
    df.loc[ df['LandUse'] == "  " , "LandUse" ] = "0"
    df['LandUse'] = df['LandUse'].astype(int).astype(str)
    df['LandUse'] = df['LandUse'].str.zfill(2) 
    
    # 2. BBL, Format
    df['BBL'] = df['BBL'].astype(str)
    df['BBL'] = df['BBL'].str.split(".",0).str[0]

    # 3. FAR, Create a maxFAR column. Reduce allFAR cols to this. 
    df['maxFAR'] = None
    if 'MaxAllwFAR' in df.columns:
        df['maxFAR'] = df['MaxAllwFAR']
        df = df.drop( 'MaxAllwFAR' , axis=1 )
    else:
        cols =  list(set(temp.columns[ (temp.columns.str.contains("FAR")) & (temp.columns !="BuiltFAR") ].tolist())) 
        df['maxFAR'] = df[ cols ].max(axis=1) # Select highest of all FARs
        df = df.drop( cols , axis=1 )

    # 3.5 Available FAR in percentage
    df['availFAR_perc'] = (df['maxFAR'] - df['BuiltFAR']) / df['maxFAR'] * 100
    df['availFAR_perc'] = df['availFAR_perc'].round( 1 )

    # 4. YearAlter - Calculate Max per Year
    #Single Year Alter option, take the latest one. 
    df['YearAlter'] = df[ ['YearAlter1','YearAlter2'] ].max( axis=1 )

    #5. 2.11 Total vs Assed Value Ratio
    # 'AssessLand','AssessTot',
    df['AssedImprov_perc'] = ((df['AssessTot'] - df['AssessLand']) / df['AssessTot']) * 100
    df['AssedImprov_perc'] = df['AssedImprov_perc'].round(1)
    
    #Give Years to Columns i.e. LandUse_08
    new_cols = []
    for c in df.columns.tolist():
        if c != "BBL":c = c + "_" + str(r['year'])
        else:c = c 
        new_cols.append( c )
    df.columns = new_cols
    df = df.sort_values(by='BBL')
    
    return df

#Import Each Year One by One
# I am taking a limited amount for now. 

single_year = all_files[ all_files['year'] == "07" ]
df07 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "08" ]
df08 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "09" ]
df09 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "10" ]
df10 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "11" ]
df11 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "12" ]
df12 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "13" ]
df13 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "14" ]
df14 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "15" ]
df15 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "16" ]
df16 = create_Pluto( single_year )

single_year = all_files[ all_files['year'] == "17" ]
df17 = create_Pluto( single_year )

#Examples
df07.head()

# %% _-_-_-_- One Pluto to Rull them all -> All BBL's Joined Right with Fields _-_-_-_-

#Merge all dfs.
def slap_it_all( dfs ):

    # 1. Get all unique BBLS in all dfs, remove duplicates
    # 2. Create an empty df with unique bbls as index
    # 3. Join all datasets to this.

    #Get all BBL's
    bbls = []
    for df in dfs: bbls = bbls +  df['BBL'].tolist()
    bbls = list(set(bbls)) #Remove Duplicates

    #Empty DF to act as the basis
    pl = pd.DataFrame( index=bbls )

    # Now join the data to this. 
    for df in dfs:
        pl = pl.join( df.set_index('BBL') )

    return pl

#Merge Them Here
pl = slap_it_all( [df07, df08, df09,df10,df11,df12,df13,df14,df15,df16,df17] ) 
del( [df07,df08, df09,df10,df11,df12,df13,df14,df15,df16,df17] )
pl

#%% Re order Columns 
# Arrange them by topic and year 
cols = pl.columns[ pl.columns.str.contains('_07') ]
all_cols = []
for c in cols:
    ts = pl.columns[ pl.columns.str.contains( c.split("_")[0] ) ].tolist()
    for t in ts: all_cols.append( t )

all_cols
pl = pl[ all_cols ]
pl

# %% _-_-_-_- Year Built and Year Alteration _-_-_-_-

# 2.1 The amount and type of recent as-of-right development in the area
# There are many Year Built info at 0
# Add last_col to the end of the df.
# recent_alter columns combine both last_built and last_alter before 2007

def detect_year(df,col):
    #get columns
    cols = df.columns[ df.columns.str.contains( col ) ].copy()
    df1 = df[cols].copy()

    #Clean
    df1 = df1.fillna( 0 )
    df1 = df1.astype(int)

    df1['last_{}'.format(col)] = df1.max(axis=1)
    df1 = df1.drop( cols , axis = 1 )

    df = df.join( df1 )
    return df

pl = detect_year( pl , "YearBuilt")
pl = detect_year( pl, "YearAlter" )

# Is the lot recently altered -> including yearbuilt and yearalter
pl['recent_alter'] = pl[['last_YearBuilt','last_YearAlter']].max(axis=1)
# Assign 1 if recent alter is more than 2007, else 0
pl['recent_alter'] = np.where( pl['recent_alter'] > 2007 , 1 , 0 )

#Give some sapmles where recently altered
pl[ pl['recent_alter'] == 1].sample(10)

#%% Remove Duplicate Columns 

pl = pl.loc[:,~pl.columns.duplicated()]

#%% _-_-_-_- 1.2 Lot Area_-_-_-_-

# Is the lot lower than the threshold value
# Assign 1 is lot is smaller than 5000 sq.ft. else 1 
# Create a new series of columns is_lot_small_YEAR

threshold = 5000
def lotarea_is_small(df):
    #Get all lot area fields
    cols = df.columns[ df.columns.str.contains("LotArea") ]
    df1 = df[ cols ].copy()

    #If is_too_small already exists
    col1 = df.columns[ df.columns.str.contains("is_lot_small") ]
    if len(col1) > 0: df = df.drop( col1 , axis = 1 )

     #Remove duplicate Columns if there any
    
    for c in cols:
        df1["is_lot_small_{}".format( c.split("_")[1] )] = np.where( df1[c] <= threshold , 1 ,0 )
    df1 = df1.drop( cols , axis = 1 )

    df = df.join( df1 )
    return df

pl = lotarea_is_small( pl )
pl.head()

#%% _-_-_-_- Available FAR Percentage _-_-_-_-

# 1.1  Is the Available FAR lower than the threshold value
# Calculated the available FAR while importing the Pluto data at create_Pluto
# 1 if FAR is less than 50%, 0 else -> adds a series of columns is_FAR_small_YEAR

threshold = 50 #Percent
def FAR_is_small(df):
    cols = df.columns[ df.columns.str.contains("availFAR_perc") ]
    df1 = df[ cols ].copy()

    col1 = df.columns[ df.columns.str.contains("is_FAR_small") ]
    if len(col1) > 0: df = df.drop( col1 , axis = 1 )

    for c in cols:
        df1["is_FAR_small_{}".format( c.split("_")[2] )] = np.where( df1[c] <= threshold , 1 ,0 )
    df1 = df1.drop( cols , axis = 1 )

    df = df.join( df1 )
    return df

pl = FAR_is_small( pl )
pl.head()


# %% 2.18 Ratio of all parcels to parcels that saw changes in zoning increasing density in the area
#Is number of units increased

def residential_change(df,col):
    cols = df.columns[ df.columns.str.contains(col) ]
    df1 = df[ cols ].copy()
    
    #Subtract first col from last, if value is positive density increased
    df1['UnitsRes_Increased'] = df1[ cols[ len(cols)-1 ] ] - df1[ cols[0] ]
    df1['UnitsRes_Increased'] = np.where( df1['UnitsRes_Increased'] > 0 , 1 , 0 )
    df1 = df1.drop( cols , axis = 1)
    df = df.join( df1 )
    return df

pl = residential_change( pl , 'UnitsRes' )

pl[pl['UnitsRes_Increased'] == 1].sample( 5 )

# %% 2.19 Landmark

def was_landmark(df,col):
    cols = df.columns[ df.columns.str.contains(col) ]
    df1 = df[ cols ].copy()
    
    for c in cols:
        df1[c] = df1[c].str.strip()
        df1.loc[ df1[c] == '' , c ] = None
        
        df1[c] = np.where( df1[c].isnull() , 0 , 1)

    df1['sum'] = df1.sum( axis = 1)
    df1['was_{}'.format(col)] = np.where( df1['sum'] > 0 , 1 , 0)
    df1 = df1.drop( cols , axis = 1)
    df1 =  df1.drop( ['sum'] , axis = 1)
    df = df.join( df1 )
    return df

pl = was_landmark(pl,'Landmark')
pl = was_landmark(pl,'HistDist')

pl[pl['was_Landmark'] == 1]

#%% Whole Block Buildings
# adds a column is_single_lot.
#Currently for _08 only. Should it be for each year?
initial_year = '07'

gr = pl[['BoroCode_{}'.format(initial_year),'Block_{}'.format(initial_year)]].groupby( 
                                       by = ['BoroCode_07','Block_07'],
                                       as_index=False
                                       ).size().reset_index()

gr = gr.drop('index',axis=1)

gr.columns = ['boro','block','count']
gr['is_single_lot'] = np.where( gr['count'] == 1 , 1, 0 )
gr = gr.set_index( ['boro','block'] )
gr = gr.drop( ['count'] , axis = 1)

pl = pl.join( gr , on=['BoroCode_07','Block_07'] )
pl
#%%
# Hard to relocate landuses
# Replace this with RPA/MAS's response

lands = ['07','08','09'] #Which landuse cats to use for this. 
pl['is_hard_to_Relocate'] = 0
pl['is_hard_to_Relocate'] = np.where( ((pl['is_single_lot'] == 1) & (pl['LandUse_{}'.format(initial_year)].isin(lands))) , 1,0 )

pl[ pl['is_hard_to_Relocate'] == 1 ]


# %% REMOVE UNNECESAARY Building Classes
# If the building is in these classes at the beginging and end year.

remove_bdlgs = 'Q0 Q1 T1 T2 U1 U2 U3 W1 Z5 Z8'.split( ' ' )
cols = pl.columns[ pl.columns.str.contains('BldgClass') ]
cols = cols[::len(cols)-1]

#Approx 3750 lines are removed here
pl = pl[ (~ pl[cols[0]].isin(remove_bdlgs) ) & (~ pl[cols[1]].isin(remove_bdlgs) )  ]
pl

#%% Clean Up -> Reduce File size 

#1. Remove all these unused columns
pl = pl.drop( pl.columns[ pl.columns.str.contains('BoroCode|Block|Lot_|OfficeArea|RetailArea|CondoNo|AssessTot|AssessLand|YearAlter2|YearAlter1') ] , axis=1)

#2. These have long spaces. Strip and replcae with Nan
t = ['HistDist_','Landmark_']

for i in t:
    cols = pl.columns[ pl.columns.str.contains(i) ]
    for c in cols:
        pl[ c ] = pl[ c ].str.strip()
        pl[ c ] = pl[ c ].replace( "" , np.nan)

pl

#%% Join Compactness

df_co = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\MapPLUTO_07_CompactScores.csv' )
df_co['BBL2'] = df_co['BBL2'].astype(str)
df_co = df_co.set_index( "BBL2" )
df_co.columns=['Compact_07']

pl = pl.join( df_co )
pl


#%% Remove unmapped Lots for all History

cols = pl.columns[ pl.columns.str.contains('LotArea_') ]

#If lot area is 0, convert it to None
for c in cols:
    pl.loc[ pl[c]==0 , c ] = None

pl = pl[ ~pl[cols].isna().all(1) ]
pl

#%% IMPORT PUMAS & Coastal Zone
import geopandas as gpd
pumas = gpd.read_file( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Boundaries\BLL_boundaries.geojson" )
pumas.columns = ['BBL','XCoord','YCoord','puma','czb','czone_name','geometry']
pumas = pumas.drop('geometry' , axis=1)
pumas.head()

#%% Join Geosptail Info

pl = pl.join( pumas.set_index('BBL') )

#%% Merge All Rent_ST info

df_rent = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\RentSt_AllYears_Filled.csv" )
df_rent['bbl'] = df_rent['bbl'].astype( str )
df_rent[df_rent['bbl'] == '1000150022' ]
df_rent= df_rent.set_index('bbl')

df_rent = df_rent.drop( 'st_2018	st_2019	st_2020	st_2021'.split("\t") , axis = 1)
df_rent.head()

cols = pl.columns[ pl.columns.str.contains("st_2")]
if len(cols) > 0:
    pl = pl.drop( cols , axis = 1 )

pl = pl.join( df_rent )
pl

#%%
#%% Passes Initial Screening

pl['pass_initial_screen'] = np.where(
    (pl['is_lot_small_07'] == 1) | (pl['is_FAR_small_07'] == 1),
    0,1
)

pl[ ['is_lot_small_07','is_FAR_small_07','pass_initial_screen'] ].sample(12)

# %% --------------------  START HERE ---------------------------
#All Above is saved to Master_Pluto.
# I use this to start over from here. 
import pandas as pd
import numpy as np
pd.set_option('max_columns',None)

#pl.to_csv( r'D:\DROPBOX\Dropbox\TASC Application\DATA\Master_Pluto.csv')
pl = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv')
pl.columns = pl.columns.str.replace( 'Unnamed: 0' , 'bbl')
pl['bbl'] = pl['bbl'].astype( str )
pl = pl.set_index( 'bbl' ) 

pl.head()


