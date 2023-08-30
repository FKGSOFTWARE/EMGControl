
// ? load onto board using Ardiuno IDE, then use serial monitor to see output
// ? use python script to read serial monitor output and save to csv file
// ? use D2 and D3 for load cell, connect the grounds, use DAC0/A12 for analogue output.

#include <Arduino.h>
#include <Arduino_AdvancedAnalog.h>
#include "HX711.h"

#define DOUT  2 // white wire
#define CLK  3 // yellow wire
HX711 scale;

AdvancedDAC DAC0(A12)
#define DAC_PIN DAC0

float lastLoadCellValue = 0;  // Store the last seen load cell value

int MIN_LOAD_CELL_VALUE = -550000;
int MAX_LOAD_CELL_VALUE = 250000;

void setup() {
  pinMode(DAC_PIN, OUTPUT);
  scale.begin(DOUT, CLK);
  Serial.begin(115200);
}

void loop() {
  if (scale.is_ready()) {  // Read and concatenate the weight from the load cell at a slower rate
    lastLoadCellValue = scale.read();  // Update the last seen value
  }

// Convert the lastLoadCellValue (or any other desired value) to an analog range.
// Assuming that the load cell value can be represented in 0-4095 range for the Due's 12-bit DAC
int analog_value = map(lastLoadCellValue, MIN_LOAD_CELL_VALUE, MAX_LOAD_CELL_VALUE, 0, 4095);
analogWrite(DAC_PIN, analog_value);
}
