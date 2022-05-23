#include <Servo.h>
Servo myServo1; 
Servo myServo2;
Servo myServo3; 
Servo myServo4;
int i = 0;

int relay1 = 2;
int relay2 = 4;

int servo1 = 3;//cac chan pwm
int servo2 = 5;
int servo3 = 6;
int servo4 = 9;

int sensor0 = 10;
int sensor1 = 11;

int value0, value1, value2, value3;
int bangTai = 0;
String inString;
bool stringComplete = false;

void robotSetup(){
  myServo4.write(85);//90
  delay(1000);
  myServo3.write(60);
  delay(1000);
  myServo2.write(90);//120
  delay(1000);
  myServo1.write(85);//80
  delay(1000);
}

//============================================ < void Setup >
void setup() {
  Serial.begin(9600);

  myServo1.attach(servo1);
  myServo2.attach(servo2);
  myServo3.attach(servo3);
  myServo4.attach(servo4);
  
  pinMode(sensor0, INPUT);
  pinMode(sensor1, INPUT);
  pinMode(relay1, OUTPUT);
  pinMode(relay2, OUTPUT);
  digitalWrite(relay1,HIGH);
  digitalWrite(relay2,HIGH);

  robotSetup();
}
//===================================== dk robot
void robotWorking(int q){
  myServo2.write(120);
  delay(1000);
  myServo4.write(90);
  delay(1000);
  myServo4.write(105);//-----kep
  delay(500);
  myServo3.write(105);
  delay(1000);
  myServo1.write(q);//-----quay
  delay(1000);
  myServo4.write(85);
  delay(500);
  myServo1.write(85);
  delay(1000);
  myServo3.write(60);//ve vi tri
  delay(1000);
  myServo2.write(90);
  delay(1000);
}
//================================================================= < void Loop >
void loop() {
  //=====================================nhan data tu python
  if(Serial.available()){
    inString = Serial.readString();
    //-----------------------------------dieu khien bang tai
    if(inString == "startPow"){
      robotSetup();
      delay(1000);
      digitalWrite(relay1,LOW);
      bangTai = 1;
    }else if(inString == "stopPow"){
      digitalWrite(relay1,HIGH);
      bangTai == 0;
      robotSetup();
    }
    //---------------------------------dieu khien he thong chieu sang
    if(inString == "startLight"){
      digitalWrite(relay2,LOW);
    }else if(inString == "stopLight"){
      digitalWrite(relay2,HIGH);
      delay(1000);
    }
  }
  //------------------------------------------------------ <sensor>
  value0 = digitalRead(sensor0);
  if(value0==0 & bangTai==1){
    digitalWrite(relay1,HIGH);
    Serial.print("sensor0_on");
    delay(2000);
    digitalWrite(relay1,LOW);
    delay(700);
    digitalWrite(relay1,HIGH);
    Serial.print("sensor1_on");
    while(Serial.available()){
      //cho
    }
    inString = Serial.readString();
    if(inString=="RED"){
      robotWorking(85);
    }else if(inString=="GREEN"){
      robotWorking(115);
    }else if(inString=="YELLOW"){
      robotWorking(65);
    }
    digitalWrite(relay1,LOW);
  }
}
