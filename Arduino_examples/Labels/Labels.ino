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
  long r2 = random(10, 20);
  long r3 = random(20, 30);
  long r4 = random(30, 40);
  long r5 = random(40, 50);

  Serial.print("First");
  Serial.print(r1);

  Serial.print("Second");
  Serial.print(r2*1.2);
  
  Serial.print("Third");
  Serial.print(r3);

  Serial.print("Fourth");
  Serial.print(r4);
  
  Serial.print("Fifth");
  Serial.print(r5);
/*
  long r6 = random(50, 60);
  Serial.print("Sight");
  Serial.print(r6);

  long r7 = random(60, 70);
  Serial.print("Seventh");
  Serial.print(r7);

  long r8 = random(70, 80);
  Serial.print("Label 8");
  Serial.print(r8/1.5);
  */
  Serial.println("Min:0, Max:100");

  delay(100);
}

