import pandas
import time
import schedule
import scrape_mls
import scrape_rf
import preprocessing_mls
import preprocessing_rf
import mls_valuation
import datetime as dt
# import report

def main():

    run_date = dt.datetime.strftime(dt.date.today(),'%Y-%m-%d')

    scrape_rf.main()
    scrape_mls.main_mp()
    preprocessing_mls.main(run_date)
    preprocessing_rf.main(run_date)

    ### Valuation Assumptions ###
    inflation_rate = 0.05
    assumptions = {
        'rent_estimation': {
            'rent_sf': 0.1,
            'vacancy_sf': 0.1,
            'rental_gr': 0.025,
        },
        'property_expenses': {
            'maintenance_factor': 0.01,
            'management_factor': 0.1,
            'insurance_factor': 0.005,
            'condo_fee_gr': inflation_rate,
            'maintenance_gr': inflation_rate,
            'management_gr': inflation_rate,
            'insurance_gr': inflation_rate,
            'tax_gr': inflation_rate,
        },
        'mortgage': {
            'interest_rate': 0.03,
            'interest_stress_test_rate': 0.05,
            'downpayment_factor': 0.2,
            'amortization_periods': 300,
        },
        'property_appreciation': {
            'property_appreciation_rate_low': 0.0,
            'property_appreciation_rate': 0.02,
            'property_appreciation_rate_high': 0.05,
        },
        'capital': {
            'closing_cost_factor': 0.03,
            'rehab_cost_factor': 0.01,
        },
        'valuation': {
            'discount_rate': 0.10,
            'inflation_rate': inflation_rate,
            'evaluation_period': 25, # [years]
            'property_valuation_factor': 0.5,
            'rental_valuation_factor': 1.0,
        },
    }
    mls_valuation.calc_valuation(run_date,assumptions)

if __name__ == '__main__':
    schedule.every().day.at('00:00').do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
