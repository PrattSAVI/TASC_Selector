

# %% --------------------  START HERE ---------------------------
#All Above is saved to Master_Pluto.
# I use this to start over from here. 
from re import A
import pandas as pd
import numpy as np
from sklearn import tree
import matplotlib.pyplot as plt

pd.set_option('max_columns',None)

def remove_outlier(df,col , high):
    st = len( df )
    df = df[ (df[col] < df[col].quantile( high ) ) & (df[col] > df[col].quantile(1-high)) ]
    en = len( df )
    print( "In vs Out {} {}".format( st,en) )
    return df

#pl.to_csv( r'D:\DROPBOX\Dropbox\TASC Application\DATA\Master_Pluto.csv')
pl = pd.read_csv( r'C:\Users\csucuogl\Dropbox\TASC Application\DATA\Master_Pluto.csv')
pl.columns = pl.columns.str.replace( 'Unnamed: 0' , 'bbl')
pl['bbl'] = pl['bbl'].astype( str )
pl = pl.set_index( 'bbl' ) 

pl.head()

#%% Is dataset balanced
#It is not so be carefull with machine learning
import seaborn as sns

sns.countplot( data = pl, x = 'recent_alter')
plt.show()

#%% ----------------- initial Tree For a single BORO (Brooklyn)
#Scikit Learn Tree for tests
import os

#Remove Some Entries
pl1 = pl[pl['is_hard_to_Relocate'] == 0 ]
pl1 = pl1[pl1['was_Landmark'] == 0]
#pl1 = pl1[ pl['LandUse_07'].isin( [1,2,3,4] ) ]

#Remove outlier in the whole dataset
for f in ['availFAR_perc_07','AssedImprov_perc_07']:
    if f != "st_2007":
        pl1 = pl1.mask(np.isinf(pl1[f]) )
        if pl[f].max() - pl[f].min() > 2:
            pl1 = remove_outlier( pl1 , f , 0.99)

pl1['boro'] = pl1.index.str[0]

# 4109 = LIC
# 4004 = DTW BK and Fort Greene
puma = 4109
explanation = 'LIC'
pl1 = pl1[ pl1['puma'] == puma ] # Set PUMA 
#pl1 = pl1[pl1['boro']== puma ]

#Reduce the data to an equal split by getting random rows as built values.
c = len( pl1[ pl1['recent_alter'] == 1 ] )
r_unbuilt = pl1[ pl1['recent_alter'] != 1 ].sample( c )
r_built = pl1[ pl1['recent_alter'] == 1 ]
pl1 = r_built.append( r_unbuilt )

pl1['recent_alter'] = np.where( pl1['recent_alter'] == 0 , 'N' , 'Y' )
pl1['st_2007'] = pl1['st_2007'].fillna( 0 )
pl1['st_perc'] = (pl1['st_2007'] * 100 / pl1['UnitsRes_07']).round()
pl1['has_st'] = np.where( pl1['st_2007'] >0 , 1 , 0 )


print( "Count Built: {} and Unbuilt {}".format( len(r_built) , len(r_unbuilt) ) )

pl1['st_2007'] = pl1['st_2007'].fillna(0)
pl1['st_2007'] = np.where( pl1['st_2007']>0 , 1, 0 )

test_cols = [
    'Compact_07',
    'availFAR_perc_07',
    'LotArea_07',
    'AssedImprov_perc_07',
    'has_st',
    #'st_perc'
    ]

target_col = 'recent_alter'
depth = 8

pl1 = pl1[ test_cols + [target_col] ]

for f in ['availFAR_perc_07']:
    if f != "st_2007":
        pl1 = pl1.mask(np.isinf(pl1[f]) )
        if pl[f].max() - pl[f].min() > 2:
            pl1 = remove_outlier( pl1 , f , 0.99)

pl1 = pl1.dropna( subset=[target_col] , axis=0)
pl1 = pl1.dropna( subset= test_cols , axis=0)

#training data , target
X,y = pl1[test_cols].values , pl1[target_col].values

print( "Here we go!" )
clf = tree.DecisionTreeClassifier( 
    max_leaf_nodes = depth,
    #min_samples_split = 200,
    #min_samples_leaf = 200,
    random_state = 1,
    criterion = 'gini',
    splitter = 'best'
    )

clf = clf.fit(X, y)

#Plot the Tree
plt.figure( figsize= (10,12) )
tree.plot_tree(
    clf, 
    precision= 2,
    filled=True,
    label='all',
    class_names = [ "N","Y"],
    feature_names= test_cols )
plt.title( '2007-17 Alteration Decision Tree for \n PUMA: {} - {} \n Independent Var: {}'.format( puma,explanation,target_col) )
#folder = r'C:\Users\csucuogl\Dropbox\TASC Application\Charts\Decision Trees'
#plt.savefig( os.path.join(folder,"DecTree_{}.png".format(puma)) )
plt.show()

print( clf.score(X,y) )

#%% ---------------- Percentiles for given tests / LotARea


import random
import statistics
import numpy as np
from scipy import stats

col = 'LotArea_07'
#Removed Outliers
plb = pl[ pl['recent_alter'] == 1 ]
plb = plb[ ~plb[col].isnull() ]
plb['boro'] = plb.index.str[0]
#plb = plb[ plb['boro'] == "1" ]

#areas = plb[ (plb[col] < plb[col].quantile(0.98)) & (plb[col] > plb[col].quantile(0.02)) ][col]
areas = plb[col]
areas = np.log(areas)

zs = 0.89

a = areas 

mean = statistics.mean(a)
std_high = mean + (statistics.stdev(a)*zs)
std_low = mean - (statistics.stdev(a)*zs)

norm_mean = np.exp( mean )
norm_high = np.exp( std_high)
norm_low = np.exp( std_low)

print(norm_low, norm_mean, norm_high)
print(len( plb[ (plb[col] > norm_low) & (plb[col] < norm_high) ] ) / len(plb))

sns.distplot(
    a , bins = 12,kde=False
)
plt.axvline( x = mean , color = 'black')
plt.axvline( x = std_low , color = 'orange')
plt.axvline( x = std_high , color = 'orange')
plt.title( "Distribution of Sampled Means \n %95 percent of mean values fall with in {} and {}".format(  round( norm_low ),round(norm_high) ))
plt.xlabel( "{} (log transformed)".format(col))
#plt.savefig( r"C:\Users\csucuogl\Desktop\Transforms.png" )
plt.show()

#%% FOR Available FAR

import random
import statistics
import numpy as np
from scipy import stats

col = 'availFAR_perc_07'
#Removed Outliers
plb = pl[ pl['recent_alter'] == 1 ]
plb = plb[ ~plb[col].isnull() ]
plb['boro'] = plb.index.str[0]
#plb = plb[ plb['boro'] == "1" ]

#plb = plb[ plb[col] > -100000 ]
areas = plb[ (plb[col] < plb[col].quantile(0.995)) & (plb[col] > plb[col].quantile(0.005)) ][col]
#areas = plb[col]
#areas = np.log(areas)

a = areas 
zs = 2.5

mean = statistics.mean(a)
std_high = mean + (statistics.stdev(a)*zs)
std_low = mean - (statistics.stdev(a)*zs)

print(std_low, mean, std_high)
print(len( plb[ (plb[col] > std_low) & (plb[col] < std_high) ] ) / len(plb))

sns.distplot(
    a , bins = 12,kde=False
)
plt.axvline( x = mean , color = 'black')
plt.axvline( x = std_low , color = 'orange')
plt.axvline( x = std_high , color = 'orange')
plt.title( "Distribution of Sampled Means \n %95 percent of mean values fall with in {} and {}".format(  round( std_low ),round(std_high) ))
plt.xlabel( "{}".format(col))
plt.savefig( r"C:\Users\csucuogl\Desktop\Transforms.png" )
plt.show()
# %%

t = pl1[ (pl1['st_perc'] < 100) & (pl1['st_perc'] > 0 ) ]['st_perc']
t .hist( bins = 100 )
plt.show()

#%% 