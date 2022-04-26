'''
Colors
Blue: #2D8ED5
Green: #6FB986
Highlight colors:
pink: #FD4EE2
orange: #FC9A45
light grey: #BCBCBC
Mid grey: #898989
dark grey: #555555
'''

#%%
# General Imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import numpy as np
import os
from matplotlib import rc

pd.set_option("max_columns",None)
plt.rcParams['pdf.fonttype'] = 42

#Final Destination folder
folder = r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Final_Replace'

from matplotlib import rcParams

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Open Sans', 'DejaVu Sans']

#General Color Scheme
color_blue = '#2D8ED5'
color_pink = '#FD4EE2'
color_lgrey = '#BCBCBC'
color_dgrey = '#555555'

pl = pd.read_csv(r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv")
pl.head()

#%%
# Slide 3
# What is covered by CEQR now. INITIAL SCREENING 
# Lot size and FAR availabilty
# is_lot_small_07 , is_FAR_small_07 ,

pl1 = pl[
    (pl['YearBuilt_17'] >= 2007) |
    (pl['has_disappered'] == 1) |
    (pl['has_lotincreased'] == 1)
].copy()

pl1 = pl1[ ~pl1['LotArea_07'].isnull() ] # Has area in 2007
pl1 = pl1[ ~pl1['puma'].isnull() ] # Has Puma by location


pl1['initial_screen'] = pl1['is_lot_small_07'] + pl1['is_FAR_small_07']
pl1['initial_screen'] = np.where( pl1['initial_screen']==0 , "Y",'N')

gr = pl1.groupby( by='initial_screen' , as_index=False ).size()

fig, ax = plt.subplots(figsize=(8, 6))
sns.barplot(data = gr,x = 'initial_screen',y = 'size' , palette=[color_lgrey,color_pink], ax=ax)
sns.despine(top=True, right=True, bottom=False,left = True, ax=ax)
ax.grid(axis="y" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
plt.xticks(fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontsize=10 , color=color_dgrey) #y axis numbers
ax.tick_params( axis="y" , left=False ) # Remove ticks above the numbers
ax.tick_params( axis="x" , color = "#333" ) # Remove ticks above the numbers
ax.spines['bottom'].set_color( "#333" ) # left axis line to grey
plt.xlabel('') 
plt.ylabel('')
plt.title('Of the Developped (Year Built > 2007) Lots,\n How many passed CEQR inital Screening', fontsize=14 , color=color_dgrey )
plt.savefig( os.path.join(folder,'InitialScreenBar.pdf'))
plt.show()

#%%
#slide 6 ->  Histogram LOT AREA, 
# for Developped Lots
# Data is Quantile transformed to Normal Distributon to calculate median - hign - low
from sklearn.preprocessing import QuantileTransformer
from matplotlib.lines import Line2D
plt.rcParams['pdf.fonttype'] = 42
color_green = '#6FB986'
var = 'LotArea_07'

qt = QuantileTransformer(n_quantiles=500, output_distribution='normal')
t = pl1[ (pl1[var] > 0.01) & (pl1[var] < pl1[var].quantile(0.95)) ].copy()

def get_bounds(data , var):
    array = np.array(  data[var] ).reshape(-1, 1)
    var2 = "{}2".format(var)
    t[ var2 ] = qt.fit_transform( array )

    median = t[var2].median()
    mean = t[var2].mean()
    std = t[var2].std()
    lower = mean - (std*2)
    higher = mean + (std*2)

    skewness = (3*(mean-median)) / std
    print( "Resulting arrays skewness is: {}".format( skewness ) )

    a = data.iloc[ (data[var2]- mean ).abs().values.argsort()[:2]]
    t2 = t[ (t[var2] > lower) & (t[var2] < higher ) ] 

    return [a[var].values[0] ,t2[var].min() , t2[var].max()]

mean,lower,higher = get_bounds( t , var )
print( lower, mean, higher )

rem = t[ (t[var] > lower) & (t[var] < higher ) ]
print( "{}% of the data is in".format(round(len(rem)*100 / len(pl1) , 2)) )

fig, ax = plt.subplots(figsize=(8, 6))

x1 = t[ t['has_disappered']==1 ][var]
x2 = t[ t['YearBuilt_17'] >= 2007 ][var]
text_h = 3000

#Stacked Histogram
plt.hist( [x1 , x2] ,bins=60, stacked=True, color = [color_blue,color_green])
plt.annotate("{}".format( round(mean) ) , xy=(mean+0.05,text_h) , color = color_pink )
plt.annotate("{}".format( round(lower) ) , xy=(lower+0.05,text_h) , color = color_dgrey )
plt.annotate("{}".format( round(higher) ) , xy=(higher+0.05,text_h) , color = color_dgrey )
plt.axvline( mean , color = color_pink , lw = 1.5 , ls ='--')
plt.axvline( higher , color = color_lgrey)
plt.axvline( lower , color = color_lgrey)
sns.despine(top=True, right=True, bottom=False,left = True, ax=ax)
ax.grid(axis="x" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
plt.xticks(fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontsize=10 , color=color_dgrey) #y axis numbers
ax.tick_params( axis="y" , left=False ) # Remove ticks above the numbers
ax.tick_params( axis="x" , color = "#333" ) # Remove ticks above the numbers
ax.spines['bottom'].set_color( "#333" ) # left axis line to grey
plt.fill_between(x=[ lower, higher ] , y1=0,y2=3500, color = color_lgrey, alpha = 0.25 )
plt.title('Distribution of Lot Areas \n {}% of the data is between {} and {} sq.ft'.format( int(round(len(rem)*100 / len(pl1) , 0)),int(lower), int(higher)) , fontsize=14 , color=color_dgrey)
plt.savefig( os.path.join(folder,'LotDistribution.pdf'))
custom_lines = [Line2D([0], [0], color=color_blue, lw=4),
                Line2D([0], [0], color=color_green, lw=4)]
plt.legend( custom_lines , ["Merged Lots","Developed>07"] , frameon=False)
plt.show()

#%%
# Slide 6 -> Histogram Available FAR perc
# Removed the 100% availability of FAR up tick. 

from sklearn.preprocessing import QuantileTransformer
var = 'availFAR_perc_07'

qt = QuantileTransformer(n_quantiles=500, output_distribution='normal')
t = pl1[ (pl1[var] >= -100) & (pl1[var] < 100) ].copy()


# High - Low bounds
def get_bounds(data , var):
    array = np.array(  data[var] ).reshape(-1, 1)
    var2 = "{}_2".format(var)
    data[ var2 ] = qt.fit_transform( array )

    median = data[var2].median()
    mean = data[var2].mean()
    std = data[var2].std()
    lower = mean - (std*2)
    higher = mean + (std*2)

    skewness = (3*(mean-median)) / std
    print( "Resulting arrays skewness is: {}".format( skewness ) )

    a = data.iloc[ (data[var2]- mean ).abs().values.argsort()[:2]]
    data2 = data[ (data[var2] > lower) & (data[var2] < higher ) ] 

    return [a[var].values[0] ,data2[var].min() , data2[var].max()]

mean,lower,higher = get_bounds( t , var )
print( "lower: {}\nmean: {}\nhigh: {}".format(lower, mean,higher) )
print( "high-low calculations done")
rem = t[ (t[var] >= lower) & (t[var] <= higher ) ]
print( "{}% of the data is in".format(round(len(rem)*100 / len(t) , 2)) )

fig, ax = plt.subplots(figsize=(8, 6))

x1 = t[ t['has_disappered']==1 ][var]
x2 = t[ t['YearBuilt_17'] >= 2007 ][var]

#Stacked Histogram
text_h = 600
plt.hist( [x1 , x2] ,bins=60, stacked=True, color = [color_blue,color_green])
plt.annotate("{}%".format( round(lower) ) , xy=(lower+0.5,text_h) , color = color_lgrey )
plt.annotate("{}%".format( round(mean) ) , xy=(mean+0.5,text_h) , color = color_pink )
plt.annotate("{}%".format( round(higher) ) , xy=(higher+0.5,text_h) , color = color_lgrey )

plt.axvline( lower , color = color_lgrey)
plt.axvline( mean , color = color_pink)
plt.axvline( higher , color = color_lgrey)

sns.despine(top=True, right=True, bottom=False,left = True, ax=ax)
ax.grid(axis="x" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
plt.xticks(fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontsize=10 , color=color_dgrey) #y axis numbers
ax.tick_params( axis="y" , left=False ) # Remove ticks above the numbers
ax.tick_params( axis="x" , color = "#333" ) # Remove ticks above the numbers
ax.spines['bottom'].set_color( "#333" ) # left axis line to grey
plt.fill_between(x=[ lower, higher ] , y1=0,y2=text_h, color = color_lgrey, alpha = 0.25 )
custom_lines = [Line2D([0], [0], color=color_blue, lw=4),
                Line2D([0], [0], color=color_green, lw=4)]
plt.legend( custom_lines , ["Merged Lots","Developed>07"] , frameon=False)
plt.title('Distribution of Available FAR % \n {}% of the data is between {}% and {}%\n100% FAR availaiblity is removed for calculations'.format( int(round(len(rem)*100 / len(t) , 0)), lower , higher ) , fontsize=14 , color=color_dgrey)
plt.savefig( os.path.join(folder,'FarDistribution.pdf'))
plt.show()

#%%
# What does 100 FAR Availabiity Look Like
# Their landuses are 10 and 11 mostly

var = 'availFAR_perc_07'
t = pl1[ (pl[var] == 100) & pl["LandUse_07"] != 0 ].copy()
t['LandUse_07'] = t['LandUse_07'].astype(int)

fig, ax = plt.subplots(figsize=(8, 6))

sns.countplot(
    data = t,
    ax = ax,
    x = 'LandUse_07',
    palette = [color_blue,color_green],
    hue = 'has_disappered'
)
sns.despine(top=True, right=True, bottom=False,left = True, ax=ax)
ax.grid(axis="x" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
plt.xticks(fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontsize=10 , color=color_dgrey) #y axis numbers
ax.grid(axis="x" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
plt.xticks(fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontsize=10 , color=color_dgrey) #y axis numbers
ax.tick_params( axis="y" , left=False ) # Remove ticks above the numbers
ax.tick_params( axis="x" , color = "#333" ) # Remove ticks above the numbers
ax.spines['bottom'].set_color( "#333" ) # left axis line to grey
ax.grid(axis="y" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
ax.set_xlabel('')
ax.set_ylabel('')
plt.legend( frameon=False , title='Disappeared')
plt.title( "Landuse Values for Lots with 100% FAR availability")
plt.savefig( os.path.join(folder,'100FAR_Landuse.pdf'))
plt.show()


#%%
# Built Year Units of Rent Stabilized - HEATMAP -> Slide 23
from matplotlib.patches import Rectangle
start = 1864
end = 2024
breaks = 10

t = pl1[ (pl1[var] > 0.01) & (pl1[var] < pl1[var].quantile(0.95)) ].copy()

t['Year_Bin'] = pd.cut(
    t['YearBuilt_07'],
    bins = [i for i in range(start,end,breaks)],
    labels = ["{}'s".format(i) for i in range(start,end,breaks)][:-1]
)

t['is_st'] = np.where(
    t['st_2007'] > 0 , 1 , 0
)

font = 'Open Sans'

pt = pd.pivot_table(
    data = t[['Year_Bin','is_st','Units']],
    index = "Year_Bin",
    columns = 'Units',
    values = 'is_st',
    aggfunc = 'sum'
)

def make_Ramp( ramp_colors ): 
    from colour import Color
    from matplotlib.colors import LinearSegmentedColormap
    color_ramp = LinearSegmentedColormap.from_list( 'my_list', [ Color( c1 ).rgb for c1 in ramp_colors ] )
    #color = [matplotlib.colors.rgb2hex(i) for i in [color_ramp(a) for a in np.linspace(0,1,5)] ]
    return color_ramp
color = make_Ramp( [ "#FFFFFF",color_blue ] ) 

fig, ax = plt.subplots( figsize=(6,6) )

sns.heatmap(
    ax = ax,
    data = pt,
    cmap = color,
    annot = True,
    fmt='g', cbar=False
)

ax.add_patch( Rectangle((6, 13),
                        2, -13,
                        fc='none',
                        alpha = 1,
                        color ='#FC9A45',
                        linewidth = 1.5,
                        linestyle="--") )
plt.xlim((0,8.1))
plt.ylim( (15,-0.1) )
plt.xticks(fontname=font,fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontname=font,fontsize=10 , color=color_dgrey) #y axis numbers
ax.tick_params( axis="y" , left=False ) # Remove ticks above the numbers
ax.tick_params( axis="x" , bottom = False ) # Remove ticks above the numbers
plt.xlabel('')
plt.ylabel('')
plt.savefig( os.path.join(folder,'Heat_RentStUnits.pdf'))
plt.title( "Number of Lots with Rent Stab. Units" , fontname = font , color = '#333')
plt.show()

#%%
# 

t = pl1[ pl1['st_2007'] > 0].copy()
t = t[ t['UnitsRes_07'] > 0 ]
t['perc_units'] = round( (t['st_2007']*100) / t['UnitsTotal_07'] , 2)

t = t[ t['perc_units'] < t['perc_units'].quantile(0.98)]

fig,ax = plt.subplots(figsize=(8, 6))

plt.axvline( t['perc_units'].median() , color = color_pink , ls='--')
plt.annotate( "Median: {}".format(t['perc_units'].median()) , xy = (t['perc_units'].median()+2, 405) , color = color_pink)
t['perc_units'].hist(bins = 30 )
plt.title('Majority of (>50%) rent stabilized units are in lots where\n the majority of units ({}%) are rent stabilized.'.format(t['perc_units'].median()))

sns.despine(top=True, right=True, bottom=False,left = True, ax=ax)
ax.grid(axis="x" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
plt.xticks(fontname=font,fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontname=font,fontsize=10 , color=color_dgrey) #y axis numbers
ax.tick_params( axis="y" , left=False ) # Remove ticks above the numbers
ax.tick_params( axis="x" , color = "#333" ) # Remove ticks above the numbers
ax.spines['bottom'].set_color( "#333" ) # left axis line to grey
locs, labels=plt.xticks()
plt.xticks(locs, ["{}%".format(round(i)) for i in plt.xticks()[0]] )
plt.xlim((0,157))
plt.savefig( os.path.join(folder,'RentSt_How.pdf'))
plt.show()

#%%
# Recent Alteration based on %rent st in the building.

t = pl[ ~pl['LotArea_07'].isnull() ].copy()
print(len(t))
t['st_2007'] = t['st_2007'].fillna( 0 )

t['is_st'] = np.where(
    t['st_2007'] > 0 , "Y","N"
)

t['perc_units'] = round( (t['st_2007']*100) / t['UnitsTotal_07'] , 2)
t['perc_units'] = t['perc_units'].fillna( 0 )
print(len(t))
bins = [0,1,10,20,30,40,50,60,70,80,90,100,500]
t['rank_units'] = pd.cut(
    t['perc_units'],
    bins = bins,
    labels = ["No",'1-10%','10-20%','20-30%','30-40%','40-50%','50-60%','60-70%','70-80%','80-90%','90-100$',"100%+"]
)
print(len(t))
pt = pd.pivot_table(
    data = t[['rank_units','recent_alter']],
    index = 'rank_units',
    columns= 'recent_alter',
    aggfunc=len
)

pt.columns = ['N','Y']
pt['perc'] = (pt["Y"]*100 / pt.sum(axis = 1) ).round(2)

fig,ax = plt.subplots(figsize=(8, 6))
pt[pt.index != "No" ]['perc'].plot(kind='bar',color = [color_blue,color_blue,color_blue,color_blue,color_blue,color_pink,color_pink,color_pink,color_pink,color_pink,color_blue] )

plt.title("Percentage of Alteration vs Percentage Rent Stabilized Units in Lot")
sns.despine(top=True, right=True, bottom=False,left = True, ax=ax)
ax.grid(axis="y" , lw=0.25, color=color_lgrey , alpha = 0.5) #add grid on x axis
plt.xticks(fontname=font,fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontname=font,fontsize=10 , color=color_dgrey) #y axis numbers
ax.tick_params( axis="y" , left=False ) # Remove ticks above the numbers
ax.tick_params( axis="x" , color = "#333" ) # Remove ticks above the numbers
ax.spines['bottom'].set_color( "#333" ) # left axis line to grey
#locs, labels=plt.yticks()
#plt.xticks(locs, ["{}%".format(round(i)) for i in plt.yticks()[0]] )
#plt.xlim((0,157))
plt.savefig( os.path.join(folder,'RentSt_How.pdf'))
plt.show()

plt.show()

#%%
# Export data for TASC SELECTOR


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import numpy as np
import os
import datetime as dt

#Final Destination folder
folder = r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Final_Replace'

plo = pd.read_csv(r"C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv")

pl = plo[
    (plo['YearBuilt_17'] >= 2007) |
    (plo['has_disappered'] == 1) |
    (plo['has_lotincreased'] == 1)
].copy()

pl = pl[ ~pl['LotArea_07'].isnull() ] # Has area in 2007

pl['recent_built'] = np.where(
    pl['YearBuilt_17'] >=2007,
    1,0
)

pl['is_st'] = np.where(
    ~pl['st_2007'].isnull(),
    1,0
)

pl['has_merged'] = np.where(
    (pl['has_disappered'] == 1) | (pl['has_lotincreased'] == 1),
    1,0
)

#%%
plb = pl[ (pl['recent_alter'] == 1) | (pl['recent_built']==1) | (pl['has_merged']==1)].copy()

plb = plb[ (plb['LotArea_07'] > 0) & (plb['LotArea_07'] < plb['LotArea_07'].quantile(0.99)) ]
plb = plb[ (plb['availFAR_perc_07'] > -100 ) & (plb['availFAR_perc_07'] <= 100) ]

plb['puma'] = plb['puma'].astype(str).str.split('.').str[0]

print("{} data points are exported".format(len(plb)) )

plb[['puma','LotArea_07','availFAR_perc_07','st_2007','recent_built','recent_alter','is_st','has_disappered','has_lotincreased','has_merged']].to_csv(
    'C:/Users/csucuogl/Documents/GitHub/TASC_Selector/data/{}_Altered.csv'.format(dt.datetime.now().strftime("%Y%m%d"))
)

#%%

plb['LotArea_07'].hist( bins = 100)
plt.xlim(0,35000)
plt.show()
