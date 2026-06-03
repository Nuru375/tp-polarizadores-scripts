#include <string.h>
#include <stdlib.h> 

#define BAUDRATE 19200
#define INPUT_BUFFER_SIZE 64

// ----MOTOR 1: A4988 PINS ----
#define PIN_EN     7
#define PIN_MS1    6
#define PIN_MS2    5
#define PIN_MS3    5 // Nota: MS2 y MS3 comparten el pin 5 en tu código original
#define PIN_RESET  3
#define PIN_SLEEP  3 // Nota: RESET y SLEEP comparten el pin 3 en tu código original
#define PIN_DIR    8
#define PIN_STEP   9

// ----MOTOR 2: DRV8825 PINS ----
#define PIN_EN2     2
#define PIN_STEP2   4

#define PIN_led    13

#define tiempo   40000
#define tiempo2  20000

char inputString[INPUT_BUFFER_SIZE];
bool stringComplete = false; 
uint8_t inputIndex = 0; 

void setup() {
  Serial.begin(BAUDRATE); 
  //analogReference(EXTERNAL); 
  DIDR0 = 0b00111111; // A0–A5 sin buffer digital para reducir ruido
  
  // --- MEJORA: Pre-setear estado HIGH (deshabilitado) antes de definir como OUTPUT ---
  // Esto evita que los drivers se activen momentáneamente durante el boot
  digitalWrite(PIN_EN, HIGH);
  digitalWrite(PIN_EN2, HIGH);
  digitalWrite(PIN_RESET, HIGH);
  digitalWrite(PIN_SLEEP, HIGH);

  pinMode(PIN_EN, OUTPUT);
  pinMode(PIN_MS1, OUTPUT);
  pinMode(PIN_MS2, OUTPUT);
  pinMode(PIN_MS3, OUTPUT);
  pinMode(PIN_RESET, OUTPUT);
  pinMode(PIN_SLEEP, OUTPUT);
  pinMode(PIN_DIR, OUTPUT);
  pinMode(PIN_STEP, OUTPUT);

  pinMode(PIN_EN2, OUTPUT);
  pinMode(PIN_STEP2, OUTPUT);

  pinMode(PIN_led, OUTPUT);
  digitalWrite(PIN_led, LOW);

  // Microstepping config (1/2 paso para motor 1)
  digitalWrite(PIN_MS1, HIGH);
  digitalWrite(PIN_MS2, LOW);
  digitalWrite(PIN_MS3, LOW);
 
  //stepMotor(1, 125, HIGH); // Gira 45/2 grados en sentido contrario (compensación)

  Serial.println("READY");
} 

void loop() {
  if (stringComplete) {
    processCommand(inputString); 
    clearBuffer();
  } 
}

void serialEvent() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      inputString[inputIndex] = '\0';
      stringComplete = true; 
      return; 
    }
    if (inputIndex < INPUT_BUFFER_SIZE - 1) {
      inputString[inputIndex++] = c;
    } 
  } 
} 

float readADC_avg() {
  analogRead(A0); // Limpiar buffer ADC
  float sum = 0; 
  for(int i=0; i<16; i++){ 
    sum += analogRead(A0); 
  } 
  return sum / 16;
}

void stepMotor(int motor, int steps, int direction) {
  if (steps <= 0) return; // No mover si los pasos son 0 o negativos

  digitalWrite(PIN_DIR, direction);
  switch (motor){
    case 1:
      digitalWrite(PIN_EN2, HIGH); // Asegurar que el otro motor esté libre
      digitalWrite(PIN_EN, LOW);   // Habilitar motor 1
      for (int i = 0; i < steps; i++) {
        digitalWrite(PIN_led, HIGH);
        digitalWrite(PIN_STEP, HIGH);
        delayMicroseconds(tiempo);
        digitalWrite(PIN_STEP, LOW);
        delayMicroseconds(tiempo);
        digitalWrite(PIN_led, LOW);
      }
      break;
    case 2:
      digitalWrite(PIN_EN, HIGH);  // Asegurar que el otro motor esté libre
      digitalWrite(PIN_EN2, LOW);  // Habilitar motor 2
      for (int i = 0; i < steps; i++) {
        digitalWrite(PIN_led, HIGH);
        digitalWrite(PIN_STEP2, HIGH);
        delayMicroseconds(tiempo2);
        digitalWrite(PIN_STEP2, LOW);
        delayMicroseconds(tiempo2);
        digitalWrite(PIN_led, LOW);
      }
      break;
  }
}

void processCommand(char *cmd) {
  if (cmd[0] == '\0') return;
  if (strcmp(cmd, "PING") == 0) {
    Serial.println("PONG"); 
    return; 
  }
  
  char localCmd[INPUT_BUFFER_SIZE];
  strncpy(localCmd, cmd, INPUT_BUFFER_SIZE); 
  localCmd[INPUT_BUFFER_SIZE - 1] = '\0'; 
    
  char *token = strtok(localCmd, "|"); 
  if (!token) { Serial.println("ERR"); return; } 
  int motor = atoi(token); 
    
  token = strtok(NULL, "|"); // ang_ini (ya no se usa para movimiento preliminar)
  if (!token) { Serial.println("ERR"); return; } 
  
  token = strtok(NULL, "|"); // ang_fin (no usado)
  if (!token) { Serial.println("ERR"); return; } 
   
  token = strtok(NULL, "|"); // paso (movimiento real deseado)
  if (!token) { Serial.println("ERR"); return; } 
  float paso = atof(token);
    
  token = strtok(NULL, "|"); 
  if (!token) { Serial.println("ERR"); return; } 
  char sentido = token[0]; 

  int dir = (sentido == 'H') ? HIGH : LOW;
    
  Serial.println("ACK"); 

  // --- CORRECCIÓN: Se eliminó el bloque que movía el motor a ang_ini ---
  // Ahora el motor solo ejecutará el movimiento especificado en 'paso'

  // Mover el motor la cantidad de pasos solicitada
  stepMotor(motor, (int)paso, dir);
  delay(200); // Pequeño delay para estabilización
          
  // Medición y respuesta
  float adc = readADC_avg();
  Serial.print("DATA|");
  Serial.print(motor);
  Serial.print("|1|");
  Serial.print(paso);
  Serial.print("|");
  Serial.println(adc, 2);

  Serial.println("DONE");
} 

void clearBuffer() { 
  memset(inputString, 0, INPUT_BUFFER_SIZE); 
  inputIndex = 0; 
  stringComplete = false; 
}