/*
 * Copyright 20.02.2021 Tauno Erik
 */


void setup() {
  Serial.begin(115200);

  randomSeed(analogRead(0));
}

void loop() {
  // print a random numbers
  long r1 = random(10);
  Serial.print(r1);
  Serial.print("_");

  long r2 = random(10, 20);
  Serial.print(r2*1.2);
  Serial.print(",");

  long r3 = random(20, 30);
  Serial.print(r3);
  Serial.print(".");

  long r4 = random(30, 40);
  Serial.print(r4);
  Serial.print("a");

  long r5 = random(40, 50);
  Serial.print(r5);
  Serial.print(":");

  long r6 = random(50, 60);
  Serial.print(r6);
  Serial.print(";");

  long r7 = random(60, 70);
  Serial.print(r7);
  Serial.print("!");

  long r8 = random(70, 80);
  Serial.print(r8/1.5);
  
  Serial.println("Min:0, Max:100");

  delay(100);
}
