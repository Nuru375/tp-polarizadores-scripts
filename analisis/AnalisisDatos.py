# -*- coding: utf-8 -*-
"""
Created on Wed May  6 17:38:43 2026
@author: O. Umedez, Agustin
Análisis de los datos recolectados
"""

import numpy as np
import pandas as pd
import MatricesJones as mj
from adquisicion.tools import ultimo_archivo
from plots import MP_polar_plot, MP_polar_plot_2


# --- CONFIGURACIÓN GENERAL DEL EXPERIMENTO ---

# Rutas y archivos
DIR_DATOS = r"datos"
PREFIJO_ARCHIVOS = "mediciones_"
EXT_ARCHIVOS = ".csv"

# Parámetros del ajuste para convertir las lecturas de ADC en Volts
# Se asume ajuste de la forma: y = b*x + a
ADC_to_VOLT__a = -5.6187
ADC_to_VOLT__b = 0.2034

# Configuración estética de las gráficas
PLOT_ARGS_MEDICIONES = {
    'marker':       '*',
    'markersize':   2,
    'linestyle':    '-',
    'linewidth':    1.2,
    'color':        'black',
    'alpha':        0.9
}

PLOT_ARGS_TEORIA = {
    'linestyle':    '-',
    'linewidth':    1.2,
    'alpha':        0.7
}


# --- FUNCIONES DE PROCESAMIENTO Y FÍSICA ---

def cargar_y_procesar_datos():
    """Busca el último archivo CSV de medición y normaliza las unidades físicas."""
    # Aquí se utiliza una función muy conveniente para ir viendo los datos a medida que
    # se mide. Si, por el contrario, se desea ver una medición en particular,
    # puede comentar esta linea y escribir debajo la ruta a la medición que desea.
    # ej: root = r"datos/mediciones_3_ejemplo.csv"
    root = ultimo_archivo(directorio=DIR_DATOS, prefijo=PREFIJO_ARCHIVOS, extension=EXT_ARCHIVOS)
    df = pd.read_csv(root)
    
    # Conversiones
    df['Angulo_Rad'] = df['Angulo_Deg'] * np.pi / 180
    df['Intensidad'] = (df['ADC'] - ADC_to_VOLT__a) / ADC_to_VOLT__b
    
    return df


# --- FUNCIONES DE GRAFICADO ---

def graficar_modo_exclusivo(df, tita, alpha):
    """Grafica el comportamiento para un barrido continuo sin separación de ciclos."""
    angulo = df['Angulo_Rad']
    intensidad_norm = df['Intensidad'] / np.max(df['Intensidad'])
    
    # Inicializamos la lista de datos a plotear con la medición experimental
    datos_grafica = [(angulo, intensidad_norm, 'Mediciones', PLOT_ARGS_MEDICIONES)]
    
    # Constantes específicas de este modelo
    offset_rad = -7 * np.pi / 180
    phi_rad = np.pi / 2
    
    for p in np.arange(0, 180, 5):
        psi_rad = p * np.pi / 180
        
        for a in alpha:
            # Estado de polarización de entrada
            E_in = np.array([np.cos(a), np.sin(a)])

            # Propagación por los elementos ópticos
            pol1  = mj.lp(E_in, phi_rad)
            pol2  = mj.compensador(pol1, tita - offset_rad, delta=np.pi/12)
            E_out = mj.lp(pol2, psi_rad)

            # Cálculo de la intensidad total
            Ex = E_out[:, 0, 0]
            Ey = E_out[:, 1, 0]
            I_out = np.abs(Ex)**2 + np.abs(Ey)**2
            
            etiqueta = fr'$\phi: {phi_rad*180/np.pi:.0f}^\circ$, $\alpha: {a*180/np.pi:.0f}^\circ$, $\psi: {psi_rad*180/np.pi:.0f}^\circ$'
            datos_grafica.append((tita, I_out, etiqueta, PLOT_ARGS_TEORIA))
            
        print(f'Offset: {offset_rad*180/np.pi:.0f}°')
        
        # Grafica la familia de curvas y reinicia la lista conservando solo la medición
        MP_polar_plot(*datos_grafica)
        datos_grafica = [(angulo, intensidad_norm, 'Mediciones', PLOT_ARGS_MEDICIONES)]

def graficar_modo_fast_slow(df, tita, alpha):
    """Segmenta los ciclos midiendo cambios bruscos en el ángulo y grafica el modo combinado."""
    # Identificación de ciclos: marca True cuando el motor da la vuelta (caída abrupta de grados)
    nuevo_ciclo = df['Angulo_Deg'] < df['Angulo_Deg'].shift(1)
    df['id_segmento'] = nuevo_ciclo.cumsum()
    
    # Agrupamos en una lista de tuplas (ID del segmento, DataFrame del segmento)
    segmentos = df.groupby('id_segmento')
    
    paso_slow_mot = 2 * np.pi / (df['id_segmento'].iloc[-1] + 1)
    max_intensidad_global = np.max(df['Intensidad'])
    datos_grafica = []
    
    for id_seg, df_seg in segmentos:
        angulo = df_seg['Angulo_Rad']
        intensidad_norm = df_seg['Intensidad'] / max_intensidad_global
        
        datos_grafica.append((angulo, intensidad_norm, id_seg, 'Mediciones', PLOT_ARGS_MEDICIONES))
        
        # Constantes específicas de este modelo
        offset_rad = 47 * np.pi / 180
        phi_rad = np.pi / 2
        
        # Tita dinámico según el ciclo
        fast_tita = tita - offset_rad
        slow_tita = paso_slow_mot * (id_seg + 1) - 0.14
        # Acá sumamos 1 al id para que no arranque en cero
        
        for a in alpha:
            # Estado de polarización de entrada
            E_in = np.array([np.cos(a), np.sin(a)])

            # Propagación por los elementos ópticos
            pol1  = mj.lp(E_in, phi_rad)
            pol2  = mj.compensador(pol1, fast_tita, delta=np.pi/12)
            E_out = mj.lp(pol2, slow_tita)

            # Cálculo de la intensidad total
            Ex = E_out[:, 0, 0]
            Ey = E_out[:, 1, 0]
            I_out = np.abs(Ex)**2 + np.abs(Ey)**2
            
            # Puede que quede apretado mostrando tantos ángulos.
            # Dado que nuestro set-up consistía de un polarizador lineal fijo a 90 grados,
            # en ocaciones nos tomamos la libertad de omitir mostrar en el plot
            # el ángulo phi, que corresponde a dicho polarizador lineal que no gira.
            etiqueta = fr'$\phi: {phi_rad*180/np.pi:.0f}^\circ$, $\alpha: {a*180/np.pi:.0f}^\circ$, $\psi: {slow_tita*180/np.pi:.0f}^\circ$'
            datos_grafica.append((tita, I_out, id_seg, etiqueta, PLOT_ARGS_TEORIA))
            
        print(f'Offset: {offset_rad*180/np.pi:.0f}°')
    
    # Disparar gráfico final en grilla
    MP_polar_plot_2((1, 3), *datos_grafica)


# --- PUNTO DE ENTRADA PRINCIPAL ---

def main():
    # Variables de control teóricas
    tita = np.linspace(0, 2*np.pi, 100)
    alpha = np.linspace(0, np.pi/2, 4)
    
    # Carga de datos
    df = cargar_y_procesar_datos()
    
    # Ruteo según volumen de datos
    if len(df['Angulo_Deg']) > (360 / 5):
        print(">> Ejecutando análisis en modo: Fast-Slow")
        graficar_modo_fast_slow(df, tita, alpha)
    else:
        print(">> Ejecutando análisis en modo: Exclusivo")
        graficar_modo_exclusivo(df, tita, alpha)

if __name__ == '__main__':
    main()

