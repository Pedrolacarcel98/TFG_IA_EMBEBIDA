import pandas as pd

# Cargar los datos originales
try:
    df = pd.read_csv('datos_nanoedge.csv', header=None)
    
    # 1. Convertir a numérico y eliminar lo que no sea número (borra la línea 40 corrupta)
    df_numeric = df.apply(pd.to_numeric, errors='coerce')
    df_clean = df_numeric.dropna()
    
    # 2. Eliminar la ventana del choque (Index 10)
    # Usamos errors='ignore' por si ya fue borrada
    df_final = df_clean.drop(index=10, errors='ignore')
    
    # 3. Guardar el archivo definitivo
    df_final.to_csv('datos_normales_listos.csv', index=False, header=False)
    
    print("¡Archivo 'datos_normales_listos.csv' generado con éxito!")
    print(f"Líneas finales: {len(df_final)}")
except Exception as e:
    print(f"Error al limpiar: {e}")