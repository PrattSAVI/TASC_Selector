#%% Import 
import pandas as pd

df = pd.read_csv(r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\DOBdata\DOB_PermitIssuance_A1_A2_DM_NB_2007-2017_se_011421.csv")
df.head()

#%% Format Data

#BBL to String
df['BBL'] = df['BBL'].astype(str)
df['BBL'] = df['BBL'].str.split(".").str[0]

#Year to integer for ordering
df['Year'] = df['Year'].astype(int)
df = df.dropna( subset=['BBL'], axis = 0)
df = df[ df['BBL'] != "nan" ] # Remove mistakes
df.head()

#%% Make Pivot Table
pt = pd.pivot_table(
    data = df[['Year','BBL']],
    columns='Year',
    index = 'BBL',
    aggfunc=len
)

pt = pt.fillna( 0 ) #Fill NaN's ith 0's
#Format Columns
pt.columns = ["permits_" + str(i)[2:] for i in pt.columns]
pt = pt.astype(int) #df to int

pt

#%% Import Temporal Pluto

pl = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv" , dtype={'bbl': object})
pl = pl.drop( ['permits_07'] , axis = 1) #This was from before, comment out if it is givving errors.
pl.head()

#%% Join permits to master pluto

pl1 = pl.join( pt , on='bbl' )
pl1.head()

#%% Export

pl1.to_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv')

