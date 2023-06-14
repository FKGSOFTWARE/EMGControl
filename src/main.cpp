// #include <Arduino.h>


//~~~ Arduino Code for two source ~~~//

#include <Arduino.h>

#define ANALOG_PIN A0  // Analog pin for sensor

void setup() {
  pinMode(ANALOG_PIN, INPUT);  // Set ANALOG_PIN as input
  Serial.begin(115200);  // Start serial communication at 115200 bps
}

void loop() {
  int val = analogRead(ANALOG_PIN);  // Read the value from sensor connected to ANALOG_PIN
  
  // Get the current time since the program started
  unsigned long time = micros(); // overflows at 70 minutes
  
  // Construct the data string and print it to the Serial Monitor
  String dataString = String(time) + "," + String(val);
  Serial.println(dataString);
}




//~~~ Arduino Code for two source ~~~//

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

// // WITH CALIBRATION

// #define ANALOG_PIN A0  // Analog pin for sensor
// #define NUM_CALIBRATION_READINGS 10  // Number of readings to take for calibration

// // Calibration variables
// int baseline = 0;
// float scale = 1.0;

// // Function declaration for calibrate
// void calibrate();

// void setup() {
//   pinMode(ANALOG_PIN, INPUT);  // Set ANALOG_PIN as input
//   Serial.begin(115200);  // Start serial communication at 115200 bps

//   // Perform calibration at startup
//   calibrate();
// }

// void loop() {
//   int raw_val = analogRead(ANALOG_PIN);  // Read the raw value from sensor connected to ANALOG_PIN

//   // Subtract baseline and apply scale to get calibrated reading
//   float val = (raw_val - baseline) * scale;
  
//   // Get the current time since the program started
//   unsigned long time = micros();
  
//   // Construct the data string and print it to the Serial Monitor
//   String dataString = String(time) + "," + String(val);
//   Serial.println(dataString);
// }

// void calibrate() {
//   // Get baseline reading
//   baseline = 0;
//   for (int i = 0; i < NUM_CALIBRATION_READINGS; i++) {
//     baseline += analogRead(ANALOG_PIN);
//     delay(1000);  // Delay between readings
//   }
//   baseline /= NUM_CALIBRATION_READINGS;  // Average the readings to get the baseline

//   // TODO: Measure at known levels of activity and calculate scale factor
//   // This will be specific to your setup and how you can produce known levels of muscle activity
//   scale = 1.0;
// }
