from pathlib import Path
from datetime import datetime
import unicodedata
import pandas as pd

# ============================================================
# AUDITORÍA DE CALIDAD DE DATOS — TALLER BI
# V2 — 6 FUENTES, PASOS 1 A 7 DEL TALLER
# ============================================================

BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / "RESULTADOS_AUDITORIA"
RESULTADOS.mkdir(parents=True, exist_ok=True)

# Los nombres se mantienen separados para poder detectar
# fácilmente cuál archivo no existe en la carpeta.
FUENTES = {
    "Homicidios": "7HOMICIDIO_20260903 (1).xlsx",
    "Secuestro": "2SECUESTRO_20260903.xlsx",
    "Extorsion": "3EXTORSIÓN_20260904.xlsx",
    "Terrorismo": "1Reporte_Delito_Terrorismo_Policía_Nacional_2019 A 2025.xlsx",
    "Coca": None,  # se localizará automáticamente por nombre
    "DIVIPOLA": "5DIVIPOLA-_Códigos_municipios_20260903vf.xlsx"
}

FECHA_AUDITORIA = datetime.now()

def normalizar_texto(valor):
    valor = str(valor).strip().upper()
    valor = ''.join(
        c for c in unicodedata.normalize("NFD", valor)
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(valor.split())

def guardar_linea(salida, texto=""):
    print(texto)
    with open(salida, "a", encoding="utf-8") as f:
        f.write(str(texto) + "\n")

def localizar_coca():
    candidatos = list(BASE.glob("*.xlsx"))
    encontrados = [
        f for f in candidatos
        if "COCA" in normalizar_texto(f.name)
        and "DETECCION" in normalizar_texto(f.name)
    ]
    return encontrados[0] if encontrados else None

def cargar_excel(archivo):
    return pd.read_excel(archivo)

# ============================================================
# PASOS COMUNES 1–4
# ============================================================

def pasos_1_4(nombre, df, archivo, salida):
    p = lambda x="": guardar_linea(salida, x)

    p("=" * 70)
    p(f"AUDITORÍA — {nombre}")
    p("=" * 70)

    # PASO 1
    p("\nPASO 1 — DESCARGA Y REGISTRO DE LA FUENTE")
    p("--------------------------------------------")
    p(f"Archivo: {archivo.name}")
    p(f"Ruta: {archivo.resolve()}")
    p(f"Fecha de auditoría/registro: {FECHA_AUDITORIA:%Y-%m-%d %H:%M}")
    p(f"Formato: {archivo.suffix}")
    p(f"Tamaño (MB): {archivo.stat().st_size / 1_000_000:.2f}")
    p(f"Filas antes de modificaciones: {df.shape[0]}")
    p(f"Columnas: {df.shape[1]}")

    # PASO 2
    p("\nPASO 2 — EXPLORACIÓN INICIAL DE LA ESTRUCTURA")
    p("-----------------------------------------------")
    p("Columnas exactas:")
    for c in df.columns:
        p(f"- {c}")

    p("\nTipos de datos:")
    p(df.dtypes.to_string())

    p("\nPrimeras 5 filas:")
    p(df.head().to_string(index=False))

    p("\nColumnas que requieren revisión mediante diccionario:")
    for c in df.columns:
        cu = str(c).strip().upper()
        if any(x in cu for x in ["COD", "ARMA", "MEDIO", "MODAL", "TIPO", "SPOA", "CARACTER"]):
            p(f"- {c}")

    p("\nEncabezados: se encuentran en la primera fila del archivo.")
    p("Separador decimal/miles: se revisa según el tipo cargado; las columnas numéricas se almacenan como números.")

    # PASO 3
    p("\nPASO 3 — DIAGNÓSTICO DE COMPLETITUD")
    p("------------------------------------")

    nulos = df.isna().sum()
    p("Nulos por columna:")
    for c in df.columns:
        p(f"- {c}: {nulos[c]} ({nulos[c]/len(df)*100:.2f}%)")

    col_fecha = next(
        (c for c in df.columns if "FECHA" in str(c).upper()),
        None
    )

    fecha = None
    if col_fecha:
        # Terrorismo necesita dayfirst porque viene como DD/MM/YYYY.
        if nombre == "Terrorismo":
            fecha = pd.to_datetime(
                df[col_fecha], errors="coerce", dayfirst=True
            )
        else:
            fecha = pd.to_datetime(df[col_fecha], errors="coerce")

        p(f"\nColumna de fecha: {col_fecha}")
        p(f"Fechas no interpretables: {fecha.isna().sum()}")

        if fecha.notna().any():
            p(f"Años disponibles: {sorted(fecha.dropna().dt.year.unique().tolist())}")
            p("Meses disponibles por año:")
            for anio in sorted(fecha.dropna().dt.year.unique()):
                meses = sorted(
                    fecha.loc[fecha.dt.year == anio].dt.month.unique().tolist()
                )
                p(f"- {anio}: {meses}")

    col_mun = next(
        (c for c in df.columns
         if str(c).strip().upper() in
         ["COD_MUNI", "CODIGO DANE", "CÓDIGO MUNICIPIO"]),
        None
    )

    col_depto = next(
        (c for c in df.columns
         if str(c).strip().upper() in
         ["DEPARTAMENTO", "NOMBRE DEPARTAMENTO"]),
        None
    )

    if col_depto:
        p(f"\nDepartamentos únicos ({col_depto}): {df[col_depto].nunique()}")

    if col_mun:
        p(f"Municipios/códigos únicos ({col_mun}): {df[col_mun].nunique()}")

    # PASO 4
    p("\nPASO 4 — DIAGNÓSTICO DE EXACTITUD Y VALIDEZ")
    p("---------------------------------------------")

    col_cantidad = next(
        (c for c in df.columns if str(c).strip().upper() == "CANTIDAD"),
        None
    )

    if col_cantidad:
        cantidad = pd.to_numeric(df[col_cantidad], errors="coerce")
        p(f"Valores negativos en {col_cantidad}: {(cantidad < 0).sum()}")
        p(f"Máximo en {col_cantidad}: {cantidad.max()}")

    if fecha is not None:
        p(f"Fechas no interpretables: {fecha.isna().sum()}")
        if fecha.notna().any():
            p(f"Fecha mínima: {fecha.min()}")
            p(f"Fecha máxima: {fecha.max()}")

            fuera = (
                (fecha < pd.Timestamp("2019-01-01")) |
                (fecha > pd.Timestamp("2025-12-31"))
            ).sum()

            p(f"Fechas fuera de 2019–2025: {fuera}")

    if col_mun:
        codigos = (
            df[col_mun]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
        )
        p("\nLongitud de códigos:")
        p(codigos.str.len().value_counts().sort_index().to_string())

    return fecha, col_fecha, col_mun, col_depto, col_cantidad

# ============================================================
# PASO 5 — CONSISTENCIA
# ============================================================

def paso_5(nombre, df, fecha, col_mun, col_depto, col_cantidad, salida, divipola=None):
    p = lambda x="": guardar_linea(salida, x)

    p("\nPASO 5 — DIAGNÓSTICO DE CONSISTENCIA")
    p("-------------------------------------")

    # 5.1 y 5.2: comparación con DIVIPOLA cuando hay códigos municipales.
    if divipola is not None and col_mun is not None:
        d = divipola.copy()

        d["COD_MUNI_VALIDADO"] = (
            d["Código Municipio"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(5)
        )

        trabajo = df.copy()
        trabajo["COD_MUNI_VALIDADO"] = (
            trabajo[col_mun]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(5)
        )

        p("5.1 Consistencia municipio/código contra DIVIPOLA:")

        cruce = trabajo.merge(
            d[[
                "COD_MUNI_VALIDADO",
                "Nombre Municipio",
                "Nombre Departamento"
            ]],
            on="COD_MUNI_VALIDADO",
            how="left"
        )

        if "MUNICIPIO" in trabajo.columns:
            cruce["NOMBRE_FUENTE_NORM"] = cruce["MUNICIPIO"].apply(normalizar_texto)
            cruce["NOMBRE_DIVIPOLA_NORM"] = cruce["Nombre Municipio"].apply(normalizar_texto)

            diferencias = cruce[
                cruce["NOMBRE_FUENTE_NORM"] != cruce["NOMBRE_DIVIPOLA_NORM"]
            ]

            p(f"Registros con diferencia de denominación: {len(diferencias)}")
            p(f"Porcentaje: {len(diferencias)/len(cruce)*100:.2f}%")

            p("Combinaciones de denominación diferentes:")
            p(
                diferencias[
                    ["COD_MUNI_VALIDADO", "MUNICIPIO", "Nombre Municipio"]
                ].drop_duplicates().to_string(index=False)
            )

        p("\n5.2 Mismo municipio con nombres distintos dentro del archivo:")

        if "MUNICIPIO" in df.columns:
            varios = df.groupby(col_mun)["MUNICIPIO"].nunique()
            p(f"Códigos con más de un nombre: {(varios > 1).sum()}")
        else:
            p("No aplica: la fuente no contiene columna MUNICIPIO.")

    else:
        p("5.1 Comparación con DIVIPOLA: no aplica con la estructura actual.")
        p("5.2 Consistencia interna de nombres: no aplica o requiere regla específica.")

    # 5.3 Agregaciones para fuentes de delitos
    if fecha is not None and col_cantidad and col_depto and col_mun:
        p("\n5.3 Coherencia de agregaciones:")

        trabajo = df.copy()
        trabajo["_FECHA"] = fecha

        anual_depto = (
            trabajo.groupby(
                [trabajo["_FECHA"].dt.year, col_depto]
            )[col_cantidad].sum()
        )

        mensual_depto = (
            trabajo.assign(
                _MES=trabajo["_FECHA"].dt.to_period("M")
            )
            .groupby(
                [trabajo["_FECHA"].dt.year, col_depto, "_MES"]
            )[col_cantidad].sum()
            .groupby(level=[0,1]).sum()
        )

        comparacion = pd.concat(
            [anual_depto.rename("ANUAL"),
             mensual_depto.rename("SUMA_MENSUAL")],
            axis=1
        ).fillna(0)

        p(
            "Diferencias año-departamento: "
            f"{(comparacion['ANUAL'] != comparacion['SUMA_MENSUAL']).sum()}"
        )

        anual_mun = (
            trabajo.groupby(
                [trabajo["_FECHA"].dt.year, col_mun]
            )[col_cantidad].sum()
        )

        mensual_mun = (
            trabajo.assign(
                _MES=trabajo["_FECHA"].dt.to_period("M")
            )
            .groupby(
                [trabajo["_FECHA"].dt.year, col_mun, "_MES"]
            )[col_cantidad].sum()
            .groupby(level=[0,1]).sum()
        )

        comparacion_mun = pd.concat(
            [anual_mun.rename("ANUAL"),
             mensual_mun.rename("SUMA_MENSUAL")],
            axis=1
        ).fillna(0)

        p(
            "Diferencias año-municipio: "
            f"{(comparacion_mun['ANUAL'] != comparacion_mun['SUMA_MENSUAL']).sum()}"
        )

    else:
        p("\n5.3 Coherencia de agregaciones: requiere estructura temporal y variable CANTIDAD.")

    # 5.4 Cobertura entre fuentes de delitos se realiza después,
    # cuando todas estén cargadas.

# ============================================================
# PASO 6
# ============================================================

def paso_6(df, col_mun, col_fecha, col_cantidad, salida):
    p = lambda x="": guardar_linea(salida, x)

    p("\nPASO 6 — DIAGNÓSTICO DE UNICIDAD")
    p("---------------------------------")

    dup_ex = df.duplicated(keep=False)
    p(f"Filas involucradas en duplicados exactos: {dup_ex.sum()}")
    p(f"Porcentaje: {dup_ex.mean()*100:.2f}%")
    p(f"Combinaciones exactas duplicadas: {(df.value_counts() > 1).sum()}")

    if col_mun and col_fecha and col_cantidad:
        dup_log = df.duplicated(
            subset=[col_mun, col_fecha, col_cantidad],
            keep=False
        )

        p(f"Filas involucradas en duplicados lógicos: {dup_log.sum()}")
        p(f"Porcentaje: {dup_log.mean()*100:.2f}%")

        combos_log = df.groupby(
            [col_mun, col_fecha, col_cantidad]
        ).size()

        p(f"Combinaciones lógicas duplicadas: {(combos_log > 1).sum()}")

        cantidad = pd.to_numeric(df[col_cantidad], errors="coerce")
        total = cantidad.sum()
        duplicada = cantidad.loc[dup_ex].sum()

        p(f"Cantidad total: {total}")
        p(f"Cantidad en filas duplicadas exactas: {duplicada}")

        if total:
            p(f"Porcentaje sobre el total: {duplicada/total*100:.2f}%")

# ============================================================
# PASO 7
# ============================================================

def paso_7(fecha, nombre, salida):
    p = lambda x="": guardar_linea(salida, x)

    p("\nPASO 7 — DIAGNÓSTICO DE OPORTUNIDAD")
    p("------------------------------------")

    if fecha is None or not fecha.notna().any():
        p("No aplica: la fuente no contiene una variable temporal utilizable.")
        return

    primera = fecha.min()
    ultima = fecha.max()

    rezago = (
        (FECHA_AUDITORIA.year - ultima.year) * 12
        + FECHA_AUDITORIA.month - ultima.month
    )

    p(f"Primera fecha disponible: {primera}")
    p(f"Última fecha disponible: {ultima}")
    p(f"Fecha de auditoría: {FECHA_AUDITORIA:%Y-%m-%d}")
    p(f"Rezago aproximado: {rezago} meses")
    p(f"2025 disponible: {2025 in fecha.dropna().dt.year.unique()}")

    if nombre in ["Homicidios", "Secuestro", "Extorsion", "Terrorismo"]:
        p("Frecuencia documentada para estas fuentes de Estadística Delictiva: mensual.")
    elif nombre == "Coca":
        p("Frecuencia: requiere documentar según la publicación oficial de SIMCI/ODC.")
    else:
        p("Frecuencia: no aplica como serie temporal; DIVIPOLA es una referencia territorial vigente.")

# ============================================================
# 5.4 — COBERTURA ENTRE LAS FUENTES DE DELITOS
# ============================================================

def paso_5_4_cobertura(dfs, salida_global):
    p = lambda x="": guardar_linea(salida_global, x)

    p("\n5.4 — COBERTURA TERRITORIAL ENTRE FUENTES DE DELITOS")
    p("------------------------------------------------------")

    sets = {}

    for nombre in ["Homicidios", "Secuestro", "Extorsion"]:
        if nombre in dfs and "COD_MUNI" in dfs[nombre].columns:
            sets[nombre] = set(
                dfs[nombre]["COD_MUNI"]
                .astype(str)
                .str.replace(r"\.0$", "", regex=True)
                .str.zfill(5)
            )

    if "Terrorismo" in dfs:
        t = dfs["Terrorismo"].copy()
        t["_TERRITORIO"] = (
            t["Departamento"].apply(normalizar_texto)
            + " | "
            + t["Municipio"].apply(normalizar_texto)
        )
        sets["Terrorismo"] = set(t["_TERRITORIO"])

    if "Homicidios" in sets:
        for otro in ["Secuestro", "Extorsion"]:
            if otro in sets:
                comunes = len(sets["Homicidios"] & sets[otro])
                p(f"Homicidios vs {otro}:")
                p(f"- Homicidios: {len(sets['Homicidios'])}")
                p(f"- {otro}: {len(sets[otro])}")
                p(f"- Municipios comunes: {comunes}")
                p(f"- Solo Homicidios: {len(sets['Homicidios'] - sets[otro])}")
                p(f"- Solo {otro}: {len(sets[otro] - sets['Homicidios'])}")

    if "Terrorismo" in dfs:
        h = dfs["Homicidios"].copy()
        h["_TERRITORIO"] = (
            h["DEPARTAMENTO"].apply(normalizar_texto)
            + " | "
            + h["MUNICIPIO"].apply(normalizar_texto)
        )
        hset = set(h["_TERRITORIO"])
        comunes = len(hset & sets["Terrorismo"])
        p("Homicidios vs Terrorismo — comparación textual departamento + municipio:")
        p(f"- Territorios Homicidios: {len(hset)}")
        p(f"- Territorios Terrorismo: {len(sets['Terrorismo'])}")
        p(f"- Territorios comunes: {comunes}")
        p(f"- Solo Terrorismo: {len(sets['Terrorismo'] - hset)}")

# ============================================================
# PROCESAMIENTO PRINCIPAL
# ============================================================

print("=" * 70)
print("AUDITORÍA DE LAS 6 FUENTES — V2")
print("=" * 70)
print("Carpeta base:", BASE)
print("Resultados:", RESULTADOS)
print("Fecha de auditoría:", FECHA_AUDITORIA.strftime("%Y-%m-%d %H:%M"))
print()

dfs = {}
metadatos = {}

for nombre, nombre_archivo in FUENTES.items():

    print("\n" + "#" * 70)
    print(f"PROCESANDO: {nombre}")
    print("#" * 70)

    if nombre == "Coca":
        archivo = localizar_coca()
        if archivo is None:
            print("ERROR: no se encontró automáticamente el archivo de Coca.")
            continue
    else:
        archivo = BASE / nombre_archivo

    if not archivo.exists():
        print(f"ERROR: no se encontró {archivo}")
        continue

    try:
        df = cargar_excel(archivo)
        dfs[nombre] = df

        carpeta = RESULTADOS / nombre
        carpeta.mkdir(parents=True, exist_ok=True)
        salida = carpeta / "resultado_auditoria.txt"

        if salida.exists():
            salida.unlink()

        fecha, col_fecha, col_mun, col_depto, col_cantidad = pasos_1_4(
            nombre, df, archivo, salida
        )

        # Para Terrorismo ya se convirtió la fecha con dayfirst=True.
        # Para el resto se conserva el comportamiento normal.
        paso_5(
            nombre, df, fecha, col_mun, col_depto,
            col_cantidad, salida,
            None  # DIVIPOLA se cruza después, con reglas controladas
        )

        paso_6(
            df,
            col_mun,
            col_fecha,
            col_cantidad,
            salida
        )

        paso_7(fecha, nombre, salida)

        metadatos[nombre] = {
            "archivo": archivo,
            "fecha": fecha,
            "col_fecha": col_fecha,
            "col_mun": col_mun,
            "col_depto": col_depto,
            "col_cantidad": col_cantidad
        }

        print("\nFIN DE AUDITORÍA")

    except Exception as e:
        print(f"ERROR procesando {nombre}: {type(e).__name__}: {e}")

# ============================================================
# CONSISTENCIA CON DIVIPOLA
# ============================================================

if "DIVIPOLA" in dfs:
    divipola = dfs["DIVIPOLA"]

    print("\n" + "#" * 70)
    print("VALIDACIÓN CON DIVIPOLA")
    print("#" * 70)

    for nombre in ["Homicidios", "Secuestro", "Extorsion"]:
        if nombre not in dfs:
            continue

        df = dfs[nombre]
        if "COD_MUNI" not in df.columns:
            continue

        salida = RESULTADOS / nombre / "resultado_auditoria.txt"

        p = lambda x="": guardar_linea(salida, x)

        p("\n5.1 — CONSISTENCIA CON DIVIPOLA")

        d = divipola.copy()
        d["_COD5"] = (
            d["Código Municipio"].astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(5)
        )

        x = df.copy()
        x["_COD5"] = (
            x["COD_MUNI"].astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(5)
        )

        cruce = x.merge(
            d[["_COD5", "Nombre Municipio", "Nombre Departamento"]],
            on="_COD5",
            how="left"
        )

        no_encontrados = cruce["Nombre Municipio"].isna().sum()
        p(f"Códigos municipales no encontrados en DIVIPOLA: {no_encontrados}")

        if "MUNICIPIO" in x.columns:
            cruce["FUENTE_NORM"] = cruce["MUNICIPIO"].apply(normalizar_texto)
            cruce["DIVIPOLA_NORM"] = cruce["Nombre Municipio"].apply(normalizar_texto)
            diferencias = cruce[
                cruce["FUENTE_NORM"] != cruce["DIVIPOLA_NORM"]
            ]
            p(f"Registros con diferencia de denominación: {len(diferencias)}")
            p(f"Porcentaje: {len(diferencias)/len(cruce)*100:.2f}%")
            p("Denominaciones diferentes por código:")
            p(
                diferencias[
                    ["_COD5", "MUNICIPIO", "Nombre Municipio"]
                ].drop_duplicates().to_string(index=False)
            )

# ============================================================
# 5.4 GLOBAL
# ============================================================

salida_global = RESULTADOS / "resumen_cobertura_territorial.txt"
if salida_global.exists():
    salida_global.unlink()

paso_5_4_cobertura(dfs, salida_global)

print("\n" + "=" * 70)
print("AUDITORÍA TERMINADA")
print("=" * 70)
print("Revisa la carpeta:", RESULTADOS)
