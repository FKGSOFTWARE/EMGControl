#include <Arduino.h>
// #include "HX711.h"

// #define DOUT  2
// #define CLK  3
// HX711 scale;

#define NUMBER_OF_SENSORS 3
int analog_pins[NUMBER_OF_SENSORS] = {A0, A1, A2};

float lastLoadCellValue = 0;  // Store the last seen load cell value

void setup() {
  for(int i = 0; i < NUMBER_OF_SENSORS; i++) {
    pinMode(analog_pins[i], INPUT);
  }

  // scale.begin(DOUT, CLK);
  Serial.begin(115200);
  // scale.power_up();

}

void loop() {
  String dataString = String(micros()) + "," + analogRead(A0) + "," + analogRead(A1) + ","+ analogRead(A2) + ",";

  // Read and concatenate the values from the EMG sensors
  // for(int i = 0; i < NUMBER_OF_SENSORS; i++) {
  //   dataString += String(analogRead(analog_pins[i])) + ",";
  // }

  // // Read and concatenate the weight from the load cell at a slower rate
  // if(scale.is_ready()) {
  //   lastLoadCellValue = scale.read();  // Update the last seen value
  // }
  // dataString += String(lastLoadCellValue);  // Use the last seen value in all iterations

  // Print the concatenated data
  Serial.println(dataString);
}
