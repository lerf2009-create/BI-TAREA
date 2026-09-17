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
    "COD_DEPTO": "CODIGO_DEPARTAMENTO",
    "COD_MUNI": "CODIGO_DANE"
})

df_secuestros = df_secuestros.rename(columns={
    "COD_DEPTO": "CODIGO_DEPARTAMENTO",
    "COD_MUNI": "CODIGO_DANE"
})

df_extorsion = df_extorsion.rename(columns={
    "COD_DEPTO": "CODIGO_DEPARTAMENTO",
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
print("\n" + "=" * 60)
print("COLUMNAS DESPUÉS DE HOMOLOGACIÓN")
print("=" * 60)

print("\nHomicidios:")
print(df_homicidios.columns.tolist())

print("\nSecuestros:")
print(df_secuestros.columns.tolist())

print("\nExtorsión:")
print(df_extorsion.columns.tolist())

print("\nTerrorismo:")
print(df_terrorismo.columns.tolist())

print("\nCoca:")
print(df_coca.columns.tolist())

print("\nDIVIPOLA:")
print(df_divipola.columns.tolist())
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
anios_coca = ["2019", "2020", "2021", "2022", "2023", "2024"]

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

df_coca_largo["ANIO"] = pd.to_numeric(
    df_coca_largo["ANIO"],
    errors="coerce"
)

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

# ============================================================
# 9. CREAR DIM_MUNICIPIO
# ============================================================

DIM_MUNICIPIO = df_divipola[
    [
        "CODIGO_DANE",
        "CODIGO_DEPARTAMENTO",
        "DEPARTAMENTO",
        "MUNICIPIO",
        "TIPO_ENTIDAD",
        "LONGITUD",
        "LATITUD"
    ]
].copy()


# Eliminar posibles duplicados por código territorial
DIM_MUNICIPIO = DIM_MUNICIPIO.drop_duplicates(
    subset=["CODIGO_DANE"]
)


print("\n" + "=" * 60)
print("DIM_MUNICIPIO")
print("=" * 60)

print("Filas:", len(DIM_MUNICIPIO))
print("Columnas:", len(DIM_MUNICIPIO.columns))

print("\nColumnas:")
print(DIM_MUNICIPIO.columns.tolist())

print("\nCódigos DANE duplicados:")
print(
    DIM_MUNICIPIO["CODIGO_DANE"].duplicated().sum()
)

print("\nPrimeras filas:")
print(
    DIM_MUNICIPIO.head(10).to_string(index=False)
)

# ============================================================
# DIM_TIEMPO
# ============================================================

DIM_TIEMPO = pd.DataFrame({
    "FECHA": pd.date_range(
        start="2019-01-01",
        end="2025-12-31",
        freq="D"
    )
})

DIM_TIEMPO["ANIO"] = DIM_TIEMPO["FECHA"].dt.year

# Clave de año para relacionar FACT_COCA
DIM_TIEMPO["ANIO_KEY"] = DIM_TIEMPO["ANIO"]
DIM_TIEMPO["MES"] = DIM_TIEMPO["FECHA"].dt.month
DIM_TIEMPO["NOMBRE_MES"] = DIM_TIEMPO["FECHA"].dt.month_name()
DIM_TIEMPO["TRIMESTRE"] = DIM_TIEMPO["FECHA"].dt.quarter
DIM_TIEMPO["DIA"] = DIM_TIEMPO["FECHA"].dt.day

print("\n" + "=" * 60)
print("DIM_TIEMPO")
print("=" * 60)

print(f"Filas: {len(DIM_TIEMPO)}")
print(f"Columnas: {len(DIM_TIEMPO.columns)}")

print("\nColumnas:")
print(DIM_TIEMPO.columns.tolist())

print("\nPrimeras filas:")
print(DIM_TIEMPO.head())

print("\nÚltimas filas:")
print(DIM_TIEMPO.tail())

# ============================================================
# FACT_HOMICIDIOS
# ============================================================

FACT_HOMICIDIOS = df_homicidios[
    [
        "FECHA_HECHO",
        "CODIGO_DEPARTAMENTO",
        "DEPARTAMENTO",
        "CODIGO_DANE",
        "MUNICIPIO",
        "ZONA",
        "SEXO",
        "ARMA_MEDIO",
        "MODALIDAD_PRESUNTA",
        "SPOA_CARACTERIZACION",
        "CANTIDAD"
    ]
].copy()

# ------------------------------------------------------------
# Limpieza de fecha
# ------------------------------------------------------------

FACT_HOMICIDIOS["FECHA_HECHO"] = pd.to_datetime(
    FACT_HOMICIDIOS["FECHA_HECHO"],
    errors="coerce"
)

# ------------------------------------------------------------
# Limpieza de cantidad
# ------------------------------------------------------------

FACT_HOMICIDIOS["CANTIDAD"] = pd.to_numeric(
    FACT_HOMICIDIOS["CANTIDAD"],
    errors="coerce"
)

# ------------------------------------------------------------
# Validaciones básicas
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FACT_HOMICIDIOS")
print("=" * 60)

print(f"Filas: {len(FACT_HOMICIDIOS)}")
print(f"Columnas: {len(FACT_HOMICIDIOS.columns)}")

print("\nColumnas:")
print(FACT_HOMICIDIOS.columns.tolist())

print("\nNulos:")
print(FACT_HOMICIDIOS.isna().sum())

print("\nFecha mínima:")
print(FACT_HOMICIDIOS["FECHA_HECHO"].min())

print("\nFecha máxima:")
print(FACT_HOMICIDIOS["FECHA_HECHO"].max())

print("\nTotal CANTIDAD:")
print(FACT_HOMICIDIOS["CANTIDAD"].sum())

print("\nCódigos DANE únicos:")
print(FACT_HOMICIDIOS["CODIGO_DANE"].nunique())

# ============================================================
# FACT_SECUESTROS
# ============================================================

FACT_SECUESTROS = df_secuestros[
    [
        "FECHA_HECHO",
        "CODIGO_DEPARTAMENTO",
        "DEPARTAMENTO",
        "CODIGO_DANE",
        "MUNICIPIO",
        "TIPO_DELITO",
        "CANTIDAD"
    ]
].copy()

# ------------------------------------------------------------
# Limpieza de fecha
# ------------------------------------------------------------

FACT_SECUESTROS["FECHA_HECHO"] = pd.to_datetime(
    FACT_SECUESTROS["FECHA_HECHO"],
    errors="coerce"
)

# ------------------------------------------------------------
# Limpieza de cantidad
# ------------------------------------------------------------

FACT_SECUESTROS["CANTIDAD"] = pd.to_numeric(
    FACT_SECUESTROS["CANTIDAD"],
    errors="coerce"
)

# ------------------------------------------------------------
# Validaciones básicas
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FACT_SECUESTROS")
print("=" * 60)

print(f"Filas: {len(FACT_SECUESTROS)}")
print(f"Columnas: {len(FACT_SECUESTROS.columns)}")

print("\nColumnas:")
print(FACT_SECUESTROS.columns.tolist())

print("\nNulos:")
print(FACT_SECUESTROS.isna().sum())

print("\nFecha mínima:")
print(FACT_SECUESTROS["FECHA_HECHO"].min())

print("\nFecha máxima:")
print(FACT_SECUESTROS["FECHA_HECHO"].max())

print("\nTotal CANTIDAD:")
print(FACT_SECUESTROS["CANTIDAD"].sum())

print("\nCódigos DANE únicos:")
print(FACT_SECUESTROS["CODIGO_DANE"].nunique())

print("\n" + "=" * 60)
print("COLUMNAS ACTUALES - EXTORSION")
print("=" * 60)

print(df_extorsion.columns.tolist())

# ============================================================
# FACT_EXTORSION
# ============================================================

FACT_EXTORSION = df_extorsion[
    [
        "FECHA_HECHO",
        "CODIGO_DEPARTAMENTO",
        "DEPARTAMENTO",
        "CODIGO_DANE",
        "MUNICIPIO",
        "CANTIDAD"
    ]
].copy()

# ------------------------------------------------------------
# Limpieza de fecha
# ------------------------------------------------------------

FACT_EXTORSION["FECHA_HECHO"] = pd.to_datetime(
    FACT_EXTORSION["FECHA_HECHO"],
    errors="coerce"
)

# ------------------------------------------------------------
# Limpieza de cantidad
# ------------------------------------------------------------

FACT_EXTORSION["CANTIDAD"] = pd.to_numeric(
    FACT_EXTORSION["CANTIDAD"],
    errors="coerce"
)

# ------------------------------------------------------------
# Validaciones básicas
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FACT_EXTORSION")
print("=" * 60)

print(f"Filas: {len(FACT_EXTORSION)}")
print(f"Columnas: {len(FACT_EXTORSION.columns)}")

print("\nColumnas:")
print(FACT_EXTORSION.columns.tolist())

print("\nNulos:")
print(FACT_EXTORSION.isna().sum())

print("\nFecha mínima:")
print(FACT_EXTORSION["FECHA_HECHO"].min())

print("\nFecha máxima:")
print(FACT_EXTORSION["FECHA_HECHO"].max())

print("\nTotal CANTIDAD:")
print(FACT_EXTORSION["CANTIDAD"].sum())

print("\nCódigos DANE únicos:")
print(FACT_EXTORSION["CODIGO_DANE"].nunique())

# ============================================================
# FACT_TERRORISMO
# ============================================================

FACT_TERRORISMO = df_terrorismo[
    [
        "FECHA_HECHO",
        "CODIGO_DANE",
        "DEPARTAMENTO",
        "MUNICIPIO",
        "ARMAS_MEDIOS",
        "CANTIDAD"
    ]
].copy()

# ------------------------------------------------------------
# Limpieza de fecha
# ------------------------------------------------------------

FACT_TERRORISMO["FECHA_HECHO"] = pd.to_datetime(
    FACT_TERRORISMO["FECHA_HECHO"],
    errors="coerce"
)

# ------------------------------------------------------------
# Limpieza de cantidad
# ------------------------------------------------------------

FACT_TERRORISMO["CANTIDAD"] = pd.to_numeric(
    FACT_TERRORISMO["CANTIDAD"],
    errors="coerce"
)

# ------------------------------------------------------------
# Validaciones básicas
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FACT_TERRORISMO")
print("=" * 60)

print(f"Filas: {len(FACT_TERRORISMO)}")
print(f"Columnas: {len(FACT_TERRORISMO.columns)}")

print("\nColumnas:")
print(FACT_TERRORISMO.columns.tolist())

print("\nNulos:")
print(FACT_TERRORISMO.isna().sum())

print("\nFecha mínima:")
print(FACT_TERRORISMO["FECHA_HECHO"].min())

print("\nFecha máxima:")
print(FACT_TERRORISMO["FECHA_HECHO"].max())

print("\nTotal CANTIDAD:")
print(FACT_TERRORISMO["CANTIDAD"].sum())

print("\nCódigos DANE únicos:")
print(FACT_TERRORISMO["CODIGO_DANE"].nunique())

# ============================================================
# FACT_COCA
# ============================================================

FACT_COCA = df_coca_largo[
    ["CODIGO_DANE", "ANIO", "HECTAREAS_COCA"]
].copy()

# ------------------------------------------------------------
# Limpieza de tipos
# ------------------------------------------------------------

FACT_COCA["ANIO"] = pd.to_numeric(
    FACT_COCA["ANIO"],
    errors="coerce"
).astype("Int64")

FACT_COCA["HECTAREAS_COCA"] = pd.to_numeric(
    FACT_COCA["HECTAREAS_COCA"],
    errors="coerce"
)

# ------------------------------------------------------------
# Validaciones básicas
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("FACT_COCA")
print("=" * 60)

print(f"Filas: {len(FACT_COCA)}")
print(f"Columnas: {len(FACT_COCA.columns)}")

print("\nColumnas:")
print(FACT_COCA.columns.tolist())

print("\nNulos:")
print(FACT_COCA.isna().sum())

print("\nAño mínimo:")
print(FACT_COCA["ANIO"].min())

print("\nAño máximo:")
print(FACT_COCA["ANIO"].max())

print("\nTotal hectáreas:")
print(FACT_COCA["HECTAREAS_COCA"].sum())

print("\nCódigos DANE únicos:")
print(FACT_COCA["CODIGO_DANE"].nunique())

print("\nAños disponibles:")
print(sorted(FACT_COCA["ANIO"].dropna().unique()))

# ============================================================
# LIMPIEZA FINAL DE TABLAS FACT
# ============================================================

FACT_HOMICIDIOS = FACT_HOMICIDIOS[
    [
        "FECHA_HECHO",
        "CODIGO_DANE",
        "ZONA",
        "SEXO",
        "ARMA_MEDIO",
        "MODALIDAD_PRESUNTA",
        "SPOA_CARACTERIZACION",
        "CANTIDAD"
    ]
].copy()

FACT_SECUESTROS = FACT_SECUESTROS[
    [
        "FECHA_HECHO",
        "CODIGO_DANE",
        "TIPO_DELITO",
        "CANTIDAD"
    ]
].copy()

FACT_EXTORSION = FACT_EXTORSION[
    [
        "FECHA_HECHO",
        "CODIGO_DANE",
        "CANTIDAD"
    ]
].copy()

FACT_TERRORISMO = FACT_TERRORISMO[
    [
        "FECHA_HECHO",
        "CODIGO_DANE",
        "ARMAS_MEDIOS",
        "CANTIDAD"
    ]
].copy()

FACT_COCA = FACT_COCA[
    [
        "CODIGO_DANE",
        "ANIO",
        "HECTAREAS_COCA"
    ]
].copy()


# ============================================================
# VALIDACIÓN DE LIMPIEZA FACT
# ============================================================

print("\n" + "=" * 60)
print("FACTS DESPUÉS DE LA LIMPIEZA")
print("=" * 60)

for nombre, tabla in {
    "FACT_HOMICIDIOS": FACT_HOMICIDIOS,
    "FACT_SECUESTROS": FACT_SECUESTROS,
    "FACT_EXTORSION": FACT_EXTORSION,
    "FACT_TERRORISMO": FACT_TERRORISMO,
    "FACT_COCA": FACT_COCA
}.items():

    print(f"\n{nombre}")
    print(f"Filas: {len(tabla)}")
    print(f"Columnas: {len(tabla.columns)}")
    print(f"Columnas: {list(tabla.columns)}")

# ============================================================
# RECONCILIACIÓN RAW vs FACT
# ============================================================

RECONCILIACION = []

def agregar_reconciliacion(
    fuente,
    metrica,
    valor_raw,
    valor_fact
):
    diferencia = valor_fact - valor_raw

    RECONCILIACION.append({
        "FUENTE": fuente,
        "METRICA": metrica,
        "VALOR_RAW": valor_raw,
        "VALOR_FACT": valor_fact,
        "DIFERENCIA": diferencia,
        "ESTADO": "OK" if diferencia == 0 else "REVISAR"
    })


# ============================================================
# HOMICIDIOS
# ============================================================

agregar_reconciliacion(
    "Homicidios",
    "Filas",
    len(df_homicidios),
    len(FACT_HOMICIDIOS)
)

agregar_reconciliacion(
    "Homicidios",
    "Total CANTIDAD",
    df_homicidios["CANTIDAD"].sum(),
    FACT_HOMICIDIOS["CANTIDAD"].sum()
)

agregar_reconciliacion(
    "Homicidios",
    "Municipios únicos",
    df_homicidios["CODIGO_DANE"].nunique(),
    FACT_HOMICIDIOS["CODIGO_DANE"].nunique()
)


# ============================================================
# SECUESTROS
# ============================================================

agregar_reconciliacion(
    "Secuestros",
    "Filas",
    len(df_secuestros),
    len(FACT_SECUESTROS)
)

agregar_reconciliacion(
    "Secuestros",
    "Total CANTIDAD",
    df_secuestros["CANTIDAD"].sum(),
    FACT_SECUESTROS["CANTIDAD"].sum()
)

agregar_reconciliacion(
    "Secuestros",
    "Municipios únicos",
    df_secuestros["CODIGO_DANE"].nunique(),
    FACT_SECUESTROS["CODIGO_DANE"].nunique()
)


# ============================================================
# EXTORSIÓN
# ============================================================

agregar_reconciliacion(
    "Extorsión",
    "Filas",
    len(df_extorsion),
    len(FACT_EXTORSION)
)

agregar_reconciliacion(
    "Extorsión",
    "Total CANTIDAD",
    df_extorsion["CANTIDAD"].sum(),
    FACT_EXTORSION["CANTIDAD"].sum()
)

agregar_reconciliacion(
    "Extorsión",
    "Municipios únicos",
    df_extorsion["CODIGO_DANE"].nunique(),
    FACT_EXTORSION["CODIGO_DANE"].nunique()
)


# ============================================================
# TERRORISMO
# ============================================================

agregar_reconciliacion(
    "Terrorismo",
    "Filas",
    len(df_terrorismo),
    len(FACT_TERRORISMO)
)

agregar_reconciliacion(
    "Terrorismo",
    "Total CANTIDAD",
    df_terrorismo["CANTIDAD"].sum(),
    FACT_TERRORISMO["CANTIDAD"].sum()
)

agregar_reconciliacion(
    "Terrorismo",
    "Municipios únicos",
    df_terrorismo["CODIGO_DANE"].nunique(),
    FACT_TERRORISMO["CODIGO_DANE"].nunique()
)


# ============================================================
# COCA
# ============================================================

agregar_reconciliacion(
    "Coca",
    "Filas",
    len(df_coca_largo),
    len(FACT_COCA)
)

agregar_reconciliacion(
    "Coca",
    "Total hectáreas",
    df_coca_largo["HECTAREAS_COCA"].sum(),
    FACT_COCA["HECTAREAS_COCA"].sum()
)

agregar_reconciliacion(
    "Coca",
    "Territorios únicos",
    df_coca_largo["CODIGO_DANE"].nunique(),
    FACT_COCA["CODIGO_DANE"].nunique()
)


# ============================================================
# RESULTADO
# ============================================================

RECONCILIACION = pd.DataFrame(RECONCILIACION)

print("\n" + "=" * 60)
print("RECONCILIACIÓN RAW vs FACT")
print("=" * 60)

print(RECONCILIACION.to_string(index=False))

# ============================================================
# DQ_RESULTS
# ============================================================

DQ_RESULTS = []


def agregar_control(
    fuente,
    dimension,
    control,
    valor,
    umbral,
    estado,
    observacion
):
    DQ_RESULTS.append({
        "FUENTE": fuente,
        "DIMENSION_DQ": dimension,
        "CONTROL": control,
        "VALOR": valor,
        "UMBRAL": umbral,
        "ESTADO": estado,
        "OBSERVACION": observacion
    })


# ============================================================
# FUNCIÓN DE CONTROLES
# ============================================================

def ejecutar_controles(
    df,
    nombre_fuente,
    columna_codigo,
    columna_fecha=None,
    columna_cantidad=None
):

    # --------------------------------------------------------
    # 1. COMPLETITUD - Códigos nulos
    # --------------------------------------------------------

    nulos_codigo = df[columna_codigo].isna().sum()

    agregar_control(
        nombre_fuente,
        "Completitud",
        "Códigos DANE nulos",
        nulos_codigo,
        0,
        "OK" if nulos_codigo == 0 else "REVISAR",
        "No se esperan códigos DANE nulos."
    )

    # --------------------------------------------------------
    # 2. VALIDEZ - Longitud código DANE
    # --------------------------------------------------------

    codigos_invalidos = (
        df[columna_codigo]
        .astype("string")
        .str.len()
        .ne(5)
        .sum()
    )

    agregar_control(
        nombre_fuente,
        "Validez",
        "Códigos DANE con longitud diferente de 5",
        codigos_invalidos,
        0,
        "OK" if codigos_invalidos == 0 else "REVISAR",
        "El código DANE debe tener exactamente 5 caracteres."
    )

    # --------------------------------------------------------
    # 3. CONSISTENCIA - Código DANE contra DIM_MUNICIPIO
    # --------------------------------------------------------

    codigos_fuente = set(
        df[columna_codigo]
        .dropna()
        .astype(str)
    )

    codigos_dim = set(
        DIM_MUNICIPIO["CODIGO_DANE"]
        .dropna()
        .astype(str)
    )

    codigos_no_dim = codigos_fuente - codigos_dim

    agregar_control(
        nombre_fuente,
        "Consistencia",
        "Códigos DANE no encontrados en DIM_MUNICIPIO",
        len(codigos_no_dim),
        0,
        "OK" if len(codigos_no_dim) == 0 else "REVISAR",
        "Todo código utilizado por una FACT debe existir en DIM_MUNICIPIO."
    )

    # --------------------------------------------------------
    # 4. COMPLETITUD - Nulos generales
    # --------------------------------------------------------

    total_nulos = int(df.isna().sum().sum())

    agregar_control(
        nombre_fuente,
        "Completitud",
        "Total de valores nulos",
        total_nulos,
        0,
        "OK" if total_nulos == 0 else "REVISAR",
        "Se identifican valores nulos en la tabla."
    )

    # --------------------------------------------------------
    # 5. FECHAS
    # --------------------------------------------------------

    if columna_fecha is not None:

        fechas_nulas = df[columna_fecha].isna().sum()

        agregar_control(
            nombre_fuente,
            "Completitud",
            "Fechas nulas",
            fechas_nulas,
            0,
            "OK" if fechas_nulas == 0 else "REVISAR",
            "No se esperan fechas nulas."
        )

        fechas_fuera = (
            (df[columna_fecha] < pd.Timestamp("2019-01-01")) |
            (df[columna_fecha] > pd.Timestamp("2025-12-31"))
        ).sum()

        agregar_control(
            nombre_fuente,
            "Validez",
            "Fechas fuera del periodo 2019-2025",
            fechas_fuera,
            0,
            "OK" if fechas_fuera == 0 else "REVISAR",
            "El periodo analítico definido es 2019-2025."
        )

    # --------------------------------------------------------
    # 6. CANTIDAD NEGATIVA
    # --------------------------------------------------------

    if columna_cantidad is not None:

        negativos = (
            pd.to_numeric(
                df[columna_cantidad],
                errors="coerce"
            ) < 0
        ).sum()

        agregar_control(
            nombre_fuente,
            "Validez",
            "Valores negativos",
            negativos,
            0,
            "OK" if negativos == 0 else "REVISAR",
            "Las cantidades de eventos no deben ser negativas."
        )


# ============================================================
# EJECUTAR CONTROLES SOBRE LAS FACT
# ============================================================

ejecutar_controles(
    FACT_HOMICIDIOS,
    "Homicidios",
    "CODIGO_DANE",
    "FECHA_HECHO",
    "CANTIDAD"
)

ejecutar_controles(
    FACT_SECUESTROS,
    "Secuestros",
    "CODIGO_DANE",
    "FECHA_HECHO",
    "CANTIDAD"
)

ejecutar_controles(
    FACT_EXTORSION,
    "Extorsión",
    "CODIGO_DANE",
    "FECHA_HECHO",
    "CANTIDAD"
)

ejecutar_controles(
    FACT_TERRORISMO,
    "Terrorismo",
    "CODIGO_DANE",
    "FECHA_HECHO",
    "CANTIDAD"
)

# Coca no tiene FECHA_HECHO ni CANTIDAD.
# Su medida es HECTAREAS_COCA y su periodo es ANIO.

ejecutar_controles(
    FACT_COCA,
    "Coca",
    "CODIGO_DANE"
)


# ============================================================
# CONTROL ESPECÍFICO COCA
# ============================================================

nulos_coca = FACT_COCA["HECTAREAS_COCA"].isna().sum()

agregar_control(
    "Coca",
    "Completitud",
    "Hectáreas de coca nulas",
    nulos_coca,
    0,
    "INFORMATIVO",
    "Los valores nulos se conservan como ausencia de dato; no se convierten automáticamente en cero."
)

anios_invalidos = (
    ~FACT_COCA["ANIO"].between(2019, 2024)
).sum()

agregar_control(
    "Coca",
    "Validez",
    "Años fuera del periodo disponible",
    anios_invalidos,
    0,
    "OK" if anios_invalidos == 0 else "REVISAR",
    "La fuente de coca disponible contiene información 2019-2024."
)


# ============================================================
# RESULTADO
# ============================================================

DQ_RESULTS = pd.DataFrame(DQ_RESULTS)

print("\n" + "=" * 60)
print("DQ_RESULTS")
print("=" * 60)

print(f"Controles ejecutados: {len(DQ_RESULTS)}")

print("\nResultado por estado:")
print(
    DQ_RESULTS["ESTADO"]
    .value_counts()
)

print("\nDetalle:")
print(
    DQ_RESULTS.to_string(index=False)
)

# ============================================================
# EXCEPCIONES DE INTEGRACIÓN - COCA
# ============================================================

codigos_coca = set(
    FACT_COCA["CODIGO_DANE"]
    .dropna()
    .astype(str)
)

codigos_dim = set(
    DIM_MUNICIPIO["CODIGO_DANE"]
    .dropna()
    .astype(str)
)

codigos_coca_sin_dim = sorted(codigos_coca - codigos_dim)

print("\n" + "=" * 60)
print("CÓDIGOS DE COCA NO ENCONTRADOS EN DIM_MUNICIPIO")
print("=" * 60)

print(codigos_coca_sin_dim)

# ============================================================
# VALIDACIÓN ESPECÍFICA DEL CÓDIGO 94663
# ============================================================

print("\n" + "=" * 60)
print("VALIDACIÓN 94663 EN DIM_MUNICIPIO")
print("=" * 60)

print(
    DIM_MUNICIPIO[
        DIM_MUNICIPIO["CODIGO_DANE"] == "94663"
    ].to_string(index=False)
)

# ============================================================
# TRAZABILIDAD DEL CÓDIGO 94663
# ============================================================

print("\n" + "=" * 60)
print("94663 EN df_divipola")
print("=" * 60)

print(
    df_divipola[
        df_divipola["CODIGO_DANE"] == "94663"
    ].to_string(index=False)
)

print("\n" + "=" * 60)
print("TIPOS DE DATOS")
print("=" * 60)

print("df_divipola:", df_divipola["CODIGO_DANE"].dtype)
print("DIM_MUNICIPIO:", DIM_MUNICIPIO["CODIGO_DANE"].dtype)

print("\n" + "=" * 60)
print("ÚLTIMOS CÓDIGOS DE DIVIPOLA")
print("=" * 60)

print(
    df_divipola[
        df_divipola["CODIGO_DANE"].astype(str).str.startswith("94")
    ][
        ["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO", "TIPO_ENTIDAD"]
    ].tail(20).to_string(index=False)
)

# ============================================================
# TRAZABILIDAD DE 94663 EN COCA
# ============================================================

print("\n" + "=" * 60)
print("94663 EN df_coca")
print("=" * 60)

print(
    df_coca[
        df_coca["CODIGO_DANE"] == "94663"
    ].to_string(index=False)
)

print(
    df_divipola[
        df_divipola["DEPARTAMENTO"].str.contains("GUAIN", case=False, na=False)
    ][
        ["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO", "TIPO_ENTIDAD"]
    ].to_string(index=False)
)

print("\n" + "="*60)
print("ANÁLISIS DE NULOS - COCA")
print("="*60)

print("\nNulos por año:")
print(
    df_coca_largo.groupby("ANIO")["HECTAREAS_COCA"]
    .apply(lambda x: x.isna().sum())
)

print("\nTotal de registros por año:")
print(
    df_coca_largo.groupby("ANIO").size()
)

print("\nRegistros con dato por año:")
print(
    df_coca_largo.groupby("ANIO")["HECTAREAS_COCA"]
    .count()
)

# ============================================================
# FILTRO DE TERRITORIOS CON OBSERVACIONES EN EL PERÍODO
# ============================================================

territorios_con_dato = (
    df_coca_largo
    .groupby("CODIGO_DANE")["HECTAREAS_COCA"]
    .count()
)

territorios_con_dato = territorios_con_dato[
    territorios_con_dato > 0
].index

df_coca_largo_modelo = df_coca_largo[
    df_coca_largo["CODIGO_DANE"].isin(territorios_con_dato)
].copy()

print("\n" + "="*60)
print("VALIDACIÓN DE FILTRO COCA")
print("="*60)

print("Territorios antes:", df_coca_largo["CODIGO_DANE"].nunique())
print("Territorios después:", df_coca_largo_modelo["CODIGO_DANE"].nunique())

print("\n¿94663 permanece?")
print("94663" in df_coca_largo_modelo["CODIGO_DANE"].unique())

territorios_sin_dato = (
    df_coca_largo
    .groupby(
        ["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO"]
    )["HECTAREAS_COCA"]
    .count()
)

territorios_sin_dato = territorios_sin_dato[
    territorios_sin_dato == 0
]

print("\n" + "="*60)
print("TERRITORIOS SIN NINGÚN DATO 2019-2024")
print("="*60)

print("Cantidad:", len(territorios_sin_dato))

print("\nListado:")
print(territorios_sin_dato.index.to_frame(index=False).to_string(index=False))

anios_historicos = [
    str(anio) for anio in range(2001, 2019)
]

territorios_sin_dato_periodo = (
    df_coca_largo
    .groupby(["CODIGO_DANE", "DEPARTAMENTO", "MUNICIPIO"])
    ["HECTAREAS_COCA"]
    .count()
)

codigos_121 = territorios_sin_dato_periodo[
    territorios_sin_dato_periodo == 0
].index.get_level_values("CODIGO_DANE")


historico_121 = df_coca[
    df_coca["CODIGO_DANE"].isin(codigos_121)
].copy()

historico_121["DATOS_2001_2018"] = historico_121[
    anios_historicos
].notna().sum(axis=1)

print("\n" + "="*60)
print("HISTORIAL DE LOS 121 TERRITORIOS")
print("="*60)

print("\nTerritorios con algún dato antes de 2019:")
print(
    (historico_121["DATOS_2001_2018"] > 0).sum()
)

print("\nTerritorios sin ningún dato entre 2001-2018:")
print(
    (historico_121["DATOS_2001_2018"] == 0).sum()
)

# ============================================================
# ÚLTIMO AÑO CON DATO DE LOS 121 TERRITORIOS
# ============================================================

anios_coca_completos = [
    str(anio) for anio in range(2001, 2025)
]

historico_121["ULTIMO_ANIO_CON_DATO"] = historico_121[
    anios_coca_completos
].apply(
    lambda fila: (
        pd.to_numeric(fila, errors="coerce")
        .dropna()
        .index
        .astype(int)
        .max()
        if fila.notna().any()
        else None
    ),
    axis=1
)

print("\n" + "="*60)
print("ÚLTIMO AÑO CON DATO - 121 TERRITORIOS")
print("="*60)

print(
    historico_121["ULTIMO_ANIO_CON_DATO"]
    .value_counts()
    .sort_index()
)

print("\n" + "="*60)
print("TIPO DE ENTIDAD - 121 TERRITORIOS")
print("="*60)

tipos_121 = historico_121.merge(
    DIM_MUNICIPIO[
        ["CODIGO_DANE", "TIPO_ENTIDAD"]
    ],
    on="CODIGO_DANE",
    how="left"
)

print(
    tipos_121["TIPO_ENTIDAD"]
    .value_counts(dropna=False)
)

print("\n" + "="*60)
print("COBERTURA TERRITORIAL COCA 2019-2024")
print("="*60)

cobertura_coca = (
    df_coca_largo
    .groupby("ANIO")["HECTAREAS_COCA"]
    .agg(
        territorios_total="size",
        territorios_con_dato="count"
    )
)

cobertura_coca["porcentaje_cobertura"] = (
    cobertura_coca["territorios_con_dato"]
    / cobertura_coca["territorios_total"]
    * 100
)

print(cobertura_coca)

# Revisar un territorio con valores vacíos
print(
    df_coca[
        df_coca["2019"].isna() &
        df_coca["2020"].isna() &
        df_coca["2021"].isna() &
        df_coca["2022"].isna() &
        df_coca["2023"].isna() &
        df_coca["2024"].isna()
    ][[
        "CODIGO_DANE",
        "MUNICIPIO",
        "2018",
        "2019",
        "2020",
        "2021",
        "2022",
        "2023",
        "2024"
    ]].head(20)
)

# Territorios sin ningún dato entre 2019 y 2024
sin_dato_2019_2024 = (
    df_coca_largo
    .groupby("CODIGO_DANE")["HECTAREAS_COCA"]
    .count()
)

codigos_sin_dato = sin_dato_2019_2024[
    sin_dato_2019_2024 == 0
].index

# Volvemos a la base original para revisar hasta qué año
# tuvieron algún valor histórico
anios_historicos = [str(a) for a in range(2001, 2019)]

df_historico = df_coca[
    df_coca["CODIGO_DANE"].isin(codigos_sin_dato)
].copy()

df_historico["ULTIMO_ANIO_CON_DATO"] = (
    df_historico[anios_historicos]
    .apply(
        lambda fila: max(
            [int(anio) for anio in anios_historicos if pd.notna(fila[anio])],
            default=None
        ),
        axis=1
    )
)

print(
    df_historico[
        ["CODIGO_DANE", "MUNICIPIO", "ULTIMO_ANIO_CON_DATO"]
    ].to_string(index=False)
)

resumen_sin_dato = (
    df_historico["ULTIMO_ANIO_CON_DATO"]
    .value_counts()
    .sort_index()
)

print(resumen_sin_dato)

# ==========================================
# MODELO FINAL PARA POWER BI
# ==========================================

# Dimensiones
DIM_MUNICIPIO.to_excel(
    "DIM_MUNICIPIO.xlsx",
    index=False
)

DIM_TIEMPO.to_excel(
    "DIM_TIEMPO.xlsx",
    index=False
)

# Hechos
FACT_HOMICIDIOS.to_excel(
    "FACT_HOMICIDIOS.xlsx",
    index=False
)

FACT_SECUESTROS.to_excel(
    "FACT_SECUESTROS.xlsx",
    index=False
)

FACT_EXTORSION.to_excel(
    "FACT_EXTORSION.xlsx",
    index=False
)

FACT_TERRORISMO.to_excel(
    "FACT_TERRORISMO.xlsx",
    index=False
)

FACT_COCA.to_excel(
    "FACT_COCA.xlsx",
    index=False
)