import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew
from scipy.signal import welch
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os

# Function to save chunks with k-means label 0 to separate CSV files
def save_chunks(chunks, output_dir='output_chunks'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for i, chunk in enumerate(chunks):
        chunk.to_csv(os.path.join(output_dir, f'chunk_{i}.csv'), index=False)

# Function to read the CSV file and split data into 3000ms chunks
def read_and_chunk_data(filename, chunk_duration=3000, time_threshold=20):
    data = pd.read_csv(filename)
    chunks = []
    chunk = []

    previous_row = None

    for index, row in data.iterrows():
        current_time = float(row[6])  # Assuming the timestamp is in the seventh column
                
        if previous_row is not None and (current_time - previous_row) > time_threshold:
            print(current_time)
            chunks.append(pd.DataFrame(chunk))
            chunk = [row]
        else:
            chunk.append(row)
        previous_row = current_time

    if chunk:
        chunks.append(pd.DataFrame(chunk))
    
    return chunks

# Function to calculate the RMS value
def calculate_rms(values):
    return np.sqrt(np.mean(np.square(values)))

# Function to calculate spectral features using Welch's method
def calculate_spectral_features(values, fs=334): # Assume sampling frequency 1000Hz
    f, Pxx = welch(values, fs=fs)
    spectral_power = np.sum(Pxx)
    spectral_kurtosis = kurtosis(Pxx)
    return spectral_power, spectral_kurtosis

# Function to calculate statistical features
def calculate_features(chunk):
    features = []
    for axis in ['AccX', 'AccY', 'AccZ', 'GyrX', 'GyrY', 'GyrZ']:
        values = chunk[axis].values
        rms = calculate_rms(values)
        k = kurtosis(values)
        s = skew(values)
        spectral_power, spectral_kurtosis = calculate_spectral_features(values)
        features.extend([rms, k, s, spectral_power, spectral_kurtosis])
    return features

# Function to plot chunks with k-means label 0
def plot_chunks_with_label_0(chunks):
    chunks_combined = chunks[0]
    for i, chunk in enumerate(chunks):
        chunks_combined = pd.concat([chunks_combined, chunk], ignore_index=True)

    plt.figure(figsize=(10, 6))
    plt.plot(chunks_combined['timestamp'], chunks_combined['AccX'], label='AccX')
    plt.plot(chunks_combined['timestamp'], chunks_combined['AccY'], label='AccY')
    plt.plot(chunks_combined['timestamp'], chunks_combined['AccZ'], label='AccZ')
    plt.plot(chunks_combined['timestamp'], chunks_combined['GyrX'], label='GyrX')
    plt.plot(chunks_combined['timestamp'], chunks_combined['GyrY'], label='GyrY')
    plt.plot(chunks_combined['timestamp'], chunks_combined['GyrZ'], label='GyrZ')
    plt.xlabel('Timestamp')
    plt.ylabel('Sensor Values')
    plt.legend()
    plt.show()

# Main function to process the data and apply k-means clustering
def main(filename):
    chunks = read_and_chunk_data(filename)
    feature_list = []

    for chunk in chunks:
        features = calculate_features(chunk)
        feature_list.append(features)

    # Convert feature list to numpy array for clustering
    feature_array = np.array(feature_list)

    # Apply k-means clustering
    kmeans = KMeans(n_clusters=2) # Example with 3 clusters; adjust as needed
    kmeans.fit(feature_array)
    cluster_labels = kmeans.predict(feature_array)

    # Find the cluster centers
    cluster_centers = kmeans.cluster_centers_
    # Calculate the distance from each point to its assigned cluster center
    distances = [np.linalg.norm(x - cluster_centers[cluster]) for x, cluster in zip(feature_array, cluster_labels)]

    # Define a threshold for anomaly detection (e.g., based on the distance percentile)
    percentile_threshold = 90
    threshold_distance = np.percentile(distances, percentile_threshold)

    anomalies = [chunks[i] for i, distance in enumerate(distances) if distance > threshold_distance]

    # Print k-means labels for each chunk
    for i, distance in enumerate(distances):
        print(f"Chunk {i}: K-means label: {distance > threshold_distance}")

    non_anomalies = [chunks[i] for i, distance in enumerate(distances) if distance < threshold_distance]

    # Plot chunks with k-means label 0
    plot_chunks_with_label_0(chunks)
    plot_chunks_with_label_0(non_anomalies)
    plot_chunks_with_label_0(anomalies)

    save_chunks(non_anomalies, output_dir="paving_non_anomalies")
    save_chunks(anomalies, output_dir="paving_anomalies")


if __name__ == '__main__':
    filename = '/home/paula/Documents/stuff/testi/paving_stones_data_2024-07-08_11-50-07.csv'  # Replace with your CSV file name
    main(filename)
