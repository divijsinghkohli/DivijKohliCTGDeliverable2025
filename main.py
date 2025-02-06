import os
import csv
from datetime import datetime, timedelta

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
                        for row in reader:
                            self.data.append(row)
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

                # Skip rows outside of trading hours (9:30 AM to 4:00 PM EST)
                if not (datetime.strptime('09:30:00', '%H:%M:%S').time() <= timestamp.time() <= datetime.strptime('16:00:00', '%H:%M:%S').time()):
                    continue

                # Append the cleaned row
                cleaned_data.append(row)

            except ValueError:
                # Skip rows with invalid data types (e.g., cannot convert to float)
                continue
            except Exception as e:
                print(f"Unexpected error with row {row}: {e}")
        
        # Remove duplicates based on Timestamp and Price
        unique_data = []
        seen = set()
        for row in cleaned_data:
            key = (row['Timestamp'], row['Price'])
            if key not in seen:
                seen.add(key)
                unique_data.append(row)
        
        self.data = unique_data
        print(f"Cleaned data contains {len(self.data)} rows.")

# 3. OHLCV Data Generation
class CTGOHLCVGenerator:
    def __init__(self, data):
        self.data = data

    def parse_interval(self, interval):
        """
        Parse the interval string (e.g., '4s', '15m', '1h', '1d') into a timedelta.
        """
        unit = interval[-1]
        value = int(interval[:-1])

        if unit == 's':
            return timedelta(seconds=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        elif unit == 'h':
            return timedelta(hours=value)
        elif unit == 'd':
            return timedelta(days=value)
        else:
            raise ValueError(f"Unsupported interval unit: {unit}")

    def generate_ohlcv(self, interval, start_time, end_time):
        """
        Generate OHLCV data for the specified time interval and time frame.
        """
        interval_timedelta = self.parse_interval(interval)
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

        ohlcv_data = []
        current_time = start_time

        while current_time < end_time:
            next_time = current_time + interval_timedelta
            interval_data = [row for row in self.data if current_time <= datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S.%f') < next_time]

            if interval_data:
                open_price = float(interval_data[0]['Price'])
                high_price = max(float(row['Price']) for row in interval_data)
                low_price = min(float(row['Price']) for row in interval_data)
                close_price = float(interval_data[-1]['Price'])
                volume = sum(int(row['Size']) for row in interval_data)

                ohlcv_data.append({
                    'timestamp': current_time,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })

            current_time = next_time

        # Write the OHLCV data to a CSV file
        with open('bruh.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            writer.writeheader()
            writer.writerows(ohlcv_data)
        print(f"Generated {len(ohlcv_data)} OHLCV records.")

# Main execution flow
if __name__ == "__main__":
    data_loader = CTGDataLoader('/Users/divijkohli/desktop/CTG/sw-challenge-spring-2025/data')
    data_loader.load_data()

    data_cleaner = CTGDataCleaner(data_loader.data)
    data_cleaner.clean_data()

    ohlcv_generator = CTGOHLCVGenerator(data_cleaner.data)
    ohlcv_generator.generate_ohlcv("1h", "2024-09-16 09:30:00", "2024-09-16 16:00:00")
