# AUDITORÍA DE DATOS — ÍNDICE INTEGRAL DE RIESGO MUNICIPAL
# V6 — detección robusta de columnas + cruces DIVIPOLA corregidos
#
# Ejecutar en PowerShell:
# python "C:\Users\lerf2\OneDrive\Escritorio\BI TAREA\auditoria_todas_las_fuentes_v6.py"

from pathlib import Path
import pandas as pd
import re
import unicodedata

BASE = Path(r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA")
AUDIT_DATE = pd.Timestamp("2026-09-04")

def norm_text(s):
    s = "" if pd.isna(s) else str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.upper().strip()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def code5(x):
    if pd.isna(x):
        return ""
    s = re.sub(r"\D", "", str(x))
    return s.zfill(5) if s else ""

def norm_col(c):
    return norm_text(c).replace(" ", "")

def find_column(df, candidates, content_keywords=None):
    # 1) coincidencia normalizada exacta
    normalized = {norm_col(c): c for c in df.columns}
    for candidate in candidates:
        k = norm_col(candidate)
        if k in normalized:
            return normalized[k]

    # 2) coincidencia parcial por nombre
    for c in df.columns:
        nc = norm_col(c)
        if any(norm_col(candidate) in nc or nc in norm_col(candidate) for candidate in candidates):
            return c

    # 3) búsqueda por contenido, si se suministran palabras clave
    if content_keywords:
        for c in df.columns:
            sample = df[c].dropna().astype(str).head(100)
            joined = " ".join(sample.tolist()).upper()
            if any(k.upper() in joined for k in content_keywords):
                return c

    return None

def first_file(patterns):
    for p in patterns:
        files = sorted(BASE.glob(p))
        if files:
            return files[0]
    return None

DIVI_FILE = first_file(["5DIVIPOLA*"])
HOM_FILE = first_file(["7HOMICIDIO*"])
SEC_FILE = first_file(["2SECUESTRO*"])
EXT_FILE = first_file(["3EXTORS*"])
COCA_FILE = first_file(["4Detección_de_Cultivos_de_Coca*", "*Cultivos*Coca*"])
TER_FILE = first_file(["*Terrorismo*"])

if not DIVI_FILE:
    raise FileNotFoundError("No se encontró el archivo 5DIVIPOLA*")
if not HOM_FILE:
    raise FileNotFoundError("No se encontró el archivo 7HOMICIDIO*")
if not SEC_FILE:
    raise FileNotFoundError("No se encontró el archivo 2SECUESTRO*")
if not EXT_FILE:
    raise FileNotFoundError("No se encontró el archivo 3EXTORS*")
if not COCA_FILE:
    raise FileNotFoundError("No se encontró el archivo de cultivos de coca")
if not TER_FILE:
    raise FileNotFoundError("No se encontró el archivo de terrorismo")

print("="*80)
print("AUDITORÍA DE DATOS — V6")
print("Fecha de auditoría:", AUDIT_DATE.date())
print("="*80)
print()

# ================================================================
# DIVIPOLA — detección robusta
# ================================================================
divi = pd.read_excel(DIVI_FILE)

print("DIVIPOLA")
print("-"*80)
print("Archivo:", DIVI_FILE.name)
print("Filas/columnas:", divi.shape)
print("Columnas reales:", list(divi.columns))

# Primero buscamos por nombres posibles.
div_code = find_column(
    divi,
    ["Código DANE del municipio","Codigo DANE del municipio",
     "Código DANE","Codigo DANE","CODIGO DANE","COD_MPIO","CODMPIO",
     "Código municipio","Codigo municipio"],
    ["CODIGO DANE","COD_MPIO","CODMPIO"]
)

div_name = find_column(
    divi,
    ["Nombre del municipio","Nombre Municipio","MUNICIPIO",
     "NOMBRE MUNICIPIO","Municipio"],
    ["MUNICIPIO"]
)

div_dept = find_column(
    divi,
    ["Nombre del departamento","Nombre Departamento","DEPARTAMENTO",
     "NOMBRE DEPARTAMENTO","Departamento"],
    ["DEPARTAMENTO"]
)

# Si no se identifican, buscamos columnas numéricas candidatas.
if div_code is None:
    numeric_candidates = []
    for c in divi.columns:
        s = pd.to_numeric(divi[c], errors="coerce")
        valid = s.notna().sum()
        if valid >= max(10, int(len(divi)*0.8)):
            lens = s.dropna().astype("Int64").astype(str).str.len()
            if ((lens >= 4) & (lens <= 5)).mean() > 0.8:
                numeric_candidates.append(c)
    if len(numeric_candidates) == 1:
        div_code = numeric_candidates[0]

if div_name is None:
    object_candidates = []
    for c in divi.columns:
        if divi[c].dtype == "object":
            s = divi[c].dropna().astype(str)
            if len(s) and s.str.len().mean() > 3:
                object_candidates.append(c)
    # Elegimos por mayor proporción de valores distintos y longitud razonable
    if object_candidates:
        scores = []
        for c in object_candidates:
            s = divi[c].dropna().astype(str)
            scores.append((s.nunique()/max(len(s),1), -abs(s.str.len().mean()-18), c))
        scores.sort(reverse=True)
        div_name = scores[0][2]

if div_code is None or div_name is None:
    print("\nERROR CONTROLADO: no fue posible identificar las columnas clave.")
    print("Código detectado:", div_code)
    print("Municipio detectado:", div_name)
    print("Columnas disponibles:", list(divi.columns))
    raise RuntimeError("Revisar columnas reales de DIVIPOLA antes de continuar.")

divi["_COD5"] = divi[div_code].map(code5)
divi["_NORM_NAME"] = divi[div_name].map(norm_text)

# Diccionario robusto: clave y valor son strings.
div_lookup = dict(zip(divi["_COD5"].astype(str), divi["_NORM_NAME"].astype(str)))
div_codes = set(divi["_COD5"].astype(str))

print("Columna código identificada:", div_code)
print("Columna municipio identificada:", div_name)
print("Columna departamento identificada:", div_dept)
print("Municipios únicos:", len(div_codes))
print("Códigos no válidos como 5 dígitos:", int((~divi["_COD5"].astype(str).str.fullmatch(r"\d{5}")).sum()))
print("Códigos duplicados:", int(divi["_COD5"].duplicated(keep=False).sum()))
print()

# ================================================================
# AUDITORÍA DE FUENTES DELICTIVAS
# ================================================================
def audit_crime(label, path, code_candidates, muni_candidates, date_candidates,
                qty_candidates, terror=False):

    df = pd.read_excel(path)

    code_col = find_column(df, code_candidates)
    muni_col = find_column(df, muni_candidates)
    date_col = find_column(df, date_candidates)
    qty_col = find_column(df, qty_candidates)

    missing = [name for name, col in {
        "código": code_col, "municipio": muni_col,
        "fecha": date_col, "cantidad": qty_col
    }.items() if col is None]

    if missing:
        print(f"{label}: columnas no identificadas: {missing}")
        print("Columnas disponibles:", list(df.columns))
        raise RuntimeError(f"No se pudieron identificar columnas en {label}")

    raw = pd.to_numeric(df[code_col], errors="coerce")

    if terror:
        # El código de Terrorismo incluye un sufijo de evento.
        df["_COD5"] = raw.floordiv(1000).astype("Int64").astype(str).str.zfill(5)
        df["_COD5"] = df["_COD5"].replace({"<NA>": ""})
    else:
        df["_COD5"] = df[code_col].map(code5)

    df["_NORM_NAME"] = df[muni_col].map(norm_text)
    df["_DIVI_NAME"] = df["_COD5"].astype(str).map(div_lookup)

    unmatched = ~df["_COD5"].astype(str).isin(div_codes)
    name_diff = (~unmatched) & (df["_NORM_NAME"] != df["_DIVI_NAME"])

    print(label)
    print("-"*80)
    print("Archivo:", path.name)
    print("Filas/columnas:", df.shape)
    print("Tamaño MB:", round(path.stat().st_size/1024**2, 2))
    print("Columnas:", list(df.columns[:len(df.columns)-3]))
    print("Nulos por columna:", df.iloc[:, :len(df.columns)-3].isna().sum().to_dict())
    print("Columnas detectadas:", {
        "codigo": code_col, "municipio": muni_col,
        "fecha": date_col, "cantidad": qty_col
    })
    print("Municipios/códigos estandarizados:", df["_COD5"].nunique())
    print("Registros con código NO encontrado en DIVIPOLA:", int(unmatched.sum()))
    print("Códigos NO encontrados (únicos):", int(df.loc[unmatched, "_COD5"].nunique()))

    if unmatched.any():
        sample = df.loc[unmatched, [code_col, muni_col, "_COD5"]].drop_duplicates().head(10)
        print("Muestra de no encontrados (máx. 10):")
        print(sample.to_string(index=False))

    print("Registros con diferencia de denominación:", int(name_diff.sum()))
    print("Códigos afectados por denominación:", int(df.loc[name_diff, "_COD5"].nunique()))

    if name_diff.any():
        sample = df.loc[name_diff, ["_COD5", muni_col, "_DIVI_NAME"]].drop_duplicates().head(10)
        print("Muestra de diferencias de nombre (máx. 10):")
        print(sample.to_string(index=False))

    dates = pd.to_datetime(df[date_col], errors="coerce", dayfirst=terror)
    print("Fechas no interpretables:", int(dates.isna().sum()))

    if dates.notna().any():
        print("Fecha mínima:", dates.min().date())
        print("Fecha máxima:", dates.max().date())
        out_range = ((dates < "2019-01-01") | (dates > "2025-12-31")).sum()
        print("Fechas fuera de 2019-2025:", int(out_range))

        years = set(dates.dt.year.dropna().astype(int))
        print("Años presentes:", sorted(years))
        print("Años faltantes 2019-2025:", sorted(set(range(2019,2026))-years))

        missing_months = {}
        for y in range(2019,2026):
            months = set(dates.loc[dates.dt.year == y].dt.month.dropna().astype(int))
            miss = sorted(set(range(1,13))-months)
            if miss:
                missing_months[y] = miss
        print("Meses faltantes:", missing_months if missing_months else "ninguno")

    q = pd.to_numeric(df[qty_col], errors="coerce")
    print("Valores negativos:", int((q < 0).sum()))
    print("Valores no numéricos en cantidad:", int(q.isna().sum()))
    print("Valor máximo:", q.max())
    print("Suma CANTIDAD:", q.sum())

    exact_mask = df.duplicated(keep=False)
    print("Filas involucradas en duplicados exactos:", int(exact_mask.sum()))
    dup_qty = q.loc[exact_mask].sum()
    total_qty = q.sum()
    print("Cantidad asociada a duplicados exactos:", dup_qty)
    print("% del total asociado:", round(dup_qty/total_qty*100,2) if total_qty else 0)
    print()

    return df

hom = audit_crime("HOMICIDIOS", HOM_FILE,
    ["COD_MUNI"], ["MUNICIPIO"], ["FECHA HECHO"], ["CANTIDAD"])

sec = audit_crime("SECUESTRO", SEC_FILE,
    ["COD_MUNI"], ["MUNICIPIO"], ["FECHA HECHO"], ["CANTIDAD"])

ext = audit_crime("EXTORSIÓN", EXT_FILE,
    ["COD_MUNI"], ["MUNICIPIO"], ["FECHA HECHO"], ["CANTIDAD"])

ter = audit_crime("TERRORISMO", TER_FILE,
    ["CODIGO DANE"], ["MUNICIPIO"], ["FECHA HECHO"], ["CANTIDAD"],
    terror=True)

# ================================================================
# COBERTURA MUNICIPAL
# ================================================================
print("COBERTURA MUNICIPAL COMPARADA")
print("-"*80)

sets = {
    "Homicidios": set(hom["_COD5"].astype(str)) - {""},
    "Secuestro": set(sec["_COD5"].astype(str)) - {""},
    "Extorsión": set(ext["_COD5"].astype(str)) - {""},
    "Terrorismo": set(ter["_COD5"].astype(str)) - {""},
}

for other in ["Secuestro","Extorsión","Terrorismo"]:
    common = sets["Homicidios"] & sets[other]
    only_h = sets["Homicidios"] - sets[other]
    only_o = sets[other] - sets["Homicidios"]
    print(f"Homicidios vs {other}: común={len(common)}, solo H={len(only_h)}, solo {other}={len(only_o)}")
    print(f"  Cobertura H={len(common)/len(sets['Homicidios'])*100:.2f}% | {other}={len(common)/len(sets[other])*100:.2f}%")
print()

# ================================================================
# COCA
# ================================================================
coca = pd.read_excel(COCA_FILE)
coca_code = find_column(coca, ["CODMPIO","COD_MPIO","CODIGO DANE","Código DANE"])
coca_muni = find_column(coca, ["MUNICIPIO"])

if coca_code is None or coca_muni is None:
    print("Columnas Coca:", list(coca.columns))
    raise RuntimeError("No se identificaron las columnas CODMPIO/MUNICIPIO de Coca.")

coca["_COD5"] = coca[coca_code].map(code5)
coca["_NORM_NAME"] = coca[coca_muni].map(norm_text)
coca["_DIVI_NAME"] = coca["_COD5"].astype(str).map(div_lookup)

unmatched = ~coca["_COD5"].astype(str).isin(div_codes)
name_diff = (~unmatched) & (coca["_NORM_NAME"] != coca["_DIVI_NAME"])

print("CULTIVOS DE HOJA DE COCA")
print("-"*80)
print("Archivo:", COCA_FILE.name)
print("Filas/columnas:", coca.shape)
print("Tamaño MB:", round(COCA_FILE.stat().st_size/1024**2,2))
print("Columnas:", list(coca.columns[:len(coca.columns)-3]))
print("Municipios/códigos estandarizados:", coca["_COD5"].nunique())
print("Registros con código NO encontrado en DIVIPOLA:", int(unmatched.sum()))
print("Códigos NO encontrados (únicos):", int(coca.loc[unmatched,"_COD5"].nunique()))

if unmatched.any():
    sample = coca.loc[unmatched,[coca_code,coca_muni,"_COD5"]].drop_duplicates().head(10)
    print("Muestra de no encontrados (máx. 10):")
    print(sample.to_string(index=False))

print("Registros con diferencia de denominación:", int(name_diff.sum()))
print("Códigos afectados por denominación:", int(coca.loc[name_diff,"_COD5"].nunique()))

if name_diff.any():
    sample = coca.loc[name_diff,["_COD5",coca_muni,"_DIVI_NAME"]].drop_duplicates().head(10)
    print("Muestra de diferencias de nombre (máx. 10):")
    print(sample.to_string(index=False))

for y in [str(i) for i in range(2019,2025)]:
    if y in coca.columns:
        q = pd.to_numeric(coca[y], errors="coerce")
        print(f"{y}: nulos={q.isna().sum()} ({q.isna().mean()*100:.2f}%), negativos={(q<0).sum()}, total={q.sum():,.2f}, máximo={q.max():,.2f}")

print("2025 disponible:", "2025" in [str(c) for c in coca.columns])
print("Duplicados exactos:", int(coca.duplicated(keep=False).sum()))
print("Códigos municipales duplicados:", int(coca["_COD5"].duplicated(keep=False).sum()))

print()
print("CRITERIO COCA:")
print("- Los nulos anuales no se convierten automáticamente en cero.")
print("- 2025 no está disponible en este archivo.")
print("- La incorporación de 2025 debe hacerse con la actualización oficial correspondiente.")
print()

print("="*80)
print("AUDITORÍA V6 TERMINADA CORRECTAMENTE")
print("="*80)

# ============================================================
# COMPARACIÓN COMPLETA DE MUNICIPIOS ENTRE TODAS LAS FUENTES
# ============================================================

import os
import pandas as pd
from itertools import combinations

print("\n" + "=" * 80)
print("COMPARACIÓN COMPLETA DE MUNICIPIOS ENTRE TODAS LAS FUENTES")
print("=" * 80)


# ------------------------------------------------------------
# 1. RUTA DE LOS ARCHIVOS
# ------------------------------------------------------------

BASE = r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA"


# ------------------------------------------------------------
# 2. BUSCAR LOS ARCHIVOS
# ------------------------------------------------------------

archivo_homicidios = next(
    f for f in os.listdir(BASE)
    if "HOMICIDIO" in f.upper()
)

archivo_secuestro = next(
    f for f in os.listdir(BASE)
    if "SECUESTRO" in f.upper()
)

archivo_extorsion = next(
    f for f in os.listdir(BASE)
    if "EXTORS" in f.upper()
)

archivo_terrorismo = next(
    f for f in os.listdir(BASE)
    if "TERRORISMO" in f.upper()
    and "2019" in f
)

archivo_coca = next(
    f for f in os.listdir(BASE)
    if "CULTIVOS" in f.upper()
    or "COCA" in f.upper()
)

archivo_divipola = next(
    f for f in os.listdir(BASE)
    if "DIVIPOLA" in f.upper()
)


print("Archivos encontrados:")
print("Homicidios :", archivo_homicidios)
print("Secuestro  :", archivo_secuestro)
print("Extorsión  :", archivo_extorsion)
print("Terrorismo :", archivo_terrorismo)
print("Coca       :", archivo_coca)
print("DIVIPOLA   :", archivo_divipola)


# ------------------------------------------------------------
# 3. CARGAR LAS BASES
# ------------------------------------------------------------

hom = pd.read_excel(
    os.path.join(BASE, archivo_homicidios)
)

sec = pd.read_excel(
    os.path.join(BASE, archivo_secuestro)
)

ext = pd.read_excel(
    os.path.join(BASE, archivo_extorsion)
)

ter = pd.read_excel(
    os.path.join(BASE, archivo_terrorismo)
)

coca = pd.read_excel(
    os.path.join(BASE, archivo_coca)
)

div = pd.read_excel(
    os.path.join(BASE, archivo_divipola)
)


# ------------------------------------------------------------
# 4. NORMALIZAR CÓDIGOS DANE
# ------------------------------------------------------------

def codigo_5_digitos(serie):

    return (
        pd.to_numeric(
            serie,
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .astype(str)
        .str.zfill(5)
    )


# HOMICIDIOS
cod_hom = set(
    codigo_5_digitos(
        hom["COD_MUNI"]
    )
)


# SECUESTROS
cod_sec = set(
    codigo_5_digitos(
        sec["COD_MUNI"]
    )
)


# EXTORSIÓN
cod_ext = set(
    codigo_5_digitos(
        ext["COD_MUNI"]
    )
)


# TERRORISMO
#
# En esta fuente el código viene con una estructura
# diferente. Se normaliza a código municipal de 5 dígitos.

cod_ter = set(
    (
        pd.to_numeric(
            ter["CODIGO DANE"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        // 1000
    )
    .astype(str)
    .str.zfill(5)
)


# COCA
cod_coca = set(
    codigo_5_digitos(
        coca["CODMPIO"]
    )
)


# DIVIPOLA
#
# Detectamos automáticamente la columna del código.

col_codigo_div = None

for col in div.columns:

    nombre = str(col).upper()

    if "CODIGO MUNICIPIO" in nombre:
        col_codigo_div = col
        break

    if "CÓDIGO MUNICIPIO" in nombre:
        col_codigo_div = col
        break


if col_codigo_div is None:

    print("\nERROR: no se encontró el código municipal en DIVIPOLA.")
    print("Columnas encontradas:")
    print(div.columns.tolist())

else:

    cod_div = set(
        codigo_5_digitos(
            div[col_codigo_div]
        )
    )


# ------------------------------------------------------------
# 5. CREAR DICCIONARIO DE FUENTES
# ------------------------------------------------------------

municipios = {

    "Homicidios": cod_hom,

    "Secuestros": cod_sec,

    "Extorsión": cod_ext,

    "Terrorismo": cod_ter,

    "Coca": cod_coca,

    "DIVIPOLA": cod_div
}


# ------------------------------------------------------------
# 6. COBERTURA DE CADA FUENTE
# ------------------------------------------------------------

print("\n")
print("=" * 80)
print("1. MUNICIPIOS ÚNICOS POR FUENTE")
print("=" * 80)

for fuente, codigos in municipios.items():

    print(
        f"{fuente:20} : "
        f"{len(codigos):4} municipios"
    )


# ------------------------------------------------------------
# 7. COMPARACIÓN TODOS CONTRA TODOS
# ------------------------------------------------------------

print("\n")
print("=" * 80)
print("2. COMPARACIÓN TODOS CONTRA TODOS")
print("=" * 80)


resultados_comparacion = []


for fuente_a, fuente_b in combinations(
    municipios.keys(),
    2
):

    conjunto_a = municipios[fuente_a]

    conjunto_b = municipios[fuente_b]

    comunes = conjunto_a & conjunto_b

    solo_a = conjunto_a - conjunto_b

    solo_b = conjunto_b - conjunto_a


    pct_a = (
        len(comunes) /
        len(conjunto_a) *
        100
    ) if len(conjunto_a) > 0 else 0


    pct_b = (
        len(comunes) /
        len(conjunto_b) *
        100
    ) if len(conjunto_b) > 0 else 0


    resultados_comparacion.append({

        "Fuente A": fuente_a,

        "Fuente B": fuente_b,

        "Municipios A": len(conjunto_a),

        "Municipios B": len(conjunto_b),

        "En ambas": len(comunes),

        "Solo A": len(solo_a),

        "Solo B": len(solo_b),

        "% A presente en B":
            round(pct_a, 2),

        "% B presente en A":
            round(pct_b, 2)
    })


df_comparacion = pd.DataFrame(
    resultados_comparacion
)


print(
    df_comparacion.to_string(
        index=False
    )
)


# ------------------------------------------------------------
# 8. MUNICIPIOS PRESENTES EN LAS 5 FUENTES DE EVENTOS
# ------------------------------------------------------------

print("\n")
print("=" * 80)
print("3. MUNICIPIOS PRESENTES EN LAS 5 FUENTES DE EVENTOS")
print("=" * 80)


fuentes_eventos = [

    "Homicidios",

    "Secuestros",

    "Extorsión",

    "Terrorismo",

    "Coca"
]


municipios_todas_eventos = set.intersection(

    *[
        municipios[f]
        for f in fuentes_eventos
    ]
)


print(
    "Municipios presentes en las 5 fuentes:",
    len(municipios_todas_eventos)
)


# ------------------------------------------------------------
# 9. MUNICIPIOS PRESENTES EN LAS 6 BASES
# ------------------------------------------------------------

print("\n")
print("=" * 80)
print("4. MUNICIPIOS PRESENTES EN LAS 6 BASES")
print("=" * 80)


municipios_todas_las_bases = set.intersection(

    *[
        municipios[f]
        for f in municipios.keys()
    ]
)


print(
    "Municipios presentes en las 6:",
    len(municipios_todas_las_bases)
)


# ------------------------------------------------------------
# 10. MUNICIPIOS DE DIVIPOLA AUSENTES EN CADA FUENTE
# ------------------------------------------------------------

print("\n")
print("=" * 80)
print("5. MUNICIPIOS DE DIVIPOLA AUSENTES EN CADA FUENTE")
print("=" * 80)


for fuente in fuentes_eventos:

    ausentes = (
        municipios["DIVIPOLA"]
        -
        municipios[fuente]
    )

    print(
        f"{fuente:20} : "
        f"{len(ausentes):4} municipios ausentes"
    )


# ------------------------------------------------------------
# 11. MUNICIPIOS DE HOMICIDIOS QUE NO APARECEN
#     EN LAS OTRAS FUENTES
# ------------------------------------------------------------

print("\n")
print("=" * 80)
print("6. MUNICIPIOS DE HOMICIDIOS AUSENTES EN OTRAS FUENTES")
print("=" * 80)


for fuente in [

    "Secuestros",

    "Extorsión",

    "Terrorismo",

    "Coca"

]:

    ausentes = (

        municipios["Homicidios"]

        -

        municipios[fuente]

    )

    print(

        f"Homicidios -> "
        f"{fuente:15} : "
        f"{len(ausentes):4} municipios"

    )


# ------------------------------------------------------------
# 12. EXPORTAR LA MATRIZ DE COMPARACIÓN
# ------------------------------------------------------------

salida = os.path.join(
    BASE,
    "comparacion_municipios_todas_las_fuentes.xlsx"
)


with pd.ExcelWriter(
    salida,
    engine="openpyxl"
) as writer:

    df_comparacion.to_excel(

        writer,

        sheet_name="Todos_contra_todos",

        index=False

    )


    cobertura = pd.DataFrame({

        "Fuente":
            list(municipios.keys()),

        "Municipios únicos":
            [
                len(municipios[f])
                for f in municipios.keys()
            ]

    })


    cobertura.to_excel(

        writer,

        sheet_name="Cobertura",

        index=False

    )


    interseccion = pd.DataFrame({

        "Indicador": [

            "Municipios en las 5 fuentes de eventos",

            "Municipios en las 6 bases"

        ],

        "Cantidad": [

            len(municipios_todas_eventos),

            len(municipios_todas_las_bases)

        ]

    })


    interseccion.to_excel(

        writer,

        sheet_name="Intersecciones",

        index=False

    )


print("\n")
print("=" * 80)
print("ARCHIVO GENERADO")
print("=" * 80)

print(salida)