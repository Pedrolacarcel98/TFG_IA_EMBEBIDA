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
        self.root.title("TFG IA Embebida - Clasificación en Tiempo Real")
        self.root.geometry("600x500")
        
        self.running = False
        self.data_log = []
        self.start_time = None
        
        # Estadísticas en vivo
        self.stats = {"REPOSO": 0, "LISO": 0, "SUELO PIEDRA": 0, "ASFALTO_RUGOSO": 0, "DESCONOCIDO": 0}
        self.last_terrain = None
        self.last_switch_time = None

        self.setup_ui()
        
    def setup_ui(self):
        # Frame Superior: Estado de conexión
        self.status_frame = ttk.LabelFrame(self.root, text="Estado del Sistema")
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_status = ttk.Label(self.status_frame, text="Esperando conexión...", foreground="blue", font=("Arial", 12, "bold"))
        self.lbl_status.pack(pady=10)
        
        # Frame Central: Terreno Actual
        self.terrain_frame = ttk.LabelFrame(self.root, text="Detección en Tiempo Real")
        self.terrain_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.lbl_terrain = tk.Label(self.terrain_frame, text="---", font=("Arial", 40, "bold"), bg="gray", fg="white")
        self.lbl_terrain.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Frame Inferior: Controles
        self.ctrl_frame = ttk.Frame(self.root)
        self.ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_start = ttk.Button(self.ctrl_frame, text="Iniciar Servidor", command=self.start_server)
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(self.ctrl_frame, text="Parar y Guardar", command=self.stop_server, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_stats = ttk.Button(self.ctrl_frame, text="Ver Métricas", command=self.show_metrics, state="disabled")
        self.btn_stats.pack(side="right", padx=5)

    def start_server(self):
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.lbl_status.config(text=f"Escuchando en puerto {PORT}...", foreground="orange")
        self.start_time = time.time()
        self.last_switch_time = self.start_time
        
        self.thread = threading.Thread(target=self.network_loop, daemon=True)
        self.thread.start()

    def stop_server(self):
        self.running = False
        self.lbl_status.config(text="Servidor detenido.", foreground="red")
        self.save_data()
        self.btn_stop.config(state="disabled")
        self.btn_stats.config(state="normal")
        messagebox.showinfo("Éxito", f"Sesión finalizada. Datos guardados en {LOG_FILE}")

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
                        self.root.after(0, lambda: self.lbl_status.config(text=f"Conectado: {addr[0]}", foreground="green"))
                        buffer = ""
                        while self.running:
                            data = conn.recv(1024)
                            if not data: break
                            
                            raw_str = data.decode('utf-8', errors='ignore')
                            print(f"[DEBUG RAW]: {raw_str.strip()}") # Ver qué llega exactamente
                            
                            buffer += raw_str
                            while '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                                line = line.strip()
                                if "DET:" in line:
                                    terrain = line.split("DET:")[1].strip()
                                    print(f"[SERVER]: Detectado -> {terrain}")
                                    self.root.after(0, lambda t=terrain: self.update_terrain_ui(t))
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error: {e}")
                    break

    def update_terrain_ui(self, terrain):
        now = time.time()
        
        # Calcular duración en el terreno anterior
        if self.last_terrain:
            duration = now - self.last_switch_time
            self.stats[self.last_terrain] = self.stats.get(self.last_terrain, 0) + duration
            self.data_log.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.last_terrain, round(duration, 2)])
        
        self.last_terrain = terrain
        self.last_switch_time = now
        
        # Actualizar UI
        colors = {"REPOSO": "gray", "LISO": "green", "SUELO PIEDRA": "orange", "ASFALTO_RUGOSO": "red", "DESCONOCIDO": "black"}
        self.lbl_terrain.config(text=terrain.upper(), bg=colors.get(terrain, "black"))

    def save_data(self):
        # Añadir el último tramo
        if self.last_terrain:
            duration = time.time() - self.last_switch_time
            self.stats[self.last_terrain] += duration
            self.data_log.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.last_terrain, round(duration, 2)])
            
        with open(LOG_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Terreno", "Duracion(s)"])
            writer.writerows(self.data_log)

    def show_metrics(self):
        total_time = sum(self.stats.values())
        if total_time == 0: return
        
        msg = f"Tiempo Total: {round(total_time, 2)}s\n\n"
        for terrain, duration in self.stats.items():
            percentage = (duration / total_time) * 100
            msg += f"- {terrain}: {round(duration, 2)}s ({round(percentage, 1)}%)\n"
            
        messagebox.showinfo("Estadísticas de la Sesión", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()
