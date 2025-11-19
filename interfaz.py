import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import random
import os
from memoria import Proceso

class InterfazGrafica:
    """Interfaz gráfica para el simulador"""
    
    def __init__(self, microprocesador, sistema_memoria):
        self.micro = microprocesador
        self.memoria = sistema_memoria
        self.root = None
        self.ejecutando = False
        self.actualizar_id = None
        
        # Procesos de ejemplo
        self.procesos = [
            Proceso(1, "chrome.exe", 512, self.generar_instrucciones(100)),
            Proceso(2, "word.exe", 256, self.generar_instrucciones(80)),
            Proceso(3, "excel.exe", 320, self.generar_instrucciones(70))
        ]
    
    def generar_instrucciones(self, cantidad):
        """Genera instrucciones aleatorias para simulación"""
        instrucciones = []
        for _ in range(cantidad):
            # Generar instrucciones aleatorias
            opcode = random.randint(1, 4)
            operando1 = random.randint(1, 2)  # AX o BX
            operando2 = random.randint(0, 255)  # Valor
            instruccion = (opcode << 24) | (operando1 << 16) | (operando2 << 8)
            instrucciones.append(instruccion)
        return instrucciones
    
    def iniciar(self):
        """Inicia la interfaz gráfica"""
        self.root = tk.Tk()
        self.root.title("Simulador de Microprocesador y Gestión de Memoria")
        self.root.geometry("1200x800")
        
        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        
        self.crear_interfaz()
        self.actualizar_estado()
        self.root.mainloop()
    
    def cerrar_aplicacion(self):
        """Maneja el cierre correcto de la aplicación"""
        self.ejecutando = False
        if self.actualizar_id:
            self.root.after_cancel(self.actualizar_id)
        self.root.quit()
        self.root.destroy()
    
    def crear_interfaz(self):
        """Crea los elementos de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Panel de control
        self.crear_panel_control(main_frame)
        
        # Panel de estado
        self.crear_panel_estado(main_frame)
        
        # Panel de memoria
        self.crear_panel_memoria(main_frame)
        
        # Panel de métricas
        self.crear_panel_metricas(main_frame)
    
    def crear_panel_control(self, parent):
        """Crea el panel de control"""
        control_frame = ttk.LabelFrame(parent, text="Control", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Fila 1: Control de simulación
        ttk.Button(control_frame, text="Iniciar Simulación", 
                  command=self.iniciar_simulacion).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Pausar", 
                  command=self.pausar_simulacion).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Paso a Paso", 
                  command=self.ejecutar_paso).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="Reiniciar", 
                  command=self.reiniciar_simulacion).grid(row=0, column=3, padx=5)
        
        # Selector de algoritmo
        ttk.Label(control_frame, text="Algoritmo:").grid(row=0, column=4, padx=(20, 5))
        self.algoritmo_var = tk.StringVar(value="LRU")
        algoritmo_combo = ttk.Combobox(control_frame, textvariable=self.algoritmo_var,
                                      values=["FIFO", "LRU", "OPTIMO"], state="readonly")
        algoritmo_combo.grid(row=0, column=5, padx=5)
        
        # Velocidad de simulación
        ttk.Label(control_frame, text="Velocidad:").grid(row=0, column=6, padx=(20, 5))
        self.velocidad_var = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.1, to=5.0, variable=self.velocidad_var,
                 orient=tk.HORIZONTAL, length=100).grid(row=0, column=7, padx=5)
        
        # Fila 2: Carga de programas
        ttk.Button(control_frame, text="Cargar Programa .exe", 
                  command=self.cargar_exe).grid(row=1, column=0, padx=5, pady=(5, 0))
        ttk.Button(control_frame, text="Cargar Programa .asm", 
                  command=self.cargar_asm).grid(row=1, column=1, padx=5, pady=(5, 0))
        
        # Selector de programas predefinidos
        ttk.Label(control_frame, text="Programas:").grid(row=1, column=2, padx=(20, 5), pady=(5, 0))
        self.programa_var = tk.StringVar(value="chrome.exe")
        programa_combo = ttk.Combobox(control_frame, textvariable=self.programa_var,
                                     values=["chrome.exe", "word.exe", "excel.exe", "deepseek.exe"], state="readonly")
        programa_combo.grid(row=1, column=3, padx=5, pady=(5, 0))
        ttk.Button(control_frame, text="Cargar", 
                  command=self.cargar_programa_predefinido).grid(row=1, column=4, padx=5, pady=(5, 0))
    
    def cargar_exe(self):
        """Simula la carga de un archivo .exe"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo .exe",
            filetypes=[("Ejecutables", "*.exe"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            nombre = os.path.basename(file_path)
            tamano = os.path.getsize(file_path) // 1024  # Tamaño en KB aproximado
            tamano = max(64, min(tamano, 1024))  # Limitar entre 64KB y 1024KB
            
            # Crear proceso simulado
            nuevo_id = max([p.id for p in self.procesos], default=0) + 1
            instrucciones = self.generar_instrucciones(tamano // 4)
            nuevo_proceso = Proceso(nuevo_id, nombre, tamano, instrucciones)
            self.procesos.append(nuevo_proceso)
            
            messagebox.showinfo("Éxito", f"Programa {nombre} cargado exitosamente\nTamaño: {tamano} KB")
    
    def cargar_asm(self):
        """Simula la carga de un archivo .asm (ensamblador)"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo .asm",
            filetypes=[("Ensamblador", "*.asm"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            nombre = os.path.basename(file_path)
            
            # Simular análisis de archivo .asm
            tamano = random.randint(128, 512)
            instrucciones = self.generar_instrucciones(tamano // 4)
            
            nuevo_id = max([p.id for p in self.procesos], default=0) + 1
            nuevo_proceso = Proceso(nuevo_id, nombre, tamano, instrucciones)
            self.procesos.append(nuevo_proceso)
            
            messagebox.showinfo("Éxito", f"Programa {nombre} ensamblado y cargado\nTamaño: {tamano} KB")
    
    def cargar_programa_predefinido(self):
        """Carga un programa predefinido"""
        programa = self.programa_var.get()
        
        if programa == "chrome.exe":
            tamano = 512
            instrucciones = self.generar_instrucciones_chrome()
        elif programa == "word.exe":
            tamano = 256
            instrucciones = self.generar_instrucciones_word()
        elif programa == "excel.exe":
            tamano = 320
            instrucciones = self.generar_instrucciones_excel()
        else:  # deepseek.exe
            tamano = 128
            instrucciones = self.generar_instrucciones_deepseek()
        
        nuevo_id = max([p.id for p in self.procesos], default=0) + 1
        nuevo_proceso = Proceso(nuevo_id, programa, tamano, instrucciones)
        self.procesos.append(nuevo_proceso)
        
        messagebox.showinfo("Éxito", f"Programa {programa} cargado\nTamaño: {tamano} KB")
    
    def generar_instrucciones_chrome(self):
        """Genera instrucciones específicas para Chrome"""
        instrucciones = []
        # Simular comportamiento de navegador
        for i in range(50):
            instrucciones.extend([
                0x01010100 + i,  # MOV AX, datos
                0x02020164,      # ADD AX, 100
                0x0302010A,      # SUB AX, 10
                0x04000000 + (i * 4) % 256  # JMP a diferentes ubicaciones
            ])
        return instrucciones
    
    def generar_instrucciones_word(self):
        """Genera instrucciones específicas para Word"""
        instrucciones = []
        # Simular comportamiento de procesador de texto
        for i in range(40):
            instrucciones.extend([
                0x01020200 + i,  # MOV BX, datos
                0x02020232,      # ADD BX, 50
                0x0302020F,      # SUB BX, 15
                0x04000000 + (i * 6) % 256  # JMP
            ])
        return instrucciones
    
    def generar_instrucciones_excel(self):
        """Genera instrucciones específicas para Excel"""
        instrucciones = []
        # Simular comportamiento de hoja de cálculo
        for i in range(35):
            instrucciones.extend([
                0x01010100 + i,  # MOV AX, datos
                0x01020200 + i,  # MOV BX, datos
                0x02010119,      # ADD AX, 25
                0x02020219,      # ADD BX, 25
                0x04000000 + (i * 8) % 256  # JMP
            ])
        return instrucciones
    
    def generar_instrucciones_deepseek(self):
        """Genera instrucciones específicas para DeepSeek"""
        instrucciones = []
        # Simular comportamiento de IA
        for i in range(32):
            instrucciones.extend([
                0x01010100 + i,      # MOV AX, datos
                0x01020200 + i * 2,  # MOV BX, datos
                0x0201013C,          # ADD AX, 60
                0x0202023C,          # ADD BX, 60
                0x0301011E,          # SUB AX, 30
                0x0302021E,          # SUB BX, 30
                0x04000000 + (i * 10) % 256  # JMP complejo
            ])
        return instrucciones
    
    def crear_panel_estado(self, parent):
        """Crea el panel de estado del microprocesador"""
        estado_frame = ttk.LabelFrame(parent, text="Estado del Microprocesador", padding="5")
        estado_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Registros
        registros_frame = ttk.Frame(estado_frame)
        registros_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.labels_registros = {}
        registros = ['AX', 'BX', 'CX', 'DX', 'PC', 'SP', 'IR']
        
        for i, registro in enumerate(registros):
            ttk.Label(registros_frame, text=f"{registro}:").grid(row=i, column=0, sticky=tk.W, padx=(0, 5))
            label_valor = ttk.Label(registros_frame, text="0", width=10)
            label_valor.grid(row=i, column=1, sticky=tk.W)
            self.labels_registros[registro] = label_valor
        
        # Estado del procesador
        ttk.Label(estado_frame, text="Estado:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.label_estado = ttk.Label(estado_frame, text="DETENIDO")
        self.label_estado.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(estado_frame, text="Ciclos:").grid(row=2, column=0, sticky=tk.W)
        self.label_ciclos = ttk.Label(estado_frame, text="0")
        self.label_ciclos.grid(row=2, column=1, sticky=tk.W)
        
        # Programa actual
        ttk.Label(estado_frame, text="Programa:").grid(row=3, column=0, sticky=tk.W)
        self.label_programa = ttk.Label(estado_frame, text="Ninguno")
        self.label_programa.grid(row=3, column=1, sticky=tk.W)
        
        # Cache
        cache_frame = ttk.LabelFrame(estado_frame, text="Cache", padding="5")
        cache_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(cache_frame, text="L1 - Accesos:").grid(row=0, column=0, sticky=tk.W)
        self.label_cache_l1 = ttk.Label(cache_frame, text="0")
        self.label_cache_l1.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(cache_frame, text="L1 - Tasa Impactos:").grid(row=1, column=0, sticky=tk.W)
        self.label_cache_l1_tasa = ttk.Label(cache_frame, text="0%")
        self.label_cache_l1_tasa.grid(row=1, column=1, sticky=tk.W)
    
    def crear_panel_memoria(self, parent):
        """Crea el panel de visualización de memoria"""
        memoria_frame = ttk.LabelFrame(parent, text="Estado de la Memoria", padding="5")
        memoria_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        memoria_frame.columnconfigure(0, weight=1)
        memoria_frame.rowconfigure(0, weight=1)
        
        # Crear gráfico de memoria
        self.fig, self.ax_memoria = plt.subplots(figsize=(8, 6))
        self.canvas_memoria = FigureCanvasTkAgg(self.fig, memoria_frame)
        self.canvas_memoria.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Información de memoria
        info_frame = ttk.Frame(memoria_frame)
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(info_frame, text="Memoria Total:").grid(row=0, column=0, sticky=tk.W)
        self.label_mem_total = ttk.Label(info_frame, text="1024 KB")
        self.label_mem_total.grid(row=0, column=1, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(info_frame, text="Memoria Usada:").grid(row=0, column=2, sticky=tk.W)
        self.label_mem_usada = ttk.Label(info_frame, text="0 KB")
        self.label_mem_usada.grid(row=0, column=3, sticky=tk.W, padx=(5, 20))
        
        ttk.Label(info_frame, text="Tasa Fallos:").grid(row=0, column=4, sticky=tk.W)
        self.label_tasa_fallos = ttk.Label(info_frame, text="0%")
        self.label_tasa_fallos.grid(row=0, column=5, sticky=tk.W)
    
    def crear_panel_metricas(self, parent):
        """Crea el panel de métricas y estadísticas"""
        metricas_frame = ttk.LabelFrame(parent, text="Métricas y Estadísticas", padding="5")
        metricas_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Crear tabla de métricas
        columns = ('Metrica', 'Valor')
        self.tree_metricas = ttk.Treeview(metricas_frame, columns=columns, show='headings', height=8)
        self.tree_metricas.heading('Metrica', text='Métrica')
        self.tree_metricas.heading('Valor', text='Valor')
        self.tree_metricas.column('Metrica', width=200)
        self.tree_metricas.column('Valor', width=100)
        
        self.tree_metricas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(metricas_frame, orient=tk.VERTICAL, command=self.tree_metricas.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree_metricas.configure(yscrollcommand=scrollbar.set)
        
        metricas_frame.columnconfigure(0, weight=1)
        metricas_frame.rowconfigure(0, weight=1)
    
    def actualizar_estado(self):
        """Actualiza el estado de la interfaz"""
        if not self.root:
            return
        
        try:
            # Actualizar registros
            estado_micro = self.micro.obtener_estado()
            for registro, valor in estado_micro['registros'].items():
                if registro in self.labels_registros:
                    self.labels_registros[registro].config(text=str(valor))
            
            self.label_estado.config(text=estado_micro['estado'])
            self.label_ciclos.config(text=str(estado_micro['ciclos']))
            programa_actual = estado_micro.get('programa', 'Ninguno')
            self.label_programa.config(text=programa_actual)
            
            # Actualizar cache
            stats_l1 = self.micro.cache_l1.obtener_estadisticas()
            self.label_cache_l1.config(text=f"{stats_l1['accesos']}")
            self.label_cache_l1_tasa.config(text=f"{stats_l1['tasa_impactos']:.1f}%")
            
            # Actualizar memoria
            self.actualizar_visualizacion_memoria()
            
            # Actualizar métricas
            self.actualizar_metricas()
            
        except Exception as e:
            print(f"Error actualizando estado: {e}")
        
        # Programar próxima actualización solo si la ventana existe
        if self.root and self.root.winfo_exists():
            self.actualizar_id = self.root.after(500, self.actualizar_estado)
    
    def actualizar_visualizacion_memoria(self):
        """Actualiza la visualización del estado de la memoria"""
        try:
            estado_memoria = self.memoria.obtener_estado_memoria()
            estadisticas = self.memoria.obtener_estadisticas()
            
            # Actualizar labels
            self.label_mem_total.config(text=f"{estadisticas['memoria_total']} KB")
            self.label_mem_usada.config(text=f"{estadisticas.get('memoria_utilizada', 0)} KB")
            tasa_fallos = estadisticas.get('tasa_fallos_pagina', 0)
            self.label_tasa_fallos.config(text=f"{tasa_fallos:.1f}%")
            
            # Actualizar gráfico
            self.ax_memoria.clear()
            
            memoria_total = estadisticas['memoria_total']
            memoria_usada = estadisticas.get('memoria_utilizada', 0)
            
            self.ax_memoria.bar(['Usada', 'Libre'], 
                               [memoria_usada, memoria_total - memoria_usada],
                               color=['red', 'green'])
            self.ax_memoria.set_ylabel('Memoria (KB)')
            self.ax_memoria.set_title('Uso de Memoria - Paginación')
            
            self.canvas_memoria.draw()
            
        except Exception as e:
            print(f"Error en visualización de memoria: {e}")
    
    def actualizar_metricas(self):
        """Actualiza la tabla de métricas"""
        try:
            # Limpiar tabla
            for item in self.tree_metricas.get_children():
                self.tree_metricas.delete(item)
            
            # Obtener estadísticas
            stats_micro = self.micro.obtener_estado()
            stats_memoria = self.memoria.obtener_estadisticas()
            stats_cache = self.micro.cache_l1.obtener_estadisticas()
            
            # Agregar métricas
            metricas = [
                ("Ciclos de CPU", stats_micro['ciclos']),
                ("Accesos a Memoria", stats_memoria.get('accesos_memoria', 0)),
                ("Fallos de Página", stats_memoria.get('fallos_pagina', 0)),
                ("Tasa de Fallos", f"{stats_memoria.get('tasa_fallos_pagina', 0):.2f}%"),
                ("Accesos a Cache L1", stats_cache['accesos']),
                ("Impactos Cache L1", stats_cache['impactos']),
                ("Tasa Impactos Cache", f"{stats_cache['tasa_impactos']:.2f}%"),
                ("Memoria Utilizada", f"{stats_memoria.get('memoria_utilizada', 0)} KB"),
                ("Algoritmo", getattr(self.memoria, 'algoritmo_reemplazo', 'LRU'))
            ]
            
            for metrica, valor in metricas:
                self.tree_metricas.insert('', tk.END, values=(metrica, valor))
                
        except Exception as e:
            print(f"Error actualizando métricas: {e}")
    
    def iniciar_simulacion(self):
        """Inicia la simulación automática"""
        if self.ejecutando:
            return
        
        self.ejecutando = True
        self.memoria.algoritmo_reemplazo = self.algoritmo_var.get()
        
        # Cargar primer proceso si no hay ninguno
        if not self.micro.programa_actual and self.procesos:
            self.micro.cargar_programa(self.procesos[0])
            self.memoria.asignar_memoria(self.procesos[0], self.procesos[0].tamano)
        
        # Iniciar hilo de simulación
        thread = threading.Thread(target=self.ejecutar_simulacion_automatica)
        thread.daemon = True
        thread.start()
    
    def ejecutar_simulacion_automatica(self):
        """Ejecuta la simulación automáticamente"""
        while self.ejecutando and self.root and self.root.winfo_exists():
            self.ejecutar_paso()
            time.sleep(1.0 / self.velocidad_var.get())
    
    def pausar_simulacion(self):
        """Pausa la simulación"""
        self.ejecutando = False
    
    def ejecutar_paso(self):
        """Ejecuta un paso de la simulación"""
        try:
            if self.micro.programa_actual:
                instruccion = self.micro.programa_actual.ejecutar_siguiente()
                if instruccion is not None:
                    self.micro.ejecutar_instruccion(instruccion)
                    
                    # Simular acceso a memoria
                    direccion = random.randint(0, self.micro.programa_actual.tamano * 1024)
                    self.memoria.acceder_memoria(direccion, self.micro.programa_actual.id)
                else:
                    # Proceso terminado, cargar siguiente
                    self.micro.programa_actual.estado = "TERMINADO"
                    self.memoria.liberar_memoria(self.micro.programa_actual.id)
                    self.cargar_siguiente_proceso()
        except Exception as e:
            print(f"Error ejecutando paso: {e}")
    
    def cargar_siguiente_proceso(self):
        """Carga el siguiente proceso en cola"""
        try:
            procesos_pendientes = [p for p in self.procesos if p.estado != "TERMINADO"]
            if procesos_pendientes:
                siguiente = procesos_pendientes[0]
                self.micro.cargar_programa(siguiente)
                self.memoria.asignar_memoria(siguiente, siguiente.tamano)
                siguiente.estado = "EJECUTANDO"
            else:
                messagebox.showinfo("Simulación", "Todos los procesos han terminado")
                self.ejecutando = False
        except Exception as e:
            print(f"Error cargando siguiente proceso: {e}")
    
    def reiniciar_simulacion(self):
        """Reinicia la simulación"""
        self.ejecutando = False
        
        # Reiniciar microprocesador
        self.micro = type(self.micro)()  # Crear nueva instancia
        
        # Reiniciar memoria
        config = self.memoria.config
        self.memoria = type(self.memoria)(config)
        
        # Reiniciar procesos
        for proceso in self.procesos:
            proceso.estado = "NUEVO"
            proceso.contador_programa = 0
        
        messagebox.showinfo("Reiniciar", "Simulación reiniciada exitosamente")