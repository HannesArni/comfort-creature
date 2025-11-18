#include <Arduino.h>

class Motor {
    public:
        String NAME;
        int MOTOR_PIN;
        int HALL_PINS[3];
        bool LAST_HALL_STATE[3];
        int speed;

    Motor(String name, int motor_pin, int hall_pins[3]) {
        NAME = name;
        MOTOR_PIN = motor_pin;
        for (int i = 0; i < 3; i++) {
            HALL_PINS[i] = hall_pins[i];
        }
    }

    void init() {
        pinMode(MOTOR_PIN, OUTPUT);
        for (int i = 0; i < 3; i++) {
            pinMode(HALL_PINS[i], INPUT_PULLUP);
        }
    }

    void set_speed(int input_speed) {
        analogWrite(MOTOR_PIN, input_speed);
        speed = input_speed;
    }

    int last_hall_pin;
    int current_count = 0;
    unsigned long last_rise;

    void check_halls() {
        for(int i = 0; i < 3; i++){
            bool is_up = digitalRead(HALL_PINS[i]);
            if(LAST_HALL_STATE[i] != is_up) {
                if(is_up) {
                    on_hall_rise(i);
                }
                LAST_HALL_STATE[i] = is_up;
            }
        }
    }

    bool is_going_forward(int pin_index) {
        // descending
        if(last_hall_pin == 0 && pin_index == 2){
            return false;
        }
        if(last_hall_pin == 2 && pin_index == 0){
            return true;
        }
        return last_hall_pin < pin_index;
    }

    void on_hall_rise(int pin_index) {
        if(is_going_forward(pin_index)){
            current_count++;
        } else {
            current_count--;
        }

        unsigned long now = millis();
        Serial.println(NAME + ": " + " count: " + current_count + " dt: " + String(now - last_rise));
        last_hall_pin = pin_index;
        last_rise = now;
    }
};
