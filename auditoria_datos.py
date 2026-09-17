
# auditoria_datos.py
# Auditoría primaria de las 6 fuentes del Taller de Auditoría de Datos.
# El script NO corrige ni elimina datos. Detecta y documenta resultados.
#
# Coloca este archivo en la misma carpeta de las 6 fuentes:
#   - DIVIPOLA-_Códigos_municipios_*.csv
#   - Detección_de_Cultivos_de_Coca_*.csv
#   - Homicidio*.xlsx
#   - Secuestro*.xlsx
#   - Extorsión*.xlsx
#   - Terrorismo*.xlsx
#
# Requiere:
#   pip install pandas openpyxl

from pathlib import Path
from datetime import datetime
import re
import pandas as pd

CARPETA = Path(__file__).resolve().parent
SALIDA = CARPETA / "RESULTADOS_AUDITORIA"
SALIDA.mkdir(exist_ok=True)

PERIODO_INICIO = 2019
PERIODO_FIN = 2025
MUNICIPIOS_DIVIPOLA_ESPERADOS = 1122

# ------------------------------------------------------------
# 1. CARGA
# ------------------------------------------------------------

def encontrar_archivo(patrones):
    archivos = []
    for patron in patrones:
        archivos.extend(CARPETA.glob(patron))
    if not archivos:
        return None
    return sorted(archivos)[0]

def leer_archivo(path):
    if path is None:
        return None

    if path.suffix.lower() in [".xlsx", ".xls"]:
        # header=None permite detectar si existen filas de título antes
        bruto = pd.read_excel(path, header=None)
        # Primera fila no completamente vacía como encabezado
        encabezado = None
        for i in range(min(20, len(bruto))):
            valores = bruto.iloc[i].astype(str).str.strip()
            if valores.notna().sum() >= 2 and any(
                x.lower() not in ["nan", "none", ""] for x in valores
            ):
                encabezado = i
                break
        if encabezado is None:
            encabezado = 0
        df = pd.read_excel(path, header=encabezado)
        return df, bruto, encabezado

    # CSV: primero intenta UTF-8, luego latin-1; detecta separador
    try:
        bruto = pd.read_csv(path, header=None, encoding="utf-8", sep=None, engine="python")
        df = pd.read_csv(path, encoding="utf-8", sep=None, engine="python")
    except Exception:
        bruto = pd.read_csv(path, header=None, encoding="latin-1", sep=None, engine="python")
        df = pd.read_csv(path, encoding="latin-1", sep=None, engine="python")
    return df, bruto, 0

def tipo_variable(dtype):
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "fecha"
    if pd.api.types.is_bool_dtype(dtype):
        return "booleano"
    if pd.api.types.is_numeric_dtype(dtype):
        return "número"
    return "texto"

# ------------------------------------------------------------
# 2. NORMALIZACIÓN SOLO PARA PRUEBAS
# ------------------------------------------------------------

def buscar_columna(df, palabras):
    columnas = [str(c) for c in df.columns]
    for p in palabras:
        for c in columnas:
            if p.lower() in c.lower():
                return c
    return None

def serie_codigo_dane(df):
    c = buscar_columna(df, ["CODIGO DANE", "Código DANE", "codigo_dane", "cod_municipio", "Código Municipio"])
    if c is None:
        return None, None
    s = df[c].astype("string").str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    return s, c

def serie_fecha(df):
    c = buscar_columna(df, ["FECHA HECHO", "fecha", "FECHA"])
    if c is None:
        return None, None
    s = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
    return s, c

def serie_anio(df):
    c = buscar_columna(df, ["año", "anio", "AÑO", "ANIO"])
    if c:
        s = pd.to_numeric(df[c], errors="coerce")
        return s, c

    fecha, fc = serie_fecha(df)
    if fecha is not None:
        return fecha.dt.year, fc
    return None, None

# ------------------------------------------------------------
# 3. PASO 1 — DESCARGA Y REGISTRO
# ------------------------------------------------------------

def paso1(path, df):
    return {
        "Archivo": path.name if path else "NO ENCONTRADO",
        "Fecha de ejecución": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Formato": path.suffix.upper() if path else "",
        "Tamaño (MB)": round(path.stat().st_size / 1_000_000, 3) if path else "",
        "Filas": len(df) if df is not None else "",
        "Columnas": len(df.columns) if df is not None else "",
        "Ruta": str(path.resolve()) if path else ""
    }

# ------------------------------------------------------------
# PASO 2 — EXPLORACIÓN INICIAL
# ------------------------------------------------------------

def paso2(df):
    registros = []
    for c in df.columns:
        registros.append({
            "Columna": str(c),
            "Tipo físico": str(df[c].dtype),
            "Tipo según Python": tipo_variable(df[c].dtype),
            "Valores únicos": df[c].nunique(dropna=True),
            "Nulos": int(df[c].isna().sum())
        })

    return pd.DataFrame(registros)

# ------------------------------------------------------------
# PASO 3 — COMPLETITUD
# ------------------------------------------------------------

def paso3(df):
    hallazgos = []

    # Nulos
    nulos = df.isna().sum()
    for c, n in nulos.items():
        pct = n / len(df) * 100 if len(df) else 0
        if n > 0:
            hallazgos.append({
                "Prueba": "Valores nulos",
                "Campo": str(c),
                "Resultado": f"{n} valores nulos ({pct:.2f}%)",
                "Afectados": int(n),
                "Porcentaje": round(pct, 2)
            })

    # Años
    anio, _ = serie_anio(df)
    if anio is not None:
        presentes = sorted(anio.dropna().astype(int).unique())
        faltantes = [a for a in range(PERIODO_INICIO, PERIODO_FIN + 1)
                     if a not in presentes]
        hallazgos.append({
            "Prueba": "Años del período 2019–2025",
            "Campo": "Año/fecha",
            "Resultado": f"Presentes: {presentes}; faltantes: {faltantes}",
            "Afectados": "",
            "Porcentaje": ""
        })

    # Municipios
    codigo, cc = serie_codigo_dane(df)
    if codigo is not None:
        unicos = codigo.dropna().nunique()
        hallazgos.append({
            "Prueba": "Municipios únicos",
            "Campo": cc,
            "Resultado": f"{unicos} municipios/códigos únicos frente a 1.122 esperados",
            "Afectados": "",
            "Porcentaje": ""
        })

    return pd.DataFrame(hallazgos)

# ------------------------------------------------------------
# PASO 4 — EXACTITUD Y VALIDEZ
# ------------------------------------------------------------

def paso4(df):
    hallazgos = []

    # Negativos
    for c in df.select_dtypes(include="number").columns:
        n = int((df[c] < 0).sum())
        if n:
            hallazgos.append({
                "Prueba": "Valores negativos",
                "Campo": str(c),
                "Resultado": f"{n} valores negativos",
                "Afectados": n,
                "Porcentaje": round(n / len(df) * 100, 2)
            })

    # Códigos DANE
    codigo, cc = serie_codigo_dane(df)
    if codigo is not None:
        longitudes = codigo.dropna().str.len()
        incorrectos = int((longitudes != 5).sum())
        hallazgos.append({
            "Prueba": "Códigos DANE de exactamente 5 dígitos",
            "Campo": cc,
            "Resultado": f"{incorrectos} códigos con longitud diferente de 5",
            "Afectados": incorrectos,
            "Porcentaje": round(incorrectos / len(df) * 100, 2)
        })

    # Fechas
    fecha, fc = serie_fecha(df)
    if fecha is not None:
        invalidas = int(fecha.isna().sum())
        fuera = int(((fecha.notna()) &
                     ((fecha.dt.year < PERIODO_INICIO) |
                      (fecha.dt.year > PERIODO_FIN))).sum())
        hallazgos.extend([
            {
                "Prueba": "Fechas inválidas/no interpretables",
                "Campo": fc,
                "Resultado": f"{invalidas} fechas no interpretables",
                "Afectados": invalidas,
                "Porcentaje": round(invalidas / len(df) * 100, 2)
            },
            {
                "Prueba": "Fechas fuera del rango 2019–2025",
                "Campo": fc,
                "Resultado": f"{fuera} fechas fuera del rango",
                "Afectados": fuera,
                "Porcentaje": round(fuera / len(df) * 100, 2)
            }
        ])

    # Posibles outliers IQR SOLO como señal, no como afirmación de error
    for c in df.select_dtypes(include="number").columns:
        s = df[c].dropna()
        if len(s) >= 4 and s.nunique() > 3:
            q1, q3 = s.quantile([.25, .75])
            iqr = q3 - q1
            if iqr > 0:
                n = int((s > q3 + 1.5 * iqr).sum())
                if n:
                    hallazgos.append({
                        "Prueba": "Valores extremos según IQR",
                        "Campo": str(c),
                        "Resultado": f"{n} valores por encima de Q3 + 1.5×IQR; requiere revisión",
                        "Afectados": n,
                        "Porcentaje": round(n / len(df) * 100, 2)
                    })

    return pd.DataFrame(hallazgos)

# ------------------------------------------------------------
# PASO 5 — CONSISTENCIA
# ------------------------------------------------------------

def paso5(df, divipola=None):
    hallazgos = []
    codigo, cc = serie_codigo_dane(df)

    if codigo is not None and divipola is not None:
        dcodigo, dcc = serie_codigo_dane(divipola)
        if dcodigo is not None:
            validos = set(dcodigo.dropna().str.zfill(5))
            cod = codigo.dropna().str.zfill(5)
            huerfanos = ~cod.isin(validos)
            n = int(huerfanos.sum())
            hallazgos.append({
                "Prueba": "Municipio/código DANE contra DIVIPOLA",
                "Campo": cc,
                "Resultado": f"{n} registros con código no encontrado en DIVIPOLA",
                "Afectados": n,
                "Porcentaje": round(n / len(df) * 100, 2)
            })

    # Múltiples nombres para un mismo código
    nombre = buscar_columna(df, ["MUNICIPIO", "Municipio", "nombre_municipio", "Nombre Municipio"])
    if codigo is not None and nombre is not None:
        tmp = pd.DataFrame({"codigo": codigo, "nombre": df[nombre].astype("string").str.strip()})
        multiples = tmp.groupby("codigo")["nombre"].nunique(dropna=True)
        n_cod = int((multiples > 1).sum())
        hallazgos.append({
            "Prueba": "Un municipio aparece con nombres distintos",
            "Campo": f"{cc} + {nombre}",
            "Resultado": f"{n_cod} códigos presentan más de un nombre",
            "Afectados": n_cod,
            "Porcentaje": ""
        })

    return pd.DataFrame(hallazgos)

# ------------------------------------------------------------
# PASO 6 — UNICIDAD
# ------------------------------------------------------------

def paso6(df):
    hallazgos = []

    exactos = int(df.duplicated(keep=False).sum())
    hallazgos.append({
        "Prueba": "Filas completamente idénticas",
        "Campo": "Todas las columnas",
        "Resultado": f"{exactos} filas pertenecen a grupos duplicados",
        "Afectados": exactos,
        "Porcentaje": round(exactos / len(df) * 100, 2)
    })

    codigo, cc = serie_codigo_dane(df)
    fecha, fc = serie_fecha(df)
    anio, ac = serie_anio(df)

    cantidad = buscar_columna(df, ["CANTIDAD", "cantidad", "víctimas", "hectáreas", "hectareas"])
    claves = []
    if codigo is not None: claves.append(codigo.rename("codigo"))
    if fecha is not None: claves.append(fecha.rename("fecha"))
    if cantidad is not None: claves.append(pd.to_numeric(df[cantidad], errors="coerce").rename("valor"))

    if len(claves) >= 2:
        tmp = pd.concat(claves, axis=1)
        dup = tmp.duplicated(keep=False)
        n = int(dup.sum())
        hallazgos.append({
            "Prueba": "Duplicado lógico",
            "Campo": "código DANE + fecha + valor",
            "Resultado": f"{n} filas pertenecen a grupos potencialmente duplicados",
            "Afectados": n,
            "Porcentaje": round(n / len(df) * 100, 2)
        })

    return pd.DataFrame(hallazgos)

# ------------------------------------------------------------
# PASO 7 — OPORTUNIDAD
# ------------------------------------------------------------

def paso7(df):
    hallazgos = []
    anio, campo = serie_anio(df)
    fecha, fc = serie_fecha(df)

    if fecha is not None and fecha.notna().any():
        ultimo = fecha.max()
        hoy = pd.Timestamp.today().normalize()
        meses = (hoy.year - ultimo.year) * 12 + (hoy.month - ultimo.month)
        hallazgos.append({
            "Prueba": "Último período disponible",
            "Campo": fc,
            "Resultado": str(ultimo.date()),
            "Afectados": "",
            "Porcentaje": ""
        })
        hallazgos.append({
            "Prueba": "Rezago",
            "Campo": fc,
            "Resultado": f"Aproximadamente {meses} meses",
            "Afectados": "",
            "Porcentaje": ""
        })
    elif anio is not None and anio.notna().any():
        ultimo = int(anio.max())
        hallazgos.append({
            "Prueba": "Último período disponible",
            "Campo": campo,
            "Resultado": str(ultimo),
            "Afectados": "",
            "Porcentaje": ""
        })

    return pd.DataFrame(hallazgos)

# ------------------------------------------------------------
# EJECUCIÓN PARA LAS 6 FUENTES
# ------------------------------------------------------------

ARCHIVOS = {
    "Homicidios": [
        "*Homicidio*.xlsx",
        "*Homicidio*.xls"
    ],

    "Secuestros": [
        "*Secuestro*.xlsx",
        "*Secuestro*.xls"
    ],

    "Extorsión": [
        "*Extorsión*.xlsx",
        "*Extorsion*.xlsx",
        "*Extorsión*.xls",
        "*Extorsion*.xls"
    ],

    "Actos terroristas": [
        "*Terrorismo*.xlsx",
        "*Terrorismo*.xls"
    ],

    "Cultivos de hoja de coca": [
        "*Cultivos*de*Coca*.xlsx",
        "*Cultivos*de*Coca*.xls",
        "*Cultivos*de*Coca*.csv"
    ],

    "División político-administrativa": [
        "*DIVIPOLA*.xlsx",
        "*DIVIPOLA*.xls",
        "*DIVIPOLA*.csv"
    ]
}

resultados_hallazgos = []
resumen_fuentes = []

archivos_cargados = {}
dfs = {}

for nombre, patrones in ARCHIVOS.items():
    path = encontrar_archivo(patrones)
    if path is None:
        resumen_fuentes.append({
            "Fuente": nombre,
            "Archivo": "NO ENCONTRADO",
            "Estado": "Pendiente: archivo no encontrado"
        })
        continue

    try:
        df, bruto, fila_encabezado = leer_archivo(path)
        archivos_cargados[nombre] = path
        dfs[nombre] = df

        carpeta = SALIDA / re.sub(r"[^A-Za-z0-9]+", "_", nombre)
        carpeta.mkdir(exist_ok=True)

        pd.DataFrame([paso1(path, df)]).to_csv(carpeta/"01_registro_fuente.csv", index=False, encoding="utf-8-sig")
        paso2(df).to_csv(carpeta/"02_exploracion_estructura.csv", index=False, encoding="utf-8-sig")
        paso3(df).to_csv(carpeta/"03_completitud.csv", index=False, encoding="utf-8-sig")
        paso4(df).to_csv(carpeta/"04_exactitud_validez.csv", index=False, encoding="utf-8-sig")
        paso5(df, dfs.get("División político-administrativa")).to_csv(carpeta/"05_consistencia.csv", index=False, encoding="utf-8-sig")
        paso6(df).to_csv(carpeta/"06_unicidad.csv", index=False, encoding="utf-8-sig")
        paso7(df).to_csv(carpeta/"07_oportunidad.csv", index=False, encoding="utf-8-sig")

        resumen_fuentes.append({
            "Fuente": nombre,
            "Archivo": path.name,
            "Estado": "Analizado",
            "Filas": len(df),
            "Columnas": len(df.columns),
            "Fila encabezado detectada": fila_encabezado + 1
        })

    except Exception as e:
        resumen_fuentes.append({
            "Fuente": nombre,
            "Archivo": path.name if path else "",
            "Estado": f"ERROR: {e}"
        })

# Segunda pasada para consistencia, porque DIVIPOLA puede haberse cargado después
if "División político-administrativa" in dfs:
    for nombre, df in dfs.items():
        if nombre == "División político-administrativa":
            continue
        carpeta = SALIDA / re.sub(r"[^A-Za-z0-9]+", "_", nombre)
        paso5(df, dfs["División político-administrativa"]).to_csv(
            carpeta/"05_consistencia.csv", index=False, encoding="utf-8-sig"
        )

# ------------------------------------------------------------
# RESUMEN CONSOLIDADO DE HALLAZGOS
# ------------------------------------------------------------

DIMENSIONES = {
    "03_completitud.csv": "Completitud",
    "04_exactitud_validez.csv": "Exactitud / Validez",
    "05_consistencia.csv": "Consistencia",
    "06_unicidad.csv": "Unicidad",
    "07_oportunidad.csv": "Oportunidad"
}

for nombre in ARCHIVOS:
    carpeta = SALIDA / re.sub(r"[^A-Za-z0-9]+", "_", nombre)
    if not carpeta.exists():
        continue
    for archivo, dimension in DIMENSIONES.items():
        p = carpeta/archivo
        if p.exists():
            dfh = pd.read_csv(p)
            if len(dfh):
                for _, r in dfh.iterrows():
                    resultados_hallazgos.append({
                        "Fuente": nombre,
                        "Dimensión de calidad": dimension,
                        "Descripción del problema": r.get("Resultado", ""),
                        "Número de registros afectados": r.get("Afectados", ""),
                        "Porcentaje sobre el total": r.get("Porcentaje", ""),
                        "Decisión propuesta de tratamiento": ""
                    })

pd.DataFrame(resumen_fuentes).to_csv(
    SALIDA/"RESUMEN_FUENTES.csv", index=False, encoding="utf-8-sig"
)

hallazgos = pd.DataFrame(resultados_hallazgos)
hallazgos.to_csv(SALIDA/"RESUMEN_HALLAZGOS.csv", index=False, encoding="utf-8-sig")

# ------------------------------------------------------------
# CREAR EXCEL FINAL
# ------------------------------------------------------------

try:

    with pd.ExcelWriter(
        SALIDA / "RESUMEN_AUDITORIA.xlsx",
        engine="openpyxl"
    ) as writer:

        # Hoja de fuentes
        pd.DataFrame(resumen_fuentes).to_excel(
            writer,
            sheet_name="Fuentes",
            index=False
        )

        # Hoja consolidada de hallazgos
        hallazgos.to_excel(
            writer,
            sheet_name="Hallazgos",
            index=False
        )

        # Resultados de cada fuente
        for nombre in dfs:

            carpeta = SALIDA / re.sub(
                r"[^A-Za-z0-9]+",
                "_",
                nombre
            )

            if not carpeta.exists():
                continue

            for archivo in DIMENSIONES:

                p = carpeta / archivo

                # Comprobar que el archivo existe
                if not p.exists():
                    continue

                # Comprobar que no esté vacío
                if p.stat().st_size == 0:
                    continue

                try:

                    resultado = pd.read_csv(p)

                    # Si no tiene columnas, no lo agregamos
                    if resultado.empty and len(resultado.columns) == 0:
                        continue

                    nombre_hoja = (
                        nombre[:20]
                        + "_"
                        + DIMENSIONES[archivo][:8]
                    )[:31]

                    resultado.to_excel(
                        writer,
                        sheet_name=nombre_hoja,
                        index=False
                    )

                except pd.errors.EmptyDataError:
                    # El archivo está vacío: continuar con el siguiente
                    continue

    print(
        "\nExcel final creado correctamente:"
    )
    print(
        SALIDA / "RESUMEN_AUDITORIA.xlsx"
    )

except Exception as e:

    print(
        "\nERROR AL CREAR EL EXCEL FINAL:"
    )
    print(e)

print("\nAUDITORÍA TERMINADA")
print("Resultados:", SALIDA.resolve())
print("Archivos encontrados:")
for n,p in archivos_cargados.items():
    print(f" - {n}: {p.name}")
