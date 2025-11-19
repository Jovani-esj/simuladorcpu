#!/usr/bin/env python3
"""
Simulador de Arquitectura de Microprocesador y Gestión de Memoria
Autor: Asistente DeepSeek
"""

import sys
import os
import random
from microprocesador import Microprocesador, Cache, MMU
from memoria import SistemaMemoria, MemoriaPrincipal, GestorPaginacion, GestorSegmentacion, GestorMemoriaVirtual, Proceso
from interfaz import InterfazGrafica

def main():
    """Función principal del simulador"""
    print("=== Simulador de Arquitectura de Microprocesador ===")
    print("Inicializando componentes...")
    
    # Configuración del sistema
    config = {
        'tamano_memoria_principal': 1024,  # KB
        'tamano_cache_l1': 64,  # KB
        'tamano_cache_l2': 256,  # KB
        'tamano_pagina': 4,  # KB
        'algoritmo_reemplazo': 'LRU'
    }
    
    # Crear instancias
    microprocesador = Microprocesador()
    sistema_memoria = SistemaMemoria(config)
    
    # Iniciar interfaz gráfica
    app = InterfazGrafica(microprocesador, sistema_memoria)
    app.iniciar()

if __name__ == "__main__":
    main()
    