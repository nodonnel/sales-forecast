# sales-forecast
Python/pandas code to generate a moving-average sales forecast (uses Jupyter Notebook)

This is a project I did for a small business client who wanted an algorithm to forecast near-term demand. The algorithm uses sales data for the two years to create a forecast for the next three months (although the number of months can be easily changed within the code) using a moving-average technique. Essentially, the percent change in year-over-year sales from the previous year to the current year, for each state, is calculated for the preceding three months, and then this percent change is applied to the target months' sales data for the previous year.  

The main code for this project is in the file "sales_forecast_anonymized.ipynb". This code takes a CSV file as input, namely "sales_anonymized.csv". As the name suggests, this is real sales data that has been anonymized, i.e. all the customer names have been replaced by "Customer [index number]", and the sales figures themselves have been changed. 

The file "anonymize_customer_data.ipynb" shows how this was accomplished. The original input was sales data exported from QuickBooks; for obvious reasons, I've kept this data private, but you can see how it was converted to the anonymized sales data. 

The output of "sales_forecast_anonymized.ipynb" is the file "anonymized forecast 2019-06-01.xlsx", which I've uploaded so you can see the results without downloading and running the code, but you can generate this file yourself if you clone the repo and test it. 
