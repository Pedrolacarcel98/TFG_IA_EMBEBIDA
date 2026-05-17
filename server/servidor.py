import socket
import csv

HOST = '0.0.0.0'
PORT = 8082

print(f"Esperando conexión en el puerto {PORT}...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    
    with conn:
        print(f"¡ESP32 conectada desde {addr}!")
        
        # Abrimos el CSV en modo escritura sin encabezados
        with open('datos_entrenamiento.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            buffer = ""
            
            while True:
                try:
                    # Leemos fragmentos grandes de red
                    data = conn.recv(8192)
                    if not data:
                        break
                    
                    buffer += data.decode('utf-8')
                    
                    # Si recibimos un salto de línea, analizamos el bloque
                    if '\n' in buffer:
                        lineas = buffer.split('\n')
                        
                        # Procesamos todas las líneas completas
                        for l in lineas[:-1]:
                            raw_data = l.strip().split(',')
                            
                            # FILTRO ESTRICTO: 64 muestras * 3 ejes = 192 columnas exactas
                            if len(raw_data) == 192:
                                writer.writerow(raw_data)
                                print("Ventana guardada perfecta -> (192 valores)")
                            elif len(raw_data) > 0:
                                print(f"Descartada línea corrupta (Tenía {len(raw_data)} valores en lugar de 192)")
                        
                        # Mantenemos el fragmento incompleto para el próximo ciclo
                        buffer = lineas[-1]
                        
                        # Forzamos escritura en disco
                        f.flush()
                        
                except Exception as e:
                    print(f"Desconexión o error de red: {e}")
                    break

print("Proceso finalizado. El archivo 'datos_entrenamiento.csv' está listo para NanoEdge AI Studio.")