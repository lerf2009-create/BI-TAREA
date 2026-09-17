#Transformación de bases
#Paso 1 — RAW
#Primero cargamos el archivo sin modificar absolutamente nada.


import pandas as pd
import os

CARPETA_PROYECTO = r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA"

archivo_homicidios = os.path.join(
    CARPETA_PROYECTO,
    "7HOMICIDIO_20260903 (1).xlsx"
)

df_homicidios = pd.read_excel(archivo_homicidios)

print("Archivo cargado correctamente")
print("Filas:", len(df_homicidios))
print("Columnas:", len(df_homicidios.columns))
print("Nombres de columnas:")
print(df_homicidios.columns.tolist())

def limpiar_nombre_columna(columna):
    columna = str(columna)
    columna = columna.strip()
    columna = columna.upper()
    columna = columna.replace(" ", "_")
    columna = columna.replace("-", "_")

    return columna

df_homicidios.columns = [
    limpiar_nombre_columna(columna)
    for columna in df_homicidios.columns
]

print("Columnas después de la transformación:")
print(df_homicidios.columns.tolist())

print("\n--- PERFIL COD_MUNI ---")

print("Tipo de dato:")
print(df_homicidios["COD_MUNI"].dtype)

print("\nPrimeros 10 valores:")
print(df_homicidios["COD_MUNI"].head(10).tolist())

print("\nLongitudes:")
print(
    df_homicidios["COD_MUNI"]
    .astype(str)
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nValores nulos:")
print(df_homicidios["COD_MUNI"].isna().sum())

df_homicidios["CODIGO_DANE"] = (
    df_homicidios["COD_MUNI"]
    .astype("string")
    .str.strip()
    .str.zfill(5)
)

print("\n--- VALIDACIÓN CODIGO_DANE ---")

print("Tipo de dato:")
print(df_homicidios["CODIGO_DANE"].dtype)

print("\nLongitud de los códigos:")
print(
    df_homicidios["CODIGO_DANE"]
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nCódigos con longitud diferente de 5:")
print(
    (df_homicidios["CODIGO_DANE"].str.len() != 5).sum()
)

print("\nPrimeros 10 códigos:")
print(df_homicidios["CODIGO_DANE"].head(10).tolist())


print('Se inicia cargue de DIVIPOLA')
# ==========================================
# PASO 4 — CARGAR DIVIPOLA
# ==========================================

archivo_divipola = os.path.join(
    CARPETA_PROYECTO,
    "5DIVIPOLA-_Códigos_municipios_20260903vf.xlsx"
)

df_divipola = pd.read_excel(archivo_divipola)

print("\n--- DIVIPOLA ---")

print("Filas:", len(df_divipola))
print("Columnas:", len(df_divipola.columns))

print("\nNombres de columnas:")
print(df_divipola.columns.tolist())

print("\nPrimeras filas:")
print(df_divipola.head())