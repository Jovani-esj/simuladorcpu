import random
import time

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