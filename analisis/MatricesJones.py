# -*- coding: utf-8 -*-
"""
Created on Mon May 18 17:44:07 2026
@author: Agustin O. Umedez, Maria E. Villalba
Matrices de Jones
"""

import numpy as np

def lp(E, tita):
    """
    Polarizador lineal ideal orientado a un ángulo variable 'tita'.
    E: Vector de Jones inicial.
    tita: Arreglo de NumPy (o float) con los ángulos de giro.
    """
    # Checkeo de dimensiones para vectorización
    tita = np.atleast_1d(tita)
    
    # Defino por comodidad el coseno y el seno
    c, s = np.cos(tita), np.sin(tita)
    
    # Matriz de Jones
    M = np.array([
        [c**2, s*c],
        [s*c, s**2]
    ]).transpose(2, 0, 1)
    
    # Corrección dimensional de E
    E = np.atleast_1d(E)
    if E.ndim == 1:
        E = E.reshape(-1, 2, 1)
    
    return M @ E

def xwp(E, tita, delta):
    """
    Lámina retardadora con un desfase arbitrario 'delta' 
    y el eje rápido orientado a un ángulo 'tita'.
    delta: Desfase en radianes (ej. np.pi/2 para qwp, np.pi para hwp).
    """
    # Checkeo de dimensiones para vectorización
    tita = np.atleast_1d(tita)
    
    # Defino por comodidad el coseno y el seno
    c, s = np.cos(tita), np.sin(tita)
    
    # Matrices de rotación distribuidas para el arreglo de tita (N, 2, 2)
    R_menos = np.array([[c, -s], [s, c]]).transpose(2, 0, 1)
    R_mas = np.array([[c, s], [-s, c]]).transpose(2, 0, 1)
    
    # Matriz del retardador en sus ejes propios
    M0 = np.array([
        [np.ones_like(delta), np.zeros_like(delta)],
        [np.zeros_like(delta), np.exp(-1j * delta)]
    ])
    
    # Corrección dimensional de E
    E = np.atleast_1d(E)
    if E.ndim == 1:
        E = E.reshape(-1, 2, 1)
    
    return R_menos @ M0 @ R_mas @ E

def lp_xwp_lp(E, tita, phi1, phi2, delta):
    """
    Simula el paso de luz por: Polarizador Lineal > Lámina Retardadora > Polarizador Lineal.
    
    E: Vector campo eléctrico incidente (lista o arreglo de 2 elementos).
    tita: Ángulo del eje rápido del retardador (escalar o arreglo).
    phi: Ángulo del eje de transmisión de los polarizadores (escalar o arreglo).
    delta: Desfase del retardador en radianes (ej. np.pi/2 para QWP, np.pi para HWP).
    """
    # Checkeo de dimensiones para vectorización
    tita = np.atleast_1d(tita)
    phi1 = np.atleast_1d(phi1)
    phi2 = np.atleast_1d(phi2)
    delta = np.atleast_1d(delta)
    
    # Funciones trigonométricas para el retardador
    c_t = np.cos(tita)
    s_t = np.sin(tita)
    
    # Funciones trigonométricas para los polarizadores
    c1, s1 = np.cos(phi1), np.sin(phi1)
    c2, s2 = np.cos(phi2), np.sin(phi2)
    
    # Matrices de rotación de la lámina (N, 2, 2)
    R_menos = np.array([[c_t, -s_t], [s_t, c_t]]).transpose(2, 0, 1)
    R_mas = np.array([[c_t, s_t], [-s_t, c_t]]).transpose(2, 0, 1)
    
    # Matriz del Polarizador Lineal 1
    M_lp_1 = np.array([
        [c1**2, s1*c1],
        [s1*c1, s1**2]
    ]).transpose(2, 0, 1)
    
    # Matriz del Polarizador Lineal 2 (Analizador)
    M_lp_2 = np.array([
        [c2**2, s2*c2],
        [s2*c2, s2**2]
    ]).transpose(2, 0, 1)
    
    # Matriz del Retardador isotrópico (XWP)
    M_xwp = np.array([
        [np.ones_like(delta), np.zeros_like(delta)],
        [np.zeros_like(delta), np.exp(-1j * delta)]
    ]).transpose(2, 0, 1)
    
    # Corrección dimensional de E
    E = np.atleast_1d(E)
    if E.ndim == 1:
        E = E.reshape(-1, 2, 1)
        
    # Multiplicación Matricial
    lp_1 = M_lp_1 @ E
    lp_xwp = R_menos @ M_xwp @ R_mas @ lp_1
    E_out = M_lp_2 @ lp_xwp
    
    return E_out

def compensador(E, tita, phi):
    """
    Simula el paso de luz por un compensador (retardador de fase general).
    
    E: Vector campo eléctrico incidente (arreglo de 2 elementos o bloque Nx2x1).
    theta: Ángulo de rotación del compensador respecto al eje x (escalar o arreglo).
    phi: Desfase introducido por el compensador en radianes (escalar o arreglo).
    """
    # Checkeo de dimensiones para vectorización
    tita = np.atleast_1d(tita)
    phi = np.atleast_1d(phi)
    
    # Defino por comodidad el coseno y el seno, así como la fase
    c, s = np.cos(tita), np.sin(tita)
    fase = np.exp(-1j * phi)
    
    # Matriz del compensador rotada un ángulo tita
    M_comp_rotada = np.array([
        [c**2 + (s**2)*fase,      s*c*(1 - fase)],
        [s*c*(1 - fase),          s**2 + (c**2)*fase]
    ]).transpose(2, 0, 1)
    
    # Corrección dimensional de E
    E = np.atleast_1d(E)
    if E.ndim == 1:
        E = E.reshape(-1, 2, 1)
    
    return M_comp_rotada @ E

def dicroismo_parcial(E, tita, px, py):
    """
    Elemento dicroico parcial (Filtro absorbedor selectivo o atenuador).
    px, py: Coeficientes de transmisión de amplitud (0 <= p <= 1).
    tita: Ángulo del eje de transmisión principal.
    """
    c = np.cos(tita)
    s = np.sin(tita)
    
    R_menos = np.array([[c, -s], [s, c]]).transpose(2, 0, 1)
    R_mas = np.array([[c, s], [-s, c]]).transpose(2, 0, 1)
    
    # Matriz de atenuación en ejes propios
    M0 = np.array([
        [px, 0],
        [0, py]
    ])
    
    return R_menos @ M0 @ R_mas @ E


def rotador_optico(E, alpha):
    """
    Elemento con actividad óptica (gira el vector de polarización un ángulo fijo).
    alpha: Ángulo de rotación pura (puede ser un único valor escalar).
    """
    c = np.cos(alpha)
    s = np.sin(alpha)
    
    # Si alpha es un único número fijo, no necesitamos transponer por lotes
    if isinstance(alpha, np.ndarray):
        M = np.array([[c, -s], [s, c]]).transpose(2, 0, 1)
    else:
        M = np.array([[c, -s], [s, c]])
        
    return M @ E


def reflexion_interfaz(E, tita, rp, rs):
    """
    Dispositivo tipo reflexión (Espejos o interfaces dieléctricas).
    Modifica las componentes p y s según los coeficientes de Fresnel del paper.
    rp, rs: Coeficientes de reflexión complejos de Fresnel.
    tita: Orientación del plano de incidencia respecto al eje x.
    """
    c = np.cos(tita)
    s = np.sin(tita)
    
    R_menos = np.array([[c, -s], [s, c]]).transpose(2, 0, 1)
    R_mas = np.array([[c, s], [-s, c]]).transpose(2, 0, 1)
    
    # Matriz de reflexión (ejes p y s)
    M0 = np.array([
        [rp, 0],
        [0, rs]
    ])
    
    return R_menos @ M0 @ R_mas @ E