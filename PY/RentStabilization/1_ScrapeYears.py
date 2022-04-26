
#%% IMPORT DEPENDENCY
import os
import time
import pandas as pd
import wget
pd.set_option("max_columns",None)

PERIODS = {
    
    ('20210605', 'SOA'):  'June 05, 2021 - Quarterly Property Tax Bill.pdf',
    #('20200606', 'SOA'):  'June 06, 2020 - Quarterly Property Tax Bill.pdf',
    #('20190605', 'SOA'):  'June 05, 2019 - Quarterly Property Tax Bill.pdf',

}

print('Yes!')


#%% Multiple Dwelling Registeration
# I am using this data as the basis of the scraping. instead of uing the whole Pluto
#https://data.cityofnewyork.us/Housing-Development/Multiple-Dwelling-Registrations/tesw-yqqr
# Merge John Krausses dataset's BBL's with Multiple Dwelling and get unique BBL's. 
# There are about 200K bbls

import os
all_folder = r'D:\DROPBOX\Dropbox\TASC Application\DATA\RentSt'

dw = pd.read_csv( os.path.join(all_folder,"Multiple_Dwelling_Registrations.csv") )
dw = dw.drop('HouseNumber,LowHouseNumber,HighHouseNumber,StreetName,StreetCode,Zip,CommunityBoard,LastRegistrationDate,RegistrationEndDate'.split(",") , axis = 1)
dw['BoroID'] = dw['BoroID'].astype(str)
dw['Block'] = dw['Block'].astype(str)
dw['Lot'] = dw['Lot'].astype(str)

#Construct BBL for the multi-dwell units
dw['bbl'] = dw['BoroID'] + dw['Block'].str.zfill(5) + dw['Lot'].str.zfill(4)
dw = dw.drop_duplicates(subset='bbl',keep='first')

djk = pd.read_csv( os.path.join(all_folder,"joined-nocrosstab.csv") )
djk['bbl'] = djk['ucbbl'] 
djk = djk[['bbl']]
dw = dw[['bbl']]

dn = pd.read_csv(r"D:\DROPBOX\Dropbox\TASC Application\DATA\RentSt\NY_RentSt_Buildings_Rd.csv")
dn = dn[['bbl']]

dw2 = dw.append( djk )
dw2 = dw2.append( dn )

dw2['bbl'] = dw2['bbl'].astype( str ) #Make sure all bbls are strings. 
dw2['blen'] = [ len(r) for r in dw2['bbl'].tolist() ]
dw2 = dw2[ dw2['blen'] == 10 ]
dw2 = dw2[['bbl']]
dw2 = dw2.drop_duplicates(subset=['bbl'],keep='first')

dw2

#%% get Missing BBLs in 2018. Only to scrape 2018 data!!!!
#This gets missing bbls from Chris Whongs dataset
d18 = pd.read_csv( r"D:\DROPBOX\Dropbox\TASC Application\DATA\RentSt\rentstab_counts_for_pluto_19v1_bbls.csv" )
d18['ucbbl'] = d18['ucbbl'].astype( str )
display( d18.head() )

dn = pd.read_csv(r"D:\DROPBOX\Dropbox\TASC Application\DATA\RentSt\NY_RentSt_Buildings_Rd.csv")
dn = dn[['bbl']]
dn['bbl'] = dn['bbl'].astype(str)
display( dn.head() )

d18c = dn[ ~dn['bbl'].isin( d18['ucbbl'].tolist() ) ]
display( d18c )

dw2 = d18c.copy()

#%% Scrape Here
#Just incase. I don't thnk this is necessary

#data_folder = r'C:\Users\csucuogl\Desktop\Tax_Scraped'
data_folder = r"D:\STORED\Rent_St_REPO_21"

def get_Download(bbl,period,doc_type):
    
    #2018 : https://a836-mspuvw-dofptsz.nyc.gov/PTSCM/StatementSearch?bbl=3027370011&stmtDate=20180601&stmtType=SOA
    #This is the new format for web queries
    url2= 'https://a836-edms.nyc.gov/dctm-rest/repositories/dofedmspts/StatementSearch?' + \
            'bbl={bbl}&stmtDate={period}&stmtType={doc_type}'.format(
                period=period, bbl=bbl, doc_type=doc_type)

    file_path = "{period}_{bbl}.pdf".format(period=period, bbl=bbl, doc_type=doc_type)
    #wget waits for the data to be downloaded
    response = wget.download(url=url2, out= os.path.join(data_folder,file_path) )

    time.sleep( 0.06 )

#Get files in the folder
def get_Done():
    files = [i.split('.')[0].split("_") for i in os.listdir( data_folder )]
    df = pd.DataFrame( columns = ['date','bbl'] , data = files)
    return df

downloaded = get_Done()
print( '{} items are downloaded'.format( len( downloaded) ) )

display( downloaded )


#%%
import time 
downloaded = get_Done()
print( '{} items are downloaded'.format( len( downloaded) ) )

for p in PERIODS: #For each November
    print( p )
    f_data = downloaded[ downloaded['date'] == p[0] ]
    dw3 = dw2[ ~dw2['bbl'].isin( f_data['bbl'].tolist() ) ].copy()
    dw3['count'] = [i for i in range(len(dw3))]
    print( '{item} items left to download'.format(item=len(dw3)))
    print( dw3['count'].max() , len(dw3) )
    
    for i,r in dw3.iterrows(): 
        try:
            get_Download( r['bbl'] , p[0] , p[1] )
            if r['count'] % 500 == 0: print( "{x}% is done".format( x = int(r['count']*100 / len(dw3))) )
            time.sleep( 0.1 )
        except :
            print(r['bbl'])

# %%
