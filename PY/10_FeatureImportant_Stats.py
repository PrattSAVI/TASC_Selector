
'''
Runs a basic decision tree on Master_Pluto
Records feature importance by PUMA
Run Recent Change, Alter and Built Seperately. 

'''

#%%
# Import dependencies and data
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

color_blue = '#2D8ED5'
color_pink = '#FD4EE2'
color_lgrey = '#BCBCBC'
color_dgrey = '#555555'

pd.set_option("max_columns",None)
pl = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv' , dtype={"bbl":object})
pl.head()

def remove_out(pls, col ,min,max):
    return pls[ (pls[col] < pls[col].quantile(max)) & (pls[col] > pls[col].quantile(min)) ].copy()

def create_rank(data,col):
    col_rank ="{}_rank".format(col)
    data[ col_rank ] = data[col].rank(pct=True).round(1).astype(str)
    return data

#%%
# Use Ranks to Plot Degrees
#pls is simplified
pls = pl[[ #Filter only necessary columns
    'bbl',
    'LotArea_07',
    'UnitsRes_07',
    'YearBuilt_07','YearBuilt_17','YearAlter_07','last_YearBuilt','recent_alter',
    'Landmark_07',"LandUse_07",
    'availFAR_perc_07','permits_07',
    'AssedImprov_perc_07','Compact_07',
    'puma','st_2007','project_na','airright_trans','merged','has_disappered','has_lotincreased'
    ]].copy()

pls = pls[ ~pls['puma'].isnull() ]
pls = pls[ ~pls['LandUse_07'].isnull() ]
pls["is_residential"] = np.where( pls['LandUse_07'].isin([1,2,3,4]) , "yes",'no' )

#If either of recent built of alter is above 0 record it to change

pls['recent_change'] = np.where(
    ((pls['YearBuilt_17'] >= 2007) |
    (pls['has_disappered'] == 1) |
    (pls['has_lotincreased'] == 1))
    ,1,0 )

#Recent_built - recent_alter
# Give a percentile ranking to each variable and calculate percentage of developped
col1 = 'AssedImprov_perc_07'

col_rank ="{}_rank".format(col1)
target = 'recent_change'

#Remove outliers
data = remove_out( pls, col1, 0.05,0.99)
#Create ranking from 0.1 to 1
data[ col_rank ] = data[col1].rank(pct=True).round(1).astype(str)
gr1 = data.groupby([col_rank , target ,"is_residential"]).agg({'bbl': len })
gr_rank = data.groupby( col_rank ).agg({'bbl': len })
grp = gr1.div(gr_rank, level=col_rank) * 100
grp = grp.reset_index()

grp[col_rank] = pd.Categorical( grp[col_rank] )

#Plot
gr2 = grp[ grp[target]==1].drop(target,axis=1).set_index(col_rank).pivot(columns='is_residential')
gr2.columns = gr2.columns.droplevel()
gr2.plot(kind='bar',stacked=True, color=['#e07a5f', '#3d405b'])

# Style
sns.despine(top=True,right=True,left=True,)
plt.tick_params(left=False)

# --- Make Ticks
axs = data.groupby(col_rank).agg({col1: [min,max]})
axs = axs.astype(int).astype(str)
axs['text'] = axs[col1,'min'] + " to " + axs[col1,'max']

# ---  Decorate
plt.title( 'Percentage of alterations based on Improv. Ratio ranking' )
plt.grid(axis='y',color='grey',lw=0.25)
plt.ylabel( '% of lots' )
plt.xticks( 
    ticks=[0,1,2,3,4,5,6,7,8,9,10],
    labels = axs['text'].tolist() ,
    rotation = 45 )
plt.show()

#%% ---------------  Replicate Decision Tree -------------------
# Using Ranks system
#Target can be recent change or recent built. 
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.tree.export import export_text
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

def make_data(pl):
    pls = pl[[ #Filter only necessary columns
    'bbl',
    'LotArea_07',
    'UnitsRes_07',
    'YearBuilt_07','YearBuilt_17','YearAlter_07','last_YearBuilt','recent_alter',
    'Landmark_07',"LandUse_07",
    'availFAR_perc_07','permits_07',
    'AssedImprov_perc_07','Compact_07',
    'puma','st_2007','project_na','airright_trans','merged','has_disappered','has_lotincreased'
    ]].copy()

    pls = pls[ ~pls['puma'].isnull() ]
    pls = pls[ ~pls['LandUse_07'].isnull() ]
    pls["is_residential"] = np.where( pls['LandUse_07'].isin([1,2,3,4]) , "yes",'no' )

    #If either of recent built of alter is above 0 record it to change

    pls['recent_change'] = np.where(
        ((pls['YearBuilt_17'] >= 2007) |
        (pls['has_disappered'] == 1) |
        (pls['has_lotincreased'] == 1))
        ,1,0 )

    # Site Types summary
    pls['LandUse_07'] = pls['LandUse_07'].astype(int)
    pls["is_residential"] = np.where( pls['LandUse_07'].isin([1,2,3,4]) , 1,0 )
    pls['is_stabilized'] = np.where( pls['st_2007']>0 , 1,0)
    pls['age'] = 2007 - pls['YearBuilt_07']
    pls['age'] = np.where( pls['age']>150, 150 , pls['age']) #nothing is older than 150

    #Clean and Rank
    pls = remove_out( pls, 'AssedImprov_perc_07', 0.01,0.999)
    pls = remove_out( pls, 'availFAR_perc_07', 0.01,0.999)
    pls = pls[ pls['availFAR_perc_07'] > -200 ]
    pls = pls.copy()

    return pls

#pls is simplified
pls = make_data(pl)

puma = 4001
pls = pls[ (pls['puma'] == puma) ].copy()

target = 'recent_change'
# - Build a balanaced Population
d1 = pls[ pls[target]==0 ].sample( len( pls[pls[target]==1])*2 )
d1= d1.append( pls[pls[target]==1] )
d1[target] = d1[target].astype(str)

# Prepare Train - Target Sets
inputs = ['AssedImprov_perc_07','LotArea_07','availFAR_perc_07','is_stabilized','is_residential']
d1 = d1[[target]+inputs].copy()
X = d1.iloc[:, 1:]
y = d1[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=100)

# Run Decision Tree
forest = DecisionTreeClassifier(
    random_state=42,
    min_samples_leaf=50,
    max_depth=3)

# Fitting a model and making predictions
forest.fit(X_train,y_train)
predictions = forest.predict(X_test)

print("Accuracy:",metrics.accuracy_score(y_test, predictions))

fig = plt.figure(figsize=(30,12))
plot_tree(forest, 
          feature_names=X.columns,
          class_names=d1[target].unique(), 
          filled=True, rounded=True)
plt.title( 'Of {} lots in PUMA:{}, {} are recently altered'.format(len(pls[ (pls['puma'] == puma) ]) , puma, len(d1[d1[target]=='1'])))
plt.show()

df = pd.DataFrame(data = list(zip(inputs,forest.feature_importances_)) , columns =['field','value'])
df['puma'] = puma 
df

#%% ----------------------- Feature Importance for Each PUMA -------------------
# This only calculates the importance in a for loop. 
#pls is simplified
pls = make_data(pl)

#Target Var for Decision Tree
target = 'recent_change'

inputs = ['AssedImprov_perc_07','LotArea_07','availFAR_perc_07','is_stabilized','is_residential','age']
imps = pd.DataFrame()

for puma in pls['puma'].unique():
    #puma = 4003
    d = pls[ (pls['puma'] == puma) ].copy()

    a = []
    #Run the tree muliple times to avereage results
    for i in range(30):
        # - Build a balanaced Population
        d1 = d[d[target]==0].sample( len( d[d[target]==1])*2 )
        d1= d1.append( d[d[target]==1] )
        d1[target] = d1[target].astype(str)

        d1 = d1[[target]+inputs].copy()
        X = d1.iloc[:, 1:]
        y = d1[target]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=100)

        forest = DecisionTreeClassifier(
            random_state=42,
            min_samples_leaf=40,
            max_depth=3)

        # Fitting a model and making predictions
        forest.fit(X_train,y_train)
        predictions = forest.predict(X_test)
        a.append( forest.feature_importances_ )
    temp = pd.DataFrame( data=a ).transpose()
    temp.index = inputs
    temp['mean'] = temp.mean(axis=1)
    temp = temp[['mean']]
    temp = temp.transpose()
    temp.index = [puma]

    imps = imps.append( temp )

plt.figure( figsize=(6,12) )
sns.heatmap(
    imps.sort_index().multiply(10).round(0) ,
    cmap = "OrRd",
    annot=True
)
plt.show()

#%% 
# Plot Feature Importantce on a map series
import seaborn as sns
import geopandas as gpd

def make_Ramp( ramp_colors ): 
    from colour import Color
    from matplotlib.colors import LinearSegmentedColormap
    color_ramp = LinearSegmentedColormap.from_list( 'my_list', [ Color( c1 ).rgb for c1 in ramp_colors ] )
    return color_ramp
cmap = make_Ramp( [ color_blue,color_pink ] ) 

# Import PUMAS
pumas = gpd.read_file( r"C:\Users\csucuogl\Desktop\DATA\NYC\2010 Public Use Microdata Areas (PUMAs).geojson" )
pumas = pumas[['puma','geometry']]
pumas['puma'] = pumas['puma'].astype(int)
pumas = pumas.join( imps ,on='puma')

#x,y for subplots
chart_num = len(imps.columns)
y=2

fig, axs = plt.subplots(   y, int(chart_num/y) , figsize=( 12, 6))
fig.subplots_adjust(hspace=0, wspace=0.05)

# For each column, plot in a specific subplot
for i in range(len(imps.columns)):
    col = imps.columns[i]
    ax = axs[  i%y , int(i%(chart_num/y)) ]
    pumas.plot( column=col,  ax = ax , cmap = cmap , legend = True , vmin=0, vmax=1)
    ax.set_title( col )
    sns.despine( ax = ax , left=True, right=True, bottom=True, top=True )
    ax.tick_params( left=False , labelleft=False,bottom=False , labelbottom=False ) # Remove original laberls

plt.tight_layout()
plt.savefig(r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Final_Replace\FeatImp_Built-02.pdf')
plt.show()


#%%


#%% ------------------------  TOOL to MEASURE FEATURE IMPORTANCE ------------------
# Slider helping to filter the data
# Can we achieve %50 coverage of the data just by looking at the sliders. 

import ipywidgets as widgets
from ipywidgets import interact
Lot_slider = widgets.IntText(
    value=0,
    step = 250,
    description='Min. Lot Area:',
)

Far_slider = widgets.IntText(
    value=-100,
    step = 10,
    description='Avail. FAR %:',
)

Improve_slider = widgets.IntText(
    value=5,
    step = 10,
    description='As. Improve Ratio:',
)

ddown = widgets.Dropdown(
    options= ["all"] + sorted(data['puma'].unique().tolist()),
    value='all',
    description='PUMA #:',
    disabled=False,
)

box = widgets.Checkbox(False, description='Use Lots without rent st. units')

def show_df(puma,lot,far,imp,st):
    if puma != 'all':
        d1 = data[data['puma']==puma].copy()
    else:
        d1 = data.copy()

    plt.figure( figsize=(12,2))
    d1['LotArea_07'].hist(bins=80,color='#b7b7a4')
    sns.despine(top=True,left=True,right=True)
    plt.tick_params(left=False)
    plt.grid(axis='x')
    plt.axvline( lot , color = '#bb3e03')
    plt.xlim( 0 , d1['LotArea_07'].max() )
    plt.title('Distribution of Lot Areas')
    plt.show()

    plt.figure( figsize=(12,2))
    d1['availFAR_perc_07'].hist(bins=50, color = '#b7b7a4')
    sns.despine(top=True,left=True,right=True)
    plt.tick_params(left=False)
    plt.grid(axis='x')
    plt.axvline( far , color = '#bb3e03')
    plt.xlim( -100 , 100 )
    plt.title('Distribution of Available FAR')
    plt.show()

    plt.figure( figsize=(12,2))
    d1['AssedImprov_perc_07'].hist(bins=50, color = '#b7b7a4')
    sns.despine(top=True,left=True,right=True)
    plt.tick_params(left=False)
    plt.grid(axis='x')
    #plt.axvline( 40 , color = '#bb3e03')
    plt.xlim( d1['AssedImprov_perc_07'].min() , d1['AssedImprov_perc_07'].max() )
    plt.title('Assesed Improv Ratio')
    plt.show()

    gr = d1.groupby(by='st_2007').size()
    plt.figure( figsize=(12,2) )
    gr.plot(kind='barh' , color = '#b7b7a4' )
    sns.despine(top=True,left=True,right=True)
    plt.title("Number of Rent Stabilized Units")
    plt.ylabel('')
    plt.yticks([0,1],['no','yes'])
    plt.show()

    count = len(d1)
    count_rent = len( d1[d1['st_2007']==1] )

    if st == True:
        d1 = d1[ (d1['LotArea_07'] > lot) & (d1['availFAR_perc_07'] > far)& (d1['AssedImprov_perc_07'] > imp)  & (d1['st_2007'] != 1) ]
    else:
        d1 = d1[ (d1['LotArea_07'] > lot) & (d1['AssedImprov_perc_07'] > imp) & (d1['availFAR_perc_07'] > far)]


    print( "Number of recently developped lots in {}: {}".format( puma, count ) )
    print( "% of Lots Covered : {}%".format( str(int(len(d1)*100/count) )) )
    print( "# of lots with Rent St. units: {} ({}%)".format(count_rent,int(count_rent*100/count)) )

#Display
hello = interact(show_df, puma=ddown , lot=Lot_slider , far=Far_slider , imp=Improve_slider , st=box)
hello

#%%

#data['st_2007'].plot(kind='bar')


#%%
# -- P-VALUE TEST for Rent Stabilized Units
# Does rent stabilized matter in CEQR soft site. 

pls = pl.copy()
pls = pls[~pls['puma'].isnull()]
pls = pl[[
    'bbl',
    'LotArea_07',
    'UnitsRes_07',
    'YearBuilt_07','YearAlter_07','last_YearBuilt','recent_alter',
    'Landmark_07',
    'availFAR_perc_07','permits_07',
    'AssedImprov_perc_07','Compact_07',
    'puma','st_2007','project_na','airright_trans','merged'
    ]].copy()

pls = pls[~pls['puma'].isnull()]
pls['puma'] = pls['puma'].astype(str).str.split('.').str[0] 

pls['is_st'] = np.where(
    pls['st_2007'] > 0,
    "has st. unit","no st. unit"
)

pls['recent_alter'] = np.where(
    pls['recent_alter'] == 1,
    'Yes',"No"
)

gr1 = pls.groupby(['puma','recent_alter','is_st']).agg({'bbl':len})
gr_rank = pls.groupby( ["puma",'recent_alter'] ).agg({'bbl': len })
grp = gr1.div(gr_rank) * 100

#grp.round(2).to_excel(r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Rent_Stab_Rates.xls')
grp.round(2)

#%%
pls = pls[~pls['puma'].isnull()]
print( "{}% of all lots have rent st units".format(len(pls[ pls['is_st']=='has st' ])*100 / len(pls)) ) 
print( "{}% of all lots were recently altered".format( len(pls[ pls['recent_alter']==1 ]) * 100 / len(pls) ) ) 
print("-----------------")
print( "{}% of all lots were recently altered had a rent st unit".format( len(pls[ (pls['recent_alter']==1) & (pls['is_st']=='has st' ) ]) * 100 / len(pls[ pls['recent_alter']==1 ])  ) ) 

#%%
# Null Hyp: Rent Stabilized units matter
# Alt Hyp: Rent Stabilized units NOT matter
from scipy.stats import ttest_ind
from scipy.stats import spearmanr

plp = pl[['puma','recent_alter','st_2007']].copy()
plp = plp[~plp['puma'].isnull()]
plp['is_st'] = np.where(
    plp['st_2007'] > 0,
    1,0
)

for puma in sorted(plp['puma'].unique()):
    plp1 = plp[ plp['puma'] == puma ]

    plp1 = plp1.drop(['st_2007','puma'],axis=1)

    data1 = plp1['is_st'].tolist()
    data2 = plp1['recent_alter'].tolist()

    stat, p = spearmanr(data1, data2)
    print('puma={} , p={}'.format(int(puma),round(p,3)))
    if p > 0.05:
        print('Probably independent')
    else:
        print('Probably dependent')

#%%
