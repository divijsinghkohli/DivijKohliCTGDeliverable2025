
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
    #Checked Errors
    
