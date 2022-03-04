import pandas as pd
import numpy as np
import re
import datetime as dt
from url_mls_searches import mls_search_urls

###############################
### Data Cleaning Functions ###
###############################

def clean_address_full(x):
    """
    Cleans the address of the MLS listing and returns it in a systematic format that can be used.
    """
    quadrants = {'NE','NW','SE','SW'}
    address = x.split(' ')
    unit = ''
    num = ''
    street = ''
    quadrant = ''
    for i in range(len(address)):
        if address[i] in quadrants:
            quadrant = address.pop(i)
            break
    for i in range(len(address)):
        if re.search('#',address[i]):
            unit = address.pop(i)
            break
    num = address.pop(0)
    street = ' '.join(address)
    if unit == '':
        return num+' '+street+' '+quadrant
    else:
        return unit+' '+num+' '+street+' '+quadrant

def clean_address_bldg(x):
    """
    Cleans the address of the MLS listing and returns the building address in a systematic format.
    This can be used to potentially group listings by building address and allow for more in-depth analyses.
    (ie. impact of floor level, building specific rent)
    """
    quadrants = {'NE','NW','SE','SW'}
    address = x.split(' ')
    unit = ''
    num = ''
    street = ''
    quadrant = ''
    for i in range(len(address)):
        if address[i] in quadrants:
            quadrant = address.pop(i)
            break
    for i in range(len(address)):
        if re.search('#',address[i]):
            unit = address.pop(i)
            break
    num = address.pop(0)
    street = ' '.join(address)
    return num+' '+street+' '+quadrant

def get_unit(x):
    """
    Using the address, extracts the unit number.
    """
    quadrants = {'NE','NW','SE','SW'}
    address = x.split(' ')
    unit = ''
    num = ''
    street = ''
    quadrant = ''
    for i in range(len(address)):
        if address[i] in quadrants:
            quadrant = address.pop(i)
            break
    for i in range(len(address)):
        if re.search('#',address[i]):
            unit = address.pop(i)
            break
    num = address.pop(0)
    street = ' '.join(address)
    return re.sub('#','',unit)

def get_num(x):
    """
    Using the address, extracts the street number.
    """
    quadrants = {'NE','NW','SE','SW'}
    address = x.split(' ')
    unit = ''
    num = ''
    street = ''
    quadrant = ''
    for i in range(len(address)):
        if address[i] in quadrants:
            quadrant = address.pop(i)
            break
    for i in range(len(address)):
        if re.search('#',address[i]):
            unit = address.pop(i)
            break
    num = address.pop(0)
    street = ' '.join(address)
    return num

def get_street(x):
    """
    Using the address, extracts the street name.
    """
    quadrants = {'NE','NW','SE','SW'}
    address = x.split(' ')
    unit = ''
    num = ''
    street = ''
    quadrant = ''
    for i in range(len(address)):
        if address[i] in quadrants:
            quadrant = address.pop(i)
            break
    for i in range(len(address)):
        if re.search('#',address[i]):
            unit = address.pop(i)
            break
    num = address.pop(0)
    street = ' '.join(address)
    return street+' '+quadrant

def get_quadrant(x):
    """
    Using the address, extracts the quadrant.
    """
    quadrants = {'NE','NW','SE','SW'}
    address = x.split(' ')
    unit = ''
    num = ''
    street = ''
    quadrant = ''
    for i in range(len(address)):
        if address[i] in quadrants:
            quadrant = address.pop(i)
            break
    for i in range(len(address)):
        if re.search('#',address[i]):
            unit = address.pop(i)
            break
    num = address.pop(0)
    street = ' '.join(address)
    return quadrant

def clean_data(df):
    """
    Iterating through the columns, transforming data to the appropriate data types usuable for further analysis transformations
    """
    for col in df.columns:
        df[col] = pd.to_numeric(df[col],errors='ignore')
    df['$/SqFt'] = df['$/SqFt'].apply(lambda x: float(re.sub('[$,]','',str(x))))
    df['BG Fin Area'] = df['BG Fin Area'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['BG Fin Area Mtr'] = df['BG Fin Area Mtr'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['Condo Fee'] = df['Condo Fee'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    # df['Close Price'] = df['Close Price'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x) # Close Price isn't normally available on these listing searches
    df['Frontage mtr'] = df['Frontage Lng'].apply(lambda x: re.sub('M','',x.split(' ')[0]) if type(x)==str else x)
    # df['Frontage ft'] = df['Frontage Lng'].apply(lambda x: float(re.sub('"','',x.split(' ')[1]).split('`')[0])+float(re.sub('"','',x.split(' ')[1]).split('`')[1])/12 if type(x)==str else x)
    df['HOA Fee'] = df['HOA Fee'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['List Price'] = df['List Price'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['Liv Area SF'] = df['Liv Area SF'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['Lot Size SF'] = df['Lot Size SF'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['Orig LP'] = df['Orig LP'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['Registered Size SF'] = df['Registered Size SF'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['Tax Amount'] = df['Tax Amount'].apply(lambda x: float(re.sub('[$,]','',x)) if type(x)==str else x)
    df['Address1'] = df['Address'].apply(lambda x: clean_address_full(x))
    df['Address2'] = df['Address'].apply(lambda x: clean_address_bldg(x))
    df['Unit'] = df['Address'].apply(lambda x: get_unit(x))
    df['Num'] = df['Address'].apply(lambda x: get_num(x))
    df['Street'] = df['Address'].apply(lambda x: get_street(x))
    df['Quadrant'] = df['Address'].apply(lambda x: get_quadrant(x))
    df['Total Baths'] = df['Full Baths']+df['Half Baths']*0.5
    return df

def analyze_data(df):
    """
    Adding derived/calculated analytical columns
    """
    df['LP-OP Variance'] = df['List Price'] - df['Orig LP']
    df['LP-OP Variance %'] = df['LP-OP Variance']/df['Orig LP']*100
    return df

def rent_key(df):
    """
    Creating a categorical key that will be used to help cluster properties.
    """
    rent_types = {
        'Duplex':'Duplex',
        'House':'House',
        'Low Rise (2-4 stories)':'Apartment',
        'High Rise (5+ stories)':'Apartment',
        'Triplex':'Duplex',
        'Four Plex':'Duplex',
        'Five Plus':'Duplex',
        'Manufactured House': 'Other',
    }
    df['Rent Type'] = df['Structure Type'].apply(lambda x: rent_types[x] if type(x) == str else x)
    df['Rent Key'] = df['Subdivision Name']+'-'+df['Rent Type']+'-'+df['Beds'].apply(lambda x: str(x))+'-'+df['Total Baths'].apply(lambda x: re.sub('.0','',str(x)))
    return df

def consolidate_data(run_date):
    df_mls = pd.DataFrame()
    for mls_search in mls_search_urls:
        try:
            df = pd.read_csv(f"./data/{run_date} - {mls_search['title']} - mls (raw).csv",index_col=0)
            df_mls = pd.concat([df_mls,df]).drop_duplicates().reset_index(drop=True)
        except:
            print("No data available.")
    return df_mls

def main(run_date, key = ''):

    df_mls = pd.DataFrame()
    for mls_search in mls_search_urls:
        try:
            df = pd.read_csv(f"./data/{run_date} - {mls_search['title']} - mls (raw).csv",index_col=0)
            df_mls = pd.concat([df_mls,df]).drop_duplicates().reset_index(drop=True)
        except:
            print('No file available.')

    # queries = ['lt500k Downtown','lt425k SWNW Condos',]
    # for q in queries:
    #     try:
    #         df = pd.read_csv(f"./data/{run_date} - {q} - mls (raw).csv",index_col=0)
    #         df_mls = pd.concat([df_mls,df]).drop_duplicates().reset_index(drop=True)
    #     except:
    #         print('No file available')

    df_mls = clean_data(df_mls)
    df_mls = analyze_data(df_mls)
    df_mls = rent_key(df_mls)

    df_mls.to_csv(f"./data/{run_date} - mls (clean).csv",index_label=False)
    # df_mls.to_csv(f"./data/{run_date}{key if key == '' else ' - '+key} - mls (clean).csv",index_label=False)

if __name__ == '__main__':
    # run_date = '2021-09-16'
    run_date = dt.datetime.strftime(dt.date.today(),'%Y-%m-%d')
    # main(run_date,'- Elizabeth')
    main(run_date)
