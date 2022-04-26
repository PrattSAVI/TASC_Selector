# %%
import pandas as pd
import geopandas as gpd # geodataframe panda
import numpy as np # math


# %%
import os
from pandas.core.indexes.api import get_objs_combined_axis 
from pandas.core.arrays import categorical

# %%#
## REDO of the DOB data post 2010
# data comes from here: https://data.cityofnewyork.us/Housing-Development/DOB-Permit-Issuance/ipu4-2q9a/data
# BBL will be needed from Boro, Block and Lot numbers 
# change year data to date and then create "Year" column from Issuance Date
# do not filter to only residential; keep all building permits
# filter data, reduce to 2010 - 2017
# Filter to these job types: A1, A2, Demo, NB
# separate code into two sections: 1 for DOB current data and second for historical. 
# use df to define dataframe and add to that 

#%%
#read in NEW DOB Permit Issuance data. Could not filter the data on website so filter to year and job type first
df= pd.read_csv('/Users/saraeichner/Dropbox/TASC_Sara/Data/DOBdata/DOB_Permit_Issuance_current.csv', low_memory=False)
df.head()

#%%%
# copy of df for reference: 
df_copy= pd.read_csv('/Users/saraeichner/Dropbox/TASC_Sara/Data/DOBdata/DOB_Permit_Issuance_current.csv', low_memory=False)
df_copy.head()
#%%
# make a list of all fields in the df
df_list=list(df)
print(df_list)
#%%
df.shape
#%%
df.dtypes
#%%
# convert data types to date, reduce to year for each permit date category
# convert dates fields to actual date type data
df['Filing Date'] = pd.to_datetime(df['Filing Date'])
df['Expiration Date']=pd.to_datetime( df['Expiration Date'])
df['Issuance Date']= pd.to_datetime(df['Issuance Date'])
# %%
df.dtypes

# %%
# Then extract just the year to a column for each: 
df['IssueYear'] = df['Issuance Date'].dt.year
df['ExpireYear'] = df['Expiration Date'].dt.year
df['FilingYear'] = df['Filing Date'].dt.year
df.head()
# %%
df_copy['Issuance Date']= pd.to_datetime(df['Issuance Date'])

#%%
df_copy['IssueYear'] = df['Issuance Date'].dt.year
#%%

# remove NaT values in issue year#
#D_check.dtypes
# there must be NA values: remove all from IssueYear (the others don't matter so will leave them rather than 
# delete rows that have an issue date but no exp. date)
df['IssueYear'] = df['IssueYear'].fillna(0)
#df['IssueYear'] = df['IssueYear'].str.split(".").str[0]
df['IssueYear'] = df['IssueYear'].astype(int)

#%%
# make column called year
df['Year']=df['IssueYear']
# %%
df.head()

# %%
# find out how many years the data covers
pd.value_counts(df.Year)
# it goes back at least to 1989 (???)
# I will remove < 2007 and > 2017
#%%
# replace Borough names with Borough ID numbers
df['BOROUGH'].replace({'BRONX':'2' , 'BROOKLYN':'3', 'MANHATTAN': '1', 'QUEENS':'4', 'STATEN ISLAND':'5'} , inplace=True)
#pd.value_counts(df.BOROUGH)
df.head()

#%%
df_list=list(df)
print(df_list)
#%%
# remove .0 from 'Block' 
# last time the block and lots were numeric. this time they are objects. so no need for code below
# get rid of NAs to convert floats to strings or int
#df.dtypes
#df['Block'] = df['Block'].fillna(0)
#df['Block'] = df['Block'].astype(int)
#df['Block'] = df['Block'].apply(str)

#%%
# Save a version of the dataframe before changing adding leading zeros to Block and Lot: Use it to 
# check for mistakes came up before
df_copy = df
df_copy.head()

#%%
# currend Permit issuance data has inconsistent Boro block and lot data, 
# some lot + block numbers have 5 digits, some 1
# also fill those that are too short belo
# block should be 5, Lot should be 4 characters
df['Lot2'] = df['Lot'].str[-4:]
df.head()
#%%
# some block numbers have 5 digits, some 1: make sure they are all 5 char long, 
# also fill those that are too short below
df['Block2'] = df['Block'].str[-5:]
df.head()

#%%
# make sure all lot and blocks have leading zeros
df['Lot2'] = df['Lot2'].str.zfill(4)
df['Block2'] = df['Block2'].str.zfill(5)

#%%
## concatenate
df['BBL'] = df['BOROUGH'] + df['Block2'] + df['Lot2'] 
df.head()
##### ##%%
#%%
df['Job Type'].unique()

# %%
df.rename(columns={'Job Type' : 'Job_Type'}, inplace = True)
pd.value_counts(df.Job_Type)

# %%
# what does building type refer to? 
df.rename(columns={'Bldg Type' : 'Bldg_Type'}, inplace = True)
#pd.value_counts(df.Bldg_Type)
#%%
jt = ['A1', 'A2', 'DM', 'NB']
df2=df[df.Job_Type.isin(jt)]
#%%
df2.head()

#%%
pd.value_counts(df2.Job_Type)
#%%
#%%
df['Job Type'].unique()
df.rename(columns={'Job Type' : 'Job_Type'}, inplace = True)
#%%
pd.value_counts(df.Job_Type)

# %%
# what does building type refer to? 
df.rename(columns={'Bldg Type' : 'Bldg_Type'}, inplace = True)
pd.value_counts(df.Bldg_Type)
#%%
jt = ['A1', 'A2', 'DM', 'NB']
df2=df[df.Job_Type.isin(jt)]
#%%
pd.value_counts(df2.Job_Type)
#__________________________________________________________________________
# load the historic dataset in to compare. Does the current dataset cover the dates we need? 
# same process below as used with curretn permit issuance data 

#%%
#read in complete copy of DOB Historical Permit Issuance data downloaded from DOB 1/14/22. 
# Could not filter the data on website so filter to year and job type first
# data comes from here: https://data.cityofnewyork.us/Housing-Development/Historical-DOB-Permit-Issuance/bty7-2jhb/data
dfh= pd.read_csv('/Users/saraeichner/Dropbox/TASC_Sara/Data/DOBdata/Historical_DOB_Permit_Issuance_complete.csv', low_memory=False)
#%%
dfh.head()

#%%%
# make a list of all fields in the df
dfh_list=list(dfh)
print(dfh_list)
#%%
dfh.shape
#%%
dfh['Job Type'].unique()

dfh.rename(columns={'Job Type' : 'Job_Type'}, inplace = True)
pd.value_counts(dfh.Job_Type)

### I am here comparing historic data to recent dataset before doing anythnig to it
#%%
# convert data types to date, reduce to year for each permit date category
# convert dates fields to actual date type data
dfh['Filing Date'] = pd.to_datetime(dfh['Filing Date'])
dfh['Expiration Date']=pd.to_datetime(dfh['Expiration Date'])
dfh['Issuance Date']= pd.to_datetime(dfh['Issuance Date'])
# %%
df.dtypes
# %%
# Then extract just the year to a column for each: 
dfh['IssueYear'] = dfh['Issuance Date'].dt.year
dfh['ExpireYear'] = dfh['Expiration Date'].dt.year
dfh['FilingYear'] = dfh['Filing Date'].dt.year

# %%
dfh.head()
#%%
# remove NaT values in issue year#
#D_check.dtypes
# there must be NA values: remove all from IssueYear (the others don't matter so will leave them rather than 
# delete rows that have an issue date but no exp. date)
dfh['IssueYear'] = dfh['IssueYear'].fillna(0)
#dfh['IssueYear'] = dfh['IssueYear'].str.split(".").str[0]
dfh['IssueYear'] = dfh['IssueYear'].astype(int)
#%%
# make column called year 
dfh['Year']=dfh['IssueYear']
dfh.head()

#%%
jt = ['A1', 'A2', 'DM', 'NB']
dfh2=dfh[dfh.Job_Type.isin(jt)]
#%%
pd.value_counts(dfh2.Job_Type)

#%%
dfh2['Job_Type'].unique()
#%%
# now count the historical issued permits per year to compare to the current issued permits
pd.value_counts(dfh2.Year)

#%%
## HISTORICAL PERMIT DATA and CURRENT PERMIT DATA are almost the same, 
# will do analysis with just the current data and will make one 10 year dataset and 1 bbl count for 2007


#%%
# filter DOB permit data to 2007 - 2017
Years = ['2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']
df3=df2[df2.Year.isin(Years)]
df3.head()

#%%
df3_list=list(df3)
print(df3_list)

#%%
# filter dataset to relevant fields
df_10yr = df3[['BBL','Bin #','Job_Type','Work Type','Permit Type','Filing Status','Year', 'Residential', 'LATITUDE', 'LONGITUDE', 'Issuance Date', 'Expiration Date', 'Job Start Date' ]]
df_10yr.head()
#%%
# save dataset for future use
df_10yr.to_csv('/Users/saraeichner/Dropbox/TASC Application/Data/DOB_PermitIssuance_A1_A2_DM_NB_2007-2017_se_011421.csv')


#%%
# Group df_10yr by BBL, include 'LATITUDE', 'LONGITUDE' so they can be joined to pumas, 
# organize in columns by 'Year'
# ---------------------------------
# this gets close but not quite: there should be one column for each year
grouped_10yr = df_10yr.groupby(['BBL', 'LATITUDE', 'LONGITUDE', 'Year']).agg({'Year': ['count']})
grouped_10yr.columns = ['count']
grouped_10yr = grouped_10yr.reset_index()

grouped_10yr.head()


#%%
# 2007 BBL counts  to join to PLUTO 
#%%filter to 2007 permits only
df_07_new = df_10yr[df_10yr.Year == 2007]
df_07_new.head()
#hist07r.shape
#%%
df_07_new['Job_Type'].unique()
#%%
#hist07r3.shape
NewGrouped07= df_07_new.groupby( by='BBL' ).size()
#%%
NewGrouped07.tail()
#final07.shape
#%%
# save all permits counted by BBL for 2007 too
# two separate csvs were saved; 
NewGrouped07.to_csv(f'/Users/saraeichner/Dropbox/TASC_Sara/Data/DOB_Permits_perBBL_2007_A1_A2_DM_NB_se_011521.csv')
# %%

#-----------------------------------------------
# Add permits to 2007 PLUTO Data 
# Code from Can
permits = pd.read_csv(/Users/saraeichner/Dropbox/TASC_Sara/Data/DOB_Permits_perBBL_2007_RESIDENTIAL_se_1-14-21.csv'
#  r is ncessary for windows, not macs: (r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\DOBdata\DOB_PermitCount_perBBL_2007.csv" )
permits.columns = ['BBL','permits_07']
pl = pl.join( permits.set_index('BBL') )
pl['permits_07'] = pl['permits_07'].fillna( 0 )
pl[ pl['permits_07'] > 0].sample(5)