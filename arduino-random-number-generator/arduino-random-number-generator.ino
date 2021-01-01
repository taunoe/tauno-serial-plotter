
void setup() {
  Serial.begin(115200);

  randomSeed(analogRead(0));
}

void loop() {
  // print a random number from 0 to 299
  long r1 = random(10);
  Serial.print(r1);
  Serial.print("_");

  long r2 = random(10, 20);
  Serial.print(r2);
  Serial.print("_");

  long r3 = random(20, 30);
  Serial.print(r3);
  Serial.print("_");

  long r4 = random(30, 40);
  Serial.print(r4);
  Serial.print("_");

  long r5 = random(40, 50);
  Serial.print(r5);
  Serial.print("_");

  long r6 = random(50, 60);
  Serial.print(r6);
  Serial.print("_");

  long r7 = random(60, 70);
  Serial.print(r7);
  Serial.print("_");

  long r8 = random(70, 80);
  Serial.println(r8);

  delay(200);
}
