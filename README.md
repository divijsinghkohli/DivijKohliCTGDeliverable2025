
# CTG Deliverable - Divij Kohli

This project is my submission for the 2025 CTG application cycle, it processes, loads, and cleans the given tick data for the fictional stock and then outputs data over a user selected timeframe and interval in OHLCV (Open, High, Low, Close, Volume) format. 



## How to Use

    1) Ensure you have python installed on your system
    2) Place your tick data CSV files in a directory on your machine.
    3) Update the file path in main.py (line 222) to point to your  data directory:
        
        data_loader = CTGDataLoader('/path/to/your/data')
        Replace /path/to/your/data with the actual path

    4) Run the program using:
        
        python main.py
    

## Specifying Time Intervals and Time Frame
To customize the time intervals for OHLCV generation, modify the calls to generate_ohlcv in main.py. The function is used as follows:

    ohlcv_generator.generate_ohlcv("<interval>", "<start_time>", "<end_time>", "<output_filename>")

    1) <interval>: Specify time intervals such as 1d (1 day), 1h30m (1   hour 30 minutes), 10m5s (10 minutes 5 seconds), etc.
    2) <start_time> and <end_time>: Define the time range in YYYY-MM-DD HH:MM:SS format.
    3) <output_filename>: Name of the output CSV file containing the OHLCV data.





## Assumptions and Limitations

    1) The script assumes that the CSV files contain columns: Timestamp, Price, and Size.
    2) Data is expected in the format: YYYY-MM-DD HH:MM:SS.ssssss for timestamps.
    3) Outliers in low prices are removed using the Interquartile Range (IQR) method.
    4) The script processes data efficiently but may have performance limitations with extremely large datasets.
## Data Cleaning Report

    1) Empty price, size, or timestamp
        - Given that the dataset contained 1.76 million values, I handled empty fields by simply not including them in my final cleaned dataset
        - I determined that omitting these values would not significantly impact the output given the size of the dataset. 
        - In retrospect however, it would have been better practice to use some kind of predictive algorithm to estimate what the missing value should have been. 
    2) Invalid type or negative value
        - I delt with invalid data formatting (ex timestamp not in XX:XX:XX format) by once again simply removing these values
        - Similarly, if I encountered a negative price or volume, I simply did not include that given row in my final cleaned dataset. 
    3) Duplicate Values
        - Using a vetting algorithim similar to a contains method, I ensured that an non initial instance of a row was not added to my cleaned data set. 
        - This ensures that I completely eliminate duplicates without accidentally eliminating all instances of a given row value in the process
    4) Outliers
        - For the purpose of this program I defined an outlier as any price who was below Quartile 1 - 1.5(IQR) or above Quartile 3 + 1.5(IQR)
        - Any prices who fit these criteria to be an outlier were not included in the final dataset

In total, the final cleaned data set contained 1726271 rows of data, out of the original 1761321 rows. This means that 35050 rows or roughly 1.98% of the data was removed in the cleaning process. 
