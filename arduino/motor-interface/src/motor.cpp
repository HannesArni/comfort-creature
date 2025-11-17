#include <Arduino.h>

// class Motor
// {
// public:
//     int HALL_EFFECT_PIN;
//     int UP_PIN;
//     int DOWN_PIN;
//     int LIMIT_SWITCH;

//     boolean is_going_up = false;

//     int target_count = 0;
//     int count = 0;

//     int max_speed = 255;
//     int min_speed = 90;

//     boolean zero_toggle = false;

//     void perform_count() {
//         if (is_going_up)
//         {
//             count += 1;
//         }
//         else
//         {
//             count -= 1;
//         }
//     }

//     Motor(int hall_effect, int up_pin, int down_pin, int limit_switch)
//     {
//         HALL_EFFECT_PIN = hall_effect;
//         UP_PIN = up_pin;
//         DOWN_PIN = down_pin;
//         LIMIT_SWITCH = limit_switch;
//     }

//     void init(){
//         pinMode(HALL_EFFECT_PIN, INPUT);
//         pinMode(LIMIT_SWITCH, INPUT_PULLUP);
//         pinMode(UP_PIN, OUTPUT);
//         pinMode(DOWN_PIN, OUTPUT);
//     }

//     void go_up(int speed)
//     {
//         analogWrite(UP_PIN, speed);
//         analogWrite(DOWN_PIN, 0);
//         is_going_up = true;
//     }

//     void go_down(int speed)
//     {
//         analogWrite(DOWN_PIN, speed);
//         analogWrite(UP_PIN, 0);
//         is_going_up = false;
//     }

//     void stop()
//     {
//         analogWrite(UP_PIN, 0);
//         analogWrite(DOWN_PIN, 0);
//     }

//     void approach_target()
//     {
//         int distance = abs(target_count - count);

//         const int start_slowing = 10;

//         int speed = constrain(map(distance, 0, start_slowing, min_speed, max_speed), min_speed, max_speed);

//         if (count < target_count)
//         {
//             go_up(speed);
//         }
//         else if (count > target_count)
//         {
//             go_down(speed);
//         }
//         else
//         {
//             stop();
//         }
//     }

//     void check_zero(){
//         if(digitalRead(LIMIT_SWITCH) == 0 && !zero_toggle){
//             count = 0;
//             target_count = 0;
//             zero_toggle = true;
//             Serial.println("0 point set");
//         } else if(digitalRead(LIMIT_SWITCH) == 1 && zero_toggle){
//             zero_toggle = false;
//         }
//     }

// };

class Motor {
    public:
        int MOTOR_PIN;
        int HALL_PINS[3];

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
};