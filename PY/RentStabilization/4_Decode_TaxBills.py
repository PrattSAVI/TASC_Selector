#%%

import pandas as pd
import geopandas as gpd
import wget
import time
from pdfminer.high_level import extract_text
import os
import sys
print( sys.prefix )

folder_path = r"D:\STORED\Rent_St_REPO_21"

# %%

def read_Doc( file_path ):
    
    pdf = os.path.join(folder_path , file_path )
    text = extract_text( pdf )

    if ("Rent Stabilization" in text):
        
        #print( pdf )
        
        text = text.split( '# Apts' ,1 )[1] 
        text = text.split( 'RS fee identifiers' ,1 )[0] 
        text = text.split( '\n' )

        apt = text[1] 
        bbl = file_path.split("_")[1].split(".")[0]
        t_date = file_path.split("_")[0]

        return [bbl,t_date,file_path,apt]
    elif 'STAB' in text.upper() :
        print (pdf)
        return 'diff'
    elif 'SCRIE' in text.upper() :
        bbl = file_path.split("_")[1].split(".")[0]
        t_date = file_path.split("_")[0]
        return [bbl,t_date,file_path,'SCRIE']
    else:
        return "NA"

bills = os.listdir( folder_path )

df = pd.DataFrame( columns = ['bbl','date','file path','st units'])
count = 0
for bill in bills:
    try:
        apts = read_Doc( bill )
    
        if apts != 'NA': #If there is something. 
            df = df.append(pd.Series( apts, index=df.columns), ignore_index=True)
        elif apts == 'diff':
            print( 'This is different')
            break
    except:
        print( bill )
    
    count = count + 1
    
    if count % 250 == 0:
        print( '{x} percent is done'.format(x= round(count*100 / len(bills),1) ) )

df.head()

#%%
#START HERE
#Save 2021 Data

#2021 & 2020 Data
#df.to_csv( r"D:\DROPBOX\Dropbox\TASC Application\DATA\RentSt\Data_2021_RentStabilzedUnits_Q1.csv" )
#df.to_csv("C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\Data_202001121_RentStabilzedUnits_Q1.csv")
import pandas as pd
import numpy as np
import os

df = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\Data_202001121_RentStabilzedUnits_Q1.csv')
df = df.drop( df.columns[ df.columns.str.contains("Unnamed")] , axis = 1)
df.head()

#%% process SCRIE and '' and empty fields

notin = ['SCRIE','diff','']
df = df[ df['st units'] != 'diff' ].copy()
dfns = df[ ~df['st units'].isin( notin ) ].copy()

dfns = dfns.dropna( axis =0 , subset=['st units'])
dfns = dfns[ ~dfns['st units'].str.contains('/') ] #Remove date like values

dfns['st units'] = dfns['st units'].astype( float )
dfdiff = df[ df['st units'] == '' ]

#dfdiff
dfdiff.loc[ dfdiff['bbl'] == '1019270033' , 'st units' ] = 56
dfdiff.loc[ dfdiff['bbl'] == '2028610135' , 'st units' ] = 35
df1 = dfns.append( dfdiff )

df1 = dfns.copy()
df1 = df1[['bbl','st units']]
df1.columns = ['bbl','st_2020']
df1['st_2020'] = df1['st_2020'].astype(float)

#1740 SCRIE units in 2020.
#3066 SCRIE units in 2021. 
dfsc = df[ df['st units'] == 'SCRIE' ].copy()
dfsc

#%% Merge all datasets

d18 = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\Init_DATA\rentstab_counts_for_pluto_19v1_bbls.csv" )
d18['ucbbl'] = d18['ucbbl'].astype( str )
d18 = d18[['ucbbl','uc2018']]
d18.columns = ['bbl','st_2018']
display( d18.head() )

d07 = pd.read_csv( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\Init_DATA\joined-nocrosstab.csv" )
d07['ucbbl'] = d07['ucbbl'].astype( str )
d07 = d07[['ucbbl','year','unitcount']]
d07['year'] = pd.to_datetime( d07['year'] ).dt.year
pt = pd.pivot_table( data=d07 , index='ucbbl',columns=['year'],values='unitcount').reset_index()
pt.columns = ['st_{}'.format(i) if i!='ucbbl' else 'bbl' for i in pt.columns ]
d07 = pt.copy()

display( d07.head() )
#%%
# df1 , dfsc , d18 -> to be addedd
# Diff valeues seem to be errors

#dfp is past values
dfp = d07.set_index('bbl').join( d18.set_index('bbl') )
dfp = dfp.join( df1.set_index('bbl') )
dfp['st_2017'] = None
dfp['st_2019'] = None
dfp = dfp[ sorted( dfp.columns ) ]
dfp
#%% FILL VALUES
#1. If values for 2016 and 2018 exsists, fill in 2017
import math
dfp.loc[ (~dfp['st_2016'].isnull() ) & (~dfp['st_2018'].isnull() ) , 'st_2017' ] = ((dfp['st_2016']+dfp['st_2018']) / 2).round(0)
#2. If values for 2018 and 2020 exsists, fill in 2019
dfp.loc[ (~dfp['st_2018'].isnull() ) & (~dfp['st_2020'].isnull() ) , 'st_2019' ] = ((dfp['st_2018']+dfp['st_2020']) / 2).round(0)
#2.5 Fill in JK dataset
jk = 'st_2007	st_2008	st_2009	st_2010	st_2011	st_2012	st_2013	st_2014	st_2015	st_2016'.split('\t')
filler1 = dfp[jk][ (dfp[jk].isnull().sum(axis=1) > 0) ].fillna(method='ffill',axis=1)
dfp.update( filler1 )

#3. If there are missing years until 2020
# Forward will missing values until 2018.
jk = 'st_2007	st_2008	st_2009	st_2010	st_2011	st_2012	st_2013	st_2014	st_2015	st_2016\tst_2017\tst_2018'.split('\t')
filler1 = dfp[jk][ (dfp[jk].isnull().sum(axis=1) > 0) & (~dfp['st_2018'].isnull()) ].fillna(method='ffill',axis=1)
dfp.update( filler1 )

#4. Fill based on 2020 availabilty
jk = 'st_2016 st_2017 st_2018 st_2019 st_2020'.split(' ')
filler2 = dfp[jk][ (dfp[jk].isnull().sum(axis=1) > 0) & (~dfp['st_2020'].isnull()) ].fillna(method='ffill',axis=1)
dfp.update( filler2 )


dfp

#%% CLEANUP 2021

df21 = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\Data_2021_RentStabilzedUnits_Q1.csv' )

notin = ['SCRIE','diff','']

df21 = df21[ ~df21['st units'].isin( notin ) ].copy()
df21 = df21.dropna( axis =0 , subset=['st units'])
df21 = df21[ ~df21['st units'].str.contains('/') ] #Remove date like values

df21['st units'] = df21['st units'].astype( float )


df21 = df21[['bbl','st units']]
df21.columns = ['bbl','st_2021']
df21['st_2021'] = df21['st_2021'].astype(float)

dfp1 = dfp.join( df21.set_index('bbl') )
dfp1

#%% Fill missing values if values available in 2021 and prior to that
jk = 'st_2007	st_2008	st_2009	st_2010	st_2011	st_2012	st_2013	st_2014	st_2015	st_2016\tst_2017\tst_2018\tst_2019\tst_2020'.split('\t')
filler3 = dfp1[ (~dfp1['st_2007'].isnull()) & (~dfp1['st_2021'].isnull()) & (dfp1[jk].isnull().sum(axis=1) > 0)].fillna(method='ffill',axis=1)
dfp1.update( filler3 )

dfp1

#%%

dfp1.to_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\RentSt\RentSt_AllYears_Filled.csv' )
