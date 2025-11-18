#include <Arduino.h>
#include "motor.cpp"
#include "command_processor.h"

Motor left_motor(5);
Motor right_motor(6);
CommandProcessor cmdProcessor(left_motor, right_motor);

String inputBuffer = "";

void setup() {
  left_motor.init();
  right_motor.init();

  Serial.begin(9600);
  Serial.println("Motor CLI ready");
  Serial.println("Type 'help' for available commands");
}

void loop() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();

    if (inChar == '\n' || inChar == '\r') {
      if (inputBuffer.length() > 0) {
        cmdProcessor.processCommand(inputBuffer);
        inputBuffer = "";
      }
    } else {
      inputBuffer += inChar;
    }
  }

  cmdProcessor.checkTimeout();

  delay(2);
}
