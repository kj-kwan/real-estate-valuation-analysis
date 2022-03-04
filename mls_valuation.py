import pandas as pd
import numpy as np
import datetime as dt
import re
import time

def mortgage_payment(principal,annual_interest_rate,periods):
    monthly_payment = principal*((1+annual_interest_rate/12)**periods)/((1+annual_interest_rate/12)**periods-1)*annual_interest_rate/12
    return round(monthly_payment,2)

def npv_cf_factor(discount_rate, growth_rate, periods):
    net_present_value = 0
    for i in range(periods):
        net_present_value += (1+growth_rate/12)**i/(1+discount_rate/12)**i
    return net_present_value

def pv_factor(discount_rate, growth_rate, periods):
    return (1+growth_rate/12)**periods/(1+discount_rate/12)**periods

def calc_valuation(run_date:str,assumptions={}):

    ### Retrieving cleaned MLS and rental data ###

    df_mls = pd.read_csv(f'./data/{run_date} - mls (clean).csv',index_col=0)
    df_rf = pd.read_csv(f'./data/{run_date} - rf (clean).csv',index_col=0)
    df_mlsv = pd.merge(df_mls,df_rf.groupby(by=['community','rent_type','Rent Key']).mean(),left_on='Rent Key',right_on='Rent Key',how='left')

    ###################
    ### Assumptions ###
    ###################

    ### Rent Estimation Assumptions ###
    rent_sf = assumptions['rent_estimation']['rent_sf']
    vacancy_sf = assumptions['rent_estimation']['vacancy_sf']
    rental_gr = assumptions['rent_estimation']['rental_gr']

    ### Property Expense Estimation Assumptions ###
    maintenance_factor = assumptions['property_expenses']['maintenance_factor']
    management_factor = assumptions['property_expenses']['management_factor']
    insurance_factor = assumptions['property_expenses']['insurance_factor']
    condo_fee_gr = assumptions['property_expenses']['condo_fee_gr']
    maintenance_gr = assumptions['property_expenses']['maintenance_gr']
    management_gr = assumptions['property_expenses']['management_gr']
    insurance_gr = assumptions['property_expenses']['insurance_gr']
    tax_gr = assumptions['property_expenses']['tax_gr']

    ### Mortgage Payment Assumptions ###
    interest_rate = assumptions['mortgage']['interest_rate']
    interest_stress_test_rate = assumptions['mortgage']['interest_stress_test_rate']
    downpayment_factor = assumptions['mortgage']['downpayment_factor']
    amortization_periods = assumptions['mortgage']['amortization_periods']

    ### Property Appreciation Assumptions ###
    property_appreciation_rate_low = assumptions['property_appreciation']['property_appreciation_rate_low']
    property_appreciation_rate = assumptions['property_appreciation']['property_appreciation_rate']
    property_appreciation_rate_high = assumptions['property_appreciation']['property_appreciation_rate_high']

    ### Capital Cost Assumptions ###
    closing_cost_factor = assumptions['capital']['closing_cost_factor']
    rehab_cost_factor = assumptions['capital']['rehab_cost_factor']

    ### Valuation Assumptions ###
    evaluation_period = assumptions['valuation']['evaluation_period'] # in years
    property_valuation_factor = assumptions['valuation']['property_valuation_factor']
    inflation_rate = assumptions['valuation']['inflation_rate']
    discount_rate = assumptions['valuation']['discount_rate']

    #############################
    ### Valuation Calculation ###
    #############################

    ### Rent & Profitability Estimation ###
    df_mlsv['Avg Cluster Rent'] = round(df_mlsv['Liv Area SF']*df_mlsv['price_sqft'],0)
    df_mlsv['Estimated Rent'] = round(df_mlsv['Liv Area SF']*df_mlsv['price_sqft']*(1-rent_sf),0)
    df_mlsv['Effective Rent'] = round(df_mlsv['Liv Area SF']*df_mlsv['price_sqft']*(1-rent_sf)*(1-vacancy_sf),0)
    df_mlsv['LP per rent/sqft'] = round(df_mlsv['List Price']/df_mlsv['price_sqft'],2)

    ### Property Expenses Estimation ###
    df_mlsv['Condo Fee per sqft'] = round(df_mlsv['Condo Fee']/df_mlsv['Liv Area SF'],2)
    df_mlsv['Property Maintenance Cost'] = round(df_mlsv['List Price']*maintenance_factor/12,2)
    df_mlsv['Property Management Cost'] = round(df_mlsv['Effective Rent']*management_factor,2)
    df_mlsv['Property Insurance Cost'] = round(df_mlsv['List Price']*insurance_factor/12,2)
    df_mlsv['Property Tax Cost'] = round(df_mlsv['Tax Amount']/12,2)
    df_mlsv['Property Costs'] = round(df_mlsv['Condo Fee']+df_mlsv['Property Maintenance Cost']+df_mlsv['Property Management Cost']+df_mlsv['Property Insurance Cost']+df_mlsv['Property Tax Cost'],2)

    ### Rental Profit ###
    df_mlsv['Rent Profit'] = round(df_mlsv['Effective Rent']-df_mlsv['Condo Fee']-df_mlsv['Property Maintenance Cost']-df_mlsv['Property Insurance Cost']-df_mlsv['Property Management Cost']-df_mlsv['Tax Amount']/12,0)

    ### Mortgage Payments ###
    df_mlsv['Downpayment'] = df_mlsv['List Price'].apply(lambda x: round(x*downpayment_factor,2))
    df_mlsv['MMP'] = df_mlsv['List Price'].apply(lambda x: mortgage_payment(x*(1-downpayment_factor),interest_rate,amortization_periods))
    df_mlsv['MMP Stress'] = df_mlsv['List Price'].apply(lambda x: mortgage_payment(x*(1-downpayment_factor),interest_stress_test_rate,amortization_periods))

    ### Capital Costs ###
    df_mlsv['Closing Cost'] = df_mlsv['List Price']*closing_cost_factor
    df_mlsv['Rehab Cost'] = df_mlsv['List Price']*rehab_cost_factor
    df_mlsv['Total Initial Cost'] = df_mlsv['Downpayment']+df_mlsv['Closing Cost']+df_mlsv['Rehab Cost']

    ### Free Cash Flow Calculations ###
    df_mlsv['Total Monthly Expenses'] = round(df_mlsv['MMP']+df_mlsv['Condo Fee']+df_mlsv['Property Maintenance Cost']+df_mlsv['Property Insurance Cost']+df_mlsv['Property Management Cost']+df_mlsv['Tax Amount']/12,2)
    df_mlsv['FCF'] = round(df_mlsv['Effective Rent']-df_mlsv['MMP']-df_mlsv['Condo Fee']-df_mlsv['Property Maintenance Cost']-df_mlsv['Property Insurance Cost']-df_mlsv['Property Management Cost']-df_mlsv['Tax Amount']/12,2)

    df_mlsv['Total Costs Stress'] = round(df_mlsv['MMP Stress']+df_mlsv['Condo Fee']+df_mlsv['Property Maintenance Cost']+df_mlsv['Property Insurance Cost']+df_mlsv['Property Management Cost']+df_mlsv['Tax Amount']/12,2)
    df_mlsv['FCF Stress'] = round(df_mlsv['Effective Rent']-df_mlsv['MMP Stress']-df_mlsv['Condo Fee']-df_mlsv['Property Maintenance Cost']-df_mlsv['Property Insurance Cost']-df_mlsv['Property Management Cost']-df_mlsv['Tax Amount']/12,2)

    ### Valuations (DCF Calculations) ###
    # Property Cash Flow Components
    df_mlsv['Rental PV'] = round(df_mlsv['Effective Rent']*npv_cf_factor(discount_rate,rental_gr,evaluation_period*12),0)
    df_mlsv['Condo Fee PV'] = round(df_mlsv['Condo Fee']*npv_cf_factor(discount_rate,condo_fee_gr,evaluation_period*12),0)
    df_mlsv['Maintenance PV'] = round(df_mlsv['Property Maintenance Cost']*npv_cf_factor(discount_rate,maintenance_gr,evaluation_period*12),0)
    df_mlsv['Management PV'] = round(df_mlsv['Property Management Cost']*npv_cf_factor(discount_rate,management_gr,evaluation_period*12),0)
    df_mlsv['Insurance PV'] = round(df_mlsv['Property Insurance Cost']*npv_cf_factor(discount_rate,insurance_gr,evaluation_period*12),0)
    df_mlsv['Tax PV'] = round(df_mlsv['Property Tax Cost']*npv_cf_factor(discount_rate,tax_gr,evaluation_period*12),0)
    df_mlsv['Rent Profit PV'] = round(df_mlsv['Rent Profit']*npv_cf_factor(discount_rate,rental_gr,evaluation_period*12),0)
    # Rental Profit Valuation
    df_mlsv['Rent Valuation'] = df_mlsv['Rental PV'] - df_mlsv['Condo Fee PV'] - df_mlsv['Maintenance PV'] - df_mlsv['Management PV'] - df_mlsv['Insurance PV'] - df_mlsv['Tax PV']
    # Property Appreciation with Sensitivities
    df_mlsv['Property Valuation'] = round(df_mlsv['List Price']*pv_factor(discount_rate,property_appreciation_rate,evaluation_period*12),0) # Using expected property appreciation rate
    df_mlsv['Property Valuation Low'] = round(df_mlsv['List Price']*pv_factor(discount_rate,property_appreciation_rate_low,evaluation_period*12),0) # Using low property appreciation rate
    df_mlsv['Property Valuation High'] = round(df_mlsv['List Price']*pv_factor(discount_rate,property_appreciation_rate_high,evaluation_period*12),0) # Using high property appreciation rate
    # Total Valuation of Property
    df_mlsv['Total Valuation'] = df_mlsv['Property Valuation'] + df_mlsv['Rent Valuation'] # Uses the expected property appreciation rate

    ### Evaluation Metrics ###
    df_mlsv['Valuation Variance'] = round(df_mlsv['Total Valuation']-df_mlsv['List Price'],2)
    df_mlsv['Valuation Variance %'] = round(df_mlsv['Valuation Variance']/df_mlsv['List Price']*100,2)
    df_mlsv['Rent Yield'] = round(df_mlsv['Effective Rent']*12/df_mlsv['List Price']*100,2)
    df_mlsv['Profit Yield'] = round(df_mlsv['Rent Profit']*12/df_mlsv['List Price']*100,2)
    df_mlsv['Cash on Cash ROI'] = round(df_mlsv['FCF']*12/df_mlsv['Total Initial Cost']*100,2)
    df_mlsv['Payout Period'] = round(df_mlsv['List Price']/(df_mlsv['Rent Profit']*12),2)

    ### Ideal Price ###
    df_mlsv['ZFCF Price'] = (df_mlsv['Effective Rent']-df_mlsv['Condo Fee']-df_mlsv['Tax Amount']/12)/(((1-assumptions['mortgage']['downpayment_factor'])*((1+assumptions['mortgage']['interest_rate']/12)**assumptions['mortgage']['amortization_periods'])/((1+assumptions['mortgage']['interest_rate']/12)**assumptions['mortgage']['amortization_periods']-1)*assumptions['mortgage']['interest_rate']/12)+assumptions['property_expenses']['management_factor']+assumptions['property_expenses']['maintenance_factor']+assumptions['property_expenses']['insurance_factor'])
    df_mlsv['10% Profit Price'] = (df_mlsv['Effective Rent']-df_mlsv['Condo Fee']-df_mlsv['Tax Amount']/12)/0.1/(assumptions['property_expenses']['management_factor']+assumptions['property_expenses']['maintenance_factor']+assumptions['property_expenses']['insurance_factor'])

    df_mlsv.to_csv(f'./data/{run_date} - mls valuation.csv',index_label=False)


if __name__ == '__main__':
    # run_date = '2021-09-16'
    run_date = dt.datetime.strftime(dt.date.today(),'%Y-%m-%d')
    inflation_rate = 0.05
    assumptions = {
        'rent_estimation': {
            'rent_sf': 0.05,
            'vacancy_sf': 0.1,
            'rental_gr': 0.025,
        },
        'property_expenses': {
            'maintenance_factor': 0.00, # Annual maintenance cost as a percentage of property value [Decimal]
            'management_factor': 0.1, # Property management cost as a percentage of rental income [Decimal]
            'insurance_factor': 0.005, # Decimal
            'condo_fee_gr': inflation_rate, # Decimal
            'maintenance_gr': inflation_rate, # Decimal
            'management_gr': inflation_rate, # Decimal
            'insurance_gr': inflation_rate, # Decimal
            'tax_gr': inflation_rate, # Decimal
        },
        'mortgage': {
            'interest_rate': 0.02, # Decimal
            'interest_stress_test_rate': 0.05, # Decimal
            'downpayment_factor': 0.2, # Decimal
            'amortization_periods': 300,
        },
        'property_appreciation': {
            'property_appreciation_rate_low': 0.0, # Decimal
            'property_appreciation_rate': 0.02, # Decimal
            'property_appreciation_rate_high': 0.05, # Decimal
        },
        'capital': {
            'closing_cost_factor': 0.03, # Decimal
            'rehab_cost_factor': 0.01, # Decimal
        },
        'valuation': {
            'discount_rate': 0.10, # Decimal
            'inflation_rate': inflation_rate, # Decimal
            'evaluation_period': 25, # [years]
            'property_valuation_factor': 0.5, # Decimal
            'rental_valuation_factor': 1.0, # Decimal
        },
    }
    calc_valuation(run_date,assumptions)
    # for run_date in ['2021-09-12','2021-09-13']:
        # calc_valuation(run_date)
