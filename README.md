# Detecting surfaces based on acceleration data recorded on a bicycle

This repository contains code for training and deploying a very simple neural network on the senseBox MCU S2 for detecting the kind of surface, which a bicycle has driven over based on recorded acceleration data.

## Option A: Training a simple model in edge impulse and exporting it as an Arduino library for deployment

### deployment_sensebox/edge_impulse_export/
I have exported the following edge impulse model as an arduino library:

![./impulse_design](./impulse_design.png)

I then adjusted the "nano_ble_33sense_acceleration" example, which comes with the library. If the impulse design is changed, the arduino code might also have to be adjusted.


## Option B: Training a simple tensorflow model and deploying in Arduino using tensorflow lite for microcontrollers

### training/
I tried to replicate the edge impulse model that uses flattened input. 
Use the file `edge_impulse_to_tf_pkl.py` to convert data recorded with edge impulse to pkl files for training, testing and validation. If you record new data just export it and unpack it in the `trainingsdata` folder.

Use the file `train_dense.py` to train a model with dense layers with the previously generated data. You can see the model structure in `model_dense.png`. You can see how well the training went in `models/training_validation_plot.png`. 
To turn the resulting trained tflite model into an array of bytes for running it on a microcontroller use the following command:

`xxd -i models/model_dense.tflite > models/model_dense.cc`

It might make sense to look into standardization or normalization of the data, as this will probably improve the training process. Note, that if you standardize/normalize during training you will also have to standardize/normalize during deployment.

### deployment_sensebox/mini_detector/
Insert the byte array, that was generated in the previous step, in the `mpu_handler.ino`. If you change the recording frequency and window size of the trainingsdata, you also need to change it here. Currently its set at 31.25 Hz with a window size of 3 seconds.
