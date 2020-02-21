# Equity_Machine_Learning

This project intends to figure out if a stock will outperform based on their SEC filings.

Many pieces of the project can be used separely, such as the SEC_Downloader_Classes.py.

To replicate this project first download company_info.csv. Then you must download the SEC indicies
for the desired time frame from https://www.sec.gov/Archives/edgar/full-index/.

Next modify SEC_Downloader_2.py to set the directory where you stored the indicies, where you want the filings to be saved to,
and set the number of programs you want to run in parallel. Then edit SEC Download Multiple.bat file to set
the path of the SEC_Downloader_2.py file. SEC Download Multiple.bat can then be run the number of times specified in SEC_Downloader_2.py.

Edit Get_Outperformance.py outperformance data by changing the path for where to store the outperformance data the running the file.

