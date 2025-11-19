#include <Arduino.h>
#include "motor.cpp"
#include "command_processor.h"

int LEFT_HALL_SENSORS[3] ={10, 3, 4};
Motor left_motor("LEFT", 5, LEFT_HALL_SENSORS);
int RIGHT_HALL_SENSORS[3] ={9, 8, 7};
Motor right_motor("RIGHT",  6, RIGHT_HALL_SENSORS);

CommandProcessor cmdProcessor(left_motor, right_motor);

String inputBuffer = "";

void interrupt_test() {
    Serial.println("Interrupt");
}

void setup() {
    left_motor.init();
    right_motor.init();

//     for (int i = 0; i < 3; i++) {
//         attachInterrupt(digitalPinToInterrupt(left_motor.HALL_PINS[i]), interrupt_test, RISING);
//     }

  Serial.begin(115200);
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

//  cmdProcessor.checkTimeout();
  left_motor.check_halls();
  right_motor.check_halls();

  delay(2);
}
