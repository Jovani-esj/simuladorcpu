import random

class Microprocesador:
    """Simula la Unidad Central de Procesamiento (CPU)"""
    
    def __init__(self):
        # Registros principales
        self.registros = {
            'AX': 0,  # Acumulador
            'BX': 0,  # Base
            'CX': 0,  # Contador
            'DX': 0,  # Datos
            'PC': 0,  # Contador de Programa
            'SP': 0,  # Puntero de Pila
            'IR': 0,  # Registro de Instrucción
            'MAR': 0, # Registro de Dirección de Memoria
            'MBR': 0  # Registro de Búfer de Memoria
        }
        
        # Estado del procesador
        self.estado = "DETENIDO"  # DETENIDO, EJECUTANDO, INTERRUMPIDO
        self.ciclos = 0
        self.programa_actual = None
        
        # Cache L1 y L2
        self.cache_l1 = Cache(64)  # 64 KB
        self.cache_l2 = Cache(256) # 256 KB
        
        # Unidad de Gestión de Memoria (MMU)
        self.mmu = MMU()
    
    def ejecutar_instruccion(self, instruccion):
        """Ejecuta una instrucción de máquina"""
        self.registros['IR'] = instruccion
        self.ciclos += 1
        self.estado = "EJECUTANDO"
        
        # Simular procesamiento de instrucción
        opcode = instruccion >> 24
        operando1 = (instruccion >> 16) & 0xFF
        operando2 = (instruccion >> 8) & 0xFF
        
        if opcode == 0x01:  # MOV
            self.mov(operando1, operando2)
        elif opcode == 0x02:  # ADD
            self.add(operando1, operando2)
        elif opcode == 0x03:  # SUB
            self.sub(operando1, operando2)
        elif opcode == 0x04:  # JMP
            self.jmp(operando1)
        
        self.registros['PC'] += 1
    
    def mov(self, destino, origen):
        """Instrucción MOV - Mover datos"""
        if destino == 0x01:  # AX
            self.registros['AX'] = origen
        elif destino == 0x02:  # BX
            self.registros['BX'] = origen
    
    def add(self, registro, valor):
        """Instrucción ADD - Sumar"""
        if registro == 0x01:  # AX
            self.registros['AX'] += valor
        elif registro == 0x02:  # BX
            self.registros['BX'] += valor
    
    def sub(self, registro, valor):
        """Instrucción SUB - Restar"""
        if registro == 0x01:  # AX
            self.registros['AX'] -= valor
        elif registro == 0x02:  # BX
            self.registros['BX'] -= valor
    
    def jmp(self, direccion):
        """Instrucción JMP - Salto"""
        self.registros['PC'] = direccion
    
    def cargar_programa(self, programa):
        """Carga un programa en memoria"""
        self.programa_actual = programa
        self.registros['PC'] = programa.direccion_inicio
        self.estado = "LISTO"
    
    def obtener_estado(self):
        """Retorna el estado actual del microprocesador"""
        return {
            'registros': self.registros.copy(),
            'estado': self.estado,
            'ciclos': self.ciclos,
            'programa': self.programa_actual.nombre if self.programa_actual else None
        }


class Cache:
    """Simula la memoria cache del procesador"""
    
    def __init__(self, tamano_kb):
        self.tamano = tamano_kb * 1024  # Convertir a bytes
        self.datos = {}
        self.accesos = 0
        self.impactos = 0
    
    def leer(self, direccion):
        """Lee datos de la cache"""
        self.accesos += 1
        if direccion in self.datos:
            self.impactos += 1
            return self.datos[direccion]
        return None
    
    def escribir(self, direccion, datos):
        """Escribe datos en la cache"""
        if len(self.datos) >= self.tamano // 4:  # Asumiendo palabras de 4 bytes
            # Algoritmo de reemplazo simple (FIFO)
            clave_eliminar = next(iter(self.datos.keys()))
            del self.datos[clave_eliminar]
        
        self.datos[direccion] = datos
    
    def obtener_estadisticas(self):
        """Retorna estadísticas de la cache"""
        tasa_impactos = (self.impactos / self.accesos * 100) if self.accesos > 0 else 0
        return {
            'accesos': self.accesos,
            'impactos': self.impactos,
            'tasa_impactos': tasa_impactos,
            'tamano_utilizado': len(self.datos) * 4  # bytes
        }


class MMU:
    """Unidad de Gestión de Memoria"""
    
    def __init__(self):
        self.tabla_paginas = {}
        self.direcciones_traducidas = 0
    
    def traducir_direccion(self, direccion_logica, proceso_id):
        """Traduce dirección lógica a física"""
        self.direcciones_traducidas += 1
        
        if proceso_id not in self.tabla_paginas:
            self.tabla_paginas[proceso_id] = {}
        
        # Simulación simple de traducción
        numero_pagina = direccion_logica // 4096  # Páginas de 4KB
        desplazamiento = direccion_logica % 4096
        
        if numero_pagina not in self.tabla_paginas[proceso_id]:
            # Asignar nueva página
            marco_pagina = len(self.tabla_paginas[proceso_id])
            self.tabla_paginas[proceso_id][numero_pagina] = marco_pagina
        
        marco = self.tabla_paginas[proceso_id][numero_pagina]
        direccion_fisica = marco * 4096 + desplazamiento
        
        return direccion_fisica