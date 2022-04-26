# %% --------------------  START HERE ---------------------------
#All Above is saved to Master_Pluto.
# I use this to start over from here. 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os 

pd.set_option('max_columns',None)

pl = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv')
pl.columns = pl.columns.str.replace( 'Unnamed: 0' , 'bbl')
pl['bbl'] = pl['bbl'].astype( str )
pl = pl.set_index( 'bbl' ) 

pl.head()

#%% Filter Recently Altered Units
plb = pl[ pl['recent_alter'] == 1]
plb.head()

# %% Plot a bar chart shoing the number of units passed or failed initial CEQR Screening

sns.countplot( data = plb , x = "pass_initial_screen")
plt.title( "Of the developped lots, \n how many passed the Initial Screening")
plt.savefig( r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Initial Screening\Screening_Pass_Fail\Citywide_PassFail.png' )
plt.xlabel( "Pass/Fail")
plt.show()
# %% ------ Per PUMA - Developped vs Initial Screening Results
# ---- Generated a table sorted by percentage of failed screenings
# List format heatmap
pt = pd.pivot_table(
    data = plb[['puma','pass_initial_screen']],
    index = 'puma',
    columns = 'pass_initial_screen',
    aggfunc=len
)

pt = pt.reset_index()
pt.columns = ['puma','failed','passed']
pt = pt[['puma','failed','passed']]
pt['puma'] = pt['puma'].astype(int)
pt = pt.set_index('puma')

pt['total'] = pt['failed'] + pt['passed']
pt['perc_failed'] = (pt['failed'] * 100 / pt['total']).round(0)

pt = pt.sort_values(by='perc_failed',ascending=False)
# -- Plot
plt.figure( figsize=(8,16))
sns.heatmap(
    data =pt,
    cmap = 'OrRd',
    annot= True,fmt='g',
    linewidths=.5, cbar = False
)
plt.ylabel('')
plt.title( "# of lots being developped vs Initial Screening Results")
plt.tick_params(left=False, bottom=False)
plt.savefig( r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Initial Screening\Screening_Pass_Fail\PerPUMA_PassFail.png' )
plt.show()
#%% -------- MAP RESULTS from PT per PUMA
# Percentage failed to be identified is mapped
import geopandas as gpd
pumas = gpd.read_file(r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Boundaries\2010 Public Use Microdata Areas (PUMAs).geojson") 
pumas.head()

#---- Format and join with PUMAS
pumas['puma'] = pumas['puma'].astype(int)
pumas = pumas.join( pt , on='puma')

# ---- PLOT
pumas = pumas.to_crs(3857) #Pseudo Mercator Projection
pumas.plot( column = 'perc_failed' , cmap = 'OrRd' , legend=True, figsize=(12,8))
# --- Format Plot
sns.despine(top=True,left=True,right=True,bottom=True)
plt.tick_params(left=False,
                bottom=False,
                labelleft=False,
                labelbottom=False)
plt.title('% Developed lot that did not pass the Initial Screening')
plt.show()

#%% Distribution of Deveopped Lots -> Available FAR %

fig = px.histogram(
    plb[(plb['availFAR_perc_07']>-100) & (plb['availFAR_perc_07'] < plb['availFAR_perc_07'].quantile(0.999)) & (plb['availFAR_perc_07'] > plb['availFAR_perc_07'].quantile(0.001)) ], 
    x="availFAR_perc_07" , nbins = 125)

fig.update_layout(title="Distrubution of available FAR of Developed Lots")
fig.write_image( r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Initial Screening\FARDist_DevSites.png' )
fig.show()

#%% Histogram of Recent Change
pl['last_Change'] = pl[['last_YearBuilt','last_YearAlter']].max(axis=1)
pl[ ['last_YearBuilt','last_YearAlter','last_Change'] ]

pl = pl[ (pl['last_Change'] < 2017) & (pl['last_Change'] > 1900) ]

pl['last_Change'].hist()
plt.show()

#%% Histogram: Distrubution of Lots with Rent St. Units Over Years
pl['boro'] = pl.index.str[0]

pl['boro'] = pl['boro'].str.replace("1","MN")
pl['boro'] = pl['boro'].str.replace("2","BX")
pl['boro'] = pl['boro'].str.replace("3","BK")
pl['boro'] = pl['boro'].str.replace("4","QN")
pl['boro'] = pl['boro'].str.replace("5","SI")

fig = px.histogram(
    pl[ (pl['st_2017']>0) & (pl['last_YearBuilt']>1899) ], 
    x="last_YearBuilt", 
    color="boro" , 
    nbins = 100)

fig.update_layout(title="Distrubution of Lots with Rent St. Units Over Years")
fig.write_image( r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\RentSt_YearHist.png' )
fig.show()

#%% Per Puma DOB's and percentage development
# Trends per PUMA based on DOB
# Sara created a per lot permit count. 
pl['is_permit'] = np.where( pl['permits_07'] > 0 , 1 , 0)
gr = pl[['puma','is_permit']].groupby(by='puma',as_index=False).agg(['sum', len ])
gr.columns = gr.columns.droplevel()

gr['Perc'] = (gr['sum']*100 / gr['len']).round()

#---- Format and join with PUMAS
pumas['puma'] = pumas['puma'].astype(int)
pumas = pumas.join( gr , on='puma')

# ---- PLOT
variety_labels = ['Very low', 'Low', 'Moderate', 'High', 'Very high']

pumas['perc_Bins'] = pd.qcut(pumas['Perc'], 
                            q=[0, 0.2, 0.4, 0.6, 0.8, 1], 
                            labels=variety_labels)

pumas = pumas.to_crs(3857) #Pseudo Mercator Projection
pumas.plot( column = 'perc_Bins' , cmap = 'OrRd', legend=True, figsize=(12,8))
# --- Format Plot
sns.despine(top=True,left=True,right=True,bottom=True)
plt.tick_params(left=False,
                bottom=False,
                labelleft=False,
                labelbottom=False)
plt.title('Ranking Percentage of Lots with Permits Issued in 07')
plt.show()

#%% Format and reduce
pumas = pumas[['puma','geometry','failed','passed','total','perc_failed','perc_Bins']]
pumas.columns = ['puma','geometry','screen_failed','screen_passed','tot_lot_count','screen_failed_perc','dev_trends_permit']
pumas.head()
#%% ---------------------------  DEV TRENDS
#Check dev trends from 97 to 07

folder = r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\T_Pluto\nyc_pluto_07c'
files = [i for i in os.listdir( folder) if i.split(".")[1] != 'pdf']

#Compile Pluto 07
pl07 = pd.DataFrame()
for f in files:
    temp = pd.read_csv( os.path.join(folder,f) )
    pl07 = pl07.append( temp )

pl07.head()

#%% --- Dev Trends per YearBuilt instead of DOB
# Percentage altered in the past 10 years

#73042 buildings were altered in the last 10 years at 2007
pl07['recent_alter'] = pl07[['YearBuilt','YearAlter1','YearAlter2']].max( axis = 1)
pl07['is_altered'] =  np.where( pl07['recent_alter']>1997 , 'Y','N' )

pl07b = pl07#[ pl07['is_altered'] == 'Y' ].copy()
pl07b['BBL'] = pl07b['BBL'].astype(str)
pl07b['BBL'] = pl07b['BBL'].str.split(".").str[0]

pl07b = pl07b.join(
    pl[['puma']],
    on = 'BBL'
)

pl07b['puma'] = pl07b['puma'].astype(str)
pl07b['puma'] = pl07b['puma'].str.split('.').str[0]

gr = pd.pivot_table(
    data = pl07b[['is_altered','puma']],
    index = 'puma',
    columns=['is_altered'],
    aggfunc=len
)

gr['total'] = gr['Y'] + gr['N']
gr['perc_altered'] =( gr['Y']*100 / gr['total']).round()

gr.sort_values(by='perc_altered',ascending=False)

#%% --- Join and Plot in GEO -> Development trands per Year Built
pumas = pumas.set_index('puma')
pumas.index = pumas.index.astype(str)
pumas = pumas[ 'geometry	screen_failed	screen_passed	tot_lot_count	screen_failed_perc	dev_trends_permit'.split("\t") ]
pumas = pumas.join(gr)

variety_labels = ['Very low', 'Low', 'Moderate', 'High', 'Very high']
pumas['dev_trends_constrcution'] = pd.qcut(pumas['perc_altered'], 
                            q=[0, 0.2, 0.4, 0.6, 0.8, 1], 
                            labels=variety_labels)

pumas = pumas.to_crs(3857) #Pseudo Mercator Projection
pumas.plot( column = 'dev_trends_constrcution' , cmap = 'OrRd', legend=True, figsize=(12,8))
# --- Format Plot
sns.despine(top=True,left=True,right=True,bottom=True)
plt.tick_params(left=False,
                bottom=False,
                labelleft=False,
                labelbottom=False)
plt.title('Altered Lot Percentage in the Past 10 years, 97-07')
plt.show()

#%% -----------------  Join Sara's Demos to PUMA files.  

demos = gpd.read_file( r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\CensusDataIndicators_PUMAs\ACS_Pop_and_HousingVacancy_Indicators_PUMAS.geojson")
demos['PUMACE10'] = demos['PUMACE10'].astype(str).str[1:]
demos = demos.drop( ['STATEFP10','GEOID10','NAMELSAD10'] , axis = 1)
demos = demos.set_index('PUMACE10')
demos.columns = [i[1]+"_"+i[0] for i in demos.columns[ demos.columns.str.contains("_") ].str.split("_",n=1)] + ['geometry']
demos.head()


#%% --- Format and Join
pumas = pumas.drop( 'N	Y	total'.split("\t") , axis = 1)
pumas.columns = pumas.columns.str.replace("perc_altered",'dev_trends_lots_altered_perc')
pumas = pumas.join( demos.drop("geometry",axis=1) )
pumas.head()

#%% ---- Export
pumas['dev_trends_constrcution'] = pumas['dev_trends_constrcution'].astype(str)
pumas[ 'dev_trends_permit' ] = pumas[ 'dev_trends_permit' ].astype(str)

pumas.to_file(
    r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\CensusDataIndicators_PUMAs\Master_Pumas.geojson',
    encoding = 'utf-8',
    driver = 'GeoJSON'
)


#%% ----------------------- How to Capture More buildings by altering thresholds.

lot = 2500
far = 0

plb['new_sc'] = np.where(
    (plb['LotArea_07'] > lot) & 
    (plb['availFAR_perc_07'] > far)
, "Captured","Not Captured")

print( 'Percentage of Developped Lots Covered: {}%'.format(round(len(plb[plb['new_sc']=="Captured"])*100 / len(plb))))

plt.figure( figsize=(12,10))

sns.scatterplot(
    data=plb[ (plb['LotArea_07'] < plb['LotArea_07'].quantile(0.9)) & (plb['availFAR_perc_07'] > -75) & (plb['availFAR_perc_07'] < 100 ) ],
    x='LotArea_07',
    y='availFAR_perc_07',
    s = 2.5,
    hue='new_sc'
)

plt.axhline(far , color = 'grey' , ls = "--")
plt.axvline(lot , color = 'grey', ls = "--")


plt.title("Distribution of Lot Area and Available FAR %")
plt.legend(title ="is lot captured?")
plt.show()
