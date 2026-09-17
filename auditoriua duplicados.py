import pandas as pd
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

CARPETA = Path(r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA")

ARCHIVOS = {
    "Homicidios": "7HOMICIDIO_20260903 (1).xlsx",
    "Secuestros": "2SECUESTRO_20260903.xlsx",
    "Extorsión": "3EXTORSIÓN_20260904.xlsx",
    "Terrorismo": "1Reporte_Delito_Terrorismo_Policía_Nacional_2019 A 2025.xlsx",
    "Coca": "4Detección_de_Cultivos_de_Coca_(hectáreas)_20260903.xlsx",
    "DIVIPOLA": "5DIVIPOLA-_Códigos_municipios_20260903vf.xlsx"
}


# ============================================================
# CONFIGURACIÓN DE CAMPOS
# ============================================================
#
# IMPORTANTE:
# Ajusta únicamente estos nombres si en tu archivo aparecen
# diferentes.
#
# ID = identificador del registro
# MUNICIPIO = municipio
# FECHA = fecha
# VALOR = cantidad/valor del fenómeno
#
# Para COCA la estructura es anual, por lo que no se puede
# aplicar directamente la misma regla municipio+fecha+valor.
# La dejamos separada para no generar falsos duplicados.
# ============================================================

CONFIG = {

    "Homicidios": {
        "id": "ID",
        "municipio": "MUNICIPIO",
        "fecha": "FECHA HECHO",
        "valor": "CANTIDAD"
    },

    "Secuestros": {
        "id": "ID",
        "municipio": "MUNICIPIO",
        "fecha": "FECHA HECHO",
        "valor": "CANTIDAD"
    },

    "Extorsión": {
        "id": "ID",
        "municipio": "MUNICIPIO",
        "fecha": "FECHA HECHO",
        "valor": "CANTIDAD"
    },

    "Terrorismo": {
        "id": "ID",
        "municipio": "Municipio",
        "fecha": "FECHA HECHO",
        "valor": "CANTIDAD"
    },

    "Coca": {
        "id": "ID",
        "municipio": "MUNICIPIO",
        "fecha": None,
        "valor": None
    },

    "DIVIPOLA": {
        "id": None,
        "municipio": "Nombre Municipio",
        "fecha": None,
        "valor": None
    }
}


# ============================================================
# FUNCIONES
# ============================================================

def normalizar_texto(serie):
    """
    Normaliza texto para evitar que espacios o mayúsculas
    generen diferencias artificiales.
    """
    return (
        serie.astype("string")
        .str.strip()
        .str.upper()
    )


def duplicados_exactos(df):
    """
    Q24:
    Filas completamente idénticas en todas sus columnas.
    """

    mascara = df.duplicated(
        subset=df.columns,
        keep=False
    )

    registros = mascara.sum()

    return mascara, registros


def duplicados_logicos(df, config):
    """
    Q25:
    Mismo municipio + misma fecha + mismo valor
    pero con diferente identificador.

    IMPORTANTE:
    No considera duplicado lógico un grupo en el que
    todos los registros tienen exactamente el mismo ID.
    """

    id_col = config["id"]
    municipio_col = config["municipio"]
    fecha_col = config["fecha"]
    valor_col = config["valor"]

    # Verificar que existan los campos
    campos = [
        id_col,
        municipio_col,
        fecha_col,
        valor_col
    ]

    faltantes = [
        c for c in campos
        if c is None or c not in df.columns
    ]

    if faltantes:
        return pd.Series(False, index=df.index), 0, pd.DataFrame()

    temp = df.copy()

    # Normalización para comparación
    temp["_MUNICIPIO_LOGICO"] = normalizar_texto(
        temp[municipio_col]
    )

    temp["_FECHA_LOGICA"] = pd.to_datetime(
        temp[fecha_col],
        errors="coerce"
    )

    temp["_VALOR_LOGICO"] = temp[valor_col]

    # Agrupar por:
    # municipio + fecha + valor
    grupos = temp.groupby(
        [
            "_MUNICIPIO_LOGICO",
            "_FECHA_LOGICA",
            "_VALOR_LOGICO"
        ],
        dropna=False
    )

    mascara = pd.Series(False, index=df.index)

    grupos_problematicos = []

    for _, grupo in grupos:

        # Debe existir más de un registro
        if len(grupo) <= 1:
            continue

        # Debe haber identificadores diferentes
        ids_unicos = grupo[id_col].astype("string").nunique()

        if ids_unicos > 1:

            indices = grupo.index

            mascara.loc[indices] = True

            grupos_problematicos.append({
                "Municipio": grupo[municipio_col].iloc[0],
                "Fecha": grupo[fecha_col].iloc[0],
                "Valor": grupo[valor_col].iloc[0],
                "Registros": len(grupo),
                "IDs_diferentes": ids_unicos
            })

    detalle = pd.DataFrame(grupos_problematicos)

    registros = mascara.sum()

    return mascara, registros, detalle


# ============================================================
# PROCESAMIENTO
# ============================================================

resultados = []

detalles_exactos = []
detalles_logicos = []

for fuente, archivo in ARCHIVOS.items():

    print("\n" + "=" * 70)
    print(f"PROCESANDO: {fuente}")
    print("=" * 70)

    ruta = CARPETA / archivo

    if not ruta.exists():
        print(f"⚠️ Archivo no encontrado: {ruta}")
        continue

    # Leer archivo
    df = pd.read_excel(ruta)

    total = len(df)

    print(f"Total de registros: {total}")

    # --------------------------------------------------------
    # Q24 — DUPLICADOS EXACTOS
    # --------------------------------------------------------

    mascara_exactos, n_exactos = duplicados_exactos(df)

    pct_exactos = (
        n_exactos / total * 100
        if total > 0 else 0
    )

    print(
        f"Duplicados exactos: "
        f"{n_exactos:,} ({pct_exactos:.2f}%)"
    )

    # --------------------------------------------------------
    # Q25 — DUPLICADOS LÓGICOS
    # --------------------------------------------------------

    mascara_logicos, n_logicos, detalle_logico = (
        duplicados_logicos(
            df,
            CONFIG[fuente]
        )
    )

    pct_logicos = (
        n_logicos / total * 100
        if total > 0 else 0
    )

    print(
        f"Duplicados lógicos: "
        f"{n_logicos:,} ({pct_logicos:.2f}%)"
    )

    # --------------------------------------------------------
    # Q26 — REGISTROS INVOLUCRADOS EN DUPLICIDAD
    # --------------------------------------------------------
    #
    # IMPORTANTE:
    # No sumamos exactos + lógicos.
    #
    # Utilizamos OR para contar cada registro una sola vez.
    # --------------------------------------------------------

    mascara_duplicados = (
        mascara_exactos |
        mascara_logicos
    )

    n_duplicados_total = mascara_duplicados.sum()

    pct_duplicados_total = (
        n_duplicados_total / total * 100
        if total > 0 else 0
    )

    print(
        f"Registros involucrados en duplicidad: "
        f"{n_duplicados_total:,} "
        f"({pct_duplicados_total:.2f}%)"
    )

    # --------------------------------------------------------
    # GUARDAR RESULTADOS
    # --------------------------------------------------------

    resultados.append({
        "Fuente": fuente,
        "Total registros": total,

        "Duplicados exactos": n_exactos,
        "% duplicados exactos": round(
            pct_exactos, 2
        ),

        "Duplicados lógicos": n_logicos,
        "% duplicados lógicos": round(
            pct_logicos, 2
        ),

        "Registros involucrados en duplicidad": n_duplicados_total,
        "% registros involucrados": round(
            pct_duplicados_total, 2
        )
    })

    # --------------------------------------------------------
    # DETALLE DUPLICADOS EXACTOS
    # --------------------------------------------------------

    if n_exactos > 0:

        detalle = df.loc[
            mascara_exactos
        ].copy()

        detalle.insert(
            0,
            "Fuente",
            fuente
        )

        detalles_exactos.append(
            detalle
        )

    # --------------------------------------------------------
    # DETALLE DUPLICADOS LÓGICOS
    # --------------------------------------------------------

    if n_logicos > 0:

        detalle = df.loc[
            mascara_logicos
        ].copy()

        detalle.insert(
            0,
            "Fuente",
            fuente
        )

        detalles_logicos.append(
            detalle
        )


# ============================================================
# CONSOLIDAR RESULTADOS
# ============================================================

df_resultados = pd.DataFrame(
    resultados
)

print("\n")
print("=" * 70)
print("RESULTADO FINAL")
print("=" * 70)

print(
    df_resultados.to_string(
        index=False
    )
)


# ============================================================
# EXPORTAR EXCEL
# ============================================================

salida = CARPETA / "Auditoria_Duplicados_Corregida.xlsx"

with pd.ExcelWriter(
    salida,
    engine="openpyxl"
) as writer:

    # Resumen
    df_resultados.to_excel(
        writer,
        sheet_name="Resumen",
        index=False
    )

    # Duplicados exactos
    if detalles_exactos:

        df_exactos = pd.concat(
            detalles_exactos,
            ignore_index=True
        )

        df_exactos.to_excel(
            writer,
            sheet_name="Duplicados exactos",
            index=False
        )

    # Duplicados lógicos
    if detalles_logicos:

        df_logicos = pd.concat(
            detalles_logicos,
            ignore_index=True
        )

        df_logicos.to_excel(
            writer,
            sheet_name="Duplicados lógicos",
            index=False
        )

print("\n")
print("Archivo generado:")
print(salida)