import csv
import matplotlib.pyplot as plt

def read_sensor_data(filename):
    accel_data = {'x': [], 'y': [], 'z': []}
    gyro_data = {'x': [], 'y': [], 'z': []}
    
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if len(row) >= 6:
                accel_data['x'].append(float(row[0]))
                accel_data['y'].append(float(row[1]))
                accel_data['z'].append(float(row[2]))
                gyro_data['x'].append(float(row[3]))
                gyro_data['y'].append(float(row[4]))
                gyro_data['z'].append(float(row[5]))
    return accel_data, gyro_data

def plot_sensor_data(accel_data, gyro_data):
    plt.figure(figsize=(12, 6))

    # Plot Acceleration Data
    plt.subplot(2, 1, 1)
    plt.plot(accel_data['x'], label='Accel X')
    plt.plot(accel_data['y'], label='Accel Y')
    plt.plot(accel_data['z'], label='Accel Z')
    plt.title('Acceleration Data')
    plt.xlabel('Sample')
    plt.ylabel('Acceleration (m/s^2)')
    plt.legend()
    plt.grid(True)

    # Plot Gyroscope Data
    plt.subplot(2, 1, 2)
    plt.plot(gyro_data['x'], label='Gyro X')
    plt.plot(gyro_data['y'], label='Gyro Y')
    plt.plot(gyro_data['z'], label='Gyro Z')
    plt.title('Gyroscope Data')
    plt.xlabel('Sample')
    plt.ylabel('Gyroscope (deg/s)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def main():
    filename = '/home/paula/Documents/stuff/testi/asphalt_data_2024-07-05_09-13-22.csv'  # Replace with your CSV file name
    accel_data, gyro_data = read_sensor_data(filename)
    plot_sensor_data(accel_data, gyro_data)

if __name__ == '__main__':
    main()
