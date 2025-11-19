import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import random
import os
import subprocess
import psutil
import platform
from memoria import Proceso

class InterfazGrafica:
    """Interfaz gráfica para el simulador con datos reales y diseño moderno"""

    def __init__(self, microprocesador, sistema_memoria):
        self.micro = microprocesador
        self.memoria = sistema_memoria
        self.root = None
        self.ejecutando = False
        self.actualizar_id = None

        # Configuración de tema
        self.tema_oscuro = False
        self.colores = self.obtener_colores_tema_claro()

        # Procesos de ejemplo
        self.procesos = []
        self.proceso_seleccionado = None
        # Información del proceso real en el SO
        self.proceso_real_nombre = None
        self.proceso_real_pid = None
        self.proceso_real_objeto = None

    def obtener_colores_tema_claro(self):
        """Define los colores para el tema claro"""
        return {
            'fondo_principal': '#f0f0f0',
            'fondo_secundario': '#ffffff',
            'fondo_terciario': '#e8e8e8',
            'texto_principal': '#2c3e50',
            'texto_secundario': '#34495e',
            'texto_terciario': '#7f8c8d',
            'borde': '#bdc3c7',
            'accent': '#3498db',
            'accent_hover': '#2980b9',
            'success': '#27ae60',
            'warning': '#f39c12',
            'error': '#e74c3c',
            'chart1': '#3498db',
            'chart2': '#e74c3c',
            'chart3': '#2ecc71',
            'chart4': '#f39c12'
        }

    def obtener_colores_tema_oscuro(self):
        """Define los colores para el tema oscuro"""
        return {
            'fondo_principal': '#1e1e1e',
            'fondo_secundario': '#252526',
            'fondo_terciario': '#2d2d30',
            'texto_principal': '#ffffff',
            'texto_secundario': '#cccccc',
            'texto_terciario': '#969696',
            'borde': '#3e3e42',
            'accent': '#007acc',
            'accent_hover': '#005a9e',
            'success': '#4ec9b0',
            'warning': '#dcdcaa',
            'error': '#f44747',
            'chart1': '#4ec9b0',
            'chart2': '#f44747',
            'chart3': '#569cd6',
            'chart4': '#dcdcaa'
        }

    def alternar_tema(self):
        """Alterna entre tema claro y oscuro"""
        self.tema_oscuro = not self.tema_oscuro
        self.colores = self.obtener_colores_tema_oscuro() if self.tema_oscuro else self.obtener_colores_tema_claro()
        self.aplicar_tema()

    def aplicar_tema(self):
        """Aplica el tema actual a toda la interfaz"""
        if not self.root:
            return

        # Configurar estilo
        style = ttk.Style()
        
        # Configurar tema para ttk
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')

        # Configurar colores del tema
        self.root.configure(bg=self.colores['fondo_principal'])
        
        # Configurar estilos para los widgets ttk
        style.configure('TFrame', background=self.colores['fondo_principal'])
        style.configure('TLabel', 
                       background=self.colores['fondo_principal'],
                       foreground=self.colores['texto_principal'])
        style.configure('TLabelframe',
                       background=self.colores['fondo_principal'],
                       foreground=self.colores['texto_principal'],
                       bordercolor=self.colores['borde'])
        style.configure('TLabelframe.Label',
                       background=self.colores['fondo_principal'],
                       foreground=self.colores['texto_principal'])
        style.configure('TButton',
                       background=self.colores['fondo_secundario'],
                       foreground=self.colores['texto_principal'],
                       bordercolor=self.colores['borde'],
                       focuscolor='none')
        style.map('TButton',
                 background=[('active', self.colores['accent_hover']),
                           ('pressed', self.colores['accent'])],
                 foreground=[('active', 'white')])
        style.configure('TNotebook',
                       background=self.colores['fondo_principal'],
                       tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab',
                       background=self.colores['fondo_terciario'],
                       foreground=self.colores['texto_principal'],
                       padding=[10, 5])
        style.map('TNotebook.Tab',
                 background=[('selected', self.colores['accent']),
                           ('active', self.colores['accent_hover'])],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])
        style.configure('Treeview',
                       background=self.colores['fondo_secundario'],
                       foreground=self.colores['texto_principal'],
                       fieldbackground=self.colores['fondo_secundario'],
                       bordercolor=self.colores['borde'])
        style.configure('Treeview.Heading',
                       background=self.colores['fondo_terciario'],
                       foreground=self.colores['texto_principal'],
                       relief='flat')
        style.map('Treeview.Heading',
                 background=[('active', self.colores['accent_hover'])])
        style.configure('Vertical.TScrollbar',
                       background=self.colores['fondo_terciario'],
                       troughcolor=self.colores['fondo_principal'],
                       bordercolor=self.colores['borde'],
                       arrowcolor=self.colores['texto_principal'])
        style.configure('Horizontal.TScrollbar',
                       background=self.colores['fondo_terciario'],
                       troughcolor=self.colores['fondo_principal'],
                       bordercolor=self.colores['borde'],
                       arrowcolor=self.colores['texto_principal'])
        style.configure('TCombobox',
                       background=self.colores['fondo_secundario'],
                       foreground=self.colores['texto_principal'],
                       fieldbackground=self.colores['fondo_secundario'])
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.colores['fondo_secundario'])],
                 background=[('readonly', self.colores['fondo_secundario'])])
        style.configure('TScale',
                       background=self.colores['fondo_principal'],
                       troughcolor=self.colores['fondo_terciario'])

        # Actualizar gráficos de matplotlib
        self.actualizar_estilo_graficos()

    def actualizar_estilo_graficos(self):
        """Actualiza el estilo de los gráficos de matplotlib según el tema"""
        if hasattr(self, 'fig'):
            if self.tema_oscuro:
                plt.style.use('dark_background')
            else:
                plt.style.use('default')
            
            # Actualizar colores específicos
            if hasattr(self, 'ax_memoria'):
                self.ax_memoria.set_facecolor(self.colores['fondo_secundario'])
            if hasattr(self, 'ax_cpu'):
                self.ax_cpu.set_facecolor(self.colores['fondo_secundario'])
            if hasattr(self, 'fig'):
                self.fig.patch.set_facecolor(self.colores['fondo_principal'])
            
            if hasattr(self, 'canvas_memoria'):
                self.canvas_memoria.draw()

    def iniciar(self):
        """Inicia la interfaz gráfica"""
        self.root = tk.Tk()
        self.root.title("Simulador de Microprocesador - Datos Reales del Sistema")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)

        # Configurar tema inicial
        self.aplicar_tema()

        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

        # Configurar grid principal para responsividad
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

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
        """Crea los elementos de la interfaz con diseño responsive"""
        # Frame principal con scroll
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid del contenedor principal
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Barra superior de control
        control_container = ttk.Frame(main_container)
        control_container.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8), padx=10)
        control_container.columnconfigure(0, weight=1)
        self.crear_panel_control(control_container)

        # Panel principal con notebook
        panel_principal = ttk.Frame(main_container)
        panel_principal.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        panel_principal.columnconfigure(0, weight=1)
        panel_principal.rowconfigure(0, weight=1)

        # Notebook principal con pestañas
        notebook_principal = ttk.Notebook(panel_principal)
        notebook_principal.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Pestaña de Dashboard
        tab_dashboard = ttk.Frame(notebook_principal)
        notebook_principal.add(tab_dashboard, text="📊 Dashboard")
        tab_dashboard.columnconfigure(0, weight=1)
        tab_dashboard.rowconfigure(0, weight=1)
        self.crear_panel_dashboard(tab_dashboard)

        # Pestaña de Procesos
        tab_procesos = ttk.Frame(notebook_principal)
        notebook_principal.add(tab_procesos, text="🔄 Procesos del Sistema")
        tab_procesos.columnconfigure(0, weight=1)
        tab_procesos.rowconfigure(0, weight=1)
        self.crear_panel_procesos_sistema(tab_procesos)

        # Pestaña de Métricas Detalladas
        tab_metricas = ttk.Frame(notebook_principal)
        notebook_principal.add(tab_metricas, text="📈 Métricas Detalladas")
        tab_metricas.columnconfigure(0, weight=1)
        tab_metricas.rowconfigure(0, weight=1)
        self.crear_panel_metricas_detalladas(tab_metricas)

        # Pestaña de Configuración
        tab_config = ttk.Frame(notebook_principal)
        notebook_principal.add(tab_config, text="⚙️ Configuración")
        tab_config.columnconfigure(0, weight=1)
        tab_config.rowconfigure(0, weight=1)
        self.crear_panel_configuracion(tab_config)

    def crear_panel_control(self, parent):
        """Crea el panel de control mejorado"""
        control_frame = ttk.LabelFrame(parent, text="🎮 Control de Programas Reales", padding="12")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)

        # Fila 1: Botones de programas populares
        frame_programas = ttk.Frame(control_frame)
        frame_programas.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        ttk.Label(frame_programas, text="Abrir Programas:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        programas = [
            ("📝 Word", "WINWORD.EXE", "Microsoft Word"),
            ("📊 Excel", "EXCEL.EXE", "Microsoft Excel"),
            ("🌐 Chrome", "chrome.exe", "Google Chrome"),
            ("🤖 Android Studio", "studio64.exe", "Android Studio"),
            ("💻 VS Code", "Code.exe", "Visual Studio Code")
        ]
        
        for i, (emoji, ejecutable, nombre) in enumerate(programas):
            btn = ttk.Button(frame_programas, 
                           text=f"{emoji} {nombre.split()[-1]}",
                           command=lambda e=ejecutable, n=nombre: self.abrir_programa_real(e, n),
                           width=15)
            btn.grid(row=0, column=i+1, padx=2)

        # Fila 2: Programas personalizados y monitoreo
        frame_control = ttk.Frame(control_frame)
        frame_control.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Programa personalizado
        ttk.Label(frame_control, text="Programa Personalizado:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.programa_var = tk.StringVar(value="notepad.exe")
        programa_combo = ttk.Combobox(frame_control, textvariable=self.programa_var,
                                     values=["notepad.exe", "calc.exe", "mspaint.exe", "cmd.exe", "explorer.exe"], 
                                     state="readonly", width=12)
        programa_combo.grid(row=0, column=1, padx=(0, 10))
        ttk.Button(frame_control, text="Abrir",
                  command=self.abrir_programa_personalizado).grid(row=0, column=2, padx=(0, 20))

        # Monitoreo de procesos existentes
        ttk.Label(frame_control, text="Monitorear Proceso:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.proceso_existente_var = tk.StringVar()
        procesos_disponibles = self.obtener_procesos_populares()
        proceso_combo = ttk.Combobox(frame_control, textvariable=self.proceso_existente_var,
                                    values=procesos_disponibles, state="readonly", width=15)
        proceso_combo.grid(row=0, column=4, padx=(0, 10))
        ttk.Button(frame_control, text="Monitorear",
                  command=self.monitorear_proceso_existente).grid(row=0, column=5, padx=(0, 20))

        # Botón de tema
        ttk.Button(frame_control, text="🌙 Tema Oscuro" if not self.tema_oscuro else "☀️ Tema Claro",
                  command=self.alternar_tema).grid(row=0, column=6)

    def crear_panel_dashboard(self, parent):
        """Crea el panel dashboard con información principal"""
        # Frame principal con scroll
        dashboard_frame = ttk.Frame(parent)
        dashboard_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid para responsividad
        for i in range(3):
            dashboard_frame.columnconfigure(i, weight=1, uniform="col")
        dashboard_frame.rowconfigure(1, weight=1)

        # Columna 1: Estado del Sistema
        frame_sistema = ttk.LabelFrame(dashboard_frame, text="🖥️ Estado del Sistema", padding="10")
        frame_sistema.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.crear_panel_estado_sistema(frame_sistema)

        # Columna 2: Proceso Monitoreado
        frame_proceso = ttk.LabelFrame(dashboard_frame, text="📋 Proceso Monitoreado", padding="10")
        frame_proceso.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.crear_panel_proceso_monitoreado(frame_proceso)

        # Columna 3: Registros (Simulados)
        frame_registros = ttk.LabelFrame(dashboard_frame, text="💾 Registros del Microprocesador", padding="10")
        frame_registros.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.crear_panel_registros(frame_registros)

        # Gráficos (ocupan toda la segunda fila)
        frame_graficos = ttk.LabelFrame(dashboard_frame, text="📈 Métricas en Tiempo Real", padding="10")
        frame_graficos.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        frame_graficos.columnconfigure(0, weight=1)
        frame_graficos.rowconfigure(0, weight=1)
        self.crear_panel_graficos(frame_graficos)

    def crear_panel_estado_sistema(self, parent):
        """Crea el panel de estado del sistema"""
        # Configurar grid
        for i in range(2):
            parent.columnconfigure(i, weight=1)

        metricas = [
            ("CPU Total:", "label_cpu_total", "0%"),
            ("RAM Total:", "label_ram_total", "0 MB"),
            ("RAM Usada:", "label_ram_usada", "0 MB"),
            ("RAM Libre:", "label_ram_libre", "0 MB"),
            ("Uso RAM:", "label_ram_porcentaje", "0%"),
            ("Procesos Activos:", "label_procesos_activos", "0"),
            ("Tiempo Activo:", "label_tiempo_activo", "0s"),
            ("Disco Usado:", "label_disco_usado", "0%")
        ]

        self.labels_sistema = {}
        for i, (texto, clave, valor_inicial) in enumerate(metricas):
            ttk.Label(parent, text=texto, font=('Arial', 9)).grid(row=i, column=0, sticky=tk.W, pady=2)
            label = ttk.Label(parent, text=valor_inicial, font=('Arial', 9, 'bold'), foreground=self.colores['accent'])
            label.grid(row=i, column=1, sticky=tk.W, pady=2)
            self.labels_sistema[clave] = label

    def crear_panel_proceso_monitoreado(self, parent):
        """Crea el panel de proceso monitoreado"""
        # Configurar grid
        for i in range(2):
            parent.columnconfigure(i, weight=1)

        metricas = [
            ("Nombre:", "label_proc_nombre", "Ninguno"),
            ("PID:", "label_proc_pid", "-"),
            ("CPU:", "label_proc_cpu", "0%"),
            ("RAM:", "label_proc_ram", "0 MB"),
            ("Estado:", "label_proc_estado", "-"),
            ("Hilos:", "label_proc_hilos", "0"),
            ("Usuario:", "label_proc_usuario", "-"),
            ("Tiempo:", "label_proc_tiempo", "0s")
        ]

        self.labels_proceso = {}
        for i, (texto, clave, valor_inicial) in enumerate(metricas):
            ttk.Label(parent, text=texto, font=('Arial', 9)).grid(row=i, column=0, sticky=tk.W, pady=2)
            label = ttk.Label(parent, text=valor_inicial, font=('Arial', 9, 'bold'), 
                            foreground=self.colores['accent'])
            label.grid(row=i, column=1, sticky=tk.W, pady=2)
            self.labels_proceso[clave] = label

    def crear_panel_registros(self, parent):
        """Crea el panel de registros simulados"""
        # Configurar grid
        for i in range(2):
            parent.columnconfigure(i, weight=1)

        self.labels_registros = {}
        registros = [
            ('AX', 'Acumulador'),
            ('BX', 'Base'),
            ('CX', 'Contador'),
            ('DX', 'Datos'),
            ('PC', 'Contador Programa'),
            ('SP', 'Puntero Pila'),
            ('IR', 'Registro Instrucción')
        ]

        for i, (registro, descripcion) in enumerate(registros):
            ttk.Label(parent, text=f"{registro} ({descripcion}):", font=('Arial', 9)).grid(row=i, column=0, sticky=tk.W, pady=2)
            label_valor = ttk.Label(parent, text="0", font=('Arial', 9, 'bold'), 
                                  foreground=self.colores['chart1'], width=8)
            label_valor.grid(row=i, column=1, sticky=tk.W, pady=2)
            self.labels_registros[registro] = label_valor

    def crear_panel_graficos(self, parent):
        """Crea el panel de gráficos"""
        # Crear figura con subplots
        self.fig, (self.ax_memoria, self.ax_cpu, self.ax_procesos) = plt.subplots(1, 3, figsize=(15, 4))
        
        # Configurar la figura para el tema
        self.fig.patch.set_facecolor(self.colores['fondo_secundario'])
        
        # Crear canvas
        self.canvas_graficos = FigureCanvasTkAgg(self.fig, parent)
        self.canvas_graficos.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def crear_panel_procesos_sistema(self, parent):
        """Crea el panel de procesos del sistema con scroll"""
        # Frame principal
        procesos_frame = ttk.LabelFrame(parent, text="📊 Procesos del Sistema en Tiempo Real", padding="10")
        procesos_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        procesos_frame.columnconfigure(0, weight=1)
        procesos_frame.rowconfigure(0, weight=1)

        # Frame para controles de filtro
        frame_controles = ttk.Frame(procesos_frame)
        frame_controles.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(frame_controles, text="Filtrar por nombre:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.filtro_procesos = tk.StringVar()
        ttk.Entry(frame_controles, textvariable=self.filtro_procesos, width=20).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(frame_controles, text="Ordenar por:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.orden_procesos = tk.StringVar(value="memoria")
        ttk.Combobox(frame_controles, textvariable=self.orden_procesos,
                    values=["memoria", "cpu", "nombre", "pid"], state="readonly", width=10).grid(row=0, column=3)

        # Frame para la tabla con scroll
        frame_tabla = ttk.Frame(procesos_frame)
        frame_tabla.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)

        # Crear tabla de procesos
        columns = ('pid', 'nombre', 'cpu', 'memoria', 'estado', 'hilos', 'usuario')
        self.tree_procesos = ttk.Treeview(frame_tabla, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        column_config = [
            ('pid', 'PID', 70, tk.CENTER),
            ('nombre', 'Nombre', 200, tk.W),
            ('cpu', 'CPU %', 80, tk.CENTER),
            ('memoria', 'Memoria (MB)', 100, tk.CENTER),
            ('estado', 'Estado', 80, tk.CENTER),
            ('hilos', 'Hilos', 60, tk.CENTER),
            ('usuario', 'Usuario', 120, tk.W)
        ]

        for col, heading, width, anchor in column_config:
            self.tree_procesos.heading(col, text=heading)
            self.tree_procesos.column(col, width=width, anchor=anchor)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree_procesos.yview)
        h_scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.HORIZONTAL, command=self.tree_procesos.xview)
        self.tree_procesos.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid de la tabla y scrollbars
        self.tree_procesos.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def crear_panel_metricas_detalladas(self, parent):
        """Crea el panel de métricas detalladas con scroll"""
        # Frame principal
        metricas_frame = ttk.LabelFrame(parent, text="📋 Métricas Detalladas del Sistema", padding="10")
        metricas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        metricas_frame.columnconfigure(0, weight=1)
        metricas_frame.rowconfigure(0, weight=1)

        # Frame para la tabla con scroll
        frame_tabla = ttk.Frame(metricas_frame)
        frame_tabla.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame_tabla.columnconfigure(0, weight=1)
        frame_tabla.rowconfigure(0, weight=1)

        # Crear tabla de métricas
        columns = ('Metrica', 'Valor')
        self.tree_metricas = ttk.Treeview(frame_tabla, columns=columns, show='headings', height=25)
        self.tree_metricas.heading('Metrica', text='Métrica del Sistema')
        self.tree_metricas.heading('Valor', text='Valor Actual')
        self.tree_metricas.column('Metrica', width=300, anchor=tk.W)
        self.tree_metricas.column('Valor', width=200, anchor=tk.W)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tree_metricas.yview)
        self.tree_metricas.configure(yscrollcommand=v_scrollbar.set)

        # Grid
        self.tree_metricas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def crear_panel_configuracion(self, parent):
        """Crea el panel de configuración"""
        config_frame = ttk.LabelFrame(parent, text="⚙️ Configuración del Simulador", padding="20")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
        
        # Configuración de actualización
        ttk.Label(config_frame, text="Intervalo de actualización:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.intervalo_var = tk.IntVar(value=1000)
        intervalos = [("1 segundo", 1000), ("2 segundos", 2000), ("5 segundos", 5000)]
        
        for i, (texto, valor) in enumerate(intervalos):
            ttk.Radiobutton(config_frame, text=texto, variable=self.intervalo_var, 
                           value=valor).grid(row=1, column=i, sticky=tk.W, pady=5)

        # Separador
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)

        # Información del sistema
        ttk.Label(config_frame, text="Información del Sistema:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        info_sistema = [
            f"Sistema Operativo: {platform.system()} {platform.release()}",
            f"Arquitectura: {platform.architecture()[0]}",
            f"Procesador: {platform.processor()}",
            f"Python: {platform.python_version()}",
            f"Total RAM: {psutil.virtual_memory().total // (1024**3)} GB"
        ]
        
        for i, info in enumerate(info_sistema):
            ttk.Label(config_frame, text=info).grid(row=4+i, column=0, sticky=tk.W, pady=2)

    # ... (los métodos restantes de abrir programas, monitoreo, y actualización se mantienen igual)
    def obtener_procesos_populares(self):
        """Obtiene lista de procesos populares del sistema"""
        procesos_populares = []
        try:
            for proc in psutil.process_iter(['name']):
                nombre = proc.info['name']
                if nombre and nombre.lower() in ['winword.exe', 'excel.exe', 'chrome.exe', 'firefox.exe', 
                                               'code.exe', 'devenv.exe', 'pycharm.exe', 'studio64.exe',
                                               'notepad.exe', 'calc.exe', 'explorer.exe']:
                    if nombre not in procesos_populares:
                        procesos_populares.append(nombre)
        except:
            pass
        return sorted(procesos_populares)

    def abrir_programa_real(self, nombre_ejecutable, nombre_amigable):
        """Abre un programa real y comienza a monitorearlo"""
        try:
            # Buscar el proceso primero
            proceso_encontrado = None
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'].lower() == nombre_ejecutable.lower():
                    proceso_encontrado = proc
                    break

            if not proceso_encontrado:
                # Intentar abrir el programa
                if nombre_ejecutable.lower() == "winword.exe":
                    os.startfile("winword")
                elif nombre_ejecutable.lower() == "excel.exe":
                    os.startfile("excel")
                elif nombre_ejecutable.lower() == "chrome.exe":
                    os.startfile("chrome")
                elif nombre_ejecutable.lower() == "studio64.exe":
                    # Buscar Android Studio en ubicaciones comunes
                    paths = [
                        r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
                        r"C:\Program Files (x86)\Android\Android Studio\bin\studio64.exe"
                    ]
                    for path in paths:
                        if os.path.exists(path):
                            subprocess.Popen([path])
                            break
                else:
                    os.startfile(nombre_ejecutable)
                
                # Esperar un momento y buscar el proceso
                time.sleep(2)
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and proc.info['name'].lower() == nombre_ejecutable.lower():
                        proceso_encontrado = proc
                        break

            if proceso_encontrado:
                self.agregar_proceso_monitoreo(proceso_encontrado, nombre_amigable)
                messagebox.showinfo("Éxito", f"Monitoreando {nombre_amigable}\nPID: {proceso_encontrado.info['pid']}")
            else:
                messagebox.showwarning("Advertencia", f"No se pudo encontrar o abrir {nombre_amigable}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir {nombre_amigable}: {str(e)}")

    def abrir_programa_personalizado(self):
        """Abre un programa personalizado"""
        programa = self.programa_var.get()
        nombre_amigable = programa.replace('.exe', '').title()
        self.abrir_programa_real(programa, nombre_amigable)

    def monitorear_proceso_existente(self):
        """Comienza a monitorear un proceso existente"""
        nombre_proceso = self.proceso_existente_var.get()
        if not nombre_proceso:
            return

        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'] == nombre_proceso:
                    nombre_amigable = nombre_proceso.replace('.exe', '').title()
                    self.agregar_proceso_monitoreo(proc, nombre_amigable)
                    messagebox.showinfo("Éxito", f"Monitoreando {nombre_amigable}\nPID: {proc.info['pid']}")
                    return
            messagebox.showwarning("Advertencia", f"No se encontró el proceso {nombre_proceso}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo monitorear el proceso: {str(e)}")

    def agregar_proceso_monitoreo(self, proceso_psutil, nombre_amigable):
        """Agrega un proceso real para monitoreo"""
        try:
            # Obtener información real del proceso
            mem_info = proceso_psutil.memory_info()
            cpu_percent = proceso_psutil.cpu_percent(interval=0.1)
            
            # Crear proceso simulado con datos reales
            nuevo_proceso = Proceso(
                proceso_psutil.info['pid'],
                nombre_amigable,
                int(mem_info.rss / 1024),  # Tamaño en KB
                []
            )
            nuevo_proceso.estado = "MONITOREANDO"
            nuevo_proceso.proceso_real = proceso_psutil
            
            # Agregar a la lista de procesos
            self.procesos.append(nuevo_proceso)
            self.proceso_seleccionado = nuevo_proceso
            self.proceso_real_objeto = proceso_psutil

        except Exception as e:
            print(f"Error agregando proceso: {e}")

    def actualizar_estado(self):
        """Actualiza el estado de la interfaz con datos reales"""
        if not self.root:
            return
        
        try:
            # Actualizar información del sistema
            self.actualizar_info_sistema()
            
            # Actualizar información del proceso monitoreado
            self.actualizar_info_proceso_monitoreado()
            
            # Actualizar registros simulados (únicos datos simulados)
            self.actualizar_registros_simulados()
            
            # Actualizar visualización de gráficos
            self.actualizar_graficos()
            
            # Actualizar métricas del sistema
            self.actualizar_metricas_sistema()
            
            # Actualizar procesos del sistema
            self.actualizar_procesos_sistema()
            
        except Exception as e:
            print(f"Error actualizando estado: {e}")
        
        # Programar próxima actualización
        if self.root and self.root.winfo_exists():
            intervalo = self.intervalo_var.get() if hasattr(self, 'intervalo_var') else 1000
            self.actualizar_id = self.root.after(intervalo, self.actualizar_estado)

    def actualizar_info_sistema(self):
        """Actualiza la información general del sistema"""
        try:
            # CPU total
            cpu_total = psutil.cpu_percent(interval=0.1)
            self.labels_sistema['label_cpu_total'].config(text=f"{cpu_total:.1f}%")
            
            # Memoria del sistema
            memoria = psutil.virtual_memory()
            mem_total_gb = memoria.total / (1024**3)
            mem_usada_mb = memoria.used / (1024**2)
            mem_libre_mb = memoria.available / (1024**2)
            mem_porcentaje = memoria.percent
            
            self.labels_sistema['label_ram_total'].config(text=f"{mem_total_gb:.1f} GB")
            self.labels_sistema['label_ram_usada'].config(text=f"{mem_usada_mb:.1f} MB")
            self.labels_sistema['label_ram_libre'].config(text=f"{mem_libre_mb:.1f} MB")
            self.labels_sistema['label_ram_porcentaje'].config(text=f"{mem_porcentaje:.1f}%")
            
            # Otros datos del sistema
            self.labels_sistema['label_procesos_activos'].config(text=str(len(psutil.pids())))
            self.labels_sistema['label_tiempo_activo'].config(text=f"{time.time() - psutil.boot_time():.0f}s")
            
            # Disco
            disco = psutil.disk_usage('/')
            self.labels_sistema['label_disco_usado'].config(text=f"{disco.percent:.1f}%")
            
        except Exception as e:
            print(f"Error actualizando info del sistema: {e}")

    def actualizar_info_proceso_monitoreado(self):
        """Actualiza la información del proceso monitoreado"""
        try:
            if self.proceso_real_objeto:
                proceso = self.proceso_real_objeto
                
                # Actualizar información del proceso
                self.labels_proceso['label_proc_nombre'].config(text=proceso.name())
                self.labels_proceso['label_proc_pid'].config(text=str(proceso.pid))
                
                # CPU del proceso
                cpu_proc = proceso.cpu_percent(interval=0.1)
                self.labels_proceso['label_proc_cpu'].config(text=f"{cpu_proc:.1f}%")
                
                # Memoria del proceso
                mem_info = proceso.memory_info()
                mem_mb = mem_info.rss / (1024**2)
                self.labels_proceso['label_proc_ram'].config(text=f"{mem_mb:.1f} MB")
                
                # Estado del proceso
                try:
                    estado = proceso.status()
                    self.labels_proceso['label_proc_estado'].config(text=estado)
                except:
                    self.labels_proceso['label_proc_estado'].config(text="ACTIVO")
                
                # Número de hilos
                try:
                    hilos = proceso.num_threads()
                    self.labels_proceso['label_proc_hilos'].config(text=str(hilos))
                except:
                    self.labels_proceso['label_proc_hilos'].config(text="N/A")
                
                # Usuario
                try:
                    usuario = proceso.username()
                    self.labels_proceso['label_proc_usuario'].config(text=usuario)
                except:
                    self.labels_proceso['label_proc_usuario'].config(text="N/A")
                
                # Tiempo de ejecución
                try:
                    tiempo = time.time() - proceso.create_time()
                    self.labels_proceso['label_proc_tiempo'].config(text=f"{tiempo:.0f}s")
                except:
                    self.labels_proceso['label_proc_tiempo'].config(text="N/A")
                    
            else:
                # Limpiar información si no hay proceso monitoreado
                for label in self.labels_proceso.values():
                    label.config(text="-")
                self.labels_proceso['label_proc_nombre'].config(text="Ninguno")
                self.labels_proceso['label_proc_cpu'].config(text="0%")
                self.labels_proceso['label_proc_ram'].config(text="0 MB")
                self.labels_proceso['label_proc_hilos'].config(text="0")
                
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # El proceso ya no existe
            self.proceso_real_objeto = None
            self.actualizar_info_proceso_monitoreado()

    def actualizar_registros_simulados(self):
        """Actualiza los registros del microprocesador (simulados)"""
        # Simular cambios en los registros
        for registro in self.labels_registros:
            valor_actual = int(self.labels_registros[registro].cget("text"))
            nuevo_valor = (valor_actual + random.randint(0, 10)) % 65536
            self.labels_registros[registro].config(text=str(nuevo_valor))

    def actualizar_graficos(self):
        """Actualiza los gráficos en tiempo real"""
        try:
            self.ax_memoria.clear()
            self.ax_cpu.clear()
            self.ax_procesos.clear()
            
            # Datos de memoria del sistema
            memoria = psutil.virtual_memory()
            mem_usada = memoria.used / (1024**3)
            mem_libre = memoria.available / (1024**3)
            
            # Gráfico de memoria
            self.ax_memoria.pie([mem_usada, mem_libre], 
                               labels=['Usada', 'Libre'], 
                               colors=[self.colores['chart2'], self.colores['chart3']],
                               autopct='%1.1f%%')
            self.ax_memoria.set_title('Uso de Memoria RAM')
            
            # Gráfico de CPU
            cpu_total = psutil.cpu_percent(interval=0.1)
            cpu_proc = 0
            if self.proceso_real_objeto:
                try:
                    cpu_proc = self.proceso_real_objeto.cpu_percent(interval=0.1)
                except:
                    pass
            
            categorias_cpu = ['Sistema', 'Proceso']
            valores_cpu = [cpu_total, cpu_proc]
            colores_cpu = [self.colores['chart1'], self.colores['chart4']]
            
            bars_cpu = self.ax_cpu.bar(categorias_cpu, valores_cpu, color=colores_cpu, alpha=0.8)
            self.ax_cpu.set_ylabel('Uso de CPU (%)')
            self.ax_cpu.set_title('Uso de Procesador')
            self.ax_cpu.set_ylim(0, 100)
            
            # Añadir valores en las barras de CPU
            for bar, valor in zip(bars_cpu, valores_cpu):
                height = bar.get_height()
                self.ax_cpu.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{valor:.1f}%', ha='center', va='bottom')
            
            # Gráfico de procesos (top 5 por memoria)
            procesos = []
            for proc in psutil.process_iter(['name', 'memory_info']):
                try:
                    info = proc.info
                    if info['memory_info']:
                        memoria_mb = info['memory_info'].rss / (1024**2)
                        procesos.append((info['name'] or 'N/A', memoria_mb))
                except:
                    continue
            
            procesos.sort(key=lambda x: x[1], reverse=True)
            top_procesos = procesos[:5]
            
            if top_procesos:
                nombres = [p[0][:15] + '...' if len(p[0]) > 15 else p[0] for p in top_procesos]
                memorias = [p[1] for p in top_procesos]
                
                self.ax_procesos.barh(nombres, memorias, color=self.colores['chart1'])
                self.ax_procesos.set_xlabel('Memoria (MB)')
                self.ax_procesos.set_title('Top 5 Procesos (Memoria)')
            
            # Aplicar estilo a los gráficos
            for ax in [self.ax_memoria, self.ax_cpu, self.ax_procesos]:
                ax.set_facecolor(self.colores['fondo_secundario'])
            
            self.canvas_graficos.draw()
            
        except Exception as e:
            print(f"Error en actualización de gráficos: {e}")

    def actualizar_metricas_sistema(self):
        """Actualiza la tabla de métricas del sistema"""
        try:
            # Limpiar tabla
            for item in self.tree_metricas.get_children():
                self.tree_metricas.delete(item)
            
            # Obtener métricas del sistema
            metricas = []
            
            # Información de CPU
            cpu_per_core = psutil.cpu_percent(percpu=True)
            metricas.extend([
                ("=== INFORMACIÓN DE CPU ===", "=========="),
                ("CPU Total del Sistema", f"{psutil.cpu_percent(interval=0.1):.1f}%"),
                ("Núcleos de CPU Físicos", str(psutil.cpu_count(logical=False))),
                ("Núcleos de CPU Lógicos", str(psutil.cpu_count(logical=True))),
                ("Frecuencia de CPU Actual", f"{psutil.cpu_freq().current:.1f} MHz"),
            ])
            
            # Información de memoria
            memoria = psutil.virtual_memory()
            swap = psutil.swap_memory()
            metricas.extend([
                ("=== INFORMACIÓN DE MEMORIA ===", "=========="),
                ("Memoria RAM Total", f"{memoria.total / (1024**3):.2f} GB"),
                ("Memoria RAM Usada", f"{memoria.used / (1024**3):.2f} GB"),
                ("Memoria RAM Libre", f"{memoria.available / (1024**3):.2f} GB"),
                ("Porcentaje de RAM Usada", f"{memoria.percent:.1f}%"),
                ("Memoria Swap Total", f"{swap.total / (1024**3):.2f} GB"),
                ("Memoria Swap Usada", f"{swap.used / (1024**3):.2f} GB"),
                ("Porcentaje de Swap Usado", f"{swap.percent:.1f}%"),
            ])
            
            # Información de disco
            disco = psutil.disk_usage('/')
            metricas.extend([
                ("=== INFORMACIÓN DE DISCO ===", "=========="),
                ("Espacio en Disco Total", f"{disco.total / (1024**3):.2f} GB"),
                ("Espacio en Disco Usado", f"{disco.used / (1024**3):.2f} GB"),
                ("Espacio en Disco Libre", f"{disco.free / (1024**3):.2f} GB"),
                ("Porcentaje de Disco Usado", f"{disco.percent:.1f}%"),
            ])
            
            # Información de red
            redes = psutil.net_io_counters()
            metricas.extend([
                ("=== INFORMACIÓN DE RED ===", "=========="),
                ("Bytes Enviados", f"{redes.bytes_sent / (1024**2):.2f} MB"),
                ("Bytes Recibidos", f"{redes.bytes_recv / (1024**2):.2f} MB"),
                ("Paquetes Enviados", str(redes.packets_sent)),
                ("Paquetes Recibidos", str(redes.packets_recv)),
            ])
            
            # Información del sistema
            metricas.extend([
                ("=== INFORMACIÓN DEL SISTEMA ===", "=========="),
                ("Tiempo de Actividad del Sistema", f"{time.time() - psutil.boot_time():.0f} segundos"),
                ("Número de Procesos Activos", str(len(psutil.pids()))),
                ("Usuario Actual", psutil.Process().username()),
            ])
            
            # Información del proceso monitoreado (si existe)
            if self.proceso_real_objeto:
                try:
                    proc = self.proceso_real_objeto
                    mem_info = proc.memory_info()
                    metricas.extend([
                        ("=== PROCESO MONITOREADO ===", "=========="),
                        ("Nombre del Proceso", proc.name()),
                        ("PID del Proceso", str(proc.pid)),
                        ("CPU del Proceso", f"{proc.cpu_percent(interval=0.1):.1f}%"),
                        ("Memoria del Proceso", f"{mem_info.rss / (1024**2):.2f} MB"),
                        ("Estado del Proceso", proc.status()),
                        ("Hilos del Proceso", str(proc.num_threads())),
                        ("Tiempo de Ejecución", f"{time.time() - proc.create_time():.0f} segundos"),
                    ])
                except:
                    pass
            
            for metrica, valor in metricas:
                self.tree_metricas.insert('', tk.END, values=(metrica, valor))
                
        except Exception as e:
            print(f"Error actualizando métricas: {e}")

    def actualizar_procesos_sistema(self):
        """Actualiza la tabla de procesos del sistema"""
        try:
            # Limpiar tabla
            for item in self.tree_procesos.get_children():
                self.tree_procesos.delete(item)
            
            # Obtener procesos del sistema
            procesos = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'num_threads', 'username']):
                try:
                    info = proc.info
                    memoria_mb = info['memory_info'].rss / (1024**2) if info['memory_info'] else 0
                    procesos.append((
                        info['pid'],
                        info['name'] or 'N/A',
                        f"{info['cpu_percent'] or 0:.1f}",
                        f"{memoria_mb:.1f}",
                        info['status'] or 'N/A',
                        str(info['num_threads'] or 0),
                        info['username'] or 'N/A'
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Aplicar filtro si existe
            filtro = self.filtro_procesos.get().lower()
            if filtro:
                procesos = [p for p in procesos if filtro in p[1].lower()]
            
            # Ordenar según selección
            orden = self.orden_procesos.get()
            if orden == "memoria":
                procesos.sort(key=lambda x: float(x[3]), reverse=True)
            elif orden == "cpu":
                procesos.sort(key=lambda x: float(x[2]), reverse=True)
            elif orden == "nombre":
                procesos.sort(key=lambda x: x[1].lower())
            elif orden == "pid":
                procesos.sort(key=lambda x: x[0])
            
            # Mostrar procesos
            for proc_info in procesos[:100]:  # Limitar a 100 procesos
                self.tree_procesos.insert('', tk.END, values=proc_info)
                
        except Exception as e:
            print(f"Error actualizando procesos del sistema: {e}")