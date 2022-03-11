# Real Estate Valuation Analysis
Analyzes real estate property listings data and rental data to estimate DCF (Discounted Cash Flow) value of a property.

## Valuation Methodology
Uses a discounted cash flow model to assess the rental income valuation of a property.

## Assumptions (Default Values)
* Discount rate = 10%
* Maintenance Costs = 1% of property value (annually)
* Property Management Costs = 10% of rental income

## Contents

### Data Scraper
Python script to acquire data from MLS listings data and Rentfaster data.

### Data Cleaning
Python script to explore and clean up the data from raw form into something that can be manipulated and used. Made use of regex to clean up addresses which were used to aid in linking MLS listings data to Rentfaster data. Limitations were seen in the ability to connect the two datasets.

### Data Analysis
Data analyses were combined to provide a valuation based on average rent expected from a property based on its location, size, property type, and number of beds and baths. Methodology is stated above. The notebook provides insight on the valuation of rental operating income.

## Data Sources
Rental Data - Rentfaster www.rentfaster.com <br>
MLS Listing Data - MLS Portal 
