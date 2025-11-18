#ifndef COMMAND_PROCESSOR_H
#define COMMAND_PROCESSOR_H

#include <Arduino.h>

class CommandProcessor {
private:
  Motor& left_motor;
  Motor& right_motor;
  unsigned long lastCommandTime;
  static const unsigned long TIMEOUT_MS = 1000;

public:
  CommandProcessor(Motor& left, Motor& right)
    : left_motor(left), right_motor(right), lastCommandTime(0) {}

  void processCommand(String command) {
    lastCommandTime = millis();
    command.trim();

    if (command.length() == 0) {
      return;
    }

    int spaceIndex = command.indexOf(' ');
    String cmd;
    String params;

    if (spaceIndex == -1) {
      cmd = command;
      params = "";
    } else {
      cmd = command.substring(0, spaceIndex);
      params = command.substring(spaceIndex + 1);
    }

    cmd.toLowerCase();

    if (cmd == "left") {
      int speed = params.toInt();
      left_motor.set_speed(speed);
      Serial.print("Left motor speed set to: ");
      Serial.println(speed);
    }
    else if (cmd == "right") {
      int speed = params.toInt();
      right_motor.set_speed(speed);
      Serial.print("Right motor speed set to: ");
      Serial.println(speed);
    }
    else if (cmd == "both") {
      int speed = params.toInt();
      left_motor.set_speed(speed);
      right_motor.set_speed(speed);
      Serial.print("Both motors speed set to: ");
      Serial.println(speed);
    }
    else if (cmd == "stop") {
      left_motor.set_speed(0);
      right_motor.set_speed(0);
      Serial.println("Both motors stopped");
    }
    else if (cmd == "status") {
      Serial.print("Left motor: ");
      Serial.println(left_motor.speed);
      Serial.print("Right motor: ");
      Serial.println(right_motor.speed);
    }
    else if (cmd == "help") {
      Serial.println("Available commands:");
      Serial.println("  left <speed>   - Set left motor speed");
      Serial.println("  right <speed>  - Set right motor speed");
      Serial.println("  both <speed>   - Set both motors speed");
      Serial.println("  stop           - Stop both motors");
      Serial.println("  status         - Show current motor speeds");
      Serial.println("  help           - Show this help message");
    }
    else {
      Serial.print("Unknown command: ");
      Serial.println(cmd);
      Serial.println("Type 'help' for available commands");
    }
  }

  void checkTimeout() {
    if (millis() - lastCommandTime > TIMEOUT_MS) {
      if (left_motor.speed != 0 || right_motor.speed != 0) {
        left_motor.set_speed(0);
        right_motor.set_speed(0);
        Serial.println("Timeout: Motors stopped");
        lastCommandTime = millis();
      }
    }
  }
};

#endif
