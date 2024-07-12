import csv
import matplotlib.pyplot as plt

def read_seventh_values(filename):
    seventh_values = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        prev_value = 0
        for row in reader:
            if len(row) >= 7:
                seventh_values.append(float(row[6])-prev_value)  # Convert the seventh value to float
                prev_value = float(row[6])
    return seventh_values

def plot_values(values):
    plt.figure(figsize=(10, 6))
    plt.plot(values[1:], marker='o')
    plt.title('Interval between measurements')
    plt.xlabel('measurement')
    plt.ylabel('milliseconds')
    plt.grid(True)
    plt.show()

def main():
    filename = '/home/paula/Documents/stuff/testi/asphalt_data_2024-07-05_09-13-22.csv'  # Replace with your CSV file name
    seventh_values = read_seventh_values(filename)
    plot_values(seventh_values)

if __name__ == '__main__':
    main()
