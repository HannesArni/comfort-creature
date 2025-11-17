int LEFT_MOTOR_PIN = 5;
int RIGHT_MOTOR_PIN = 6;
bool is_going_up = true;
int min = 60;
int current_speed = min;
int max = 95;

int test_speed = 88;

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LEFT_MOTOR_PIN, OUTPUT);
  pinMode(RIGHT_MOTOR_PIN, OUTPUT);
  Serial.begin(9600);
//   analogWrite(LEFT_MOTOR_PIN, test_speed + 10);
//   analogWrite(RIGHT_MOTOR_PIN, test_speed + 20);
//   delay(500);

  analogWrite(LEFT_MOTOR_PIN, test_speed + 3);
  analogWrite(RIGHT_MOTOR_PIN, test_speed);

  delay(5000);
  analogWrite(LEFT_MOTOR_PIN, 0);
  analogWrite(RIGHT_MOTOR_PIN, 0);
}

// the loop function runs over and over again forever
void loop() {
//   analogWrite(LEFT_MOTOR_PIN, 80);
//   analogWrite(RIGHT_MOTOR_PIN, 80);
//   analogWrite(LEFT_MOTOR_PIN, current_speed);
//   analogWrite(RIGHT_MOTOR_PIN, max-current_speed);
  Serial.println(current_speed);
  if(is_going_up){
    current_speed++;
    if(current_speed == max){
      is_going_up = false;
    }
  } else {
    current_speed--;
    if(current_speed == min){
      is_going_up = true;
    }
  }
  delay(100);
}

