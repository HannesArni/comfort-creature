#include <Arduino.h>

class Motor {
    public:
        int MOTOR_PIN;
        int HALL_PINS[3];
        int speed;

    Motor(int motor_pin) {
        MOTOR_PIN = motor_pin;
        // for (int i = 0; i < 3; i++) {
        //     HALL_PINS[i] = hall_pins[i];
        // }
    }

    void init() {
        pinMode(MOTOR_PIN, OUTPUT);
        // for (int i = 0; i < 3; i++) {
        //     pinMode(HALL_PINS[i], INPUT);
        // }
    }

    void set_speed(int input_speed) {
        analogWrite(MOTOR_PIN, input_speed);
        speed = input_speed;
    }
};
