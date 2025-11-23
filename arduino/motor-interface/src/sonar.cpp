#include "sonar.h"
#include <Arduino.h>
#include <HCSR04.h>

const int TRIGGER_PIN = 11;
const int ECHO_PIN = 2;
UltraSonicDistanceSensor sonar_sensor(TRIGGER_PIN, ECHO_PIN);

unsigned long last_ultrasonic_reading = millis();

void maybe_read_sonar() {
    if(millis() - last_ultrasonic_reading > 1000){
        Serial.println("ULTRA: " + String(sonar_sensor.measureDistanceCm(20)) + "cm");
        last_ultrasonic_reading = millis();
    }
}
