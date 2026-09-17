from pathlib import Path
from datetime import datetime
import unicodedata
import pandas as pd
import numpy as np

# ============================================================
# AUDITORÍA DE CALIDAD DE DATOS — TALLER BI
# V3 — estructura alineada con los 7 pasos solicitados
# ============================================================

BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / "RESULTADOS_AUDITORIA_V3"
RESULTADOS.mkdir(parents=True, exist_ok=True)
FECHA_AUDITORIA = datetime.now()

def norm(v):
    s = str(v).strip().upper()
    s = ''.join(c for c in unicodedata.normalize("NFD", s)
                if unicodedata.category(c) != "Mn")
    return " ".join(s.split())

def write(out, text=""):
    print(text)
    with open(out, "a", encoding="utf-8") as f:
        f.write(str(text) + "\n")

def code5(series):
    return (series.astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
            .str.zfill(5))

def find_file(patterns):
    for f in BASE.glob("*.xlsx"):
        n = norm(f.name)
        if all(p in n for p in patterns):
            return f
    return None

def parse_dates(s, terrorism=False):
    return pd.to_datetime(s, errors="coerce", dayfirst=terrorism)

# ------------------------------------------------------------
# DIVIPOLA
# ------------------------------------------------------------

div_file = find_file(["DIVIPOLA"])
if div_file is None:
    raise FileNotFoundError("No se encontró el archivo DIVIPOLA.")

DIV = pd.read_excel(div_file)

DIV["_COD5"] = code5(DIV["Código Municipio"])
DIV["_DEP2"] = DIV["_COD5"].str[:2]
DIV["_CODDEP5"] = DIV["Código Departamento"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2)

# ------------------------------------------------------------
# LOCALIZACIÓN DE LAS 5 fuentes
# ------------------------------------------------------------

files = {
    "Homicidios": find_file(["HOMICIDIO"]),
    "Secuestro": find_file(["SECUESTRO"]),
    "Extorsion": find_file(["EXTORS"]),
    "Terrorismo": find_file(["TERRORISMO", "2019", "2025"]),
    "Coca": find_file(["DETECCION", "CULTIVOS", "COCA"]),
    "DIVIPOLA": div_file
}

for k, v in files.items():
    if v:
        print(f"{k}: {v.name}")
    else:
        print(f"{k}: NO ENCONTRADO")

# ------------------------------------------------------------
# AUDITORÍA DIVIPOLA
# ------------------------------------------------------------

def audit_divipola():
    out = RESULTADOS / "DIVIPOLA" / "resultado_auditoria.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists(): out.unlink()

    write(out, "="*70)
    write(out, "AUDITORÍA — DIVIPOLA")
    write(out, "="*70)

    write(out, "\nPASO 1 — DESCARGA Y REGISTRO")
    write(out, f"Archivo: {div_file.name}")
    write(out, f"Ruta: {div_file.resolve()}")
    write(out, f"Fecha de auditoría/registro: {FECHA_AUDITORIA:%Y-%m-%d %H:%M}")
    write(out, "Formato: .xlsx")
    write(out, f"Tamaño (MB): {div_file.stat().st_size/1_000_000:.2f}")
    write(out, f"Filas antes de modificación: {len(DIV)}")
    write(out, f"Columnas: {len(DIV.columns)-3}")  # columnas originales

    write(out, "\nPASO 2 — EXPLORACIÓN")
    write(out, "Columnas exactas:")
    for c in [c for c in DIV.columns if not c.startswith("_")]:
        write(out, f"- {c}")
    write(out, "\nTipos:")
    write(out, DIV[[c for c in DIV.columns if not c.startswith("_")]].dtypes.to_string())
    write(out, "\nObservación: longitud y Latitud están almacenadas como texto y usan coma decimal.")
    write(out, "La fuente no contiene una columna explícita de región.")

    write(out, "\nPASO 3 — COMPLETITUD")
    for c in [c for c in DIV.columns if not c.startswith("_")]:
        n = DIV[c].isna().sum()
        write(out, f"- {c}: {n} ({n/len(DIV)*100:.2f}%)")
    write(out, f"Departamentos únicos: {DIV['Nombre Departamento'].nunique()}")
    write(out, f"Códigos municipales únicos: {DIV['_COD5'].nunique()}")

    write(out, "\nPASO 4 — EXACTITUD Y VALIDEZ")
    raw_codes = (DIV["Código Municipio"].astype(str)
                 .str.replace(r"\.0$", "", regex=True).str.strip())
    write(out, "Longitud de códigos almacenados:")
    write(out, raw_codes.str.len().value_counts().sort_index().to_string())
    write(out, f"Códigos municipales no válidos como 5 dígitos tras zfill: "
               f"{(~DIV['_COD5'].str.fullmatch(r'\\d{5}')).sum()}")
    write(out, f"Códigos municipales duplicados: "
               f"{DIV['_COD5'].duplicated(keep=False).sum()}")
    write(out, f"Duplicados de nombre+departamento: "
               f"{DIV.duplicated(['Nombre Departamento','Nombre Municipio'], keep=False).sum()}")

    # Coherencia código departamento vs primeros 2 dígitos del municipio
    mismatch_dep = DIV["_DEP2"] != DIV["_CODDEP5"]
    write(out, f"Municipios cuyo prefijo departamental no coincide con Código Departamento: "
               f"{mismatch_dep.sum()}")

    # Coordenadas: coma decimal
    lon = pd.to_numeric(DIV["longitud"].astype(str).str.replace(",", ".", regex=False),
                        errors="coerce")
    lat = pd.to_numeric(DIV["Latitud"].astype(str).str.replace(",", ".", regex=False),
                        errors="coerce")
    write(out, f"Longitudes no interpretables: {lon.isna().sum()}")
    write(out, f"Latitudes no interpretables: {lat.isna().sum()}")
    write(out, f"Longitudes fuera de [-180,180]: {((lon < -180)|(lon > 180)).sum()}")
    write(out, f"Latitudes fuera de [-90,90]: {((lat < -90)|(lat > 90)).sum()}")

    write(out, "\nPASO 5 — CONSISTENCIA")
    write(out, f"Filas: {len(DIV)}; códigos municipales únicos: {DIV['_COD5'].nunique()}")
    write(out, f"Correspondencia código departamento-prefijo municipal: "
               f"{len(DIV)-mismatch_dep.sum()} de {len(DIV)}")
    write(out, "No se evalúan agregaciones anuales porque DIVIPOLA no es una serie de hechos.")
    write(out, "No se identifica región en las columnas de la fuente; requiere fuente/regla adicional si el índice la necesita.")

    write(out, "\nPASO 6 — UNICIDAD")
    exact = DIV.duplicated(keep=False)
    write(out, f"Filas involucradas en duplicados exactos: {exact.sum()}")
    write(out, f"Combinaciones de código municipal repetidas: {DIV['_COD5'].duplicated(keep=False).sum()}")

    write(out, "\nPASO 7 — OPORTUNIDAD")
    write(out, "No existe fecha de hecho ni periodo temporal en el archivo.")
    write(out, "Se evalúa como catálogo territorial: la fuente debe tratarse según su vigencia/versionado 2025.")
    write(out, "El archivo auditado no contiene una columna que permita medir rezago mensual.")

# ------------------------------------------------------------
# AUDITORÍA DE FUENTES DE DELITOS
# ------------------------------------------------------------

def audit_crime(name, df, archivo):
    folder = RESULTADOS / name
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / "resultado_auditoria.txt"
    if out.exists(): out.unlink()

    terrorism = name == "Terrorismo"

    date_col = next((c for c in df.columns if "FECHA" in str(c).upper()), None)
    qty_col = next((c for c in df.columns if str(c).strip().upper()=="CANTIDAD"), None)

    if name == "Terrorismo":
        mun_col = "Municipio"
        dept_col = "Departamento"
        raw_code_col = "CODIGO DANE"
    else:
        mun_col = "MUNICIPIO"
        dept_col = "DEPARTAMENTO"
        raw_code_col = "COD_MUNI"

    dates = parse_dates(df[date_col], terrorism) if date_col else None

    write(out, "="*70)
    write(out, f"AUDITORÍA — {name}")
    write(out, "="*70)

    write(out, "\nPASO 1 — DESCARGA Y REGISTRO")
    write(out, f"Archivo: {archivo.name}")
    write(out, f"Ruta: {archivo.resolve()}")
    write(out, f"Fecha de auditoría/registro: {FECHA_AUDITORIA:%Y-%m-%d %H:%M}")
    write(out, f"Formato: {archivo.suffix}")
    write(out, f"Tamaño (MB): {archivo.stat().st_size/1_000_000:.2f}")
    write(out, f"Filas antes de modificación: {len(df)}")
    write(out, f"Columnas: {len(df.columns)}")

    write(out, "\nPASO 2 — EXPLORACIÓN")
    write(out, "Columnas exactas:")
    for c in df.columns: write(out, f"- {c}")
    write(out, "\nTipos:")
    write(out, df.dtypes.to_string())
    write(out, "\nPrimeras 5 filas:")
    write(out, df.head().to_string(index=False))
    write(out, "\nVariables que requieren diccionario:")
    for c in df.columns:
        u = str(c).strip().upper()
        if any(x in u for x in ["COD","ARMA","MEDIO","MODAL","TIPO","SPOA","CARACTER"]):
            write(out, f"- {c}")
    write(out, "Encabezados: primera fila.")

    write(out, "\nPASO 3 — COMPLETITUD")
    for c in df.columns:
        n = df[c].isna().sum()
        write(out, f"- {c}: {n} ({n/len(df)*100:.2f}%)")

    if dates is not None:
        write(out, f"Fechas no interpretables: {dates.isna().sum()}")
        if dates.notna().any():
            years = sorted(dates.dropna().dt.year.unique())
            write(out, f"Años: {years}")
            for y in years:
                months = sorted(dates.loc[dates.dt.year==y].dt.month.unique())
                write(out, f"- {y}: {months}")

    write(out, f"Departamentos únicos: {df[dept_col].nunique()}")
    write(out, f"Municipios/códigos únicos: {df[raw_code_col].nunique()}")

    write(out, "\nPASO 4 — EXACTITUD Y VALIDEZ")
    if qty_col:
        q = pd.to_numeric(df[qty_col], errors="coerce")
        write(out, f"Valores negativos en CANTIDAD: {(q<0).sum()}")
        write(out, f"Valores no numéricos en CANTIDAD: {q.isna().sum()}")
        write(out, f"Máximo CANTIDAD: {q.max()}")

    if dates is not None and dates.notna().any():
        write(out, f"Fecha mínima: {dates.min()}")
        write(out, f"Fecha máxima: {dates.max()}")
        fuera = ((dates < pd.Timestamp("2019-01-01")) |
                 (dates > pd.Timestamp("2025-12-31"))).sum()
        write(out, f"Fechas fuera de 2019–2025: {fuera}")

    raw = (df[raw_code_col].astype(str)
           .str.replace(r"\.0$", "", regex=True).str.strip())

    write(out, "Longitud de código almacenado:")
    write(out, raw.str.len().value_counts().sort_index().to_string())

    if name != "Terrorismo":
        std = code5(df[raw_code_col])
        found = std.isin(set(DIV["_COD5"]))
        write(out, f"Códigos municipales no encontrados en DIVIPOLA: {(~found).sum()}")

    else:
        # Terrorismo: CODIGO DANE representa el código municipal seguido de 000.
        # Se valida quitando los tres últimos dígitos y completando a 5.
        nums = pd.to_numeric(df[raw_code_col], errors="coerce")
        derived = (nums // 1000).astype("Int64").astype(str).str.replace("<NA>","",regex=False).str.zfill(5)
        found = derived.isin(set(DIV["_COD5"]))
        write(out, "Regla de validación territorial: CODIGO DANE // 1000 -> código municipal de 5 dígitos.")
        write(out, f"Códigos derivados no encontrados en DIVIPOLA: {(~found).sum()}")

    # Consistencia interna
    write(out, "\nPASO 5 — CONSISTENCIA")

    if name != "Terrorismo":
        std = code5(df[raw_code_col])
        cr = df.copy()
        cr["_COD5"] = std
        ref = DIV[["_COD5","Nombre Municipio","Nombre Departamento"]]
        cr = cr.merge(ref, on="_COD5", how="left")

        cr["_N_F"] = cr[mun_col].apply(norm)
        cr["_N_D"] = cr["Nombre Municipio"].apply(norm)
        diff = cr[cr["_N_F"] != cr["_N_D"]]
        no_ref = cr["Nombre Municipio"].isna()

        write(out, f"Códigos no encontrados en DIVIPOLA: {no_ref.sum()}")
        write(out, f"Registros con diferencia de denominación: {len(diff)} ({len(diff)/len(cr)*100:.2f}%)")
        write(out, "Diferencias de denominación por código:")
        write(out, diff[["_COD5",mun_col,"Nombre Municipio"]].drop_duplicates().to_string(index=False))

        mult = df.groupby(raw_code_col)[mun_col].nunique()
        write(out, f"Códigos con más de un nombre dentro de la fuente: {(mult>1).sum()}")

    else:
        nums = pd.to_numeric(df[raw_code_col], errors="coerce")
        cr = df.copy()
        cr["_COD5"] = (nums//1000).astype("Int64").astype(str).str.replace("<NA>","",regex=False).str.zfill(5)
        ref = DIV[["_COD5","Nombre Municipio","Nombre Departamento"]]
        cr = cr.merge(ref, on="_COD5", how="left")
        cr["_N_F"] = cr[mun_col].apply(norm)
        cr["_N_D"] = cr["Nombre Municipio"].apply(norm)
        diff = cr[cr["_N_F"] != cr["_N_D"]]
        no_ref = cr["Nombre Municipio"].isna()

        write(out, f"Códigos derivados no encontrados en DIVIPOLA: {no_ref.sum()}")
        write(out, f"Registros con diferencia de denominación: {len(diff)} ({len(diff)/len(cr)*100:.2f}%)")
        write(out, "Diferencias de denominación por código:")
        write(out, diff[["_COD5",mun_col,"Nombre Municipio"]].drop_duplicates().to_string(index=False))

    # Agregaciones
    if dates is not None and qty_col:
        work = df.copy()
        work["_DATE"] = dates
        work["_YEAR"] = dates.dt.year
        work["_MONTH"] = dates.dt.month

        a = work.groupby(["_YEAR",dept_col])[qty_col].sum()
        m = work.groupby(["_YEAR",dept_col,"_MONTH"])[qty_col].sum().groupby(level=[0,1]).sum()
        cmp = pd.concat([a.rename("ANUAL"),m.rename("MENSUAL")],axis=1).fillna(0)
        write(out, f"Diferencias año-departamento: {(cmp['ANUAL'] != cmp['MENSUAL']).sum()}")

        a2 = work.groupby(["_YEAR",raw_code_col])[qty_col].sum()
        m2 = work.groupby(["_YEAR",raw_code_col,"_MONTH"])[qty_col].sum().groupby(level=[0,1]).sum()
        cmp2 = pd.concat([a2.rename("ANUAL"),m2.rename("MENSUAL")],axis=1).fillna(0)
        write(out, f"Diferencias año-municipio/código: {(cmp2['ANUAL'] != cmp2['MENSUAL']).sum()}")

    # Unicidad
    write(out, "\nPASO 6 — UNICIDAD")
    exact = df.duplicated(keep=False)
    write(out, f"Filas involucradas en duplicados exactos: {exact.sum()}")
    write(out, f"Porcentaje: {exact.mean()*100:.2f}%")
    write(out, f"Combinaciones exactas duplicadas: {(df.value_counts()>1).sum()}")

    if date_col and qty_col:
        logical = df.duplicated([raw_code_col,date_col,qty_col], keep=False)
        write(out, f"Filas involucradas en duplicados lógicos: {logical.sum()}")
        write(out, f"Porcentaje: {logical.mean()*100:.2f}%")
        write(out, f"Combinaciones lógicas duplicadas: "
                   f"{(df.groupby([raw_code_col,date_col,qty_col]).size()>1).sum()}")

        q = pd.to_numeric(df[qty_col],errors="coerce")
        total = q.sum()
        qdup = q[exact].sum()
        write(out, f"Cantidad total: {total}")
        write(out, f"Cantidad en filas duplicadas exactas: {qdup}")
        if total:
            write(out, f"Porcentaje de cantidad: {qdup/total*100:.2f}%")

    write(out, "\nPASO 7 — OPORTUNIDAD")
    if dates is None or not dates.notna().any():
        write(out, "No aplica: no existe fecha de hechos.")
    else:
        last = dates.max()
        lag = (FECHA_AUDITORIA.year-last.year)*12 + FECHA_AUDITORIA.month-last.month
        write(out, f"Primera fecha: {dates.min()}")
        write(out, f"Última fecha: {last}")
        write(out, f"Rezago aproximado: {lag} meses")
        write(out, f"2025 disponible: {2025 in dates.dropna().dt.year.unique()}")
        write(out, "Frecuencia documentada: mensual para Estadística Delictiva.")

    return df

# ------------------------------------------------------------
# AUDITORÍA COCA — estructura ancha (años como columnas)
# ------------------------------------------------------------

def audit_coca():
    archivo = files["Coca"]
    if archivo is None:
        print("Coca: NO ENCONTRADO")
        return None

    df = pd.read_excel(archivo)
    folder = RESULTADOS/"Coca"
    folder.mkdir(parents=True, exist_ok=True)
    out = folder/"resultado_auditoria.txt"
    if out.exists(): out.unlink()

    year_cols = [str(y) for y in range(2019,2026) if str(y) in df.columns]
    available_years = [int(y) for y in year_cols]

    write(out,"="*70)
    write(out,"AUDITORÍA — CULTIVOS DE HOJA DE COCA")
    write(out,"="*70)

    write(out,"\nPASO 1 — DESCARGA Y REGISTRO")
    write(out,f"Archivo: {archivo.name}")
    write(out,f"Ruta: {archivo.resolve()}")
    write(out,f"Fecha de auditoría/registro: {FECHA_AUDITORIA:%Y-%m-%d %H:%M}")
    write(out,"Formato: .xlsx")
    write(out,f"Tamaño (MB): {archivo.stat().st_size/1_000_000:.2f}")
    write(out,f"Filas: {len(df)}")
    write(out,f"Columnas: {len(df.columns)}")

    write(out,"\nPASO 2 — EXPLORACIÓN")
    write(out,"Columnas exactas:")
    for c in df.columns: write(out,f"- {c}")
    write(out,"\nTipos:")
    write(out,df.dtypes.to_string())
    write(out,"Estructura temporal: formato ancho; cada año se encuentra como una columna.")
    write(out,"Variable de interés: hectáreas detectadas.")
    write(out,"La fuente no contiene una columna 2025.")

    write(out,"\nPASO 3 — COMPLETITUD")
    for c in df.columns:
        n=df[c].isna().sum()
        write(out,f"- {c}: {n} ({n/len(df)*100:.2f}%)")
    write(out,f"Años requeridos por el taller: 2019–2025")
    write(out,f"Años disponibles: {available_years}")
    write(out,f"Años faltantes: {[y for y in range(2019,2026) if y not in available_years]}")

    write(out,"\nPASO 4 — EXACTITUD Y VALIDEZ")
    for y in available_years:
        s=pd.to_numeric(df[str(y)],errors="coerce")
        write(out,f"{y}: negativos={(s<0).sum()}, no numéricos={s.notna().sum()-df[str(y)].notna().sum()}, máximo={s.max()}")
    raw=code5(df["CODMPIO"])
    write(out,f"Códigos municipales no encontrados en DIVIPOLA: {(~raw.isin(set(DIV['_COD5']))).sum()}")
    write(out,f"Duplicidad de códigos municipales: {raw.duplicated(keep=False).sum()}")

    write(out,"\nPASO 5 — CONSISTENCIA")
    cr=df.copy()
    cr["_COD5"]=raw
    cr=cr.merge(DIV[["_COD5","Nombre Municipio","Nombre Departamento"]],on="_COD5",how="left")
    cr["_N_F"]=cr["MUNICIPIO"].apply(norm)
    cr["_N_D"]=cr["Nombre Municipio"].apply(norm)
    diff=cr[cr["_N_F"]!=cr["_N_D"]]
    write(out,f"Códigos no encontrados en DIVIPOLA: {cr['Nombre Municipio'].isna().sum()}")
    write(out,f"Registros con diferencia de denominación: {len(diff)} ({len(diff)/len(cr)*100:.2f}%)")
    write(out,"La fuente usa estructura anual ancha; la coherencia anual se revisa directamente por columna.")
    for y in available_years:
        write(out,f"Total hectáreas {y}: {pd.to_numeric(df[str(y)],errors='coerce').sum():.2f}")

    write(out,"\nPASO 6 — UNICIDAD")
    exact=df.duplicated(keep=False)
    write(out,f"Filas involucradas en duplicados exactos: {exact.sum()}")
    write(out,f"Porcentaje: {exact.mean()*100:.2f}%")
    write(out,"Duplicados lógicos no se calculan como municipio-fecha-cantidad porque la fuente no tiene fecha/registro largo; cada año es una columna.")

    write(out,"\nPASO 7 — OPORTUNIDAD")
    write(out,f"Último año disponible: {max(available_years)}")
    write(out,"2025 disponible: NO")
    write(out,"Impacto: no es posible construir directamente el componente 2025 del índice con esta versión de la fuente.")
    write(out,"Tratamiento propuesto: documentar el faltante; buscar/publicar una versión oficial 2025 antes de cerrar el índice. No imputar 2025 como cero.")
    write(out,"Frecuencia/actualización: debe documentarse con la publicación oficial de SIMCI/UNODC; el archivo auditado no contiene esa metadata.")

    return df

# ------------------------------------------------------------
# EJECUCIÓN
# ------------------------------------------------------------

audit_divipola()

dfs={}
for name in ["Homicidios","Secuestro","Extorsion","Terrorismo"]:
    if files[name] is not None:
        dfs[name]=audit_crime(name,pd.read_excel(files[name]),files[name])

dfs["Coca"]=audit_coca()

# ------------------------------------------------------------
# COBERTURA TERRITORIAL ENTRE FUENTES
# ------------------------------------------------------------

out=RESULTADOS/"resumen_cobertura_territorial.txt"
if out.exists(): out.unlink()
write(out,"="*70)
write(out,"5.4 — COBERTURA TERRITORIAL ENTRE FUENTES DE DELITOS")
write(out,"="*70)

sets={}
for n in ["Homicidios","Secuestro","Extorsion"]:
    if n in dfs:
        sets[n]=set(code5(dfs[n]["COD_MUNI"]))

if "Terrorismo" in dfs:
    t=dfs["Terrorismo"].copy()
    nums=pd.to_numeric(t["CODIGO DANE"],errors="coerce")
    t["_COD5"]=(nums//1000).astype("Int64").astype(str).str.replace("<NA>","",regex=False).str.zfill(5)
    sets["Terrorismo"]=set(t["_COD5"])

for other in ["Secuestro","Extorsion","Terrorismo"]:
    if "Homicidios" in sets and other in sets:
        common=len(sets["Homicidios"]&sets[other])
        write(out,f"Homicidios vs {other}: comunes={common}; solo Homicidios={len(sets['Homicidios']-sets[other])}; solo {other}={len(sets[other]-sets['Homicidios'])}")

write(out,"\nNota: diferencias de cobertura no se interpretan automáticamente como errores ni como ceros. Pueden obedecer a la naturaleza del delito, cobertura territorial o estructura de la fuente.")

print("\nAUDITORÍA V3 TERMINADA")
print("Resultados:",RESULTADOS)
