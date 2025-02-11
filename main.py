#Title: CTG Deliverable Spring 2025
#Author: Divij Kohli
#Date (Last Modified): Feb 10, 2025
from datetime import datetime, timedelta
import os
import csv
import re
from collections import defaultdict

# 1. Data Loading
class CTGDataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.data = []

    def load_data(self):
        """
        Load and process all CSV files from the provided directory.
        """
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r') as file:
                        reader = csv.DictReader(file)
                        self.data.extend(reader)  # Use extend instead of append in a loop
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        print(f"Loaded {len(self.data)} rows of data.")

# 2. Data Cleaning
class CTGDataCleaner:
    def __init__(self, data):
        self.data = data

    def clean_data(self):
        """
        Clean the data by applying validation checks.
        """
        cleaned_data = []
        seen = set()  # To track duplicates

        for row in self.data:
            try:
                # Ensure that Price, Size, and Timestamp are not empty
                price_str = row['Price'].strip() if row['Price'] else ''
                size_str = row['Size'].strip() if row['Size'] else ''
                timestamp_str = row['Timestamp'].strip() if row['Timestamp'] else ''

                # Skip row if any field is missing or invalid
                if not price_str or not size_str or not timestamp_str:
                    continue

                price = float(price_str)
                size = int(size_str)
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')

                # Skip rows with negative price or size
                if price < 0 or size < 0:
                    continue

                # Check for duplicates
                key = (timestamp_str, price_str)
                if key not in seen:
                    seen.add(key)
                    cleaned_data.append({
                        'Timestamp': timestamp,
                        'Price': price,
                        'Size': size
                    })

            except ValueError:
                # Skip rows with invalid data types (e.g., cannot convert to float)
                continue
            except Exception as e:
                print(f"Unexpected error with row {row}: {e}")
        
        # Sort the cleaned data by timestamp
        cleaned_data.sort(key=lambda x: x['Timestamp'])
        self.data = cleaned_data
        print(f"Cleaned data contains {len(self.data)} rows.")

# 3. OHLCV Data Generation (Optimized)
class CTGOHLCVGenerator:
    def __init__(self, data):
        self.data = data

    def parse_interval(self, interval):
        """
        Parse the interval string (e.g., '1h30m', '10m5s', '1h2m3s') into a timedelta.
        Handles mixed combinations of hours, minutes, and seconds.
        """
        # Regex to find hours, minutes, and seconds
        time_units = re.findall(r'(\d+)([hmsd])', interval)

        total_seconds = 0

        for value, unit in time_units:
            value = int(value)  # Convert the number to an integer
            if unit == 'd':
                total_seconds += value * 86400  # Convert days to seconds
            elif unit == 'h':
                total_seconds += value * 3600  # Convert hours to seconds
            elif unit == 'm':
                total_seconds += value * 60    # Convert minutes to seconds
            elif unit == 's':
                total_seconds += value         # Seconds remain as is

        # Return the total as a timedelta object
        return timedelta(seconds=total_seconds)

    def remove_outliers(self, price_data):
        """
        Remove outliers using the Interquartile Range (IQR) method.
        """
        # Calculate Q1, Q3, and IQR
        sorted_data = sorted(price_data)
        Q1 = sorted_data[len(sorted_data) // 4]
        Q3 = sorted_data[3 * len(sorted_data) // 4]
        IQR = Q3 - Q1

        # Define outlier bounds
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        # Filter out outliers
        return [price for price in price_data if lower_bound <= price <= upper_bound]

    def generate_ohlcv(self, interval, start_time, end_time, title):
        """
        Generate OHLCV data for the specified time interval and time frame.
        """
        interval_timedelta = self.parse_interval(interval)
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        ohlcv_data = []
        current_interval_start = start_time
        current_interval_end = current_interval_start + interval_timedelta

        # Initialize OHLCV values for the current interval
        open_price = None
        high_price = None
        low_price = None
        close_price = None
        volume = 0
        prices_in_interval = []

        for row in self.data:
            timestamp = row['Timestamp']
            price = row['Price']
            size = row['Size']

            # Skip data outside the specified time range
            if timestamp < start_time or timestamp > end_time:
                continue

            # If the timestamp is beyond the current interval, finalize the OHLCV record
            while timestamp >= current_interval_end:
                if open_price is not None:  # Ensure there is data for the interval
                    # Remove outliers from low prices
                    low_prices = self.remove_outliers(prices_in_interval)
                    low_price = min(low_prices) if low_prices else high_price

                    ohlcv_data.append({
                        'timestamp': current_interval_start,
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'close': close_price,
                        'volume': volume
                    })
                else:
                    # If no data exists for this interval, skip it or fill with placeholders
                    pass

                # Move to the next interval
                current_interval_start = current_interval_end
                current_interval_end = current_interval_start + interval_timedelta

                # Reset OHLCV values for the new interval
                open_price = None
                high_price = None
                low_price = None
                close_price = None
                volume = 0
                prices_in_interval = []

            # Update OHLCV values for the current interval
            if open_price is None:
                open_price = price  # First price in the interval is the open price
            close_price = price  # Last price in the interval is the close price
            high_price = max(high_price, price) if high_price is not None else price
            low_price = min(low_price, price) if low_price is not None else price
            volume += size
            prices_in_interval.append(price)

        # Finalize the last interval if it has data
        if open_price is not None:
            low_prices = self.remove_outliers(prices_in_interval)
            low_price = min(low_prices) if low_prices else high_price

            ohlcv_data.append({
                'timestamp': current_interval_start,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            })

        # Write the OHLCV data to a CSV file
        with open(title + '.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            writer.writeheader()
            writer.writerows(ohlcv_data)
        print(f"Generated {len(ohlcv_data)} OHLCV records.")

# Main execution flow
if __name__ == "__main__":
    data_loader = CTGDataLoader('/Users/divijkohli/desktop/Clubs/CTG/sw-challenge-spring-2025/data')
    data_loader.load_data()

    data_cleaner = CTGDataCleaner(data_loader.data)
    data_cleaner.clean_data()

    ohlcv_generator = CTGOHLCVGenerator(data_cleaner.data)
    ohlcv_generator.generate_ohlcv("1d", "2024-09-16 09:30:00", "2024-09-17 16:00:00", "Day")
    ohlcv_generator.generate_ohlcv("1h", "2024-09-16 09:30:00", "2024-09-17 16:00:00", "Hour")
    ohlcv_generator.generate_ohlcv("1m", "2024-09-16 09:30:00", "2024-09-17 16:00:00", "Minute")
    ohlcv_generator.generate_ohlcv("1s", "2024-09-16 09:30:00", "2024-09-16 16:00:00", "Second")