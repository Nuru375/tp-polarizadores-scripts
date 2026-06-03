# -*- coding: utf-8 -*-
"""
Created on Thu May 21 19:19:17 2026
@author: Agustin O. Umedez
Commonly used plots
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import plotly.graph_objects as go

def graf_doble(datos, ajuste=[], ejes=['x', ['y1', 'y2']]):
    """
    Para 'datos' y 'ajuste':
    - datos[0]: superior
    - datos[1]: inferior
    - datos[0][0]: x
    - datos[0][1]: y
    - datos[0][2]: label
    
    Para 'ejes':
    - ejes[0]: x
    - ejes[1][0]: y superior
    - ejes[1][1]: y inferior
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
    
    if ajuste:
        ax1.plot(ajuste[0][0], ajuste[0][1], 'r', label=ajuste[0][2])
        ax2.plot(ajuste[1][0], ajuste[1][1], 'r', label=ajuste[1][2])
    
    ax1.plot(datos[0][0], datos[0][1], 'bo', markersize=6, label=datos[0][2])
    ax1.set_ylabel(ejes[1][0])
    ax1.grid(True)
    ax1.legend(fontsize=13)
    
    ax2.plot(datos[1][0], datos[1][1], 'b^', markersize=6, label=datos[1][2])
    ax2.set_xlabel(ejes[0])
    ax2.set_ylabel(ejes[1][0])
    ax2.grid(True)
    ax2.legend(fontsize=13)
    
    plt.tight_layout()
    plt.show()
    return

def graf_simple(datos, ajuste=[], ejes=['x', 'y']):
    """
    Para 'datos' y 'ajuste':
    - datos[0]: x
    - datos[1]: y
    - datos[2]: label
    
    Para 'ejes':
    - ejes[0]: x
    - ejes[1]: y
    """
    plt.figure()
    
    if ajuste:
        plt.plot(ajuste[0], ajuste[1], 'r', label=ajuste[2])
    plt.plot(datos[0], datos[1], 'bo', markersize=6, label=datos[2])
    
    plt.xlabel(ejes[0])
    plt.ylabel(ejes[1])
    
    plt.grid(True)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()
    return

def MP_polar_plot(*data):
    """
    Se asume que cada input 'data' tiene la siguiente forma:
    x: datos polares
    y: datos radiales
    
    (x, y, n, label, plot_args)
    """
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    
    # for n, val in enumerate(kwargs.values()):
    for d in data:
        x, y, label, args = d
        ax.plot(x, y, label=label, **args)
    
    angles_deg = np.arange(0, 360, 45)
    labels = ['0', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$', r'$\frac{3\pi}{4}$',
              r'$\pi$', r'$\frac{5\pi}{4}$', r'$\frac{3\pi}{2}$', r'$\frac{7\pi}{4}$']
    ax.set_thetagrids(angles_deg, labels=labels)
    
    ax.grid(which='major', color='dimgray', linestyle='-', linewidth=0.9, alpha=0.9)

    ax.xaxis.set_minor_locator(ticker.MultipleLocator(np.pi/16))
    ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)
    
    ax.set_rlabel_position(0)
    
    ax.tick_params(axis='x', which='major', pad=10, labelsize=12)
    
    for label in ax.get_yticklabels():
        label.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.6, pad=0.5))
    
    # Definimos los límites y divisiones del radio
    
    # Escala personalizada
    # rmax = 0.06
    # rticks = np.linspace(0,0.06,3)
    # Escala normal
    rmax = 1.0
    rticks = [0.2, 0.4, 0.6, 0.8, 1.0]
    
    ax.set_rmax(rmax)
    ax.set_rticks(rticks)
    ax.set_yticklabels([str(i) for i in rticks], fontsize=10,
                       horizontalalignment='center', verticalalignment='top')
    
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3,
              frameon=True, edgecolor='black', fontsize=9)
    
    plt.tight_layout()
    plt.show()


def MP_polar_plot_2(grid, *datasets):
    """
    Parámetros:
    -----------
    grid : tupla (filas, columnas). Ej: (2, 2)
    *datasets : cantidad variable de datos a graficar. 
                Cada dataset debe ser una tupla con la siguiente estructura:
                (x, y, n, label, plot_args)
                
                - x, y: arreglos de datos polares y radiales.
                - n: identificador (int o string). Curvas con el mismo 'n' 
                     van al mismo subplot.
                - label: string para la leyenda.
                - plot_args: diccionario con kwargs de plt.plot (color, marker, etc).
    """
    f, c = grid
    
    # Creamos la grilla. Ajustamos el tamaño dinámicamente según filas y columnas
    fig, axs = plt.subplots(f, c, figsize=(5*c, 5*f), subplot_kw={'projection': 'polar'})
    
    # TRUCO 1: Aplanamos el arreglo de ejes. 
    # Esto transforma una matriz 2x2 en una lista 1D [ax1, ax2, ax3, ax4]
    # garantizando el orden: izquierda a derecha, de arriba a abajo.
    # np.atleast_1d evita errores si la grilla es (1,1)
    axs = np.atleast_1d(axs).flatten()
    
    # TRUCO 2: Diccionario para recordar qué subplot le tocó a cada identificador 'n'
    mapa_n_a_eje = {}
    indice_subplot_actual = 0
    
    # --- PASADA 1: Mapeo de subplots base ---
    for data in datasets:
        n = data[2]
        
        # Ignoramos temporalmente los datasets que van a múltiples gráficos
        if n == 'all' or isinstance(n, (list, tuple)):
            continue
            
        # Asignamos un nuevo subplot si el identificador no existe
        if n not in mapa_n_a_eje:
            if indice_subplot_actual >= len(axs):
                raise ValueError(f"La grilla {grid} es muy chica para tantos identificadores base distintos.")
            
            mapa_n_a_eje[n] = axs[indice_subplot_actual]
            indice_subplot_actual += 1

    # --- PASADA 2: Graficado ---
    for data in datasets:
        x, y, n, label, plot_args = data
        
        if n == 'all':
            # Graficar en todos los subplots activos
            for ax in mapa_n_a_eje.values():
                ax.plot(x, y, label=label, **plot_args)
                
        elif isinstance(n, (list, tuple)):
            # Graficar solo en los subplots solicitados en la lista
            for sub_n in n:
                if sub_n in mapa_n_a_eje:
                    mapa_n_a_eje[sub_n].plot(x, y, label=label, **plot_args)
                else:
                    print(f"Advertencia: El identificador '{sub_n}' no tiene un subplot base asignado. Ignorando curva '{label}' para este eje.")
                    
        else:
            # Graficado normal
            ax = mapa_n_a_eje[n]
            ax.plot(x, y, label=label, **plot_args)
        
    # --- CONFIGURACIÓN FINAL ---
    for ax in mapa_n_a_eje.values():
        # ax.legend()
        pass
        
    # Ocultar los subplots que no se usaron
    for i in range(indice_subplot_actual, len(axs)):
        axs[i].set_visible(False)
        
    angles_deg = np.arange(0, 360, 45)
    labels = ['0', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$', r'$\frac{3\pi}{4}$',
              r'$\pi$', r'$\frac{5\pi}{4}$', r'$\frac{3\pi}{2}$', r'$\frac{7\pi}{4}$']
    
    for ax in mapa_n_a_eje.values():
        ax.set_thetagrids(angles_deg, labels=labels)
        
        ax.grid(which='major', color='dimgray', linestyle='-', linewidth=0.9, alpha=0.9)
    
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(np.pi/16))
        ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.5)
        
        ax.set_rlabel_position(0)
        
        ax.tick_params(axis='x', which='major', pad=12, labelsize=12)
        ax.tick_params(axis='y', direction='out', pad=10)
        
        for label in ax.get_yticklabels():
            label.set_bbox(dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.5))
        
        # Definimos los límites y divisiones del radio
        
        # Escala personalizada
        rmax = 0.06
        rticks = np.linspace(0,0.06,3)
        # Escala normal
        # rmax = 1.0
        # rticks = [0.2, 0.4, 0.6, 0.8, 1.0]
        
        ax.set_rmax(rmax)
        ax.set_rticks(rticks)
        ax.set_yticklabels([str(i) for i in rticks], fontsize=10,
                           horizontalalignment='center', verticalalignment='top')
        
        # ax.set_axisbelow(False)

        
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.17), ncol=3,
                  frameon=True, edgecolor='black', fontsize=8)
        
    plt.tight_layout()
    plt.show()


def PL_polar_plot(*data):
    """
    Parámetros:
    -----------
    *data : Tuplas con la forma (x, y, label, args)
            - x: arreglo de datos polares en RADIANES.
            - y: arreglo de datos radiales.
            - label: string para la leyenda.
            - args: diccionario con configuraciones de línea de Plotly 
                    (ej: {'line': dict(color='blue', width=2)})
    """
    
    # Inicializamos la figura de Plotly
    fig = go.Figure()

    # --- PASO 1: Agregar las curvas ---
    for d in data:
        x, y, label, args = d
        
        # go.Scatterpolar es el equivalente a ax.plot para coordenadas polares
        fig.add_trace(go.Scatterpolar(
            r=y,
            theta=x,
            thetaunit='radians', # Le indicamos explícitamente que 'x' viene en radianes
            mode='lines',
            name=label,
            **args 
        ))

    # --- PASO 2: Configurar las etiquetas angulares ---
    # Definimos dónde irán las marcas (en radianes) y qué texto mostrarán
    tick_vals = [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi, 5*np.pi/4, 3*np.pi/2, 7*np.pi/4]
    tick_texts = ['0', 'π/4', 'π/2', '3π/4', 'π', '5π/4', '3π/2', '7π/4']

    # --- PASO 3: Configurar el Layout (Diseño) ---
    fig.update_layout(
        polar=dict(
            bgcolor='white', # Fondo del gráfico limpio
            
            # Configuración del eje Angular (θ)
            angularaxis=dict(
                tickmode='array',
                tickvals=tick_vals,
                ticktext=tick_texts,
                direction='counterclockwise',
                gridcolor='dimgray',   # Color de la grilla principal
                gridwidth=1,           # Grosor de la grilla principal
                linecolor='black',     # Borde exterior del círculo
                tickfont=dict(size=14, color='black')
            ),
            
            # Configuración del eje Radial (r)
            radialaxis=dict(
                tickmode='array',
                tickvals=[0.2, 0.4, 0.6, 0.8, 1.0],
                ticktext=['0.2', '0.4', '0.6', '0.8', '1.0'],
                range=[0, 1.0],        # Límites del radio (rmax)
                angle=0,               # ¡Esto clava los números en la línea de 0 grados!
                gridcolor='lightgray', # Grilla radial más tenue
                gridwidth=1,
                tickfont=dict(size=12, color='black'),
                tickangle=0            # Mantiene los números derechos, sin rotar
            )
        ),
        
        # --- PASO 4: Configurar la Leyenda ---
        legend=dict(
            orientation="h",           # Leyenda horizontal
            yanchor="top",
            y=-0.1,                    # Posición por debajo del gráfico
            xanchor="center",
            x=0.5,
            bordercolor="black",       # Marco de la leyenda
            borderwidth=1
        ),
        
        # Estética general de la ventana
        paper_bgcolor='white',
        margin=dict(t=50, b=50, l=50, r=50) # Márgenes limpios
    )

    # Mostrar gráfico interactivo
    fig.show()


