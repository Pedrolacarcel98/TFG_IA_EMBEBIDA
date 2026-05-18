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
        self.root.geometry("600x450")
        
        self.running = False
        self.batch_data = []
        self.is_collecting = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame Superior: Estado de conexión
        self.status_frame = ttk.LabelFrame(self.root, text="Estado de la Conexión")
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_status = ttk.Label(self.status_frame, text="Servidor Apagado", foreground="red", font=("Arial", 12, "bold"))
        self.lbl_status.pack(pady=10)
        
        # Frame Central: Información de Lote
        self.info_frame = ttk.LabelFrame(self.root, text="Información del Lote de Datos")
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.lbl_info = tk.Label(self.info_frame, text="Esperando inicio de programa en STM32...", font=("Arial", 14), wraplength=500)
        self.lbl_info.pack(expand=True, padx=20, pady=20)
        
        self.progress = ttk.Progressbar(self.info_frame, mode='indeterminate')
        
        # Frame Inferior: Controles
        self.ctrl_frame = ttk.Frame(self.root)
        self.ctrl_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_start = ttk.Button(self.ctrl_frame, text="Iniciar Servidor", command=self.start_server)
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_stop = ttk.Button(self.ctrl_frame, text="Detener Servidor", command=self.stop_server, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_stats = ttk.Button(self.ctrl_frame, text="Ver Últimas Métricas", command=self.show_metrics, state="disabled")
        self.btn_stats.pack(side="right", padx=5)

    def start_server(self):
        self.running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.lbl_status.config(text=f"Escuchando en puerto {PORT}...", foreground="orange")
        
        self.thread = threading.Thread(target=self.network_loop, daemon=True)
        self.thread.start()

    def stop_server(self):
        self.running = False
        self.lbl_status.config(text="Servidor detenido.", foreground="red")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

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
                        self.root.after(0, lambda: self.lbl_status.config(text=f"Conectado con ESP32: {addr[0]}", foreground="green"))
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
                                        self.is_collecting = False
                                        self.root.after(0, self.on_end_batch)
                                    
                                    elif "DET:" in line and self.is_collecting:
                                        terrain = line.split("DET:")[1].strip()
                                        self.batch_data.append(terrain)
                            except ConnectionResetError:
                                break 
                        self.root.after(0, lambda: self.lbl_status.config(text="ESP32 Desconectado. Esperando...", foreground="orange"))
                                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error en servidor: {e}")
                    time.sleep(1) # Evitar bucle infinito de errores acelerado
                    continue # Seguir escuchando

    def on_start_batch(self):
        self.lbl_info.config(text="Recibiendo lote de datos desde STM32...", foreground="blue")
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.start()
        self.btn_stats.config(state="disabled")

    def on_end_batch(self):
        self.progress.stop()
        self.progress.pack_forget()
        count = len(self.batch_data)
        self.lbl_info.config(text=f"¡ÉXITO!\nLote de {count} muestras recibido correctamente.", foreground="green")
        self.btn_stats.config(state="normal")
        messagebox.showinfo("Datos Obtenidos", f"Se han recibido {count} muestras de clasificación.\nHaga clic en 'Ver Últimas Métricas' para el análisis.")
        self.save_to_csv()

    def save_to_csv(self):
        if not self.batch_data: return
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for terrain in self.batch_data:
                writer.writerow([timestamp, terrain, 0.1]) # 0.1s por muestra aprox

    def show_metrics(self):
        if not self.batch_data:
            messagebox.showwarning("Sin datos", "No hay datos en el último lote.")
            return
            
        total = len(self.batch_data)
        counts = {}
        for t in self.batch_data:
            counts[t] = counts.get(t, 0) + 1
            
        msg = f"Métricas del Último Lote ({total} muestras):\n\n"
        for terrain, count in counts.items():
            percentage = (count / total) * 100
            msg += f"- {terrain}: {count} muestras ({round(percentage, 1)}%)\n"
            
        messagebox.showinfo("Estadísticas del Lote", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()
