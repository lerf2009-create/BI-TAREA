# AUDITORÍA DE DATOS — ÍNDICE INTEGRAL DE RIESGO MUNICIPAL
# V5 — salida resumida + cruce robusto con DIVIPOLA
#
# Ejecutar:
# python "C:\Users\lerf2\OneDrive\Escritorio\BI TAREA\auditoria_todas_las_fuentes_v5.py"

from pathlib import Path
import pandas as pd
import re
import unicodedata

BASE = Path(r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA")
AUDIT_DATE = pd.Timestamp("2026-09-04")

def first_file(patterns):
    for pattern in patterns:
        files = list(BASE.glob(pattern))
        if files:
            return files[0]
    return None

DIVI_FILE = first_file(["5DIVIPOLA*"])
HOM_FILE  = first_file(["7HOMICIDIO*"])
SEC_FILE  = first_file(["2SECUESTRO*"])
EXT_FILE  = first_file(["3EXTORS*"])
COCA_FILE = first_file(["4Detección_de_Cultivos_de_Coca*", "*Cultivos*Coca*"])
TER_FILE  = first_file(["*Terrorismo*"])

def norm(s):
    s = "" if pd.isna(s) else str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode("ascii")
    s = s.upper().strip()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = re.sub(r"[^A-Z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def code5(x):
    if pd.isna(x):
        return ""
    s = re.sub(r"\D", "", str(x))
    return s.zfill(5) if s else ""

def findcol(df, names):
    cols = {str(c).strip().upper(): c for c in df.columns}
    for n in names:
        if n.upper() in cols:
            return cols[n.upper()]
    for c in df.columns:
        u = str(c).strip().upper()
        for n in names:
            if n.upper() in u:
                return c
    return None

def show_sample(df, cols, n=10):
    if len(df):
        print(df[cols].drop_duplicates().head(n).to_string(index=False))
    else:
        print("  Ninguno.")

print("="*78)
print("AUDITORÍA DE DATOS — V5")
print("Fecha de auditoría:", AUDIT_DATE.date())
print("="*78)
print("Objetivo de V5: corregir cruces con DIVIPOLA y limitar la salida de terminal.")
print()

# ----------------------------------------------------------------------
# DIVIPOLA
# ----------------------------------------------------------------------
divi = pd.read_excel(DIVI_FILE)
div_code = findcol(divi, ["Código DANE del municipio","CODIGO DANE","Código DANE","COD_MPIO","CODMPIO"])
div_name = findcol(divi, ["Nombre del municipio","MUNICIPIO","NOMBRE MUNICIPIO"])
div_dept = findcol(divi, ["Nombre del departamento","DEPARTAMENTO"])

divi["_COD5"] = divi[div_code].map(code5)
divi["_NORM_NAME"] = divi[div_name].map(norm)

# IMPORTANTE: diccionario explícito, normalizado y con claves de texto.
div_lookup = dict(zip(divi["_COD5"].astype(str), divi["_NORM_NAME"]))
div_codes = set(divi["_COD5"].astype(str))

print("DIVIPOLA")
print("-"*78)
print("Archivo:", DIVI_FILE.name)
print("Filas/columnas:", divi.shape)
print("Columnas:", list(divi.columns))
print("Nulos totales:", int(divi.isna().sum().sum()))
print("Municipios únicos:", len(div_codes))
print("Códigos con formato distinto de 5 dígitos después de zfill:", 
      int((~divi["_COD5"].astype(str).str.fullmatch(r"\d{5}")).sum()))
print("Códigos duplicados:", int(divi["_COD5"].duplicated(keep=False).sum()))
print()

# ----------------------------------------------------------------------
# AUDITORÍA CRIMEN
# ----------------------------------------------------------------------
def audit_crime(label, path, code_names, muni_names, date_names, qty_names, terror=False):
    df = pd.read_excel(path)

    code_col = findcol(df, code_names)
    muni_col = findcol(df, muni_names)
    date_col = findcol(df, date_names)
    qty_col = findcol(df, qty_names)

    raw = pd.to_numeric(df[code_col], errors="coerce")

    if terror:
        # Terrorismo: CODIGO DANE contiene código municipal + sufijo.
        # Regla observada: división entera entre 1000.
        df["_COD5"] = raw.floordiv(1000).astype("Int64").astype(str).str.zfill(5)
        df["_COD5"] = df["_COD5"].replace({"<NA>": ""})
    else:
        df["_COD5"] = df[code_col].map(code5)

    df["_NORM_NAME"] = df[muni_col].map(norm)
    df["_DIVI_NAME"] = df["_COD5"].astype(str).map(div_lookup)

    unmatched_mask = ~df["_COD5"].astype(str).isin(div_codes)
    name_mask = (~unmatched_mask) & (df["_NORM_NAME"] != df["_DIVI_NAME"])

    print(label)
    print("-"*78)
    print("Archivo:", path.name)
    print("Filas/columnas:", df.shape)
    print("Tamaño MB:", round(path.stat().st_size/1024**2, 2))
    print("Columnas:", list(df.columns[:len(df.columns)-3]))
    print("Nulos por columna:", df.iloc[:, :len(df.columns)-3].isna().sum().to_dict())
    print("Municipios/códigos estandarizados:", df["_COD5"].nunique())
    print("Registros con código NO encontrado en DIVIPOLA:", int(unmatched_mask.sum()))
    print("Códigos NO encontrados (únicos):", int(df.loc[unmatched_mask, "_COD5"].nunique()))
    if unmatched_mask.any():
        print("Muestra de códigos no encontrados:")
        show_sample(df.loc[unmatched_mask], [code_col, muni_col, "_COD5"])
    print("Registros con diferencia de denominación:", int(name_mask.sum()))
    print("Códigos afectados por denominación:", int(df.loc[name_mask, "_COD5"].nunique()))
    if name_mask.any():
        print("Muestra de diferencias de nombre:")
        show_sample(df.loc[name_mask], ["_COD5", muni_col, "_DIVI_NAME"])

    dates = pd.to_datetime(df[date_col], errors="coerce", dayfirst=terror)
    print("Fechas no interpretables:", int(dates.isna().sum()))
    if dates.notna().any():
        print("Fecha mínima:", dates.min().date())
        print("Fecha máxima:", dates.max().date())
        print("Fechas fuera de 2019-2025:", int(((dates < "2019-01-01") | (dates > "2025-12-31")).sum()))
        years = set(dates.dt.year.dropna().astype(int))
        print("Años presentes:", sorted(years))
        print("Años faltantes 2019-2025:", sorted(set(range(2019,2026))-years))
        missing_months = {}
        for y in range(2019,2026):
            months = set(dates.loc[dates.dt.year == y].dt.month.dropna().astype(int))
            missing_months[y] = sorted(set(range(1,13))-months)
        print("Meses faltantes:", {y:m for y,m in missing_months.items() if m} or "ninguno")

    q = pd.to_numeric(df[qty_col], errors="coerce")
    print("Valores negativos:", int((q < 0).sum()))
    print("Valor máximo:", q.max())
    print("Suma CANTIDAD:", q.sum())

    exact_mask = df.duplicated(keep=False)
    print("Filas involucradas en duplicados exactos:", int(exact_mask.sum()))
    dup_qty = q.loc[exact_mask].sum()
    total_qty = q.sum()
    print("Cantidad asociada a duplicados exactos:", dup_qty)
    print("% del total asociado:", round(dup_qty/total_qty*100,2) if total_qty else 0)
    print()

    return df, code_col

hom, hom_code = audit_crime("HOMICIDIOS", HOM_FILE,
    ["COD_MUNI"],["MUNICIPIO"],["FECHA HECHO"],["CANTIDAD"])

sec, sec_code = audit_crime("SECUESTRO", SEC_FILE,
    ["COD_MUNI"],["MUNICIPIO"],["FECHA HECHO"],["CANTIDAD"])

ext, ext_code = audit_crime("EXTORSIÓN", EXT_FILE,
    ["COD_MUNI"],["MUNICIPIO"],["FECHA HECHO"],["CANTIDAD"])

ter, ter_code = audit_crime("TERRORISMO", TER_FILE,
    ["CODIGO DANE"],["MUNICIPIO"],["FECHA HECHO"],["CANTIDAD"],terror=True)

# ----------------------------------------------------------------------
# COBERTURA
# ----------------------------------------------------------------------
print("COBERTURA MUNICIPAL COMPARADA")
print("-"*78)

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

# ----------------------------------------------------------------------
# COCA
# ----------------------------------------------------------------------
coca = pd.read_excel(COCA_FILE)
coca_code = findcol(coca, ["CODMPIO","COD_MPIO","CODIGO DANE"])
coca_muni = findcol(coca, ["MUNICIPIO"])
coca["_COD5"] = coca[coca_code].map(code5)
coca["_NORM_NAME"] = coca[coca_muni].map(norm)
coca["_DIVI_NAME"] = coca["_COD5"].astype(str).map(div_lookup)

unmatched = ~coca["_COD5"].astype(str).isin(div_codes)
name_diff = (~unmatched) & (coca["_NORM_NAME"] != coca["_DIVI_NAME"])

print("CULTIVOS DE HOJA DE COCA")
print("-"*78)
print("Archivo:", COCA_FILE.name)
print("Filas/columnas:", coca.shape)
print("Tamaño MB:", round(COCA_FILE.stat().st_size/1024**2,2))
print("Columnas:", list(coca.columns[:len(coca.columns)-3]))
print("Municipios/códigos estandarizados:", coca["_COD5"].nunique())
print("Registros con código NO encontrado en DIVIPOLA:", int(unmatched.sum()))
print("Códigos NO encontrados (únicos):", int(coca.loc[unmatched,"_COD5"].nunique()))
if unmatched.any():
    print("Muestra de códigos no encontrados:")
    show_sample(coca.loc[unmatched], [coca_code,coca_muni,"_COD5"])

print("Registros con diferencia de denominación:", int(name_diff.sum()))
print("Códigos afectados por denominación:", int(coca.loc[name_diff,"_COD5"].nunique()))
if name_diff.any():
    print("Muestra de diferencias de nombre:")
    show_sample(coca.loc[name_diff], ["_COD5",coca_muni,"_DIVI_NAME"])

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

print("="*78)
print("AUDITORÍA V5 TERMINADA CORRECTAMENTE")
print("="*78)
