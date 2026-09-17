#Auditoría de calidad de datos para la construcción de un Índice Integral de Riesgo Municipal
from pathlib import Path
from datetime import datetime
import pandas as pd

BASE = Path(__file__).resolve().parents[2]

archivo = BASE / "7HOMICIDIO_20260903 (1).xlsx"

print("PASO 1 — DESCARGA Y REGISTRO DE LA FUENTE")
print("--------------------------------------------")

print("Estoy ejecutando desde:", Path.cwd())
print("El código está en:", Path(__file__).resolve())
print("Carpeta base:", BASE)
print("Estoy buscando el archivo en:", archivo.resolve())
print("¿Existe el archivo?:", archivo.exists())

df = pd.read_excel(archivo)

print("Archivo:", archivo.name)
print("Ruta:", archivo.resolve())
print("Fecha de descarga/registro:", datetime.now().strftime("%Y-%m-%d %H:%M"))
print("Formato:", archivo.suffix)
print("Tamaño (MB):", round(archivo.stat().st_size / 1_000_000, 2))
print("Número de filas:", df.shape[0])
print("Número de columnas:", df.shape[1])


print()
print("PASO 2 — EXPLORACIÓN INICIAL DE LA ESTRUCTURA")
print("-----------------------------------------------")

print()
print("NOMBRES DE LAS COLUMNAS:")
for columna in df.columns:
    print("-", columna)

print()
print("TIPO DE DATO DE CADA COLUMNA:")
print(df.dtypes)

print()
print("PRIMERAS 5 FILAS:")
print(df.head())

print()
print("INFORMACIÓN GENERAL:")
df.info()

print()
print("PREGUNTA 3 — COLUMNAS QUE REQUIEREN REVISIÓN")
print("-----------------------------------------------")

columnas_revisar = [
    "COD_DEPTO",
    "COD_MUNI",
    "ARMA MEDIO",
    " MODALIDAD PRESUNTA",
    "SPOA_CARACTERIZACION"
]

for columna in columnas_revisar:
    print("-", columna)


print()
print("PREGUNTA 5 — SEPARADOR DECIMAL")
print("--------------------------------")

print("Columnas numéricas:")
print(df.select_dtypes(include="number").columns.tolist())

print()
print("Ejemplos de valores numéricos:")
for columna in df.select_dtypes(include="number").columns:
    print(columna, "→", df[columna].head().tolist())


print()
print("PREGUNTA 6 — SEPARADOR DE MILES")
print("---------------------------------")

print("Los valores numéricos fueron cargados como números por pandas.")
print("Por lo tanto, el separador de miles no forma parte del valor almacenado.")

print()
print("PASO 3 — DIAGNÓSTICO DE COMPLETITUD")
print("------------------------------------")

print()
print("3.1 — VALORES NULOS POR COLUMNA")
print("--------------------------------")

nulos = df.isnull().sum()

for columna in df.columns:
    cantidad_nulos = nulos[columna]
    porcentaje = (cantidad_nulos / len(df)) * 100

    print(f"{columna}: {cantidad_nulos} nulos ({porcentaje:.2f}%)")

    print()
print("3.2 — AÑOS Y MESES")
print("-------------------")

# Años disponibles
años = sorted(df["FECHA HECHO"].dt.year.unique())

print("Años disponibles:")
print(años)


# Años faltantes
años_esperados = set(range(2019, 2026))
años_encontrados = set(años)

años_faltantes = sorted(años_esperados - años_encontrados)

print()
print("Años faltantes entre 2019 y 2025:")
print(años_faltantes)


# Meses disponibles por año
print()
print("Meses disponibles por año:")

for año in años:
    meses = sorted(
        df.loc[df["FECHA HECHO"].dt.year == año, "FECHA HECHO"]
        .dt.month
        .unique()
    )

    print(año, "→", meses)

    print()
print("3.3 — DEPARTAMENTOS Y MUNICIPIOS")
print("----------------------------------")

print("Número de departamentos únicos:")
print(df["COD_DEPTO"].nunique())

print()
print("Número de municipios únicos:")
print(df["COD_MUNI"].nunique())

print()
print("Primeros 20 departamentos:")
print(df[["COD_DEPTO", "DEPARTAMENTO"]].drop_duplicates().head(20))

print()
print("Primeros 20 municipios:")
print(df[["COD_MUNI", "MUNICIPIO"]].drop_duplicates().head(20))

print()
print("3.4 — COMPARACIÓN CON DIVIPOLA")
print("--------------------------------")

archivos_divipola = list(BASE.glob("*DIVIPOLA*.xlsx"))

print("Archivos DIVIPOLA encontrados:")

for archivo_divipola in archivos_divipola:
    print("-", archivo_divipola.name)

print()
print("Cantidad de archivos encontrados:", len(archivos_divipola))

# Cargar DIVIPOLA
archivo_divipola = archivos_divipola[0]

divipola = pd.read_excel(archivo_divipola)

print()
print("Filas de DIVIPOLA:", len(divipola))

print()
print("Columnas de DIVIPOLA:")
print(divipola.columns.tolist())

print()
print("Municipios únicos en DIVIPOLA:")
print(divipola["Código Municipio"].nunique())

print()
print("MUNICIPIOS DE DIVIPOLA QUE NO APARECEN EN HOMICIDIOS")
print("------------------------------------------------------")

municipios_homicidios = set(df["COD_MUNI"])
municipios_divipola = set(divipola["Código Municipio"])

municipios_faltantes = municipios_divipola - municipios_homicidios

print("Cantidad de municipios que no aparecen en Homicidios:")
print(len(municipios_faltantes))

print()
print("MUNICIPIOS NO ENCONTRADOS EN HOMICIDIOS")
print("-----------------------------------------")

faltantes = divipola[
    divipola["Código Municipio"].isin(municipios_faltantes)
]

print(
    faltantes[
        ["Código Departamento", "Nombre Departamento",
         "Código Municipio", "Nombre Municipio"]
    ].to_string(index=False)
)

print()
print("DEPARTAMENTOS DE DIVIPOLA QUE NO APARECEN EN HOMICIDIOS")
print("--------------------------------------------------------")

departamentos_homicidios = set(df["COD_DEPTO"])
departamentos_divipola = set(divipola["Código Departamento"])

departamentos_faltantes = departamentos_divipola - departamentos_homicidios

print("Cantidad de departamentos que no aparecen:")
print(len(departamentos_faltantes))

print()
print("Códigos de departamentos faltantes:")
print(sorted(departamentos_faltantes))

print()
print("PASO 4 — DIAGNÓSTICO DE EXACTITUD Y VALIDEZ")
print("---------------------------------------------")

print()
print("4.1 — VALORES NEGATIVOS EN CANTIDAD")
print("-------------------------------------")

negativos = df[df["CANTIDAD"] < 0]

print("Cantidad de registros con CANTIDAD negativa:")
print(len(negativos))

print()
print("4.2 — VALORES EXTREMOS EN CANTIDAD")
print("----------------------------------")

print("Valor máximo de CANTIDAD:")
print(df["CANTIDAD"].max())

print()
print("Los 10 valores más altos:")
print(df.nlargest(10, "CANTIDAD")[
    ["FECHA HECHO", "DEPARTAMENTO", "MUNICIPIO", "CANTIDAD"]
].to_string(index=False))

print()
print("4.3 — VALIDACIÓN DE CÓDIGOS DE MUNICIPIO")
print("-------------------------------------------")

codigos = df["COD_MUNI"].astype(str)

cantidad_digitos = codigos.str.len()

print("Cantidad de códigos con 5 dígitos:")
print((cantidad_digitos == 5).sum())

print()
print("Cantidad de códigos con menos de 5 dígitos:")
print((cantidad_digitos < 5).sum())

print()
print("Códigos con menos de 5 dígitos:")
print(
    df.loc[cantidad_digitos < 5, ["COD_MUNI", "MUNICIPIO"]]
      .drop_duplicates()
      .to_string(index=False)
)

print()
print("VALIDACIÓN DE CÓDIGOS CONTRA DIVIPOLA")
print("--------------------------------------")

# Convertimos los códigos de Homicidios a texto y agregamos ceros a la izquierda
codigos_homicidios = (
    df["COD_MUNI"]
    .astype(str)
    .str.zfill(5)
)

codigos_divipola = (
    divipola["Código Municipio"]
    .astype(str)
    .str.zfill(5)
)

# Comparamos cuántos códigos de Homicidios existen en DIVIPOLA
coincidencias = codigos_homicidios.isin(codigos_divipola)

print("Registros de Homicidios cuyo código coincide con DIVIPOLA:")
print(coincidencias.sum())

print()
print("Registros de Homicidios cuyo código NO coincide con DIVIPOLA:")
print((~coincidencias).sum())

print()
print("4.4 — VALIDACIÓN DE FECHAS")
print("---------------------------")

fecha_minima = df["FECHA HECHO"].min()
fecha_maxima = df["FECHA HECHO"].max()

print("Fecha mínima:", fecha_minima)
print("Fecha máxima:", fecha_maxima)

fechas_fuera_rango = df[
    (df["FECHA HECHO"] < "2019-01-01") |
    (df["FECHA HECHO"] >= "2026-01-01")
]

print()
print("Registros fuera del rango 2019–2025:")
print(len(fechas_fuera_rango))

print()
print("4.5 — CONSISTENCIA DE NOMBRES")
print("------------------------------")

print("Departamentos con más de un nombre para el mismo código:")

departamentos = (
    df.groupby("COD_DEPTO")["DEPARTAMENTO"]
    .nunique()
)

print(departamentos[departamentos > 1])


print()
print("Municipios con más de un nombre para el mismo código:")

municipios = (
    df.groupby("COD_MUNI")["MUNICIPIO"]
    .nunique()
)

print(municipios[municipios > 1])

print()
print("PASO 5 — DIAGNÓSTICO DE CONSISTENCIA")
print("-------------------------------------")

print()
print("5.1 — COMPARACIÓN CON DIVIPOLA")
print("--------------------------------")

# Creamos una copia para no modificar el dataset original
homicidios = df.copy()

# Estandarizamos temporalmente los códigos a 5 dígitos
homicidios["COD_MUNI_VALIDADO"] = (
    homicidios["COD_MUNI"]
    .astype(str)
    .str.zfill(5)
)

divipola_validada = divipola.copy()

divipola_validada["COD_MUNI_VALIDADO"] = (
    divipola_validada["Código Municipio"]
    .astype(str)
    .str.zfill(5)
)

print("Códigos preparados para la comparación.")

cruce = homicidios.merge(
    divipola_validada[
        ["COD_MUNI_VALIDADO", "Nombre Municipio", "Nombre Departamento"]
    ],
    on="COD_MUNI_VALIDADO",
    how="left"
)

print()
print("Registros después del cruce:", len(cruce))

print()
print("5.1.1 — COMPARACIÓN DE NOMBRES DE MUNICIPIOS")
print("-----------------------------------------------")

import unicodedata

def normalizar_texto(valor):
    valor = str(valor).strip().upper()
    valor = ''.join(
        c for c in unicodedata.normalize('NFD', valor)
        if unicodedata.category(c) != 'Mn'
    )
    return ' '.join(valor.split())

cruce["MUNICIPIO_NORMALIZADO"] = cruce["MUNICIPIO"].apply(normalizar_texto)
cruce["MUNICIPIO_DIVIPOLA_NORMALIZADO"] = cruce["Nombre Municipio"].apply(normalizar_texto)

diferencias_municipio = cruce[
    cruce["MUNICIPIO_NORMALIZADO"] != cruce["MUNICIPIO_DIVIPOLA_NORMALIZADO"]
]

print("Registros con nombres diferentes:", len(diferencias_municipio))
print("Porcentaje:", round(len(diferencias_municipio) / len(cruce) * 100, 2), "%")

print()
print("5.1.2 — DETALLE DE LAS DIFERENCIAS")
print("-----------------------------------")

print(
    diferencias_municipio[
        [
            "COD_MUNI_VALIDADO",
            "MUNICIPIO",
            "Nombre Municipio"
        ]
    ]
    .drop_duplicates()
    .sort_values("COD_MUNI_VALIDADO")
    .head(30)
    .to_string(index=False)
)

print()
print("5.1.3 — MUNICIPIOS ÚNICOS CON DIFERENCIAS DE NOMBRE")
print("-----------------------------------------------------------")

municipios_diferentes = (
    diferencias_municipio[
        [
            "COD_MUNI_VALIDADO",
            "MUNICIPIO",
            "Nombre Municipio"
        ]
    ]
    .drop_duplicates()
)

print("Municipios únicos con diferencia:", len(municipios_diferentes))

print()
print("Primeros municipios afectados:")
print(
    municipios_diferentes
    .sort_values("COD_MUNI_VALIDADO")
    .head(30)
    .to_string(index=False)
)

print()
print("5.2 — CONSISTENCIA INTERNA DE LOS NOMBRES")
print("-------------------------------------------")

nombres_por_codigo = (
    df.groupby("COD_MUNI")["MUNICIPIO"]
    .nunique()
)

municipios_con_varios_nombres = nombres_por_codigo[
    nombres_por_codigo > 1
]

print(
    "Municipios que aparecen con más de un nombre:",
    len(municipios_con_varios_nombres)
)

print()
print("5.3 — COHERENCIA DE TOTALES")
print("----------------------------")

# Total de homicidios por año y departamento
totales_departamento = (
    df.groupby(
        [df["FECHA HECHO"].dt.year, "DEPARTAMENTO"]
    )["CANTIDAD"]
    .sum()
)

# Total de homicidios por año, departamento y municipio
totales_municipio = (
    df.groupby(
        [df["FECHA HECHO"].dt.year, "DEPARTAMENTO", "MUNICIPIO"]
    )["CANTIDAD"]
    .sum()
)

# Volvemos a sumar los municipios para obtener
# nuevamente el total por año y departamento
totales_municipio_reagrupado = (
    totales_municipio
    .groupby(level=[0, 1])
    .sum()
)

# Comparamos ambos resultados
comparacion = pd.DataFrame({
    "Total_departamento": totales_departamento,
    "Total_municipios": totales_municipio_reagrupado
})

comparacion["Diferencia"] = (
    comparacion["Total_departamento"]
    - comparacion["Total_municipios"]
)

print("Combinaciones año-departamento evaluadas:", len(comparacion))

print(
    "Combinaciones con diferencias:",
    (comparacion["Diferencia"] != 0).sum()
)

print(
    "Diferencia máxima:",
    comparacion["Diferencia"].abs().max()
)

print()
print("5.3.1 — COHERENCIA MENSUAL POR MUNICIPIO")
print("------------------------------------------")

# Total anual por municipio
totales_anuales = (
    df.groupby(
        [
            df["FECHA HECHO"].dt.year,
            "DEPARTAMENTO",
            "MUNICIPIO"
        ]
    )["CANTIDAD"]
    .sum()
)

# Total por mes y municipio
totales_mensuales = (
    df.groupby(
        [
            df["FECHA HECHO"].dt.year,
            df["FECHA HECHO"].dt.month,
            "DEPARTAMENTO",
            "MUNICIPIO"
        ]
    )["CANTIDAD"]
    .sum()
)

# Sumamos los meses para reconstruir el total anual
totales_mensuales_reagrupados = (
    totales_mensuales
    .groupby(level=[0, 2, 3])
    .sum()
)

comparacion_mensual = pd.DataFrame({
    "Total_anual": totales_anuales,
    "Total_meses": totales_mensuales_reagrupados
})

comparacion_mensual["Diferencia"] = (
    comparacion_mensual["Total_anual"]
    - comparacion_mensual["Total_meses"]
)

print(
    "Combinaciones año-municipio evaluadas:",
    len(comparacion_mensual)
)

print(
    "Combinaciones con diferencias:",
    (comparacion_mensual["Diferencia"] != 0).sum()
)

print(
    "Diferencia máxima:",
    comparacion_mensual["Diferencia"].abs().max()
)

print()
print("5.4.1 — CARGA DE LA FUENTE DE EXTORSIÓN")
print("-----------------------------------------")

archivos_extorsion = list(BASE.glob("*EXTORS*.xlsx"))

archivo_extorsion = archivos_extorsion[0]

print("Archivo seleccionado:", archivo_extorsion.name)
print("Ruta:", archivo_extorsion.resolve())

extorsion = pd.read_excel(archivo_extorsion)

print("Filas:", len(extorsion))
print("Columnas:", len(extorsion.columns))

print()
print("Columnas de Extorsión:")
print(extorsion.columns.tolist())

print()
print("5.4.2 — HOMICIDIOS VS EXTORSIÓN")
print("--------------------------------")

municipios_homicidios = set(
    df["COD_MUNI"].astype(str).str.zfill(5)
)

municipios_extorsion = set(
    extorsion["COD_MUNI"].astype(str).str.zfill(5)
)

# Municipios que aparecen en ambas fuentes
municipios_comunes = municipios_homicidios & municipios_extorsion

# Municipios que aparecen en Homicidios pero no en Extorsión
solo_homicidios = municipios_homicidios - municipios_extorsion

# Municipios que aparecen en Extorsión pero no en Homicidios
solo_extorsion = municipios_extorsion - municipios_homicidios

print("Municipios únicos en Homicidios:", len(municipios_homicidios))
print("Municipios únicos en Extorsión:", len(municipios_extorsion))
print("Municipios presentes en ambas:", len(municipios_comunes))
print("Solo en Homicidios:", len(solo_homicidios))
print("Solo en Extorsión:", len(solo_extorsion))

print()
print("COBERTURA COMPARTIDA")
print("---------------------")

porcentaje_homicidios = (
    len(municipios_comunes) / len(municipios_homicidios) * 100
)

porcentaje_extorsion = (
    len(municipios_comunes) / len(municipios_extorsion) * 100
)

print(
    "De los municipios de Homicidios que también aparecen en Extorsión:",
    round(porcentaje_homicidios, 2),
    "%"
)

print(
    "De los municipios de Extorsión que también aparecen en Homicidios:",
    round(porcentaje_extorsion, 2),
    "%"
)

archivo_terrorismo = [
    archivo for archivo in BASE.glob("*Terrorismo*.xlsx")
    if "2019 A 2025" in archivo.name
][0]

print()
print("Archivo de Terrorismo seleccionado:", archivo_terrorismo.name)
print("Ruta:", archivo_terrorismo.resolve())

terrorismo = pd.read_excel(archivo_terrorismo)

print("Filas de Terrorismo:", len(terrorismo))
print("Columnas de Terrorismo:", len(terrorismo.columns))
print("Columnas:")
print(terrorismo.columns.tolist())

# Cargar Secuestro
archivo_secuestro = BASE / "2SECUESTRO_20260903.xlsx"

print()
print("CARGA DE SECUESTRO")
print("------------------")
print("Archivo:", archivo_secuestro.name)
print("¿Existe?:", archivo_secuestro.exists())

secuestro = pd.read_excel(archivo_secuestro)

print("Filas:", len(secuestro))
print("Columnas:", len(secuestro.columns))
print("Nombres de columnas:")
print(secuestro.columns.tolist())

print()
print("5.4.3 — HOMICIDIOS VS SECUESTRO Y TERRORISMO")
print("------------------------------------------------")

# Municipios de Homicidios
municipios_homicidios = set(
    df["COD_MUNI"].astype(str).str.zfill(5)
)

# Municipios de Secuestro
municipios_secuestro = set(
    secuestro["COD_MUNI"].astype(str).str.zfill(5)
)

# Municipios de Terrorismo
municipios_terrorismo = set(
    terrorismo["CODIGO DANE"].astype(str).str.zfill(5)
)


# ==============================
# HOMICIDIOS VS SECUESTRO
# ==============================

comunes_secuestro = (
    municipios_homicidios & municipios_secuestro
)

solo_homicidios_secuestro = (
    municipios_homicidios - municipios_secuestro
)

solo_secuestro = (
    municipios_secuestro - municipios_homicidios
)

print()
print("HOMICIDIOS VS SECUESTRO")
print("-----------------------")

print("Municipios únicos en Homicidios:",
      len(municipios_homicidios))

print("Municipios únicos en Secuestro:",
      len(municipios_secuestro))

print("Municipios presentes en ambas:",
      len(comunes_secuestro))

print("Solo en Homicidios:",
      len(solo_homicidios_secuestro))

print("Solo en Secuestro:",
      len(solo_secuestro))

print("Cobertura de Homicidios compartida:",
      round(
          len(comunes_secuestro) /
          len(municipios_homicidios) * 100, 2
      ),
      "%")

print("Cobertura de Secuestro compartida:",
      round(
          len(comunes_secuestro) /
          len(municipios_secuestro) * 100, 2
      ),
      "%")


# ==============================
# HOMICIDIOS VS TERRORISMO
# ==============================

comunes_terrorismo = (
    municipios_homicidios & municipios_terrorismo
)

solo_homicidios_terrorismo = (
    municipios_homicidios - municipios_terrorismo
)

solo_terrorismo = (
    municipios_terrorismo - municipios_homicidios
)

print()
print("HOMICIDIOS VS TERRORISMO")
print("------------------------")

print("Municipios únicos en Homicidios:",
      len(municipios_homicidios))

print("Municipios únicos en Terrorismo:",
      len(municipios_terrorismo))

print("Municipios presentes en ambas:",
      len(comunes_terrorismo))

print("Solo en Homicidios:",
      len(solo_homicidios_terrorismo))

print("Solo en Terrorismo:",
      len(solo_terrorismo))

print("Cobertura de Homicidios compartida:",
      round(
          len(comunes_terrorismo) /
          len(municipios_homicidios) * 100, 2
      ),
      "%")

print("Cobertura de Terrorismo compartida:",
      round(
          len(comunes_terrorismo) /
          len(municipios_terrorismo) * 100, 2
      ),
      "%")

print()
print("VERIFICACIÓN DE CÓDIGOS DE TERRORISMO")
print("--------------------------------------")

print("Primeros códigos de Terrorismo:")
print(
    terrorismo["CODIGO DANE"]
    .head(20)
    .to_string(index=False)
)

print()
print("Tipo de dato:")
print(terrorismo["CODIGO DANE"].dtype)

print()
print("VERIFICACIÓN DEL CÓDIGO DANE DE TERRORISMO")
print("-------------------------------------------")

terrorismo["COD_MUNI_PRUEBA"] = (
    terrorismo["CODIGO DANE"]
    .astype(str)
    .str[:5]
)

codigos_divipola = set(
    divipola["Código Municipio"]
    .astype(str)
    .str.zfill(5)
)

coinciden = terrorismo["COD_MUNI_PRUEBA"].isin(codigos_divipola)

print("Registros de Terrorismo:", len(terrorismo))
print("Códigos que coinciden con DIVIPOLA:", coinciden.sum())
print("Códigos que NO coinciden:", (~coinciden).sum())

print()
print(
    "Porcentaje que coincide:",
    round(coinciden.mean() * 100, 2),
    "%"
)

print()
print("DETALLE DE CÓDIGOS DE TERRORISMO SIN COINCIDENCIA")
print("--------------------------------------------------")

terrorismo_no_coincide = terrorismo.loc[
    ~coinciden,
    ["CODIGO DANE", "COD_MUNI_PRUEBA", "Departamento", "Municipio"]
]

print(
    terrorismo_no_coincide
    .drop_duplicates()
    .head(30)
    .to_string(index=False)
)

print()
print("COMPROBACIÓN DIRECTA EN DIVIPOLA")
print("--------------------------------")

codigos_prueba = ["57900", "58540", "51200", "55790", "53610"]

for codigo in codigos_prueba:
    
    resultado = divipola[
        divipola["Código Municipio"]
        .astype(str)
        .str.zfill(5) == codigo
    ]

    print()
    print("Código:", codigo)

    if len(resultado) > 0:
        print(
            resultado[
                ["Código Municipio", "Nombre Municipio", "Nombre Departamento"]
            ].to_string(index=False)
        )
    else:
        print("NO encontrado en DIVIPOLA")

        print()
print("INSPECCIÓN DE CÓDIGOS DE DIVIPOLA")
print("---------------------------------")

print("Tipo de dato:")
print(divipola["Código Municipio"].dtype)

print()
print("Primeros 20 códigos de municipio:")
print(
    divipola["Código Municipio"]
    .head(20)
    .to_string(index=False)
)

print()
print("Ejemplos de DIVIPOLA para Antioquia:")

print(
    divipola[
        divipola["Nombre Departamento"]
        .astype(str)
        .str.upper()
        .str.contains("ANTIOQUIA", na=False)
    ][
        [
            "Código Departamento",
            "Nombre Departamento",
            "Código Municipio",
            "Nombre Municipio"
        ]
    ]
    .head(30)
    .to_string(index=False)
)

print()
print("5.4.4 — VALIDACIÓN TERRITORIAL DE TERRORISMO")
print("--------------------------------------------")

terrorismo_nombres = (
    terrorismo[["Departamento", "Municipio"]]
    .drop_duplicates()
)

print("Combinaciones departamento-municipio en Terrorismo:",
      len(terrorismo_nombres))

print()
print("Primeras 20 combinaciones:")
print(
    terrorismo_nombres
    .head(20)
    .to_string(index=False)
)

print()
print("5.4.5 — TERRORISMO VS DIVIPOLA")
print("--------------------------------")

# Normalizar texto
terrorismo["DEP_NORMALIZADO"] = (
    terrorismo["Departamento"]
    .apply(normalizar_texto)
)

terrorismo["MUN_NORMALIZADO"] = (
    terrorismo["Municipio"]
    .apply(normalizar_texto)
)

divipola["DEP_NORMALIZADO"] = (
    divipola["Nombre Departamento"]
    .apply(normalizar_texto)
)

divipola["MUN_NORMALIZADO"] = (
    divipola["Nombre Municipio"]
    .apply(normalizar_texto)
)

# Pares únicos de territorio
territorios_terrorismo = (
    terrorismo[
        ["DEP_NORMALIZADO", "MUN_NORMALIZADO"]
    ]
    .drop_duplicates()
)

territorios_divipola = (
    divipola[
        ["DEP_NORMALIZADO", "MUN_NORMALIZADO"]
    ]
    .drop_duplicates()
)

# Comparación
territorios_comunes = territorios_terrorismo.merge(
    territorios_divipola,
    on=["DEP_NORMALIZADO", "MUN_NORMALIZADO"],
    how="inner"
)

print(
    "Territorios únicos en Terrorismo:",
    len(territorios_terrorismo)
)

print(
    "Territorios encontrados en DIVIPOLA:",
    len(territorios_comunes)
)

print(
    "Territorios no encontrados en DIVIPOLA:",
    len(territorios_terrorismo) -
    len(territorios_comunes)
)

print(
    "Porcentaje con correspondencia:",
    round(
        len(territorios_comunes) /
        len(territorios_terrorismo) * 100,
        2
    ),
    "%"
)

print()
print("TERRITORIOS DE TERRORISMO SIN CORRESPONDENCIA EN DIVIPOLA")
print("----------------------------------------------------------")

territorios_no_encontrados = (
    territorios_terrorismo.merge(
        territorios_divipola,
        on=["DEP_NORMALIZADO", "MUN_NORMALIZADO"],
        how="left",
        indicator=True
    )
)

territorios_no_encontrados = territorios_no_encontrados[
    territorios_no_encontrados["_merge"] == "left_only"
]

print(
    territorios_no_encontrados[
        ["DEP_NORMALIZADO", "MUN_NORMALIZADO"]
    ]
    .to_string(index=False)
)

def normalizar_terrorismo(valor):
    valor = normalizar_texto(valor)
    valor = valor.replace("(CT)", "")
    valor = valor.replace("D.C.", "DC")
    return " ".join(valor.split())

    terrorismo["MUN_NORMALIZADO"] = (
    terrorismo["Municipio"]
    .apply(normalizar_terrorismo)
)

divipola["MUN_NORMALIZADO"] = (
    divipola["Nombre Municipio"]
    .apply(normalizar_terrorismo)
)

territorios_terrorismo = (
    terrorismo[
        ["DEP_NORMALIZADO", "MUN_NORMALIZADO"]
    ]
    .drop_duplicates()
)

territorios_divipola = (
    divipola[
        ["DEP_NORMALIZADO", "MUN_NORMALIZADO"]
    ]
    .drop_duplicates()
)

territorios_comunes = territorios_terrorismo.merge(
    territorios_divipola,
    on=["DEP_NORMALIZADO", "MUN_NORMALIZADO"],
    how="inner"
)

print()
print("TERRORISMO VS DIVIPOLA — COMPARACIÓN NORMALIZADA")
print("--------------------------------------------------")

print("Territorios únicos en Terrorismo:",
      len(territorios_terrorismo))

print("Territorios con correspondencia:",
      len(territorios_comunes))

print("Territorios sin correspondencia:",
      len(territorios_terrorismo) - len(territorios_comunes))

print("Porcentaje de correspondencia:",
      round(
          len(territorios_comunes) /
          len(territorios_terrorismo) * 100,
          2
      ),
      "%")

print()
print("PASO 6 — DIAGNÓSTICO DE UNICIDAD")
print("---------------------------------")

print()
print("6.1 — FILAS COMPLETAMENTE DUPLICADAS")
print("--------------------------------------")

duplicados_exactos = df.duplicated(keep=False)

print(
    "Filas completamente duplicadas:",
    duplicados_exactos.sum()
)

print(
    "Porcentaje sobre el total:",
    round(
        duplicados_exactos.sum() / len(df) * 100,
        2
    ),
    "%"
)

print()
print("6.1.1 — FRECUENCIA DE LAS FILAS DUPLICADAS")
print("--------------------------------------------")

frecuencia_duplicados = (
    df.value_counts()
    .reset_index(name="frecuencia")
)

frecuencia_duplicados = frecuencia_duplicados[
    frecuencia_duplicados["frecuencia"] > 1
]

print(
    "Combinaciones de filas duplicadas:",
    len(frecuencia_duplicados)
)

print()
print("Distribución de la frecuencia:")

print(
    frecuencia_duplicados["frecuencia"]
    .value_counts()
    .sort_index()
    .to_string()
)

print()
print("6.2 — DUPLICADOS LÓGICOS")
print("-------------------------")

columnas_logicas = [
    "COD_MUNI",
    "FECHA HECHO",
    "CANTIDAD"
]

duplicados_logicos = df.duplicated(
    subset=columnas_logicas,
    keep=False
)

print(
    "Registros involucrados en duplicados lógicos:",
    duplicados_logicos.sum()
)

print(
    "Porcentaje sobre el total:",
    round(
        duplicados_logicos.sum() / len(df) * 100,
        2
    ),
    "%"
)

print()
print("6.2.1 — ANÁLISIS DE DUPLICADOS LÓGICOS")
print("----------------------------------------")

muestra_logicos = (
    df[duplicados_logicos]
    .sort_values(
        ["COD_MUNI", "FECHA HECHO", "CANTIDAD"]
    )
    .head(20)
)

print(
    muestra_logicos.to_string(index=False)
)

print()
print("6.2.2 — CLASIFICACIÓN DE DUPLICADOS LÓGICOS")
print("--------------------------------------------")

duplicados_logicos_diferentes = (
    df[duplicados_logicos]
    .drop_duplicates()
)

duplicados_logicos_diferentes = (
    duplicados_logicos_diferentes
    .groupby(
        ["COD_MUNI", "FECHA HECHO", "CANTIDAD"]
    )
    .size()
)

print(
    "Combinaciones lógicas con más de un registro:",
    len(duplicados_logicos_diferentes)
)

print()
print(
    "Estas combinaciones representan múltiples registros "
    "que comparten municipio, fecha y cantidad."
)

print()
print("6.3 — IMPACTO DE LOS DUPLICADOS EXACTOS")
print("-----------------------------------------")

filas_originales = len(df)

filas_duplicadas = duplicados_exactos.sum()

filas_a_conservar = filas_originales - filas_duplicadas + (
    df.value_counts().loc[
        df.value_counts() > 1
    ].shape[0]
)

print("Filas originales:", filas_originales)
print("Filas involucradas en duplicados:", filas_duplicadas)
print("Combinaciones duplicadas:", len(frecuencia_duplicados))
print("Filas después de conservar una sola copia:", filas_a_conservar)
print(
    "Filas potencialmente eliminables:",
    filas_originales - filas_a_conservar
)

cantidad_total = df["CANTIDAD"].sum()

cantidad_duplicados_exactos = df.loc[
    df.duplicated(keep=False),
    "CANTIDAD"
].sum()

porcentaje_duplicados = (
    cantidad_duplicados_exactos / cantidad_total
) * 100

print("Cantidad total:", cantidad_total)
print("Cantidad en filas duplicadas:", cantidad_duplicados_exactos)
print("Porcentaje sobre el total:", round(porcentaje_duplicados, 2), "%")

print()
print("PASO 7 — DIAGNÓSTICO DE OPORTUNIDAD")
print("------------------------------------")

ultima_fecha = df["FECHA HECHO"].max()
primera_fecha = df["FECHA HECHO"].min()

print("Primera fecha disponible:", primera_fecha)
print("Última fecha disponible:", ultima_fecha)

from datetime import datetime

hoy = datetime.now()

diferencia_meses = (
    (hoy.year - ultima_fecha.year) * 12
    + (hoy.month - ultima_fecha.month)
)

print()
print("7.2 — REZAGO DE LA INFORMACIÓN")
print("--------------------------------")
print("Fecha actual:", hoy.strftime("%Y-%m-%d"))
print("Última fecha del dataset:", ultima_fecha.strftime("%Y-%m-%d"))
print("Rezago aproximado:", diferencia_meses, "meses")

#Fin código