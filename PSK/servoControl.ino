#include <Servo.h>

// 사물함과 연결된 서보모터, 초기상태
Servo locker3, locker5;
int prevState = 123;

// LED에 연결된 핀들을 input으로 설정, 서보모터 초기화
void setup() {
  locker3.attach(3);
  locker5.attach(5);
  pinMode(2, INPUT);
  pinMode(4, INPUT);
}

void loop() {
  int state2 = digitalRead(2);
  int state4 = digitalRead(4);

  // HIGH == 1, LOW == 0 이기 때문에 가능한 연산이다. 서보모터에 무한 명령을 방지한다.
  int curState = 1 * state2 | 2 * state4;
  
  // HIGH == 180 열기, LOW == 90 닫기
  if( prevState != curState ){
    locker3.write( ( state2 + 1 ) * 90 );
    locker5.write( ( state4 + 1 ) * 90 );
    prevState = curState;
  }
}
