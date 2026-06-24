import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import time
import csv
import os
import sys
from datetime import datetime
import sqlite3

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 8082
LOG_FILE = 'log_implementacion.csv' # Mantenemos el CSV para compatibilidad, opcional

class Database:
    def __init__(self, db_name="viajes_terrenos.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
        
    def create_tables(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                duration REAL,
                total_samples INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS muestras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                terrain TEXT,
                FOREIGN KEY(session_id) REFERENCES sesiones(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()
        
    def save_session(self, duration, samples_list):
        c = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_samples = len(samples_list)
        c.execute("INSERT INTO sesiones (timestamp, duration, total_samples) VALUES (?, ?, ?)", 
                  (timestamp, duration, total_samples))
        session_id = c.lastrowid
        
        c.executemany("INSERT INTO muestras (session_id, terrain) VALUES (?, ?)",
                      [(session_id, t) for t in samples_list])
        self.conn.commit()
        return session_id
        
    def get_sessions(self):
        c = self.conn.cursor()
        c.execute("SELECT id, timestamp, duration, total_samples FROM sesiones ORDER BY id DESC")
        return c.fetchall()
        
    def get_samples(self, session_id):
        c = self.conn.cursor()
        c.execute("SELECT terrain FROM muestras WHERE session_id = ?", (session_id,))
        return [row[0] for row in c.fetchall()]
        
    def get_all_samples(self):
        c = self.conn.cursor()
        c.execute("SELECT terrain FROM muestras")
        return [row[0] for row in c.fetchall()]
        
    def get_total_duration(self):
        c = self.conn.cursor()
        c.execute("SELECT SUM(duration) FROM sesiones")
        res = c.fetchone()
        return res[0] if res and res[0] else 0.0
        
    def delete_session(self, session_id):
        c = self.conn.cursor()
        c.execute("DELETE FROM muestras WHERE session_id = ?", (session_id,))
        c.execute("DELETE FROM sesiones WHERE id = ?", (session_id,))
        self.conn.commit()

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TFG IA Embebida - Analítica de Terrenos")
        self.root.geometry("800x650")
        
        # Variables de estado
        self.running = False
        self.batch_data = []
        self.is_collecting = False
        self.travel_time_s = 0.0
        
        # Base de datos
        self.db = Database()
        
        self.setup_ui()
        self.refresh_history()
        
    def setup_ui(self):
        # Estilo principal
        style = ttk.Style()
        style.configure("TNotebook", tabposition='nw')
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Pestaña 1: Control del Servidor ---
        self.tab_control = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_control, text="Recepción en Vivo")
        
        self.status_frame = ttk.LabelFrame(self.tab_control, text="Estado de la Conexión")
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_status = ttk.Label(self.status_frame, text="Servidor Apagado", foreground="red", font=("Arial", 12, "bold"))
        self.lbl_status.pack(pady=10)
        
        self.info_frame = ttk.LabelFrame(self.tab_control, text="Información del Lote Actual")
        self.info_frame.pack(side="top", fill="x", padx=10, pady=5)
        
        self.lbl_info = tk.Label(self.info_frame, text="Esperando inicio de programa en STM32...", font=("Arial", 12), wraplength=500)
        self.lbl_info.pack(expand=True, padx=20, pady=10)
        
        self.progress = ttk.Progressbar(self.info_frame, mode='indeterminate')
        
        self.log_frame = ttk.LabelFrame(self.tab_control, text="Registro de Eventos")
        self.log_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)
        
        self.txt_log = tk.Text(self.log_frame, height=10, state="disabled", font=("Consolas", 10))
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.ctrl_frame = ttk.Frame(self.tab_control)
        self.ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_start = ttk.Button(self.ctrl_frame, text="Iniciar Servidor", command=self.start_server)
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(self.ctrl_frame, text="Detener Servidor", command=self.stop_server, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        self.btn_restart = ttk.Button(self.ctrl_frame, text="Reiniciar Servidor", command=self.restart_server)
        self.btn_restart.pack(side="left", padx=5)

        self.btn_hard_reset = ttk.Button(self.ctrl_frame, text="Reset Completo", command=self.hard_reset)
        self.btn_hard_reset.pack(side="right", padx=5)

        # --- Pestaña 2: Historial y Analítica ---
        self.tab_history = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_history, text="Historial de Viajes")
        
        self.hist_frame = ttk.Frame(self.tab_history)
        self.hist_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("id", "fecha", "duracion", "muestras")
        self.tree = ttk.Treeview(self.hist_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha y Hora")
        self.tree.heading("duracion", text="Duración (s)")
        self.tree.heading("muestras", text="Total Muestras")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fecha", width=200, anchor="center")
        self.tree.column("duracion", width=100, anchor="center")
        self.tree.column("muestras", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.hist_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botones de la pestaña de historial
        self.hist_ctrl_frame = ttk.Frame(self.tab_history)
        self.hist_ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_metrics = ttk.Button(self.hist_ctrl_frame, text="📊 Ver Métricas", command=self.show_metrics)
        self.btn_metrics.pack(side="left", padx=5)
        
        self.btn_global_metrics = ttk.Button(self.hist_ctrl_frame, text="🌍 Métricas Globales", command=self.show_global_metrics)
        self.btn_global_metrics.pack(side="left", padx=5)
        
        self.btn_delete = ttk.Button(self.hist_ctrl_frame, text="🗑️ Borrar Viaje", command=self.delete_session)
        self.btn_delete.pack(side="left", padx=5)
        
        self.btn_refresh = ttk.Button(self.hist_ctrl_frame, text="🔄 Actualizar", command=self.refresh_history)
        self.btn_refresh.pack(side="right", padx=5)

    def log_event(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", f"[{timestamp}] {message}\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    def start_server(self):
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_restart.config(state="normal")
        self.lbl_status.config(text=f"Escuchando en puerto {PORT}...", foreground="orange")
        self.log_event("Servidor iniciado.")
        
        self.thread = threading.Thread(target=self.network_loop, daemon=True)
        self.thread.start()

    def stop_server(self):
        self.running = False
        self.lbl_status.config(text="Servidor detenido.", foreground="red")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.btn_restart.config(state="normal")
        self.log_event("Servidor detenido manualmente.")

    def restart_server(self):
        self.log_event("Reiniciando servidor...")
        self.stop_server()
        self.btn_restart.config(state="disabled")
        # Esperamos un poco más que el timeout del socket (1s) para asegurar que el hilo termine
        self.root.after(1500, self.start_server)

    def hard_reset(self):
        if messagebox.askyesno("Reset Completo", "¿Estás seguro de que quieres reiniciar TODA la aplicación?"):
            self.log_event("Ejecutando reset completo del programa...")
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def network_loop(self):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind((HOST, PORT))
                    s.listen(5)
                    s.settimeout(1.0)
                    
                    while self.running:
                        try:
                            conn, addr = s.accept()
                            with conn:
                                # Usamos addr[0] para obtener la IP
                                ip_addr = addr[0]
                                self.root.after(0, lambda: self.on_connect(ip_addr))
                                buffer = ""
                                conn.settimeout(2.0) # Timeout para recv
                                while self.running:
                                    try:
                                        data = conn.recv(4096)
                                        if not data: break
                                        
                                        raw_str = data.decode('utf-8', errors='ignore')
                                        buffer += raw_str
                                        
                                        while '\n' in buffer:
                                            line, buffer = buffer.split('\n', 1)
                                            line = line.strip()
                                            
                                            if "START_BATCH" in line:
                                                self.is_collecting = True
                                                self.batch_data = []
                                                self.root.after(0, self.on_start_batch)
                                            
                                            elif "END_BATCH" in line:
                                                time_ms = 0
                                                if ":" in line:
                                                    try:
                                                        time_ms = int(line.split(":")[1])
                                                    except: pass
                                                self.travel_time_s = time_ms / 1000.0
                                                self.is_collecting = False
                                                self.root.after(0, self.on_end_batch)
                                            
                                            elif "DET:" in line and self.is_collecting:
                                                terrain = line.split("DET:")[1].strip()
                                                self.batch_data.append(terrain)
                                    except socket.timeout:
                                        continue
                                    except ConnectionResetError:
                                        break
                                    except Exception as e:
                                        print(f"Error en recepción: {e}")
                                        break
                                self.root.after(0, self.on_disconnect)
                        except socket.timeout:
                            continue
                        except Exception as e:
                            if self.running:
                                print(f"Error aceptando conexión: {e}")
                            break
            except Exception as e:
                if self.running:
                    self.root.after(0, lambda: self.log_event(f"Error crítico de red: {e}"))
                time.sleep(2)

    def on_connect(self, ip):
        self.lbl_status.config(text=f"Conectado con ESP32: {ip}", foreground="green")
        self.log_event(f"ESP32 conectada desde {ip}")

    def on_disconnect(self):
        self.lbl_status.config(text="ESP32 Desconectada. Esperando...", foreground="orange")
        self.log_event("ESP32 se ha desconectado.")

    def on_start_batch(self):
        self.lbl_info.config(text="Recibiendo lote de datos desde STM32...", foreground="blue")
        self.log_event("Iniciando recepción de lote...")
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.start()

    def on_end_batch(self):
        self.progress.stop()
        self.progress.pack_forget()
        count = len(self.batch_data)
        self.lbl_info.config(text=f"¡Lote Recibido!\n{count} muestras en {round(self.travel_time_s, 2)}s.", foreground="green")
        self.log_event(f"Lote finalizado. Muestras: {count}, Tiempo: {round(self.travel_time_s, 2)}s")
        
        # Guardar en Base de Datos
        if count > 0:
            self.db.save_session(self.travel_time_s, self.batch_data)
            self.refresh_history()
            # Mantenemos también el archivo CSV original para retrocompatibilidad
            self.save_to_csv()
            messagebox.showinfo("Nuevo Viaje Registrado", f"Se ha registrado un nuevo viaje de {round(self.travel_time_s, 2)}s con {count} muestras.")
        else:
            self.log_event("Lote vacío. No se ha guardado.")

    def save_to_csv(self):
        if not self.batch_data: return
        try:
            with open(LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([f"# NUEVA SESION - Duracion: {round(self.travel_time_s, 2)}s"])
                for terrain in self.batch_data:
                    writer.writerow([timestamp, terrain])
        except Exception as e:
            self.log_event(f"Error guardando CSV: {e}")

    def refresh_history(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        sessions = self.db.get_sessions()
        for session in sessions:
            self.tree.insert("", "end", values=(session[0], session[1], round(session[2], 2), session[3]))

    def delete_session(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor, selecciona un viaje del historial para borrar.")
            return
            
        item = self.tree.item(selected[0])
        session_id = int(item['values'][0])
        
        if messagebox.askyesno("Confirmar Borrado", f"¿Estás seguro de que quieres borrar el viaje ID {session_id}?"):
            self.db.delete_session(session_id)
            self.refresh_history()
            self.log_event(f"Viaje ID {session_id} borrado de la base de datos.")

    def show_metrics(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor, selecciona un viaje del historial para ver sus métricas.")
            return
            
        item = self.tree.item(selected[0])
        session_id = int(item['values'][0])
        travel_time_s = float(item['values'][2])
        
        samples = self.db.get_samples(session_id)
        if not samples:
            messagebox.showinfo("Vacío", "El viaje seleccionado no tiene muestras.")
            return
            
        total_muestras = len(samples)
        counts = {}
        for t in samples:
            counts[t] = counts.get(t, 0) + 1
            
        # Ventana de Métricas
        top = tk.Toplevel(self.root)
        top.title(f"Analítica del Viaje ID: {session_id}")
        top.geometry("750x550")
        
        # Frame de Resumen
        sum_frame = ttk.LabelFrame(top, text="Resumen del Viaje")
        sum_frame.pack(fill="x", padx=10, pady=10)
        
        resumen_texto = f"Duración Total: {travel_time_s}s   |   Total Muestras: {total_muestras}\n\n"
        
        for terrain, count in counts.items():
            percentage = (count / total_muestras) * 100
            terrain_time = (count / total_muestras) * travel_time_s
            resumen_texto += f"• {terrain}: {round(percentage, 1)}% ({round(terrain_time, 2)}s est.)\n"
            
        lbl_resumen = ttk.Label(sum_frame, text=resumen_texto, font=("Arial", 11), justify="left")
        lbl_resumen.pack(padx=10, pady=10, anchor="w")
        
        # Frame de Gráficos
        if MATPLOTLIB_AVAILABLE:
            graf_frame = ttk.Frame(top)
            graf_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
            
            labels = list(counts.keys())
            sizes = list(counts.values())
            
            # Pie Chart
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax1.axis('equal')
            ax1.set_title("Proporción de Terrenos")
            
            # Bar Chart
            bars = ax2.bar(labels, sizes, color=plt.cm.Paired.colors)
            ax2.set_ylabel('Nº de Muestras')
            ax2.set_title("Ocurrencias por Terreno")
            plt.xticks(rotation=45, ha="right")
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=graf_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            lbl_no_plot = ttk.Label(top, text="⚠️ Matplotlib no está instalado.\nPara ver gráficos detallados abre una terminal y ejecuta:\npip install matplotlib", foreground="red", font=("Arial", 11, "bold"))
            lbl_no_plot.pack(pady=20)

    def show_global_metrics(self):
        samples = self.db.get_all_samples()
        if not samples:
            messagebox.showinfo("Vacío", "No hay viajes registrados en la base de datos.")
            return
            
        travel_time_s = self.db.get_total_duration()
        total_muestras = len(samples)
        
        counts = {}
        for t in samples:
            counts[t] = counts.get(t, 0) + 1
            
        top = tk.Toplevel(self.root)
        top.title("Analítica Global de Todos los Viajes")
        top.geometry("750x550")
        
        sum_frame = ttk.LabelFrame(top, text="Resumen Global")
        sum_frame.pack(fill="x", padx=10, pady=10)
        
        resumen_texto = f"Duración Total Acumulada: {round(travel_time_s, 2)}s   |   Total Muestras Registradas: {total_muestras}\n\n"
        
        for terrain, count in counts.items():
            percentage = (count / total_muestras) * 100
            terrain_time = (count / total_muestras) * travel_time_s
            resumen_texto += f"• {terrain}: {round(percentage, 1)}% ({round(terrain_time, 2)}s est.)\n"
            
        lbl_resumen = ttk.Label(sum_frame, text=resumen_texto, font=("Arial", 11), justify="left")
        lbl_resumen.pack(padx=10, pady=10, anchor="w")
        
        if MATPLOTLIB_AVAILABLE:
            graf_frame = ttk.Frame(top)
            graf_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
            
            labels = list(counts.keys())
            sizes = list(counts.values())
            
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax1.axis('equal')
            ax1.set_title("Proporción Global de Terrenos")
            
            bars = ax2.bar(labels, sizes, color=plt.cm.Paired.colors)
            ax2.set_ylabel('Nº de Muestras')
            ax2.set_title("Ocurrencias Globales por Terreno")
            plt.xticks(rotation=45, ha="right")
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, master=graf_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            lbl_no_plot = ttk.Label(top, text="⚠️ Matplotlib no está instalado.\nPara ver gráficos detallados abre una terminal y ejecuta:\npip install matplotlib", foreground="red", font=("Arial", 11, "bold"))
            lbl_no_plot.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()
