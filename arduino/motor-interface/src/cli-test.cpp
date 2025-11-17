#include <Arduino.h>
#include "motor.cpp"


Motor left_motor(5, {2, 3, 10});
Motor right_motor(6, {7, 8, 9});

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  left_motor.init();
  right_motor.init();
  attachInterrupt(digitalPinToInterrupt(2), interrupt, RISING);
  pinMode(2, INPUT);
  Serial.begin(9600);
}

// the loop function runs over and over again forever
void loop() {
  Serial.println(digitalRead(2));
  delay(1000);
}

void interrupt() {
    Serial.println("Hello");
}
