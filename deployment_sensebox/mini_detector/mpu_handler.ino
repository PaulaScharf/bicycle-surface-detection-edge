
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

// A buffer holding the last 3000 ms of data at 31.25 Hz
const int RING_BUFFER_SIZE = int(3*31.25);
float save_data[RING_BUFFER_SIZE][6] = {{0.0,0.0,0.0,0.0,0.0,0.0}};
// Most recent position in the save_data buffer
int begin_index = 0;
// True if there is not yet enough data to run inference
bool pending_initial_data = true;
// How often we should save a measurement during downsampling
int sample_every_n;
// The number of measurements since we last saved one
int sample_skip_counter = 1;


// Define an array to store the column averages
float averages[6] = {0.0,0.0,0.0,0.0,0.0,0.0};
float min_values[6] = {0.0,0.0,0.0,0.0,0.0,0.0};
float max_values[6] = {0.0,0.0,0.0,0.0,0.0,0.0};
float std_values[6] = {0.0,0.0,0.0,0.0,0.0,0.0};
float rms[6] = {0.0,0.0,0.0,0.0,0.0,0.0};
float skew[6] = {0.0,0.0,0.0,0.0,0.0,0.0};
float kurt[6] = {0.0,0.0,0.0,0.0,0.0,0.0};


bool SetupMPU() {
  Wire1.begin();
  mpu.begin(0x68, &Wire1);
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);

  return true;
}


int lastReading = 0;
bool ReadMPU(float* input,
                       int length) {
  // Serial.println(millis()-lastReading);
  lastReading = millis();
  mpu.getEvent(&a, &g, &temp);
  begin_index=begin_index+1;
  save_data[begin_index][0] = a.acceleration.x;
  save_data[begin_index][1] = a.acceleration.y;
  save_data[begin_index][2] = a.acceleration.z;
  save_data[begin_index][3] = a.gyro.x;
  save_data[begin_index][4] = a.gyro.y;
  save_data[begin_index][5] = a.gyro.z;
  bool new_data = false;
  // If we reached the end of the circle buffer, reset
  if (begin_index >= (RING_BUFFER_SIZE)) {
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

  // Iterate over each column
  for (int j = 0; j < 6; ++j) {
      // Calculate the sum of values in the current column
      float sum = 0;
      float max_val = -10000;
      float min_val = 10000;
      float sum_squared = 0;
      float sum_cubed = 0;
      float sum_fourth = 0;
      for (int i = 0; i < RING_BUFFER_SIZE; ++i) {
          float current = save_data[i][j];
          sum += current;
          min_val = min(min_val, current);
          max_val = max(max_val, current);
          sum_squared += pow(current, 2);
          sum_cubed += pow(current, 3);
          sum_fourth += pow(current, 4);
      }
      // Calculate the average of values in the current column
      input[j*7] = sum / RING_BUFFER_SIZE; // average
      input[j*7+1] = min_val; // minimum
      input[j*7+2] = max_val; // maximum
      float variance = (sum_squared / RING_BUFFER_SIZE) - pow(averages[j], 2);
      input[j*7+3] = sqrt(variance); // standard deviation
      input[j*7+4] = sqrt(sum_squared / RING_BUFFER_SIZE); // rms
      if (input[j*7+3] > 0) {
        input[j*7+5] = (sum_cubed / RING_BUFFER_SIZE - (3 * averages[j] * variance) - pow(averages[j], 3)) / pow(input[j*7+3], 3); // skew
      } else {
        input[j*7+5] = 0; // Set skewness to 0 if standard deviation is close to zero
      }
      input[j*7+6] = (sum_fourth / RING_BUFFER_SIZE - (4 * averages[j] * (sum_cubed / RING_BUFFER_SIZE)) + (6 * pow(averages[j], 2) * variance) - (3 * pow(averages[j], 4))) / pow(variance, 2); // kurt
  }

  // Flattening is very slow, so we cant do it live. So we have to reset everytime
  memset(save_data, 0, sizeof(save_data));
  begin_index = 0;
  pending_initial_data = true;

  return true;
}
