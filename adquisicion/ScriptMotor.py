# -*- coding: utf-8 -*-
"""
Created on Wed May 6 2026
@author: O. Umedez, Agustin
Control de motores paso a paso y adquisición ADC
"""

import serial
import time
import csv
from tools import generar_proximo_nombre


# --- Configuración ---
PUERTO    = 'COM11'  # Ajustar según tu PC
BAUD_RATE = 19200
TIMEOUT   = 2
ARCHIVO_DESTINO = generar_proximo_nombre(
    directorio=r"datos",
    descripcion="",
    prefijo="mediciones_",
    extension=".csv"
)

# Resoluciones de los motores (grados/micropaso) 
RES_MOT1 = 360 / 2000 # 0.18°/micropaso
RES_MOT2 = 360 / 2300 # 0.156°/micropaso

# --- Parámetros del experimento (en GRADOS) ---
# Acá es donde vas a pasar la mayor parte del tiempo
MOT1 = {'inicio': 0, 'final': 360, 'paso': 5, 'sentido': 'H'}
MOT2 = {'inicio': 0, 'final': 0, 'paso': 5, 'sentido': 'H'}

def select_fast_motor():
    info = """
El motor rápido es aquel que gira todo 
su recorrido en cada paso del motor lento.
    
    1: motor 1 (carcasa negra)
    2: motor 2 (carcasa blanca)

Elija cuál desea configurar como motor rápido.
    """ # Modificar según su propio setup
    while True:
        try:
            print(info)
            us_input = input(">> ")
            fast_motor = int(us_input)
            if fast_motor not in [1, 2]: raise ValueError
            break
            
        except KeyboardInterrupt:
            fast_motor = 1
            break
            
        except ValueError:
            print("Seleccione una opción válida.")
            time.sleep(1)
            continue
        
    print(f"El motor rápido será el Motor {fast_motor}.")
    return fast_motor

def configurar_puerto():
    """
    Aplica la conexión al puerto serie con la configuración definida y
    corrobora la comunicación con Arduino con el protocolo PING/PONG.
    """
    # Configuración del puerto con DTR/RTS para asegurar control
    arduino = serial.Serial(PUERTO, BAUD_RATE, timeout=TIMEOUT)
    arduino.dtr = True
    arduino.rts = True
    time.sleep(3) # Esperar reset de Arduino
    
    # Limpiamos el buffer de registros viejos
    arduino.reset_input_buffer()

    # Handshake PING/PONG
    arduino.write(b"PING\n")
    respuesta = arduino.readline().decode('utf-8').strip()
    if "PONG" not in respuesta:
        print(f"Error: Arduino no respondió PONG. Recibido: {respuesta}")
        return
    
    print("Conexión exitosa.")
    return arduino

def enviar_comando(ser, motor, ang_ini, paso, sentido):
    """
    Formatea el comando y espera el flujo ACK -> DATA -> DONE del Arduino.
    """
    # Conversión de grados a pasos enteros antes de enviar
    res = RES_MOT1 if motor == 1 else RES_MOT2
    steps_ini = int(round(ang_ini / res))
    steps_paso = int(round(paso / res))
    
    # Formato: motor|ang_ini|ang_fin|paso|sentido\n (ang_fin no se usa en este firmware)
    cmd = f"{motor}|{steps_ini}|0|{steps_paso}|{sentido}\n"
    ser.write(cmd.encode('utf-8'))
    
    data_received = None
    
    # Gestionar la respuesta del Arduino
    while True:
        line = ser.readline().decode('utf-8').strip()
        if not line: continue
        
        if "ACK" in line:
            continue # Comando aceptado
        elif line.startswith("DATA"):
            # DATA|motor|index|paso|adc
            data_received = line.split('|')
        elif "DONE" in line:
            return data_received # Fin del movimiento
        elif "ERR" in line:
            print(f"Error de Arduino: {line}")
            return


def ejecutar_experimento():
    print(f"Estableciendo conexión en {PUERTO}...")
    
    try:
        arduino = configurar_puerto()

        # Preparamos archivo CSV donde se almacenarán los datos
        with open(ARCHIVO_DESTINO, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Tiempo (s)", "Motor", "Angulo_Deg", "ADC"])
            
            t_inicio = time.perf_counter()

            # Movemos a posiciones iniciales
            enviar_comando(arduino, 1, MOT1['inicio'], 0, MOT1['sentido'])
            enviar_comando(arduino, 2, MOT2['inicio'], 0, MOT2['sentido'])
            
            # --- Cálculo de iteraciones ---
            # Se calcula la cantidad de pasos necesarios para cada motor basándose en el rango y el paso
            n_pasos_1 = int(round((MOT1['final'] - MOT1['inicio']) / MOT1['paso']))
            n_pasos_2 = int(round((MOT2['final'] - MOT2['inicio']) / MOT2['paso']))
            
            # --- Ejecución adaptativa ---
            # Se adapta para los dos usos posibles del script:
            # 1. Barrido anidado
            # 2. Giro exclusivo de un motor
            if n_pasos_1 and n_pasos_2: # CASO 1: Barrido anidado
                print("Detectado barrido anidado")
                time.sleep(1)
                
                if (fast := select_fast_motor()) == 1:
                    fast_mot, fast_steps = MOT1, n_pasos_1
                    slow_mot, slow_steps, slow = MOT2, n_pasos_2, 2
                else: # fast == 2
                    fast_mot, fast_steps = MOT2, n_pasos_2
                    slow_mot, slow_steps, slow = MOT1, n_pasos_1, 1
                
                for i in range(slow_steps + 1):
                    for j in range(fast_steps):
                        # Comando para el Motor Rápido (Fast Scan)
                        res = enviar_comando(arduino, fast, 0, fast_mot['paso'], fast_mot['sentido'])
                        
                        if res:
                            t_rel = time.perf_counter() - t_inicio
                            
                            # Calculamos el ángulo real acumulado para el Motor
                            fast_ang = fast_mot['inicio'] + (j + 1) * fast_mot['paso']
                            
                            print(f"t: {t_rel:6.3f}s | Mot {fast} | Ang: {fast_ang:6.2f}° | ADC: {res[4]}")
                            
                            # Registro de datos: Tiempo, ID Motor, Ángulo, ADC
                            writer.writerow([f"{t_rel:.3f}", res[1], fast_ang, res[4]])
                            file.flush() # Asegura la escritura inmediata en disco
                            
                    # Avanzar el Motor Lento (Slow Scan) al finalizar cada barrido del Motor Rápido
                    if i < fast_steps:
                        enviar_comando(arduino, slow, 0, slow_mot['paso'], slow_mot['sentido'])
                        slow_ang = slow_mot['inicio'] + (i + 1) * slow_mot['paso']
                        print(f"--- Motor {slow} avanzó a {slow_ang}° ---")
            
            else: # CASO 2: Giro exclusivo de uno de los motores
                if n_pasos_2 == 0:
                    mot, mot_pasos, mot_n = MOT1, n_pasos_1, 1
                else: # n_pasos_1 == 0
                    mot, mot_pasos, mot_n = MOT2, n_pasos_2, 2
                
                print(f"Detectado giro exclusivo de Motor {mot_n}: de {mot['inicio']}° a {mot['final']}°")
                
                for i in range(mot_pasos):
                    # Movemos Motor (paso a paso) y recibimos la cadena DATA del Arduino
                    res = enviar_comando(arduino, mot_n, 0, mot['paso'], mot['sentido'])
                    
                    if res:    
                        t_rel = time.perf_counter() - t_inicio
                        ang_actual = mot['inicio'] + (i + 1) * mot['paso']
                        
                        print(f"t: {t_rel:6.3f}s | Mot {mot_n} | Ang: {ang_actual:6.2f}° | ADC: {res[4]}")
                        
                        writer.writerow([f"{t_rel:.3f}", res[1], ang_actual, res[4]])
                        file.flush()

    except Exception as e:
        print(f"Error en el sistema: {e}")
        
    except KeyboardInterrupt:
        print("\nFinalizando captura y liberando equipo...")
        
    finally:
        print(f"\n--- Datos guardados en {ARCHIVO_DESTINO} ---")
        print("\nDesea cerrar el puerto serie? Escriba 0 o 1.")
        print("0: NO")
        print("1: SI")
        
        try:
            us_input = input(">> ")
            choice = int(us_input)
        
        except ValueError:
            print("ERROR: Se ingresó una respuesta no válida. Se cerrará el puerto preventivamente.")
            choice = 1
        
        finally:
            if choice and arduino.is_open:
                arduino.close()
                print("Puerto cerrado.")
            else:
                print("El puerto serie no está abierto.")


if __name__ == "__main__":
    ejecutar_experimento()
