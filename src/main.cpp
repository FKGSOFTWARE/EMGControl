#include <Arduino.h>

#define ANALOG_PIN A0



//~~~ Arduino Code for one source ~~~//

// int analogPin = A0; // potentiometer wiper (middle terminal) connected to analog pin 3 outside leads to ground and +5V
// int val = 0;  // variable to store the value read

// void setup() {
//   pinMode(ANALOG_PIN, INPUT);
//   Serial.begin(9600);           // Start serial communication at 9600 bps
// }

// void loop() {
//   val = analogRead(ANALOG_PIN);  // read the input pin
//   Serial.println(val);          // debug value
//   delayMicroseconds(100000); // delay in micro seconds 1000 micro seconds = 1 nano second = 0.01 seconds
// }




//~~~ Arduino Code for two source ~~~//

void setup() {
  Serial.begin(9600); // Start serial communication at 9600 bps
}

void loop() {
  int sensorValue1 = analogRead(A0); // Read the analog input on pin A0
  int sensorValue2 = analogRead(A1); // Read the analog input on pin A1
  Serial.print(sensorValue1);
  Serial.print(",");
  Serial.println(sensorValue2);
  delayMicroseconds(100000); // delay in micro seconds 1000 micro seconds = 1 nano second = 0.01 seconds
}