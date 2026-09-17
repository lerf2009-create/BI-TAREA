# AUDITORÍA DE DATOS — ÍNDICE INTEGRAL DE RIESGO MUNICIPAL
# V4 — correcciones de DIVIPOLA, terrorismo y cultivos de coca
# Ejecutar desde VS Code / PowerShell:
# python "C:\Users\lerf2\OneDrive\Escritorio\BI TAREA\auditoria_todas_las_fuentes_v4.py"

from pathlib import Path
import pandas as pd
import numpy as np
import re
import unicodedata
from datetime import datetime

BASE = Path(r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA")
DIVI_FILE = next(BASE.glob("5DIVIPOLA*"), None)
HOM_FILE = next(BASE.glob("7HOMICIDIO*"), None)
SEC_FILE = next(BASE.glob("2SECUESTRO*"), None)
EXT_FILE = next(BASE.glob("3EXTORS*"), None)
COCA_FILE = next(BASE.glob("4Detección_de_Cultivos_de_Coca*"), None)
if COCA_FILE is None:
    COCA_FILE = next(BASE.glob("*Cultivos*Coca*"), None)
TER_FILES = [p for p in BASE.glob("*.xlsx") if "Terrorismo" in p.name or "Terrorismo" in p.name]
TER_FILE = TER_FILES[0] if TER_FILES else None

AUDIT_DATE = pd.Timestamp("2026-09-04")

def norm(s):
    s = "" if pd.isna(s) else str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = s.upper().strip()
    s = re.sub(r"\([^)]*\)", "", s)   # elimina sufijos como (CT)
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def code5(x):
    if pd.isna(x): return ""
    s = re.sub(r"\D", "", str(x))
    return s.zfill(5) if s else ""

def read_excel(path):
    return pd.read_excel(path)

def duplicate_stats(df):
    exact = int(df.duplicated(keep=False).sum())
    return exact

def print_header(title):
    print("\n" + "="*80)
    print(title)
    print("="*80)

print("AUDITORÍA V4 —", AUDIT_DATE.date())
print("Carpeta:", BASE)

# ---------------------------------------------------------------------
# DIVIPOLA
# ---------------------------------------------------------------------
print_header("DIVIPOLA")
divi = read_excel(DIVI_FILE)
print("Archivo:", DIVI_FILE.name)
print("Filas/columnas:", divi.shape)
print("Columnas:", list(divi.columns))
print("Nulos:", int(divi.isna().sum().sum()))

# Detectar columnas
def findcol(df, candidates):
    for c in candidates:
        for actual in df.columns:
            if str(actual).strip().upper() == c.upper():
                return actual
    return None

div_code = findcol(divi, ["Código DANE del municipio", "CODIGO DANE", "Código DANE", "COD_MPIO", "CODMPIO"])
div_name = findcol(divi, ["Nombre del municipio", "MUNICIPIO", "NOMBRE MUNICIPIO"])
div_dept = findcol(divi, ["Nombre del departamento", "DEPARTAMENTO", "DEPARTAMENTO NOMBRE"])

if div_code is None:
    # búsqueda flexible
    div_code = next((c for c in divi.columns if "DANE" in str(c).upper() or "MUNIC" in str(c).upper() and "COD" in str(c).upper()), divi.columns[0])
if div_name is None:
    div_name = next((c for c in divi.columns if "MUNIC" in str(c).upper() and "COD" not in str(c).upper()), None)
if div_dept is None:
    div_dept = next((c for c in divi.columns if "DEPART" in str(c).upper() and "COD" not in str(c).upper()), None)

divi["_COD5"] = divi[div_code].map(code5)
divi["_NORM_NAME"] = divi[div_name].map(norm) if div_name else ""

print("Columna código:", div_code)
print("Columna municipio:", div_name)
print("Columna departamento:", div_dept)
print("Municipios:", divi["_COD5"].nunique())
print("Códigos inválidos después de zfill (debe ser 0):", int((~divi["_COD5"].str.fullmatch(r"\d{5}")).sum()))
print("Códigos duplicados:", int(divi["_COD5"].duplicated(keep=False).sum()))

# ---------------------------------------------------------------------
# Función común para fuentes delictivas
# ---------------------------------------------------------------------
def audit_crime(name, path, code_col, muni_col, date_col=None, quantity_col=None, terror=False):
    print_header(name)
    df = read_excel(path)
    print("Archivo:", path.name)
    print("Filas/columnas:", df.shape)
    print("Tamaño MB:", round(path.stat().st_size/1024**2, 2))
    print("Columnas:", list(df.columns))
    print("Tipos:", {str(k): str(v) for k,v in df.dtypes.items()})
    print("Nulos por columna:", df.isna().sum().to_dict())

    df["_COD5"] = df[code_col].map(code5)
    if terror:
        # En terrorismo el código contiene normalmente código municipal + dígito(s)
        # La regla observada para esta fuente es dividir entre 1000 antes de estandarizar.
        raw_num = pd.to_numeric(df[code_col], errors="coerce")
        df["_COD5"] = raw_num.floordiv(1000).astype("Int64").astype("string").str.zfill(5)
        df["_COD5"] = df["_COD5"].fillna("")

    df["_NORM_NAME"] = df[muni_col].map(norm)
    div_lookup = divi.set_index("_COD5")["_NORM_NAME"].to_dict()
    df["_DIVI_NAME"] = df["_COD5"].map(div_lookup)
    unmatched = int(df["_DIVI_NAME"].isna().sum())
    name_diff = int((df["_DIVI_NAME"].notna() & (df["_NORM_NAME"] != df["_DIVI_NAME"])).sum())
    name_diff_codes = int(df.loc[df["_DIVI_NAME"].notna() & (df["_NORM_NAME"] != df["_DIVI_NAME"]), "_COD5"].nunique())

    print("Municipios únicos estandarizados:", df["_COD5"].nunique())
    print("Registros con código no encontrado en DIVIPOLA:", unmatched)
    print("Registros con diferencia de denominación frente a DIVIPOLA:", name_diff)
    print("Códigos afectados por denominación:", name_diff_codes)

    if unmatched:
        print("\nDETALLE DE CÓDIGOS NO ENCONTRADOS EN DIVIPOLA:")
        tmp = df.loc[df["_DIVI_NAME"].isna(), [code_col, muni_col, "_COD5"]].drop_duplicates()
        print(tmp.to_string(index=False))

    if name_diff:
        tmp = df.loc[df["_DIVI_NAME"].notna() & (df["_NORM_NAME"] != df["_DIVI_NAME"]),
                     ["_COD5", muni_col, "_DIVI_NAME"]].drop_duplicates().sort_values("_COD5")
        print("\nDIFERENCIAS DE NOMBRE (muestra / hasta 50):")
        print(tmp.head(50).to_string(index=False))

    if date_col:
        dates = pd.to_datetime(df[date_col], errors="coerce", dayfirst=terror)
        print("Fechas no interpretables:", int(dates.isna().sum()))
        if dates.notna().any():
            print("Fecha mínima:", dates.min().date())
            print("Fecha máxima:", dates.max().date())
            print("Fechas fuera 2019-2025:", int(((dates < "2019-01-01") | (dates > "2025-12-31")).sum()))
            years = dates.dt.year
            months = dates.dt.month
            print("Años presentes:", sorted(years.dropna().unique().tolist()))
            missing_years = sorted(set(range(2019,2026)) - set(years.dropna().unique()))
            print("Años faltantes 2019-2025:", missing_years)
            print("Meses faltantes por año:")
            for y in range(2019,2026):
                got = set(months.loc[years == y].dropna().astype(int))
                miss = sorted(set(range(1,13))-got)
                print(f"  {y}: {miss if miss else 'ninguno'}")

    if quantity_col:
        q = pd.to_numeric(df[quantity_col], errors="coerce")
        print("Valores negativos:", int((q < 0).sum()))
        print("Valor máximo:", q.max())
        print("Suma CANTIDAD:", q.sum())

    exact = duplicate_stats(df)
    print("Filas involucradas en duplicados exactos:", exact)
    if quantity_col:
        dup_qty = q[df.duplicated(keep=False)].sum()
        total = q.sum()
        print("Cantidad asociada a filas duplicadas exactas:", dup_qty)
        print("% del total asociado a duplicados exactos:", round(dup_qty/total*100,2) if total else 0)

    return df

# Homicidios
hom = audit_crime(
    "HOMICIDIOS", HOM_FILE,
    findcol(pd.read_excel(HOM_FILE, nrows=2), ["COD_MUNI"]),
    findcol(pd.read_excel(HOM_FILE, nrows=2), ["MUNICIPIO"]),
    findcol(pd.read_excel(HOM_FILE, nrows=2), ["FECHA HECHO"]),
    findcol(pd.read_excel(HOM_FILE, nrows=2), ["CANTIDAD"])
)

# Secuestro
sec = audit_crime(
    "SECUESTRO", SEC_FILE,
    findcol(pd.read_excel(SEC_FILE, nrows=2), ["COD_MUNI"]),
    findcol(pd.read_excel(SEC_FILE, nrows=2), ["MUNICIPIO"]),
    findcol(pd.read_excel(SEC_FILE, nrows=2), ["FECHA HECHO"]),
    findcol(pd.read_excel(SEC_FILE, nrows=2), ["CANTIDAD"])
)

# Extorsión
ext = audit_crime(
    "EXTORSIÓN", EXT_FILE,
    findcol(pd.read_excel(EXT_FILE, nrows=2), ["COD_MUNI"]),
    findcol(pd.read_excel(EXT_FILE, nrows=2), ["MUNICIPIO"]),
    findcol(pd.read_excel(EXT_FILE, nrows=2), ["FECHA HECHO"]),
    findcol(pd.read_excel(EXT_FILE, nrows=2), ["CANTIDAD"])
)

# Terrorismo
ter = audit_crime(
    "TERRORISMO", TER_FILE,
    findcol(pd.read_excel(TER_FILE, nrows=2), ["CODIGO DANE"]),
    findcol(pd.read_excel(TER_FILE, nrows=2), ["MUNICIPIO"]),
    findcol(pd.read_excel(TER_FILE, nrows=2), ["FECHA HECHO"]),
    findcol(pd.read_excel(TER_FILE, nrows=2), ["CANTIDAD"]),
    terror=True
)

# ---------------------------------------------------------------------
# COBERTURA MUNICIPAL COMPARADA CON HOMICIDIOS
# ---------------------------------------------------------------------
print_header("COBERTURA MUNICIPAL COMPARADA")
sets = {
    "Homicidios": set(hom["_COD5"].dropna()),
    "Secuestro": set(sec["_COD5"].dropna()),
    "Extorsión": set(ext["_COD5"].dropna()),
    "Terrorismo": set(ter["_COD5"].dropna()),
}
for other in ["Secuestro", "Extorsión", "Terrorismo"]:
    common = sets["Homicidios"] & sets[other]
    only_h = sets["Homicidios"] - sets[other]
    only_o = sets[other] - sets["Homicidios"]
    print(f"Homicidios vs {other}: común={len(common)}, solo H={len(only_h)}, solo {other}={len(only_o)}")
    print(f"  Cobertura dentro de H={len(common)/len(sets['Homicidios'])*100:.2f}% | dentro de {other}={len(common)/len(sets[other])*100:.2f}%")

# ---------------------------------------------------------------------
# COCA — formato ancho
# ---------------------------------------------------------------------
print_header("CULTIVOS DE HOJA DE COCA")
coca = read_excel(COCA_FILE)
print("Archivo:", COCA_FILE.name)
print("Filas/columnas:", coca.shape)
print("Tamaño MB:", round(COCA_FILE.stat().st_size/1024**2, 2))
print("Columnas:", list(coca.columns))
print("Tipos:", {str(k): str(v) for k,v in coca.dtypes.items()})

year_cols = [str(y) for y in range(2019,2025) if str(y) in coca.columns]
if not year_cols:
    year_cols = [y for y in range(2019,2025) if y in coca.columns]
print("Años disponibles:", year_cols)
print("2025 disponible:", "2025" in [str(c) for c in coca.columns])

coca_code = findcol(coca, ["CODMPIO", "COD_MPIO", "CODIGO DANE"])
coca_muni = findcol(coca, ["MUNICIPIO"])
coca["_COD5"] = coca[coca_code].map(code5)
coca["_NORM_NAME"] = coca[coca_muni].map(norm)
coca["_DIVI_NAME"] = coca["_COD5"].map(divi.set_index("_COD5")["_NORM_NAME"].to_dict())

print("Municipios únicos:", coca["_COD5"].nunique())
unmatched_coca = coca[coca["_DIVI_NAME"].isna()][[coca_code, coca_muni, "_COD5"]].drop_duplicates()
print("Códigos no encontrados en DIVIPOLA:", len(unmatched_coca))
if len(unmatched_coca):
    print("DETALLE:")
    print(unmatched_coca.to_string(index=False))

name_diff_coca = coca[coca["_DIVI_NAME"].notna() & (coca["_NORM_NAME"] != coca["_DIVI_NAME"])]
print("Registros con diferencia de denominación:", len(name_diff_coca))
print("Códigos afectados por denominación:", name_diff_coca["_COD5"].nunique())

for y in year_cols:
    q = pd.to_numeric(coca[y], errors="coerce")
    print(f"{y}: nulos={q.isna().sum()} ({q.isna().mean()*100:.2f}%), negativos={(q<0).sum()}, total={q.sum():,.2f}, máximo={q.max():,.2f}")

print("Duplicados exactos:", int(coca.duplicated(keep=False).sum()))
print("Códigos municipales duplicados:", int(coca["_COD5"].duplicated(keep=False).sum()))

print("\nNOTA DE CALIDAD PARA COCA:")
print("- Los nulos anuales NO se convierten automáticamente en 0: representan ausencia de dato/observación y deben documentarse antes de imputar.")
print("- 2025 no está disponible en este archivo; no se imputará.")
print("- Para integrar 2025 debe incorporarse la actualización oficial correspondiente cuando esté publicada.")

print("\n" + "="*80)
print("AUDITORÍA V4 TERMINADA")
print("="*80)
