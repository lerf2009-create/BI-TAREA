import os
import pandas as pd

# ============================================================
# AUDITORÍA DE UNICIDAD
# Preguntas 24, 25 y 26 del taller
# ============================================================

BASE = r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA"

print("=" * 90)
print("AUDITORÍA DE UNICIDAD — PREGUNTAS 24, 25 Y 26")
print("=" * 90)


# ------------------------------------------------------------
# 1. BUSCAR ARCHIVOS
# ------------------------------------------------------------

archivos = os.listdir(BASE)


def buscar_archivo(texto, excluir=None):

    for archivo in archivos:

        nombre = archivo.upper()

        if texto.upper() in nombre:

            if excluir and excluir.upper() in nombre:
                continue

            return os.path.join(BASE, archivo)

    return None


HOM_FILE = buscar_archivo("HOMICIDIO")

SEC_FILE = buscar_archivo("SECUESTRO")

EXT_FILE = buscar_archivo("EXTORS")

TER_FILE = None

for archivo in archivos:

    nombre = archivo.upper()

    if "TERRORISMO" in nombre and "2019" in nombre:
        TER_FILE = os.path.join(BASE, archivo)
        break


COCA_FILE = buscar_archivo("COCA")


# ------------------------------------------------------------
# 2. FUNCIÓN GENERAL DE AUDITORÍA
# ------------------------------------------------------------

def auditar_duplicados(
    nombre,
    archivo,
    columna_municipio,
    columna_fecha,
    columna_valor
):

    print("\n")
    print("#" * 90)
    print(f"FUENTE: {nombre}")
    print("#" * 90)

    print("Archivo:", os.path.basename(archivo))

    # --------------------------------------------------------
    # CARGAR
    # --------------------------------------------------------

    df = pd.read_excel(archivo)

    print("Filas totales:", len(df))
    print("Columnas:", len(df.columns))


    # --------------------------------------------------------
    # PREGUNTA 24
    # DUPLICADOS EXACTOS
    # --------------------------------------------------------

    duplicados_exactos = df.duplicated(
        keep=False
    )

    n_exactos = duplicados_exactos.sum()

    pct_exactos = (
        n_exactos / len(df) * 100
    )


    print("\nPREGUNTA 24")
    print("-" * 60)

    print(
        "¿Hay filas completamente idénticas?"
    )

    print(
        f"Filas involucradas en duplicados exactos: "
        f"{n_exactos:,}"
    )

    print(
        f"Porcentaje del dataset: "
        f"{pct_exactos:.2f}%"
    )


    # --------------------------------------------------------
    # PREGUNTA 25
    # DUPLICADOS LÓGICOS
    # --------------------------------------------------------

    columnas_logicas = [

        columna_municipio,

        columna_fecha,

        columna_valor

    ]


    duplicados_logicos = df.duplicated(

        subset=columnas_logicas,

        keep=False

    )


    n_logicos = duplicados_logicos.sum()


    pct_logicos = (

        n_logicos /

        len(df) *

        100

    )


    # Número de combinaciones repetidas
    grupos_logicos = (

        df.groupby(columnas_logicas)

        .size()

    )


    grupos_repetidos = (

        grupos_logicos[

            grupos_logicos > 1

        ]

    )


    print("\nPREGUNTA 25")
    print("-" * 60)

    print(
        "¿Hay filas con el mismo municipio, "
        "misma fecha y mismo valor?"
    )

    print(
        f"Filas involucradas en duplicados lógicos: "
        f"{n_logicos:,}"
    )

    print(
        f"Porcentaje del dataset: "
        f"{pct_logicos:.2f}%"
    )

    print(
        f"Combinaciones municipio-fecha-valor repetidas: "
        f"{len(grupos_repetidos):,}"
    )


    # --------------------------------------------------------
    # PREGUNTA 26
    # IMPACTO SOBRE EL TOTAL
    # --------------------------------------------------------

    # Cantidad total de la fuente
    total_valor = pd.to_numeric(

        df[columna_valor],

        errors="coerce"

    ).sum()


    # Cantidad correspondiente a las filas
    # involucradas en duplicados exactos
    valor_duplicados_exactos = pd.to_numeric(

        df.loc[
            duplicados_exactos,
            columna_valor
        ],

        errors="coerce"

    ).sum()


    pct_valor_exactos = (

        valor_duplicados_exactos /

        total_valor *

        100

    ) if total_valor != 0 else 0


    # Cantidad correspondiente a las filas
    # involucradas en duplicados lógicos
    valor_duplicados_logicos = pd.to_numeric(

        df.loc[
            duplicados_logicos,
            columna_valor
        ],

        errors="coerce"

    ).sum()


    pct_valor_logicos = (

        valor_duplicados_logicos /

        total_valor *

        100

    ) if total_valor != 0 else 0


    print("\nPREGUNTA 26")
    print("-" * 60)

    print(
        "¿Si se suman los registros duplicados "
        "cuánto representan sobre el total?"
    )

    print(
        f"Total de {columna_valor}: "
        f"{total_valor:,.2f}"
    )

    print(
        f"Valor en filas duplicadas exactas: "
        f"{valor_duplicados_exactos:,.2f}"
    )

    print(
        f"% del total asociado a duplicados exactos: "
        f"{pct_valor_exactos:.2f}%"
    )

    print(
        f"Valor en filas duplicadas lógicas: "
        f"{valor_duplicados_logicos:,.2f}"
    )

    print(
        f"% del total asociado a duplicados lógicos: "
        f"{pct_valor_logicos:.2f}%"
    )


    # --------------------------------------------------------
    # MOSTRAR EJEMPLOS
    # --------------------------------------------------------

    if n_logicos > 0:

        print("\nEJEMPLOS DE DUPLICADOS LÓGICOS")

        print("-" * 60)

        ejemplos = (

            df.loc[
                duplicados_logicos
            ]

            .sort_values(
                columnas_logicas
            )

            .head(10)

        )

        print(
            ejemplos.to_string(
                index=False
            )
        )


    # --------------------------------------------------------
    # RETORNAR RESULTADOS
    # --------------------------------------------------------

    return {

        "Fuente": nombre,

        "Filas": len(df),

        "Duplicados exactos": n_exactos,

        "% duplicados exactos":
            round(pct_exactos, 2),

        "Duplicados lógicos": n_logicos,

        "% duplicados lógicos":
            round(pct_logicos, 2),

        "Combinaciones lógicas repetidas":
            len(grupos_repetidos),

        "Total valor":
            total_valor,

        "Valor duplicados exactos":
            valor_duplicados_exactos,

        "% valor duplicados exactos":
            round(pct_valor_exactos, 2),

        "Valor duplicados lógicos":
            valor_duplicados_logicos,

        "% valor duplicados lógicos":
            round(pct_valor_logicos, 2)

    }


# ============================================================
# 3. EJECUTAR PARA LAS BASES
# ============================================================

resultados = []


# HOMICIDIOS
resultados.append(

    auditar_duplicados(

        "Homicidios",

        HOM_FILE,

        "COD_MUNI",

        "FECHA HECHO",

        "CANTIDAD"

    )

)


# SECUESTROS
resultados.append(

    auditar_duplicados(

        "Secuestros",

        SEC_FILE,

        "COD_MUNI",

        "FECHA HECHO",

        "CANTIDAD"

    )

)


# EXTORSIÓN
resultados.append(

    auditar_duplicados(

        "Extorsión",

        EXT_FILE,

        "COD_MUNI",

        "FECHA HECHO",

        "CANTIDAD"

    )

)


# TERRORISMO
resultados.append(

    auditar_duplicados(

        "Actos terroristas",

        TER_FILE,

        "CODIGO DANE",

        "FECHA HECHO",

        "CANTIDAD"

    )

)


# ============================================================
# 4. RESUMEN FINAL
# ============================================================

print("\n")
print("=" * 90)
print("RESUMEN GENERAL — PREGUNTAS 24, 25 Y 26")
print("=" * 90)


resumen = pd.DataFrame(
    resultados
)


columnas_resumen = [

    "Fuente",

    "Filas",

    "Duplicados exactos",

    "% duplicados exactos",

    "Duplicados lógicos",

    "% duplicados lógicos",

    "Combinaciones lógicas repetidas",

    "Total valor",

    "Valor duplicados exactos",

    "% valor duplicados exactos",

    "Valor duplicados lógicos",

    "% valor duplicados lógicos"

]


print(

    resumen[
        columnas_resumen
    ]

    .to_string(
        index=False
    )

)


# ============================================================
# 5. EXPORTAR A EXCEL
# ============================================================

salida = os.path.join(

    BASE,

    "auditoria_duplicados_preguntas_24_25_26.xlsx"

)


with pd.ExcelWriter(

    salida,

    engine="openpyxl"

) as writer:

    resumen.to_excel(

        writer,

        sheet_name="Resumen",

        index=False

    )


print("\n")
print("=" * 90)
print("ARCHIVO GENERADO")
print("=" * 90)

print(salida)