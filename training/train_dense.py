import pickle
import tensorflow as tf
from tensorflow.keras.models import Sequential
import numpy as np
from tensorflow.keras.layers import Dense
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import EarlyStopping

data_path = "training/trainingsdata/traintestval/"

mapping = {"paving_stones": 0.0, "sett": 1.0, "asphalt": 2.0}

# This data is for training the model
with open(data_path + 'train_data.pkl', 'rb') as file:
    data_train, labels_train = pickle.load(file)
labels_train = np.asarray([mapping[element] for element in labels_train])
# This data is used during training to validate the current status of the model and keep from overfitting on the trainingsdata
with open(data_path + 'val_data.pkl', 'rb') as file:
    data_val, labels_val = pickle.load(file)
labels_val = np.asarray([mapping[element] for element in labels_val])
# This data is used to evaluate the final trained model
with open(data_path + 'test_data.pkl', 'rb') as file:
    data_test, labels_test = pickle.load(file)
labels_test = np.asarray([mapping[element] for element in labels_test])


print("Daten geladen...")

# Modell aufbauen
model = Sequential()
model.add(Dense(20, activation='relu', input_shape=(42,)))
model.add(Dense(10, activation='relu'))
model.add(Dense(3, activation='softmax')) # Sigmoid-Aktivierung für binäre Klassifikation

tf.keras.utils.plot_model(
    model,
    to_file='training/model_dense.png',
	show_shapes=True,
)

# Modell kompilieren
print("Starte Training...")
optimizer = tf.keras.optimizers.Adam(learning_rate=0.0005)
model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Define early stopping callback to monitor validation loss
early_stopping = EarlyStopping(monitor='val_loss', patience=7)

# Modell trainieren
history = model.fit(data_train, labels_train, epochs=100, batch_size=32, validation_data=(data_val, labels_val), callbacks=[early_stopping])

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Epoch')
plt.legend()
plt.savefig('training/models/training_validation_plot.png')

# Modell evaluieren
metrics = model.evaluate(data_test, labels_test, return_dict=True)
print(metrics)

# Model speichern
model.save('training/models/model.keras')

# Convert model to tflite
def convert_tflite_model(model):
	import tensorflow as tf
	converter = tf.lite.TFLiteConverter.from_keras_model(model)
	tflite_model = converter.convert()
	return tflite_model

def save_tflite_model(tflite_model, save_dir, model_name):
	import os
	if not os.path.exists(save_dir):
		os.makedirs(save_dir)
	save_path = os.path.join(save_dir, model_name)
	with open(save_path, "wb") as f:
		f.write(tflite_model)
	print("Tflite model saved to %s", save_dir)
     
tflite_model = convert_tflite_model(model)

save_tflite_model(tflite_model, './training/models', 'model_dense.tflite')
model.save_weights('./training/models/model_dense')

# after converting to tflite convert it to tflite for micro with the following:
# xxd -i models/model_dense.tflite > models/model_dense.cc
