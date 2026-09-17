# ============================================================
# ETL - ÍNDICE INTEGRAL DE RIESGO MUNICIPAL
# Especialización en Analítica de Datos e IA
# ============================================================

import pandas as pd
import os


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

CARPETA_PROYECTO = r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA"


# ============================================================
# 2. RUTAS DE LOS ARCHIVOS RAW
# ============================================================

archivo_homicidios = os.path.join(
    CARPETA_PROYECTO,
    "7HOMICIDIO_20260903 (1).xlsx"
)

archivo_secuestros = os.path.join(
    CARPETA_PROYECTO,
    "2SECUESTRO_20260903.xlsx"
)

archivo_extorsion = os.path.join(
    CARPETA_PROYECTO,
    "3EXTORSIÓN_20260904.xlsx"
)

archivo_terrorismo = os.path.join(
    CARPETA_PROYECTO,
    "1Reporte_Delito_Terrorismo_Policía_Nacional_2019 A 2025.xlsx"
)

archivo_coca = os.path.join(
    CARPETA_PROYECTO,
    "4Detección_de_Cultivos_de_Coca_(hectáreas)_20260903.xlsx"
)

archivo_divipola = os.path.join(
    CARPETA_PROYECTO,
    "5DIVIPOLA-_Códigos_municipios_20260903vf.xlsx"
)


# ============================================================
# 3. CARGAR LAS FUENTES
# ============================================================

print("=" * 60)
print("CARGANDO FUENTES RAW")
print("=" * 60)


df_homicidios = pd.read_excel(archivo_homicidios)
df_secuestros = pd.read_excel(archivo_secuestros)
df_extorsion = pd.read_excel(archivo_extorsion)
df_terrorismo = pd.read_excel(archivo_terrorismo)
df_coca = pd.read_excel(archivo_coca)
df_divipola = pd.read_excel(archivo_divipola)


# ============================================================
# 4. CONTROL INICIAL
# ============================================================

fuentes = {
    "Homicidios": df_homicidios,
    "Secuestros": df_secuestros,
    "Extorsión": df_extorsion,
    "Terrorismo": df_terrorismo,
    "Coca": df_coca,
    "DIVIPOLA": df_divipola
}

for nombre, df in fuentes.items():

    print("\n" + "-" * 60)
    print(nombre)
    print("-" * 60)

    print("Filas:", len(df))
    print("Columnas:", len(df.columns))
    print("Columnas:", df.columns.tolist())


print("\n" + "=" * 60)
print("TODAS LAS FUENTES FUERON CARGADAS")
print("=" * 60)

# ============================================================
# 5. ESTANDARIZAR NOMBRES DE COLUMNAS
# ============================================================

def limpiar_nombre_columna(columna):

    columna = str(columna)
    columna = columna.strip()
    columna = columna.upper()
    columna = columna.replace(" ", "_")
    columna = columna.replace("-", "_")

    return columna


for nombre, df in fuentes.items():

    df.columns = [
        limpiar_nombre_columna(columna)
        for columna in df.columns
    ]


print("\n" + "=" * 60)
print("COLUMNAS ESTANDARIZADAS")
print("=" * 60)

for nombre, df in fuentes.items():

    print("\n" + nombre)
    print(df.columns.tolist())  

# ============================================================
# 6. HOMOLOGAR NOMBRES DE CAMPOS
# ============================================================

df_homicidios = df_homicidios.rename(columns={
    "COD_MUNI": "CODIGO_DANE"
})

df_secuestros = df_secuestros.rename(columns={
    "COD_MUNI": "CODIGO_DANE"
})

df_extorsion = df_extorsion.rename(columns={
    "COD_MUNI": "CODIGO_DANE"
})

df_coca = df_coca.rename(columns={
    "CODDEPTO": "CODIGO_DEPARTAMENTO",
    "CODMPIO": "CODIGO_DANE"
})

df_divipola = df_divipola.rename(columns={
    "CÓDIGO_DEPARTAMENTO": "CODIGO_DEPARTAMENTO",
    "NOMBRE_DEPARTAMENTO": "DEPARTAMENTO",
    "CÓDIGO_MUNICIPIO": "CODIGO_DANE",
    "NOMBRE_MUNICIPIO": "MUNICIPIO",
    "TIPO:_MUNICIPIO_/_ISLA_/_ÁREA_NO_MUNICIPALIZADA": "TIPO_ENTIDAD"
})


# Actualizamos el diccionario DESPUÉS de las transformaciones

fuentes = {
    "Homicidios": df_homicidios,
    "Secuestros": df_secuestros,
    "Extorsión": df_extorsion,
    "Terrorismo": df_terrorismo,
    "Coca": df_coca,
    "DIVIPOLA": df_divipola
}


print("\n" + "=" * 60)
print("CAMPOS HOMOLOGADOS")
print("=" * 60)

for nombre, df in fuentes.items():

    print("\n" + nombre)
    print(df.columns.tolist())

# ============================================================
# 7. ESTANDARIZAR CÓDIGOS DANE
# ============================================================

def estandarizar_codigo_dane(df, columna="CODIGO_DANE"):

    df[columna] = (
        pd.to_numeric(
            df[columna],
            errors="coerce"
        )
        .astype("Int64")
        .astype("string")
        .str.zfill(5)
    )

    return df


# Fuentes con códigos municipales de 4/5 dígitos
df_homicidios = estandarizar_codigo_dane(df_homicidios)
df_secuestros = estandarizar_codigo_dane(df_secuestros)
df_extorsion = estandarizar_codigo_dane(df_extorsion)
df_coca = estandarizar_codigo_dane(df_coca)
df_divipola = estandarizar_codigo_dane(df_divipola)


# Terrorismo: transformación especial
df_terrorismo["CODIGO_DANE"] = (
    pd.to_numeric(
        df_terrorismo["CODIGO_DANE"],
        errors="coerce"
    )
    .floordiv(1000)
    .astype("Int64")
    .astype("string")
    .str.zfill(5)
)


# Actualizar diccionario
fuentes = {
    "Homicidios": df_homicidios,
    "Secuestros": df_secuestros,
    "Extorsión": df_extorsion,
    "Terrorismo": df_terrorismo,
    "Coca": df_coca,
    "DIVIPOLA": df_divipola
}


print("\n" + "=" * 60)
print("VALIDACIÓN FINAL DE CÓDIGOS DANE")
print("=" * 60)

for nombre, df in fuentes.items():

    print("\n" + nombre)

    print("Tipo:", df["CODIGO_DANE"].dtype)

    print(
        "Códigos con longitud diferente de 5:",
        (df["CODIGO_DANE"].str.len() != 5).sum()
    )

    print(
        "Códigos nulos:",
        df["CODIGO_DANE"].isna().sum()
    )

    print(
        "Códigos únicos:",
        df["CODIGO_DANE"].nunique()
    )

    # ============================================================
# 8. TRANSFORMAR COCA DE FORMATO ANCHO A FORMATO LARGO
# ============================================================

# Años que necesitamos para el proyecto
anios_coca = [
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024"
]


df_coca_largo = df_coca.melt(
    id_vars=[
        "CODIGO_DEPARTAMENTO",
        "DEPARTAMENTO",
        "CODIGO_DANE",
        "MUNICIPIO"
    ],
    value_vars=anios_coca,
    var_name="ANIO",
    value_name="HECTAREAS_COCA"
)


# Convertir año a número
df_coca_largo["ANIO"] = pd.to_numeric(
    df_coca_largo["ANIO"],
    errors="coerce"
)


# Convertir hectáreas a número
df_coca_largo["HECTAREAS_COCA"] = pd.to_numeric(
    df_coca_largo["HECTAREAS_COCA"],
    errors="coerce"
)


print("\n" + "=" * 60)
print("COCA - FORMATO LARGO")
print("=" * 60)

print("Filas:", len(df_coca_largo))
print("Columnas:", len(df_coca_largo.columns))

print("\nColumnas:")
print(df_coca_largo.columns.tolist())

print("\nPrimeras filas:")
print(
    df_coca_largo.head(10).to_string(index=False)
)