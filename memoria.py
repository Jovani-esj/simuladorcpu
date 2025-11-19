import random
from collections import OrderedDict, deque

class Proceso:
    """Representa un proceso en el sistema"""
    
    def __init__(self, id, nombre, tamano, instrucciones=None):
        self.id = id
        self.nombre = nombre
        self.tamano = tamano  # en KB
        self.estado = "NUEVO"  # NUEVO, LISTO, EJECUTANDO, TERMINADO
        self.instrucciones = instrucciones or []
        self.direccion_inicio = 0
        self.contador_programa = 0
    
    def ejecutar_siguiente(self):
        """Ejecuta la siguiente instrucción"""
        if self.contador_programa < len(self.instrucciones):
            instruccion = self.instrucciones[self.contador_programa]
            self.contador_programa += 1
            return instruccion
        return None
    
    def esta_terminado(self):
        """Verifica si el proceso ha terminado"""
        return self.contador_programa >= len(self.instrucciones)

class SistemaMemoria:
    """Sistema completo de gestión de memoria"""
    
    def __init__(self, config):
        self.config = config
        
        # Memoria principal
        self.memoria_principal = MemoriaPrincipal(config['tamano_memoria_principal'])
        
        # Gestores de memoria
        self.paginacion = GestorPaginacion(config['tamano_pagina'])
        self.segmentacion = GestorSegmentacion()
        self.memoria_virtual = GestorMemoriaVirtual(config['tamano_memoria_principal'])
        
        # Algoritmos de reemplazo
        self.algoritmo_reemplazo = config['algoritmo_reemplazo']
        self.modo_memoria = config.get('modo_memoria', 'paginacion')
        
        # Procesos en memoria
        self.procesos = {}
        self.estadisticas = {
            'accesos_memoria': 0,
            'fallos_pagina': 0,
            'fragmentacion_externa': 0,
            'fragmentacion_interna': 0
        }
    
    def asignar_memoria(self, proceso, tamano):
        """Asigna memoria a un proceso"""
        proceso_id = proceso.id
        
        if self.modo_memoria == 'paginacion':
            return self.paginacion.asignar_memoria(proceso_id, tamano)
        else:
            return self.segmentacion.asignar_memoria(proceso_id, tamano)
    
    def liberar_memoria(self, proceso_id):
        """Libera memoria de un proceso"""
        if self.modo_memoria == 'paginacion':
            self.paginacion.liberar_memoria(proceso_id)
        else:
            self.segmentacion.liberar_memoria(proceso_id)
    
    def acceder_memoria(self, direccion, proceso_id, operacion='lectura'):
        """Simula acceso a memoria"""
        self.estadisticas['accesos_memoria'] += 1
        
        if self.modo_memoria == 'paginacion':
            exito = self.paginacion.acceder_pagina(direccion, proceso_id, operacion)
            if not exito:
                self.estadisticas['fallos_pagina'] += 1
                self.manejar_fallo_pagina(direccion, proceso_id)
            return exito
        else:
            return self.segmentacion.acceder_segmento(direccion, proceso_id, operacion)
    
    def manejar_fallo_pagina(self, direccion, proceso_id):
        """Maneja fallos de página usando el algoritmo de reemplazo seleccionado"""
        if self.algoritmo_reemplazo == 'FIFO':
            pagina_victima = self.algoritmo_fifo()
        elif self.algoritmo_reemplazo == 'LRU':
            pagina_victima = self.algoritmo_lru()
        elif self.algoritmo_reemplazo == 'OPTIMO':
            pagina_victima = self.algoritmo_optimo()
        else:
            pagina_victima = self.algoritmo_lru()  # Por defecto LRU
        
        # Reemplazar página
        if pagina_victima:
            self.memoria_virtual.intercambiar_entrada(pagina_victima[0], pagina_victima[1])
            nueva_pagina = direccion // self.paginacion.tamano_pagina
            self.memoria_virtual.intercambiar_salida(proceso_id, nueva_pagina)
            self.paginacion.reemplazar_pagina(pagina_victima, direccion, nuevo_proceso_id=proceso_id)
    
    def algoritmo_fifo(self):
        """Algoritmo de reemplazo FIFO"""
        if not self.paginacion.paginas_en_memoria:
            return None
        return next(iter(self.paginacion.paginas_en_memoria))
    
    def algoritmo_lru(self):
        """Algoritmo de reemplazo LRU"""
        if not self.paginacion.paginas_en_memoria:
            return None
        
        # En una implementación real, se usaría información de tiempo de acceso
        return random.choice(list(self.paginacion.paginas_en_memoria.keys()))
    
    def algoritmo_optimo(self):
        """Algoritmo de reemplazo Óptimo (aproximado)"""
        if not self.paginacion.paginas_en_memoria:
            return None
        
        # En una implementación real, se predeciría el futuro uso
        return random.choice(list(self.paginacion.paginas_en_memoria.keys()))
    
    def obtener_estado_memoria(self):
        """Retorna el estado actual de la memoria"""
        if self.modo_memoria == 'paginacion':
            return self.paginacion.obtener_estado()
        else:
            return self.segmentacion.obtener_estado()
    
    def obtener_estadisticas(self):
        """Retorna estadísticas del sistema de memoria"""
        tasa_fallos = (self.estadisticas['fallos_pagina'] / 
                      self.estadisticas['accesos_memoria'] * 100) if self.estadisticas['accesos_memoria'] > 0 else 0
        
        return {
            **self.estadisticas,
            'tasa_fallos_pagina': tasa_fallos,
            'memoria_total': self.config['tamano_memoria_principal'],
            'memoria_utilizada': self.paginacion.memoria_utilizada if self.modo_memoria == 'paginacion' else self.segmentacion.memoria_utilizada
        }


class MemoriaPrincipal:
    """Simula la memoria principal (RAM)"""
    
    def __init__(self, tamano_kb):
        self.tamano = tamano_kb * 1024  # bytes
        self.datos = [0] * self.tamano
        self.estado = ['LIBRE'] * (self.tamano // 1024)  # Estado por KB
    
    def escribir(self, direccion, valor):
        """Escribe un valor en memoria"""
        if 0 <= direccion < self.tamano:
            self.datos[direccion] = valor
            # Actualizar estado (simplificado)
            bloque = direccion // 1024
            if bloque < len(self.estado):
                self.estado[bloque] = 'OCUPADO'
    
    def leer(self, direccion):
        """Lee un valor de memoria"""
        if 0 <= direccion < self.tamano:
            return self.datos[direccion]
        return None
    
    def obtener_estado(self):
        """Retorna el estado de la memoria"""
        return self.estado


class GestorPaginacion:
    """Gestiona memoria usando paginación"""
    
    def __init__(self, tamano_pagina_kb):
        self.tamano_pagina = tamano_pagina_kb * 1024  # bytes
        self.tabla_paginas = {}  # proceso_id -> tabla de páginas
        self.marcos_memoria = {}  # marco -> (proceso_id, pagina)
        self.paginas_en_memoria = OrderedDict()  # (proceso_id, pagina) -> marco
        self.memoria_utilizada = 0
        self.contador_marco = 0
    
    def asignar_memoria(self, proceso_id, tamano):
        """Asigna memoria paginada a un proceso"""
        num_paginas = (tamano + self.tamano_pagina - 1) // self.tamano_pagina
        
        if proceso_id not in self.tabla_paginas:
            self.tabla_paginas[proceso_id] = {}
        
        paginas_asignadas = []
        for i in range(num_paginas):
            marco = self.contador_marco
            self.contador_marco += 1
            
            pagina_id = len(self.tabla_paginas[proceso_id])
            self.tabla_paginas[proceso_id][pagina_id] = {
                'marco': marco,
                'presente': True,
                'modificado': False,
                'referenciada': False
            }
            
            self.marcos_memoria[marco] = (proceso_id, pagina_id)
            self.paginas_en_memoria[(proceso_id, pagina_id)] = marco
            paginas_asignadas.append(pagina_id)
            
            self.memoria_utilizada += self.tamano_pagina
        
        return paginas_asignadas
    
    def liberar_memoria(self, proceso_id):
        """Libera memoria de un proceso"""
        if proceso_id in self.tabla_paginas:
            for pagina_id, info in self.tabla_paginas[proceso_id].items():
                if info['presente']:
                    marco = info['marco']
                    if marco in self.marcos_memoria:
                        del self.marcos_memoria[marco]
                    clave = (proceso_id, pagina_id)
                    if clave in self.paginas_en_memoria:
                        del self.paginas_en_memoria[clave]
                    self.memoria_utilizada -= self.tamano_pagina
            
            del self.tabla_paginas[proceso_id]
    
    def acceder_pagina(self, direccion, proceso_id, operacion):
        """Accede a una página de memoria"""
        if proceso_id not in self.tabla_paginas:
            return False
        
        numero_pagina = direccion // self.tamano_pagina
        desplazamiento = direccion % self.tamano_pagina
        
        if numero_pagina in self.tabla_paginas[proceso_id]:
            pagina_info = self.tabla_paginas[proceso_id][numero_pagina]
            pagina_info['referenciada'] = True
            
            if operacion == 'escritura':
                pagina_info['modificado'] = True
            
            # Mover al final para LRU
            clave = (proceso_id, numero_pagina)
            if clave in self.paginas_en_memoria:
                self.paginas_en_memoria.move_to_end(clave)
            
            return pagina_info['presente']
        
        return False
    
    def reemplazar_pagina(self, pagina_victima, nueva_direccion, nuevo_proceso_id):
        """Reemplaza una página en memoria"""
        if pagina_victima in self.paginas_en_memoria:
            marco = self.paginas_en_memoria[pagina_victima]
            proceso_viejo, pagina_vieja = pagina_victima
            
            # Liberar página vieja
            if proceso_viejo in self.tabla_paginas and pagina_vieja in self.tabla_paginas[proceso_viejo]:
                self.tabla_paginas[proceso_viejo][pagina_vieja]['presente'] = False
            
            # Asignar a nuevo proceso
            nueva_pagina = nueva_direccion // self.tamano_pagina
            if nuevo_proceso_id not in self.tabla_paginas:
                self.tabla_paginas[nuevo_proceso_id] = {}
            
            self.tabla_paginas[nuevo_proceso_id][nueva_pagina] = {
                'marco': marco,
                'presente': True,
                'modificado': False,
                'referenciada': True
            }
            
            self.marcos_memoria[marco] = (nuevo_proceso_id, nueva_pagina)
            self.paginas_en_memoria[(nuevo_proceso_id, nueva_pagina)] = marco
            self.paginas_en_memoria.move_to_end((nuevo_proceso_id, nueva_pagina))
    
    def obtener_estado(self):
        """Retorna el estado de la paginación"""
        estado = {
            'tipo': 'PAGINACION',
            'tamano_pagina': self.tamano_pagina,
            'paginas_activas': len(self.paginas_en_memoria),
            'marcos_ocupados': len(self.marcos_memoria),
            'memoria_utilizada': self.memoria_utilizada,
            'procesos': list(self.tabla_paginas.keys())
        }
        return estado


class GestorSegmentacion:
    """Gestiona memoria usando segmentación"""
    
    def __init__(self):
        self.segmentos = {}  # proceso_id -> lista de segmentos
        self.memoria_libre = []  # lista de bloques libres
        self.memoria_utilizada = 0
    
    def asignar_memoria(self, proceso_id, tamano):
        """Asigna memoria segmentada a un proceso"""
        # Implementación simple de First Fit
        segmento = {
            'base': 0,  # Simulado
            'limite': tamano,
            'tipo': 'CODIGO'  # Simulado
        }
        
        if proceso_id not in self.segmentos:
            self.segmentos[proceso_id] = []
        
        self.segmentos[proceso_id].append(segmento)
        self.memoria_utilizada += tamano
        
        return [segmento]
    
    def liberar_memoria(self, proceso_id):
        """Libera memoria de un proceso"""
        if proceso_id in self.segmentos:
            for segmento in self.segmentos[proceso_id]:
                self.memoria_utilizada -= segmento['limite']
            del self.segmentos[proceso_id]
    
    def acceder_segmento(self, direccion, proceso_id, operacion):
        """Accede a un segmento de memoria"""
        if proceso_id in self.segmentos:
            for segmento in self.segmentos[proceso_id]:
                if segmento['base'] <= direccion < segmento['base'] + segmento['limite']:
                    return True
        return False
    
    def obtener_estado(self):
        """Retorna el estado de la segmentación"""
        return {
            'tipo': 'SEGMENTACION',
            'segmentos_activos': sum(len(seg) for seg in self.segmentos.values()),
            'memoria_utilizada': self.memoria_utilizada,
            'procesos': list(self.segmentos.keys())
        }


class GestorMemoriaVirtual:
    """Gestiona memoria virtual"""
    
    def __init__(self, tamano_memoria_principal):
        self.tamano_memoria_virtual = tamano_memoria_principal * 4  # 4 veces la memoria física
        self.espacio_swap = {}  # Simula el espacio de intercambio
        self.paginas_swap = 0
    
    def intercambiar_entrada(self, proceso_id, pagina_id):
        """Intercambia una página a memoria virtual"""
        clave = (proceso_id, pagina_id)
        self.espacio_swap[clave] = f"Datos_pagina_{proceso_id}_{pagina_id}"
        self.paginas_swap += 1
    
    def intercambiar_salida(self, proceso_id, pagina_id):
        """Intercambia una página de memoria virtual a RAM"""
        clave = (proceso_id, pagina_id)
        if clave in self.espacio_swap:
            del self.espacio_swap[clave]
            self.paginas_swap -= 1
            return True
        return False