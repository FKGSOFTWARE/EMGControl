#include <Arduino.h>

#define NUMBER_OF_SENSORS 2 // Define the number of sensors connected to the Arduino

int analog_pins[NUMBER_OF_SENSORS] = {A0, A1}; // Define an array with the pins connected to the sensors. Change the values to match your own setup.

void setup() {
  // Set each pin in analog_pins as input
  for(int i = 0; i < NUMBER_OF_SENSORS; i++) {
    pinMode(analog_pins[i], INPUT);
  }
  
  Serial.begin(115200);  // Start serial communication at 115200 bps
}

void loop() {
  // Get the current time since the program started
  String dataString = String(micros()) + ",";

    // Read and concatenate the values from the EMG sensors
    // for(int i = 0; i < NUMBER_OF_SENSORS; i++) {
  dataString += String(abs(analogRead(analog_pins[0]))) + "," + String(abs(analogRead(analog_pins[1])));
      // Serial.println(i);
    // }
  // Print the data string to the Serial Monitor
  Serial.println(dataString);
 

  
}