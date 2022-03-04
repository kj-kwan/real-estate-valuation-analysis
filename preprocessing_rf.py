import pandas as pd
import numpy as np
import re
import datetime as dt

# Cleaning functions
def clean_quadrant(x):
    quadrant_dict = {
        'northwest':'NW',
        'southwest':'SW',
        'northeast':'NE',
        'southeast':'SE'
    }
    for k,v in quadrant_dict.items():
        if k in x.lower():
            x = re.sub(k,v,x.lower())
            break
        if v.lower() == x.lower():
            x = x.upper()
            break
    return x
def clean_street(street):
    street_dict = {
        'st':'Street',
        'dr':'Drive',
        'cr':'Crescent',
        'ave':'Avenue',
        'av':'Avenue',
        'rd':'Road',
        'tr':'Trail',
        'blvd':'Boulevard',
        'bv':'Boulevard',
        'pk':'Park',
        'pa':'Park',
        'crl':'Circle'
    }
    for k,v in street_dict.items():
        if k == street.lower():
            return v
    return street.title()
def clean_numbers(num):
    num_dict = {
        '1st':'1',
        '2nd':'2',
        '3rd':'3',
        '4th':'4',
        '5th':'5',
        '6th':'6',
        '7th':'7',
        '8th':'8',
        '9th':'9',
        '0th':'0'
    }
    for k,v in num_dict.items():
        if k in num.lower():
            num = re.sub(k,v,num.lower())
    return num

def clean_rent_address(x):
    address = re.sub('[.]','',x).title()
    elements = re.split(' |, ',address)
    new_address = []
    for e in elements:
        a = clean_numbers(e)
        if a == e:
            a = clean_street(e)
        if a == e:
            a = clean_quadrant(e)
        if e.lower() not in {'canada','calgary','ab'}:
            new_address.append(a)
    return ' '.join(new_address)

def clean_rent_address_full(x):
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
    if re.search('\d',address[0]):
        num = address.pop(0)
    street = ' '.join([re.sub('[-\s]','',y).title() for y in address])
    if unit == '':
        return num+' '+street+' '+quadrant
    else:
        return unit+' '+num+' '+street+' '+quadrant

def clean_rent_address_bldg(x):
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
    if re.search('\d',address[0]):
        num = address.pop(0)
    street = ' '.join([re.sub('[-\s]','',y).title() for y in address])
    return num+' '+street+' '+quadrant

def get_rent_unit(x):
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
    if re.search('\d',address[0]):
        num = address.pop(0)
    street = ' '.join([re.sub('[-\s]','',y).title() for y in address])
    return re.sub('#','',unit)

def get_rent_num(x):
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
    if re.search('\d',address[0]):
        num = address.pop(0)
    street = ' '.join([re.sub('[-\s]','',y).title() for y in address])
    return num

def get_rent_street(x):
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
    if re.search('\d',address[0]):
        num = address.pop(0)
    street = ' '.join([re.sub('[-\s]','',y).title() for y in address])
    return street+' '+quadrant

def get_rent_quadrant(x):
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
    if re.search('\d',address[0]):
        num = address.pop(0)
    street = ' '.join([re.sub('[-\s]','',y).title() for y in address])
    return quadrant

def community_cleanup(x):
    '''
    Changes the Rentfaster community to Subdivision Name in mls listing.
    '''
    modbus = {
        'Killarney': 'Killarney/Glengarry',
        'Glengarry': 'Killarney/Glengarry',
        'Beddington': 'Beddington Heights',
        'Sandstone': 'Sandstone Valley',
        'Richmond/Knob Hill': 'Richmond',
        'Parkhill-Stanley Park': 'Parkhill',
        'Bridgeland': 'Bridgeland/Riverside',
        'Tuxedo': 'Tuxedo Park',
    }
    return modbus[x] if x in modbus.keys() else x

def clean_data(df):

    # df['intro'] = df['intro'].fillna('',inplace=True)
    df['Address'] = np.where(df['intro'].isnull(),'',df['intro'].apply(lambda x: clean_rent_address(str(x))))
    df['Address Full'] = df['Address'].apply(lambda x: clean_rent_address_full(x))
    df['Address Bldg'] = df['Address'].apply(lambda x: clean_rent_address_bldg(x))
    df['Unit'] = df['Address'].apply(lambda x: get_rent_unit(x))
    df['Num'] = df['Address'].apply(lambda x: get_rent_num(x))
    df['Street'] = df['Address'].apply(lambda x: get_rent_street(x))
    df['Quadrant'] = df['Address'].apply(lambda x: get_rent_quadrant(x))
    df['price'] = pd.to_numeric(df['price'], errors='ignore')
    df['sq_feet'] = df['sq_feet'].apply(lambda x: str(x))
    df['sqft'] = pd.to_numeric(df['sq_feet'].apply(lambda x: re.sub('[><~\+\/\-,a-zA-Z]','',re.split('\s|\+|-',x,1)[0]) if type(x)==str else x), errors='coerce')
    df['sqft'] = np.where(df['sqft'].isnull(),pd.to_numeric(df['sq_feet'].apply(lambda x: re.sub('[><~\+\/\-,a-zA-Z]','',re.split('\s',x,1)[0]) if type(x)==str else x),errors='coerce'),df['sqft'])
    df['sqft'] = np.where(df['sqft'].isnull(),pd.to_numeric(df['sq_feet'].apply(lambda x: re.sub('[><~\+\/\-,a-zA-Z]','',x.split(' ')[1]) if (len(x.split(' '))>1) else x), errors='coerce'),df['sqft'])
    df['sqft'] = df['sqft'].apply(lambda x: x if x>0 else np.nan)
    df['price_sqft'] = df['price']/df['sqft']
    df['beds'] = df['beds'].apply(lambda x: 0 if x == 'studio' or x == 'none' else x)
    df['beds'] = pd.to_numeric(df['beds'],errors='coerce')
    df['beds1'] = df['beds'].apply(lambda x: re.sub('[+a-zA-Z]','',x) if type(x)==str else x)
    df['baths'] = df['baths'].apply(lambda x: 0 if x == 'none' else x)
    df['baths'] = pd.to_numeric(df['baths'],errors='coerce')
    df['utilities_included'] = df['utilities_included'].apply(lambda x: str(x) if not type(x) == str else x)
    df['heat'] = df['utilities_included'].apply(lambda x: 1 if 'Heat' in x else 0)
    df['water'] = df['utilities_included'].apply(lambda x: 1 if 'Water' in x else 0)
    df['electricity'] = df['utilities_included'].apply(lambda x: 1 if 'Electricity' in x else 0)
    df['internet'] = df['utilities_included'].apply(lambda x: 1 if 'Internet' in x else 0)
    df['cable'] = df['utilities_included'].apply(lambda x: 1 if 'Cable' in x else 0)
    df['cats'] = df['cats'].apply(lambda x: x/2)
    df['dogs'] = df['dogs'].apply(lambda x: x/2)
    df['Community'] = df['community'].apply(lambda x: community_cleanup(x))

    ### Removing extreme values ###
    df = df[df['sqft'] > 10] ### Remove extremely low sqft entries
    return df

def make_rent_key(df):
    rental_types = {
        'Duplex':'Duplex',
        'House':'House',
        'Apartment':'Apartment',
        'Condo':'Apartment',
        'Loft':'Apartment',
        'Townhouse':'Apartment',
        'Shared':'Other',
        'Office Space':'Other',
        'Main Floor':'Other',
        'Acreage':'Other',
        'Basement':'Other',
        'Mobile': 'Other',
        'Parking Spot': 'Other',
        'Storage': 'Other',
        'Vacation': 'Other',
    }
    df['rent_type'] = df['type'].apply(lambda x: rental_types[x])
    df['Rent Key'] = df['Community']+'-'+df['rent_type']+'-'+df['beds1'].apply(lambda x: re.sub('.0','',str(x)))+'-'+df['baths'].apply(lambda x: re.sub('.0','',str(x)))
    return df

def clean_rf_data(run_date):

    df = clean_data(pd.read_csv(f'./data/{run_date} - rf (raw).csv',index_col=0))
    df = make_rent_key(df)
    df.to_csv(f'./data/{run_date} - rf (clean).csv',index_label=False)

def main(run_date):

    ### Prep the Rentfaster data ###
    df = clean_data(pd.read_csv(f'./data/{run_date} - rf (raw).csv',index_col=0))
    df = make_rent_key(df)
    df.to_csv(f'./data/{run_date} - rf (clean).csv',index_label=False)

    ### Clustering data by "Rent Key" ###
    df_clusters = df.groupby(by='Rent Key').mean()
    df_clusters.to_csv(f'./data/{run_date} - rf clusters.csv')

if __name__ == '__main__':
    # run_date = '2021-09-13'
    run_date = dt.datetime.strftime(dt.date.today(),'%Y-%m-%d')
    main(run_date)
