import csv
import os

def create_new_csv(filename, rows, file_index):
    new_filename = f"{os.path.splitext(filename)[0]}_part_{file_index}.csv"
    with open(new_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    print(f"Created {new_filename}")

def split_csv_by_time_interval(filename, time_threshold=2000, time_interval=85):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # Read the header
        
        previous_time = None
        previous_row = None
        file_index = 1
        rows = [header]

        for row in reader:
            if len(row) >= 7:
                current_time = float(row[6])  # Assuming the timestamp is in the seventh column
                
                if previous_row is not None and (current_time - previous_row) > time_threshold:
                    create_new_csv(filename, rows, file_index)
                    file_index += 1
                    rows = [header]  # Start new CSV with header
                    previous_time = 0
                if previous_time is None or (current_time - previous_time) >= time_interval:
                    rows.append(row)
                    previous_time = current_time
                previous_row = current_time

        # Create the last file with remaining rows
        if len(rows) > 1:
            create_new_csv(filename, rows, file_index)

def main():
    filename = 'asphalt_data_2024-07-05_09-13-22.csv'  # Replace with your CSV file name
    split_csv_by_time_interval(filename)

if __name__ == '__main__':
    main()
