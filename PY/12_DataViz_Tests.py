
"""
This code is for testing simple data viz and styling to be replicated in the TASC web tool
Imported data has recent-alter recent-change recent built together. Make sure to pick one for analysis
recent-alter : max(YearBuilt,YearAlter1,YearAlter2) < 10 years
recent-change: If there was a A1, NB or DM permits applied
recent built: YearBuilt > Now-10 years 
"""

'''
VIZ TO DO:
1. FAR-Size
2. PUMA generelizations
3. Rent stabts
4. Ceqr / Pass-Fail / Per PUMA or Boro

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
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import numpy as np
import matplotlib

pd.set_option("max_columns",None)

color_blue = '#2D8ED5'
color_pink = '#FD4EE2'
color_lgrey = '#BCBCBC'
color_dgrey = '#555555'

# _3 file is in Psuedo Mercator, Also expoted from QGIS
# Other files are giving an error that I do not understand
path = '/Users/saraeichner/Dropbox/TASC Application/DATA/SoftSites/RecentChange_2022_4.geojson'
df = gpd.read_file( 
    path,
    encoding='utf-8',
    crs=3857
     )

#%%
# I am taking only the recent_alters
# Convert data to centroids, I don't need polygons for this 
alt = df[ df['recent_alter'] == 1].copy()
alt = alt.set_index("BBL")
#Convert data to points at centeroid
alt.geometry = alt['geometry'].centroid

alt.head()

#%%
# Import and match Pumas and add to alt
#Add puma names to each lot centroid
path = '/Users/saraeichner/Dropbox/TASC Application/DATA/Master_PUMA.geojson'
pumas = gpd.read_file( path )
pumas = pumas.to_crs( 3857 )

alt1 = gpd.sjoin( alt, pumas[['puma','geometry']],op='intersects' )
alt1.sample(10)

#%%
# Percentage of Major Alterations Covered by CEQR per BORO & PUMA
import matplotlib.ticker as mtick

# Calculate is_ceqr counts per puma
pt = pd.pivot_table(
    alt1[["Borough",'puma','is_ceqr']],
    index=["Borough",'puma'],
    columns='is_ceqr',
    aggfunc= len 
)

#Calculate percentage
pt.columns = ['no','yes']
pt['total'] = pt['yes']+ pt['no']
pt['perc_yes'] = (pt['yes']*100 / pt['total']).round(2)
pt['perc_no'] = (pt['no']*100 / pt['total']).round(2)

pt = pt.sort_values(by=['Borough','perc_yes'] , ascending=False)

font = 'Source Sans' 

#Plot
fig, ax = plt.subplots(figsize=(8, 12))
pt[['perc_yes','perc_no']].plot(kind='barh', ax=ax, stacked=True, width=.75, color=[color_blue, color_pink])
sns.despine(
    top=True, right=True, bottom=True
)

#PLot Styling
plt.grid(axis="x" , lw=0.25, color=color_lgrey) #add grid on x axis
plt.xticks(fontname=font,fontsize=10 , color=color_dgrey) #x axis numbers
plt.yticks(fontname=font,fontsize=10 , color=color_dgrey) #y axis numbers
plt.tick_params( axis="x" , bottom=False ) # Remove ticks above the numbers
ax.xaxis.set_major_formatter( '{x:2.0f}%' ) # Add % to x axis
ax.spines['left'].set_color( color_dgrey ) # left axis line to grey
plt.xlabel('') #remove labels
plt.ylabel('')
plt.title('Percentage of Major Alterations Covered by CEQR', fontname=font, fontsize=14 , color=color_dgrey )
plt.savefig("/Users/saraeichner/Dropbox/TASC_dataviz_exports/puma_majorAltCoveredbyCeqr.pdf")
plt.show()

#%%
# Percentage of Major Alterations Covered by CEQR per BORO

pt = pd.pivot_table(
    alt1[["Borough",'puma','is_ceqr']],
    index=["Borough"],
    columns='is_ceqr',
    aggfunc= len 
)

#Calc percentages
pt.columns = ['no','yes']
pt['total'] = pt['yes']+ pt['no']
pt['perc_yes'] = (pt['yes']*100 / pt['total']).round(2)
pt['perc_no'] = (pt['no']*100 / pt['total']).round(2)

pt = pt.sort_values(by=['perc_yes'] , ascending=False)

#Plot
font = 'Corbel' 
fig, ax = plt.subplots(figsize=(12, 4))
pt[['perc_no','perc_yes']].plot(kind='barh', width=0.8, ax=ax, stacked=True, color=[color_pink, color_blue])
sns.despine(
    top=True, right=True, bottom=True
)

#Styling
plt.grid(axis="x" , lw=0.25, color=color_lgrey)
plt.xticks(fontname=font,fontsize=12 , color=color_dgrey)
plt.yticks(fontname=font,fontsize=12 , color=color_dgrey)
plt.tick_params( axis="x" , bottom=False )
ax.xaxis.set_major_formatter( '{x:1.0f}%' )
ax.spines['left'].set_color( color_dgrey )
plt.xlabel('')
plt.ylabel('')
plt.title('Percentage of Major Alterations Covered by CEQR', fontname=font, fontsize=18 , color=color_dgrey )
plt.show()

#%%

pumas.head(20)

#%%

#Which columns to plot
vars = ['NU_uniqueOwners','NU_unitResInc','PERC_rentSt_17','NU_permits_17','PERC_recentAlter','EA_GrdPf_17','GRAPI>30_17','LimELP_17']

divs = 5 #How many divisions
height = 0.3 #height of the value line
height_tick = 0.05 #height of the ticks
ranks = ['lower','low','avg','high','higher'] #labels on x axis
y = 0.5
pumaCode = '04010'
font = 'Source Sans' 

#Make a color ramp from pink to blue
def make_Ramp( ramp_colors ): 
    from colour import Color
    from matplotlib.colors import LinearSegmentedColormap
    color_ramp = LinearSegmentedColormap.from_list( 'my_list', [ Color( c1 ).rgb for c1 in ramp_colors ] )
    color = [matplotlib.colors.rgb2hex(i) for i in [color_ramp(a) for a in np.linspace(0,1,5)] ]
    return color
color = make_Ramp( [ color_blue,color_pink ] ) 

# There are 8 rows and 2 columns. first column is for text
fig, axs = plt.subplots(len(vars),2, figsize=(10,7), gridspec_kw={'width_ratios': [1, 9]})

for i in range(len(vars)): # Draw for each vars
    
    var = vars[i]
    ax = axs[i][1] # Axis for plotting
    text_ax = axs[i][0] # Axis for text
    text_ax.annotate( var , ( 0 , 0.48) , ha='left') # Write Text

    var_cut = "{}_rank".format(var)
    pumas[var_cut] = pd.qcut( # Quantile classify data to 0-5 based on div #
        pumas[var].rank(method='first') , # This allows for a more equal division on equal numbers
        q = [i/divs for i in range(divs+1)] , 
        labels = [i+1 for i in range(divs)] )

    #Value to plot / Isolate by puma as well.
    value = pumas[ pumas['puma'] == pumaCode][var_cut].tolist()[0]

    #Start Plot
    ax.axhline( y , color=color_dgrey ) #x-axis
    for t in range(5):ax.annotate( ranks[t] , (t+1,0.35) , ha='center' , fontname = font, fontsize=8 , color=color_lgrey)
    for t in range(divs): ax.plot( [t+1,t+1],[y-height_tick,y+height_tick] , color = color_dgrey , lw = 0.75 ) # x-ticks
    ax.plot( [value,value],[y-(height/2),y+(height/2)] , color = color[value-1] , lw = 5 ) # colored line
    ax.tick_params( left=False , labelleft=False,bottom=False , labelbottom=False ) # Remove original laberls
    text_ax.tick_params( left=False , labelleft=False,bottom=False , labelbottom=False ) # Remove original laberls
    ax.set_xlim( left=0.95,right=5.05 )
sns.despine(top=True, right=True, bottom=True,left=True) #remove the default box around the plot
plt.show()

#%%

import random

var_cut = "{}_rank".format(var)
pumas[var_cut] = pd.qcut( 
    pumas[var].rank(method='first') , # This allows for a more equal division on equal numbers
    q = [i/divs for i in range(divs+1)] , 
    labels = [i+1 for i in range(divs)] )

pumas['y'] = [random.gauss(0.5,0.25)+0.1 for i in range(len(pumas))]
pumas['dodger'] = np.where( pumas['puma'] == pumaCode , "Y","N" )
print( var , var_cut )

fig, axs = plt.subplots(len(vars),2, figsize=(10,7), gridspec_kw={'width_ratios': [1, 9]})

for i in range(len(vars)): # Draw for each vars
    
    var = vars[i]
    ax = axs[i][1] # Axis for plotting
    text_ax = axs[i][0] # Axis for text
    text_ax.annotate( var , ( 0 , 0.48) , ha='left') # Write Text

    var_cut = "{}_rank".format(var)
    pumas[var_cut] = pd.qcut( # Quantile classify data to 0-5 based on div #
        pumas[var].rank(method='first') , # This allows for a more equal division on equal numbers
        q = [i/divs for i in range(divs+1)] , 
        labels = [i+1 for i in range(divs)] )

    #Value to plot / Isolate by puma as well.
    value = pumas[ pumas['puma'] == pumaCode][var_cut].tolist()[0]

    #Start Plot
    plt.figure( figsize=(8,1.3) )
    sns.swarmplot(
        data = pumas,x = var_cut, y = "y",
        size= 6,
        hue = 'dodger',
        palette = [ color_dgrey,color_pink ],
        ax=ax, alpha=0.9
    )
    ax.grid(axis='x', lw=0.45, color = color_dgrey)
    ax.get_legend().remove()
    sns.despine(top=True, right=True, bottom=True,left=True,ax=ax) #remove the default box around the plot
    sns.despine(top=True, right=True, bottom=True,left=True,ax=text_ax) #remove the default box around the plot
    ax.tick_params( left=False , labelleft=False ,bottom=False , labelbottom=False ) # Remove original laberls
    text_ax.tick_params( left=False , labelleft=False ,bottom=False , labelbottom=False ) # Remove original laberls
    ax.set_ylim( top=1.2, bottom=0 )
    text_ax.set_ylim( top=1, bottom=0 )
    ax.set_xlabel('')
    ax.set_ylabel('')
    text_ax.set_xlabel('')
    text_ax.set_ylabel('')
plt.show()
