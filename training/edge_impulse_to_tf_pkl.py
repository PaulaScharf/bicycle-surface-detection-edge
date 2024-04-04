import json
import numpy as np
from scipy.stats import skew, kurtosis
import pandas as pd
from sklearn.model_selection import train_test_split
import pickle
from sklearn.preprocessing import StandardScaler

window_size = int(2000/17.24137931034483)
window_increase = int(400/17.24137931034483)

with open('training/trainingsdata/info.labels.json', 'r') as f:
  paths_labels = json.load(f)

statistics = []
for file_info in paths_labels["files"]:
  print(file_info["path"])
  with open('training/trainingsdata/' + file_info["path"], 'r') as f:
    file = json.load(f)
  length_file = len(file["payload"]["values"])
  amount_windows = 1
  if length_file > window_size:
    amount_windows = int((length_file - window_size) / window_increase)
  for i in range(amount_windows):
    start = i * window_increase
    end = min((i) * window_increase + window_size, length_file)
    statistics_row = [file_info["label"]["label"]]
    for j in range(6):
      pheno = np.array(file["payload"]["values"][start:end][j])
      statistics_row.append(np.mean(pheno)) # average
      statistics_row.append(np.min(pheno)) # min_value
      statistics_row.append(np.max(pheno)) # max_value
      statistics_row.append(np.std(pheno)) # std_deviation
      statistics_row.append(np.sqrt(np.mean(pheno**2))) # rms
      statistics_row.append(skew(pheno)) # skewness
      statistics_row.append(kurtosis(pheno)) # kurt
      
    statistics.append(statistics_row)

df = pd.DataFrame(statistics, columns=['Label',
                                       'AccX_Average', 'AccX_Min', 'AccX_Max', 'AccX_Std Deviation', 'AccX_RMS', 'AccX_Skewness', 'AccX_Kurtosis',
                                       'AccY_Average', 'Min', 'Max', 'Std Deviation', 'RMS', 'Skewness', 'Kurtosis',
                                       'AccZ_Average', 'Min', 'Max', 'Std Deviation', 'RMS', 'Skewness', 'Kurtosis',
                                       'GyrX_Average', 'Min', 'Max', 'Std Deviation', 'RMS', 'Skewness', 'Kurtosis',
                                       'GyrY_Average', 'Min', 'Max', 'Std Deviation', 'RMS', 'Skewness', 'Kurtosis',
                                       'GyrZ_Average', 'Min', 'Max', 'Std Deviation', 'RMS', 'Skewness', 'Kurtosis'])

data = df.iloc[:, 1:].values
labels = df.iloc[:, 0].values


# TODO: Luca normalised the data in his code. Why?? Do we need to do that?
scaler = StandardScaler()
data = scaler.fit_transform(data)

# Daten in Trainings- und Testsets aufteilen
data_train, data_test, labels_train, labels_test = train_test_split(data, labels, test_size=0.15, random_state=42)
# Validation set
data_train, data_valid, labels_train, labels_valid = train_test_split(data, labels, test_size=0.20, random_state=42)

# speichern der Daten um Zeit zu sparen
with open('training/trainingsdata/traintestval/train_data.pkl', 'wb') as file:
    pickle.dump((data_train, labels_train), file)

with open('training/trainingsdata/traintestval/test_data.pkl', 'wb') as file:
    pickle.dump((data_test, labels_test), file)

# Validation set
with open('training/trainingsdata/traintestval/val_data.pkl', 'wb') as file:
    pickle.dump((data_valid, labels_valid), file)
