#include <Servo.h>

Servo locker3, locker5;
int prevState = 123;

void setup() {
  locker3.attach(3);
  locker5.attach(5);
  pinMode(2, INPUT);
  pinMode(4, INPUT);
}

void loop() {
  int state2 = digitalRead(2);
  int state4 = digitalRead(4);

  int curState = 1 * state2 | 2 * state4;

  if( prevState != curState ){
    locker3.write( ( state2 + 1 ) * 90 );
    locker5.write( ( state4 + 1 ) * 90 );
    prevState = curState;
  }
}
