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

def estandarizar_codigo_dane(df, columna):
    df["CODIGO_DANE"] = (
        df[columna]
        .astype("string")
        .str.strip()
        .str.replace(".0", "", regex=False)
        .str.zfill(5)
    )

    return df

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

# ==========================================
# PASO 4.1 — ESTANDARIZAR DIVIPOLA
# ==========================================

df_divipola.columns = [
    limpiar_nombre_columna(columna)
    for columna in df_divipola.columns
]

print("\nColumnas DIVIPOLA estandarizadas:")
print(df_divipola.columns.tolist())

# ==========================================
# PASO 4.2 — RENOMBRAR COLUMNAS
# ==========================================

df_divipola = df_divipola.rename(columns={
    "CÓDIGO_DEPARTAMENTO": "CODIGO_DEPARTAMENTO",
    "NOMBRE_DEPARTAMENTO": "DEPARTAMENTO",
    "CÓDIGO_MUNICIPIO": "CODIGO_DANE",
    "NOMBRE_MUNICIPIO": "MUNICIPIO",
    "TIPO:_MUNICIPIO_/_ISLA_/_ÁREA_NO_MUNICIPALIZADA": "TIPO_ENTIDAD"
})

# ==========================================
# PASO 4.3 — ESTANDARIZAR CODIGO_DANE
# ==========================================

df_divipola["CODIGO_DANE"] = (
    df_divipola["CODIGO_DANE"]
    .astype("string")
    .str.strip()
    .str.zfill(5)
)

# ==========================================
# PASO 4.4 — VALIDACIÓN
# ==========================================

print("\n--- VALIDACIÓN DIVIPOLA ---")

print("Filas:", len(df_divipola))

print("\nTipo CODIGO_DANE:")
print(df_divipola["CODIGO_DANE"].dtype)

print("\nLongitud de códigos:")
print(
    df_divipola["CODIGO_DANE"]
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nCódigos diferentes de 5:")
print(
    (df_divipola["CODIGO_DANE"].str.len() != 5).sum()
)

print("\nCódigos duplicados:")
print(
    df_divipola["CODIGO_DANE"].duplicated().sum()
)

print("\nCódigos nulos:")
print(
    df_divipola["CODIGO_DANE"].isna().sum()
)

# ==========================================
# PASO 5 — SECUESTROS
# ==========================================

archivo_secuestros = os.path.join(
    CARPETA_PROYECTO,
    "2SECUESTRO_20260903.xlsx"
)

df_secuestros = pd.read_excel(archivo_secuestros)

print("\n==========================================")
print("SECUESTROS")
print("==========================================")

print("Archivo cargado correctamente")
print("Filas:", len(df_secuestros))
print("Columnas:", len(df_secuestros.columns))

print("\nColumnas originales:")
print(df_secuestros.columns.tolist())

df_secuestros.columns = [
    limpiar_nombre_columna(columna)
    for columna in df_secuestros.columns
]

print("\nColumnas después de la transformación:")
print(df_secuestros.columns.tolist())
print("\n--- PERFIL COD_MUNI SECUESTROS ---")

print("Tipo de dato:")
print(df_secuestros["COD_MUNI"].dtype)

print("\nPrimeros 10 valores:")
print(df_secuestros["COD_MUNI"].head(10).tolist())

print("\nLongitudes:")
print(
    df_secuestros["COD_MUNI"]
    .astype(str)
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nValores nulos:")
print(df_secuestros["COD_MUNI"].isna().sum())

df_secuestros = estandarizar_codigo_dane(
    df_secuestros,
    "COD_MUNI"
)

print("\n--- VALIDACIÓN CODIGO_DANE SECUESTROS ---")

print("Tipo de dato:")
print(df_secuestros["CODIGO_DANE"].dtype)

print("\nLongitudes:")
print(
    df_secuestros["CODIGO_DANE"]
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nCódigos diferentes de 5:")
print(
    (df_secuestros["CODIGO_DANE"].str.len() != 5).sum()
)

print("\nValores nulos:")
print(df_secuestros["CODIGO_DANE"].isna().sum())

print("\nPrimeros 10:")
print(df_secuestros["CODIGO_DANE"].head(10).tolist())

# ==========================================
# PASO 6 — EXTORSIÓN
# ==========================================

archivo_extorsion = os.path.join(
    CARPETA_PROYECTO,
    "3EXTORSIÓN_20260904.xlsx"
)

df_extorsion = pd.read_excel(archivo_extorsion)

print("\n==========================================")
print("EXTORSIÓN")
print("==========================================")

print("Archivo cargado correctamente")
print("Filas:", len(df_extorsion))
print("Columnas:", len(df_extorsion.columns))

print("\nColumnas originales:")
print(df_extorsion.columns.tolist())

df_extorsion.columns = [
    limpiar_nombre_columna(columna)
    for columna in df_extorsion.columns
]

print("\nColumnas estandarizadas:")
print(df_extorsion.columns.tolist())

print("\n--- PERFIL COD_MUNI EXTORSIÓN ---")

print("Tipo de dato:")
print(df_extorsion["COD_MUNI"].dtype)

print("\nLongitudes:")
print(
    df_extorsion["COD_MUNI"]
    .astype(str)
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nValores nulos:")
print(df_extorsion["COD_MUNI"].isna().sum())

df_extorsion = estandarizar_codigo_dane(
    df_extorsion,
    "COD_MUNI"
)

print("\n--- VALIDACIÓN CODIGO_DANE EXTORSIÓN ---")

print("Tipo:")
print(df_extorsion["CODIGO_DANE"].dtype)

print("\nLongitudes:")
print(
    df_extorsion["CODIGO_DANE"]
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nCódigos diferentes de 5:")
print(
    (df_extorsion["CODIGO_DANE"].str.len() != 5).sum()
)

print("\nNulos:")
print(df_extorsion["CODIGO_DANE"].isna().sum())

# ==========================================
# PASO 7 — TERRORISMO
# ==========================================

archivo_terrorismo = os.path.join(
    CARPETA_PROYECTO,
    "1Reporte_Delito_Terrorismo_Policía_Nacional_2019 A 2025.xlsx"
)

df_terrorismo = pd.read_excel(archivo_terrorismo)

print("\n==========================================")
print("TERRORISMO")
print("==========================================")

print("Archivo cargado correctamente")
print("Filas:", len(df_terrorismo))
print("Columnas:", len(df_terrorismo.columns))

print("\nColumnas originales:")
print(df_terrorismo.columns.tolist())

df_terrorismo.columns = [
    limpiar_nombre_columna(columna)
    for columna in df_terrorismo.columns
]

print("\nColumnas estandarizadas:")
print(df_terrorismo.columns.tolist())

print(df_terrorismo.columns.tolist())

# ==========================================
# PERFIL CODIGO_DANE - TERRORISMO
# ==========================================

print("\n--- PERFIL CODIGO_DANE TERRORISMO ---")

print("Tipo de dato:")
print(df_terrorismo["CODIGO_DANE"].dtype)

print("\nPrimeros 10 valores:")
print(df_terrorismo["CODIGO_DANE"].head(10).tolist())

print("\nLongitudes:")
print(
    df_terrorismo["CODIGO_DANE"]
    .astype(str)
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nValores nulos:")
print(df_terrorismo["CODIGO_DANE"].isna().sum())

# ==========================================
# TRANSFORMACIÓN CODIGO_DANE - TERRORISMO
# ==========================================

df_terrorismo["CODIGO_DANE"] = (
    df_terrorismo["CODIGO_DANE"]
    .astype("string")
    .str[:5]
)

print("\n--- VALIDACIÓN CODIGO_DANE TERRORISMO ---")

print("Tipo:")
print(df_terrorismo["CODIGO_DANE"].dtype)

print("\nLongitudes:")
print(
    df_terrorismo["CODIGO_DANE"]
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nCódigos diferentes de 5:")
print(
    (df_terrorismo["CODIGO_DANE"].str.len() != 5).sum()
)

print("\nNulos:")
print(df_terrorismo["CODIGO_DANE"].isna().sum())

print("\nPrimeros 10:")
print(
    df_terrorismo["CODIGO_DANE"]
    .head(10)
    .tolist()
)

print("\n--- MUESTRA CODIGOS TERRORISMO ---")

print(
    df_terrorismo[
        ["DEPARTAMENTO", "MUNICIPIO", "CODIGO_DANE"]
    ].head(20).to_string(index=False)
)

print("\n--- CRUCE TERRORISMO VS DIVIPOLA ---")

codigos_terrorismo = set(
    df_terrorismo["CODIGO_DANE"].dropna()
)

codigos_divipola = set(
    df_divipola["CODIGO_DANE"].dropna()
)

codigos_no_encontrados = codigos_terrorismo - codigos_divipola

print("Códigos únicos Terrorismo:", len(codigos_terrorismo))
print("Códigos únicos DIVIPOLA:", len(codigos_divipola))
print("Códigos de Terrorismo NO encontrados en DIVIPOLA:",
      len(codigos_no_encontrados))

print("\nCódigos no encontrados:")
print(sorted(codigos_no_encontrados))

print("\n--- CÓDIGOS TERRORISMO NO ENCONTRADOS EN DIVIPOLA ---")

territorios_no_encontrados = (
    df_terrorismo[
        df_terrorismo["CODIGO_DANE"].isin(codigos_no_encontrados)
    ][
        ["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO"]
    ]
    .drop_duplicates()
    .sort_values("CODIGO_DANE")
)

print(territorios_no_encontrados.to_string(index=False))

print("\n--- COMPARACIÓN POR NOMBRE ---")

comparacion_nombres = (
    df_terrorismo[
        df_terrorismo["CODIGO_DANE"].isin(codigos_no_encontrados)
    ][["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO"]]
    .drop_duplicates()
    .merge(
        df_divipola[["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO"]],
        on=["MUNICIPIO"],
        how="left",
        suffixes=("_TERRORISMO", "_DIVIPOLA")
    )
)

print(comparacion_nombres.to_string(index=False))

print("\n--- PRUEBA DE TRANSFORMACIÓN TERRORISMO ---")

muestra = df_terrorismo["CODIGO_DANE"].head(10)

for codigo in muestra:
    numero = int(codigo)
    codigo_correcto = str(numero // 1000).zfill(5)
    print(codigo, "→", codigo_correcto)

    # RECARGAR TERRORISMO DESDE EL ARCHIVO ORIGINAL

df_terrorismo = pd.read_excel(archivo_terrorismo)

df_terrorismo.columns = [
    limpiar_nombre_columna(columna)
    for columna in df_terrorismo.columns
]

print("\n--- TERRORISMO ORIGINAL RECARGADO ---")
print(df_terrorismo["CODIGO_DANE"].head(10).tolist())
print(df_terrorismo["CODIGO_DANE"].dtype)

# ESTANDARIZAR CÓDIGO DANE DE TERRORISMO

df_terrorismo["CODIGO_DANE"] = (
    pd.to_numeric(df_terrorismo["CODIGO_DANE"], errors="coerce")
    .floordiv(1000)
    .astype("Int64")
    .astype("string")
    .str.zfill(5)
)

print("\n--- VALIDACIÓN CODIGO_DANE TERRORISMO ---")
print("Tipo:")
print(df_terrorismo["CODIGO_DANE"].dtype)

print("\nLongitudes:")
print(
    df_terrorismo["CODIGO_DANE"]
    .str.len()
    .value_counts()
    .sort_index()
)

print("\nCódigos diferentes de 5:")
print(
    (df_terrorismo["CODIGO_DANE"].str.len() != 5).sum()
)

print("\nNulos:")
print(df_terrorismo["CODIGO_DANE"].isna().sum())

print("\nPrimeros 10:")
print(df_terrorismo["CODIGO_DANE"].head(10).tolist())

print("\n--- CRUCE TERRORISMO VS DIVIPOLA ---")

codigos_terrorismo = set(
    df_terrorismo["CODIGO_DANE"].dropna()
)

codigos_divipola = set(
    df_divipola["CODIGO_DANE"].dropna()
)

codigos_no_encontrados = codigos_terrorismo - codigos_divipola

print("Códigos únicos Terrorismo:", len(codigos_terrorismo))
print("Códigos únicos DIVIPOLA:", len(codigos_divipola))
print(
    "Códigos de Terrorismo NO encontrados en DIVIPOLA:",
    len(codigos_no_encontrados)
)

print("\nCódigos no encontrados:")
print(sorted(codigos_no_encontrados))

print("\n--- CONSISTENCIA MUNICIPIO TERRORISMO VS DIVIPOLA ---")

comparacion_territorial = (
    df_terrorismo[
        ["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO"]
    ]
    .drop_duplicates()
    .merge(
        df_divipola[
            ["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO"]
        ],
        on="CODIGO_DANE",
        how="left",
        suffixes=("_TERRORISMO", "_DIVIPOLA")
    )
)

diferencias_nombre = comparacion_territorial[
    comparacion_territorial["MUNICIPIO_TERRORISMO"]
    != comparacion_territorial["MUNICIPIO_DIVIPOLA"]
]

print("Territorios comparados:", len(comparacion_territorial))
print("Diferencias de nombre:", len(diferencias_nombre))

print("\nPrimeras diferencias:")
print(
    diferencias_nombre.head(20).to_string(index=False)
)

import unicodedata

def normalizar_nombre(nombre):
    if pd.isna(nombre):
        return ""
    
    nombre = str(nombre).upper().strip()
    
    # Quitar (CT)
    nombre = nombre.replace("(CT)", "")
    
    # Quitar tildes
    nombre = unicodedata.normalize("NFD", nombre)
    nombre = "".join(
        caracter for caracter in nombre
        if unicodedata.category(caracter) != "Mn"
    )
    
    # Normalizar espacios
    nombre = " ".join(nombre.split())
    
    return nombre

comparacion_territorial["NOMBRE_TERRORISMO_NORMALIZADO"] = (
    comparacion_territorial["MUNICIPIO_TERRORISMO"]
    .apply(normalizar_nombre)
)

comparacion_territorial["NOMBRE_DIVIPOLA_NORMALIZADO"] = (
    comparacion_territorial["MUNICIPIO_DIVIPOLA"]
    .apply(normalizar_nombre)
)

diferencias_reales = comparacion_territorial[
    comparacion_territorial["NOMBRE_TERRORISMO_NORMALIZADO"]
    != comparacion_territorial["NOMBRE_DIVIPOLA_NORMALIZADO"]
]

print("\n--- DIFERENCIAS REALES DE DENOMINACIÓN ---")
print("Territorios comparados:", len(comparacion_territorial))
print("Diferencias después de normalizar:",
      len(diferencias_reales))

print("\nPrimeras diferencias:")
print(
    diferencias_reales[
        [
            "CODIGO_DANE",
            "MUNICIPIO_TERRORISMO",
            "MUNICIPIO_DIVIPOLA"
        ]
    ].head(30).to_string(index=False)
)

print("\n--- DUPLICADOS EXACTOS TERRORISMO ---")

duplicados_exactos = df_terrorismo.duplicated(keep=False)

print("Registros duplicados exactos:",
      duplicados_exactos.sum())

print("Porcentaje:",
      round(duplicados_exactos.mean() * 100, 2), "%")

print("\n--- EJEMPLOS DE DUPLICADOS EXACTOS ---")

print(
    df_terrorismo[
        df_terrorismo.duplicated(keep=False)
    ]
    .sort_values(
        ["CODIGO_DANE", "FECHA_HECHO"]
    )
    .head(20)
    .to_string(index=False)
)

print("\n--- IMPACTO DE DUPLICADOS EXACTOS ---")

filas_originales = len(df_terrorismo)

filas_sin_duplicados = len(
    df_terrorismo.drop_duplicates()
)

filas_eliminadas = filas_originales - filas_sin_duplicados

print("Filas originales:", filas_originales)
print("Filas después de eliminar duplicados:", filas_sin_duplicados)
print("Filas duplicadas que se eliminarían:", filas_eliminadas)
print(
    "Porcentaje de filas afectadas:",
    round(filas_eliminadas / filas_originales * 100, 2),
    "%"
)

print("\n--- IMPACTO SOBRE CANTIDAD ---")

cantidad_original = df_terrorismo["CANTIDAD"].sum()

cantidad_sin_duplicados = (
    df_terrorismo
    .drop_duplicates()["CANTIDAD"]
    .sum()
)

cantidad_duplicada = (
    cantidad_original - cantidad_sin_duplicados
)

porcentaje_cantidad = (
    cantidad_duplicada / cantidad_original * 100
)

print("CANTIDAD total original:", cantidad_original)
print("CANTIDAD después de deduplicar:", cantidad_sin_duplicados)
print("CANTIDAD asociada a copias redundantes:", cantidad_duplicada)
print(
    "Porcentaje de CANTIDAD afectada:",
    round(porcentaje_cantidad, 2),
    "%"
)