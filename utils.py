import random
import time
import psutil

def obtener_estadisticas_reales():
    """Obtiene estadísticas reales del sistema"""
    try:
        # CPU
        cpu_total = psutil.cpu_percent(interval=0.1)
        cpu_per_core = psutil.cpu_percent(percpu=True)
        cpu_freq = psutil.cpu_freq()
        
        # Memoria
        memoria = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disco
        disco = psutil.disk_usage('/')
        
        # Red
        red = psutil.net_io_counters()
        
        # Sistema
        boot_time = psutil.boot_time()
        procesos = len(psutil.pids())
        
        return {
            'cpu': {
                'total': cpu_total,
                'por_nucleo': cpu_per_core,
                'frecuencia_actual': cpu_freq.current if cpu_freq else 0,
                'nucleos_fisicos': psutil.cpu_count(logical=False),
                'nucleos_logicos': psutil.cpu_count(logical=True)
            },
            'memoria': {
                'total': memoria.total,
                'usada': memoria.used,
                'libre': memoria.available,
                'porcentaje': memoria.percent
            },
            'swap': {
                'total': swap.total,
                'usado': swap.used,
                'porcentaje': swap.percent
            },
            'disco': {
                'total': disco.total,
                'usado': disco.used,
                'libre': disco.free,
                'porcentaje': disco.percent
            },
            'red': {
                'bytes_enviados': red.bytes_sent,
                'bytes_recibidos': red.bytes_recv,
                'paquetes_enviados': red.packets_sent,
                'paquetes_recibidos': red.packets_recv
            },
            'sistema': {
                'tiempo_actividad': time.time() - boot_time,
                'procesos_activos': procesos,
                'usuario_actual': psutil.Process().username()
            }
        }
    except Exception as e:
        print(f"Error obteniendo estadísticas reales: {e}")
        return {}

def obtener_procesos_detallados(limite=20):
    """Obtiene información detallada de los procesos del sistema"""
    procesos = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 
                                       'num_threads', 'create_time', 'username']):
            try:
                info = proc.info
                memoria_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0
                
                procesos.append({
                    'pid': info['pid'],
                    'nombre': info['name'] or 'N/A',
                    'cpu': info['cpu_percent'] or 0,
                    'memoria_mb': memoria_mb,
                    'estado': info['status'] or 'N/A',
                    'hilos': info['num_threads'] or 0,
                    'usuario': info['username'] or 'N/A',
                    'tiempo_ejecucion': time.time() - info['create_time'] if info['create_time'] else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordenar por uso de memoria (descendente)
        procesos.sort(key=lambda x: x['memoria_mb'], reverse=True)
        return procesos[:limite]
        
    except Exception as e:
        print(f"Error obteniendo procesos: {e}")
        return []

def generar_programa_ejemplo(nombre, tamano_kb):
    """Genera un programa de ejemplo para simulación"""
    instrucciones = []
    for i in range(tamano_kb // 4):  # Aproximadamente 1 instrucción por 4 bytes
        # Generar instrucciones variadas
        tipo = random.choice(['mov', 'add', 'sub', 'jmp'])
        if tipo == 'mov':
            instruccion = (0x01 << 24) | (random.randint(1, 2) << 16) | (random.randint(0, 255) << 8)
        elif tipo == 'add':
            instruccion = (0x02 << 24) | (random.randint(1, 2) << 16) | (random.randint(1, 100) << 8)
        elif tipo == 'sub':
            instruccion = (0x03 << 24) | (random.randint(1, 2) << 16) | (random.randint(1, 50) << 8)
        else:  # jmp
            instruccion = (0x04 << 24) | (random.randint(0, tamano_kb * 256) << 8)
        
        instrucciones.append(instruccion)
    
    return instrucciones

def calcular_fragmentacion(memoria_utilizada, memoria_total, tipo='externa'):
    """Calcula la fragmentación de memoria"""
    if tipo == 'externa':
        # Fragmentación externa: memoria libre pero no contigua
        return (memoria_total - memoria_utilizada) / memoria_total * 100
    else:
        # Fragmentación interna: memoria asignada pero no utilizada
        return min(10, random.random() * 20)  # Simulación

def medir_tiempo_ejecucion(func):
    """Decorador para medir tiempo de ejecución"""
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        print(f"Tiempo de ejecución de {func.__name__}: {fin - inicio:.4f} segundos")
        return resultado
    return wrapper