
#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;
sensors_event_t a, g, temp;

void measure(void);
String dataStr = "";

char report[256];
volatile int interruptCount = 0;

// A buffer holding the last 4000 ms of data at 17 Hz and 6 recorded values at a time
const int RING_BUFFER_SIZE = int((4000/17)*6);
float save_data[RING_BUFFER_SIZE] = {0.0};
// Most recent position in the save_data buffer
int begin_index = 0;
// True if there is not yet enough data to run inference
bool pending_initial_data = true;
// How often we should save a measurement during downsampling
int sample_every_n;
// The number of measurements since we last saved one
int sample_skip_counter = 1;


bool SetupMPU() {
  Wire1.begin();
  mpu.begin(0x68, &Wire1);
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);

  return true;
}


int lastReading = 0;
bool ReadMPU(float* input,
                       int length, bool reset_buffer) {
                        // Clear the buffer if required, e.g. after a successful prediction
  if (reset_buffer) {
    memset(save_data, 0, RING_BUFFER_SIZE * sizeof(float)*64);
    begin_index = 0;
    pending_initial_data = true;
  }
  mpu.getEvent(&a, &g, &temp);
  save_data[begin_index++] = a.acceleration.x;
  save_data[begin_index++] = a.acceleration.y;
  save_data[begin_index++] = a.acceleration.z;
  save_data[begin_index++] = a.gyro.x;
  save_data[begin_index++] = a.gyro.y;
  save_data[begin_index++] = a.gyro.z;
  bool new_data = false;
  // If we reached the end of the circle buffer, reset
  if (begin_index >= (1400)) {
    begin_index = 0;
    // Check if we are ready for prediction or still pending more initial data
    if (pending_initial_data) {
      pending_initial_data = false;
    }
  }

  // Return if we don't have enough data
  if (pending_initial_data) {
    return false;
  }

  // Copy the requested number of bytes to the provided input tensor
  for (int i = 0; i < length; ++i) {
    int ring_array_index = begin_index + i - length;
    if (ring_array_index < 0) {
      ring_array_index += (1400);
    }
    input[i] = save_data[ring_array_index];
    // Serial.print(input[i]);
    // Serial.print(",");
  }
  // Serial.print("\n");
  // TODO: Flatten
  return true;
}
