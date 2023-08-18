
#include <Arduino.h>
#include "HX711.h" // Include the HX711 library

#define DOUT  2
#define CLK  3
HX711 scale;

#define NUMBER_OF_SENSORS 2 // Define the number of sensors connected to the Arduino
int analog_pins[NUMBER_OF_SENSORS] = {A0, A1}; // Define an array with the pins connected to the sensors. Change the values to match your own setup.

void setup() {
  // Set each pin in analog_pins as input
  for(int i = 0; i < NUMBER_OF_SENSORS; i++) {
    pinMode(analog_pins[i], INPUT);
  }
  
  // Initialize the scale
  scale.begin(DOUT, CLK);
  scale.set_scale(2280.f);  // Calibration value (this will need to be adjusted for your setup)
  scale.tare();  // Reset the scale to 0
  
  Serial.begin(57200);  // Start serial communication at 115200 bps
}

void loop() {
  // Get the current time since the program started
  unsigned long time = micros(); // overflows at 70 minutes

  // Start the data string with the time
  String dataString = String(time);

  // Read the value from each sensor and append it to the data string
  for(int i = 0; i < NUMBER_OF_SENSORS; i++) {
    int val = analogRead(analog_pins[i]);
    dataString += "," + String(val);
  }
  
  // Read weight from load cell and append to data string
  float weight = scale.get_units(10);
  dataString += "," + String(weight, 2) + "g";

  // Print the data string to the Serial Monitor
  Serial.println(dataString);
}
