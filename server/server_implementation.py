import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import time
import csv
from datetime import datetime

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 8082
LOG_FILE = 'log_implementacion.csv'

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TFG IA Embebida - Monitor de Terrenos (Modo Lote)")
        self.root.geometry("650x550")
        
        self.running = False
        self.batch_data = []
        self.is_collecting = False
        self.travel_time_s = 0.0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame Superior: Estado de conexión
        self.status_frame = ttk.LabelFrame(self.root, text="Estado de la Conexión")
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_status = ttk.Label(self.status_frame, text="Servidor Apagado", foreground="red", font=("Arial", 12, "bold"))
        self.lbl_status.pack(pady=10)
        
        # Frame Central: Información de Lote e Historial de Eventos
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Información del Lote")
        self.info_frame.pack(side="top", fill="x", pady=5)
        
        self.lbl_info = tk.Label(self.info_frame, text="Esperando inicio de programa en STM32...", font=("Arial", 12), wraplength=500)
        self.lbl_info.pack(expand=True, padx=20, pady=10)
        
        self.progress = ttk.Progressbar(self.info_frame, mode='indeterminate')
        
        self.log_frame = ttk.LabelFrame(self.main_frame, text="Registro de Eventos")
        self.log_frame.pack(side="bottom", fill="both", expand=True, pady=5)
        
        self.txt_log = tk.Text(self.log_frame, height=10, state="disabled", font=("Consolas", 10))
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame Inferior: Controles
        self.ctrl_frame = ttk.Frame(self.root)
        self.ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_start = ttk.Button(self.ctrl_frame, text="Iniciar Servidor", command=self.start_server)
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(self.ctrl_frame, text="Detener Servidor", command=self.stop_server, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_stats = ttk.Button(self.ctrl_frame, text="Ver Últimas Métricas", command=self.show_metrics, state="disabled")
        self.btn_stats.pack(side="right", padx=5)

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
        self.lbl_status.config(text=f"Escuchando en puerto {PORT}...", foreground="orange")
        self.log_event("Servidor iniciado.")
        
        self.thread = threading.Thread(target=self.network_loop, daemon=True)
        self.thread.start()

    def stop_server(self):
        self.running = False
        self.lbl_status.config(text="Servidor detenido.", foreground="red")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.log_event("Servidor detenido manualmente.")

    def network_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen(1)
            s.settimeout(1.0)
            
            while self.running:
                try:
                    conn, addr = s.accept()
                    with conn:
                        self.root.after(0, lambda: self.on_connect(addr[0]))
                        buffer = ""
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
                                        # Extraer tiempo si existe (END_BATCH:ms)
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
                            except ConnectionResetError:
                                break 
                        self.root.after(0, self.on_disconnect)
                                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error en servidor: {e}")
                    time.sleep(1)
                    continue

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
        self.btn_stats.config(state="disabled")

    def on_end_batch(self):
        self.progress.stop()
        self.progress.pack_forget()
        count = len(self.batch_data)
        self.lbl_info.config(text=f"¡Lote Recibido!\n{count} muestras en {round(self.travel_time_s, 2)}s.", foreground="green")
        self.log_event(f"Lote finalizado. Muestras: {count}, Tiempo: {round(self.travel_time_s, 2)}s")
        self.btn_stats.config(state="normal")
        messagebox.showinfo("Datos Obtenidos", f"Sesión de {round(self.travel_time_s, 2)} segundos finalizada.\nSe han recibido {count} muestras.")
        self.save_to_csv()

    def save_to_csv(self):
        if not self.batch_data: return
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Registramos el lote con su duración total
            writer.writerow([f"# NUEVA SESION - Duracion: {round(self.travel_time_s, 2)}s"])
            for terrain in self.batch_data:
                writer.writerow([timestamp, terrain])

    def show_metrics(self):
        if not self.batch_data:
            messagebox.showwarning("Sin datos", "No hay datos en el último lote.")
            return
            
        total_muestras = len(self.batch_data)
        counts = {}
        for t in self.batch_data:
            counts[t] = counts.get(t, 0) + 1
            
        msg = f"--- RESULTADOS DE LA SESIÓN ---\n"
        msg += f"Tiempo Total de Viaje: {round(self.travel_time_s, 2)}s\n"
        msg += f"Total Muestras: {total_muestras}\n\n"
        
        for terrain, count in counts.items():
            percentage = (count / total_muestras) * 100
            # Tiempo estimado en este terreno basado en el porcentaje del tiempo total
            terrain_time = (count / total_muestras) * self.travel_time_s
            msg += f"- {terrain}:\n"
            msg += f"  Proporción: {round(percentage, 1)}%\n"
            msg += f"  Tiempo Est.: {round(terrain_time, 2)}s\n\n"
            
        messagebox.showinfo("Métricas del Viaje", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()
