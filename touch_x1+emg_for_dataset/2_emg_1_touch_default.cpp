#include <Arduino.h>

// ! ~~~ Arduino Code for two source ~~~//

// #define ANALOG_PIN A0  // Analog pin for sensor

// void setup() {
//   pinMode(ANALOG_PIN, INPUT);  // Set ANALOG_PIN as input
//   Serial.begin(115200);  // Start serial communication at 115200 bps
// }

// void loop() {
//   int val = analogRead(ANALOG_PIN);  // Read the value from sensor connected to ANALOG_PIN
  
//   // Get the current time since the program started
//   unsigned long time = micros(); // overflows at 70 minutes
  
//   // Construct the data string and print it to the Serial Monitor
//   String dataString = String(time) + "," + String(val);
//   Serial.println(dataString);
// }

//  ! ~~~ Arduino Code for two sources ~~~//

// void setup() {
//   Serial.begin(9600); // Start serial communication at 9600 bps
// }

// void loop() {
//   int sensorValue1 = analogRead(A0); // Read the analog input on pin A0
//   int sensorValue2 = analogRead(A1); // Read the analog input on pin A1
//   Serial.print(sensorValue1);
//   Serial.print(",");
//   Serial.println(sensorValue2);
//   delayMicroseconds(100000); // delay in micro seconds 1000 micro seconds = 1 nano second = 0.01 seconds
// }

// ! ~~~ Arduino Code for n sources ~~~//

#define NUMBER_OF_SENSORS 2 // Define the number of sensors connected to the Arduino

int analog_pins[NUMBER_OF_SENSORS] = {A0, A1}; // Define an array with the pins connected to the sensors. Change the values to match your own setup.

void setup() {
  // Set each pin in analog_pins as input
  for(int i = 0; i < NUMBER_OF_SENSORS; i++) {
    pinMode(analog_pins[i], INPUT);
  }

  pinMode(10, INPUT);
  
  Serial.begin(115200);  // Start serial communication at 115200 bps
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

  int touchVal = digitalRead(10);

  // Print the data string to the Serial Monitor
  Serial.println(dataString + "," + touchVal);
  // delay(200);

}