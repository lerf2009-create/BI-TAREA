import os
import pandas as pd
from datetime import datetime

# ============================================================
# AUDITORÍA DE OPORTUNIDAD
# Rezago frente a la fecha de descarga
# ============================================================

BASE = r"C:\Users\lerf2\OneDrive\Escritorio\BI TAREA"


print("=" * 90)
print("AUDITORÍA DE OPORTUNIDAD — REZAGO FRENTE A FECHA DE DESCARGA")
print("=" * 90)


# ============================================================
# FECHAS DE DESCARGA
# ============================================================
#
# IMPORTANTE:
# Estas fechas deben corresponder a la fecha REAL en que
# descargaste cada archivo.
#
# Las fechas que ponemos inicialmente corresponden a la
# nomenclatura que tienen tus archivos.
# ============================================================

FECHAS_DESCARGA = {

    "Homicidios":
        datetime(2026, 9, 3),

    "Secuestros":
        datetime(2026, 9, 3),

    "Extorsión":
        datetime(2026, 9, 4),

    "Terrorismo":
        datetime(2026, 9, 3),

    "Coca":
        datetime(2026, 9, 3),

    "DIVIPOLA":
        datetime(2026, 9, 3)
}


# ============================================================
# BUSCAR ARCHIVOS
# ============================================================

archivos = os.listdir(BASE)


def buscar_archivo(texto):

    for archivo in archivos:

        if texto.upper() in archivo.upper():

            return os.path.join(
                BASE,
                archivo
            )

    return None


HOM_FILE = buscar_archivo("HOMICIDIO")

SEC_FILE = buscar_archivo("SECUESTRO")

EXT_FILE = buscar_archivo("EXTORS")

COCA_FILE = buscar_archivo("COCA")

DIV_FILE = buscar_archivo("DIVIPOLA")


# Terrorismo:
# Tenemos dos archivos relacionados.
# Buscamos específicamente el de 2019–2025.

TER_FILE = None

for archivo in archivos:

    nombre = archivo.upper()

    if (
        "TERRORISMO" in nombre
        and "2019" in nombre
    ):

        TER_FILE = os.path.join(
            BASE,
            archivo
        )

        break


# ============================================================
# FUNCIÓN PARA CALCULAR MESES DE REZAGO
# ============================================================

def meses_rezago(fecha_ultimo_dato, fecha_descarga):

    dias = (
        fecha_descarga -
        fecha_ultimo_dato
    ).days

    meses = dias / 30.4375

    return round(meses, 2)


# ============================================================
# FUNCIÓN GENERAL
# ============================================================

def auditar_oportunidad(
    nombre,
    archivo,
    columna_fecha
):

    print("\n")
    print("#" * 90)
    print(f"FUENTE: {nombre}")
    print("#" * 90)


    if archivo is None:

        print("ERROR: archivo no encontrado.")

        return None


    # --------------------------------------------------------
    # CARGAR
    # --------------------------------------------------------

    df = pd.read_excel(
        archivo
    )


    # --------------------------------------------------------
    # CONVERTIR FECHA
    # --------------------------------------------------------

    df[columna_fecha] = pd.to_datetime(

        df[columna_fecha],

        errors="coerce",

        dayfirst=True

    )


    # --------------------------------------------------------
    # ÚLTIMA FECHA
    # --------------------------------------------------------

    ultimo_dato = df[
        columna_fecha
    ].max()


    # --------------------------------------------------------
    # FECHA DE DESCARGA
    # --------------------------------------------------------

    fecha_descarga = FECHAS_DESCARGA[
        nombre
    ]


    # --------------------------------------------------------
    # REZAGO
    # --------------------------------------------------------

    rezago = meses_rezago(

        ultimo_dato,

        fecha_descarga

    )


    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    print(
        "Último dato disponible:",
        ultimo_dato.strftime(
            "%Y-%m-%d"
        )
    )

    print(
        "Fecha de descarga:",
        fecha_descarga.strftime(
            "%Y-%m-%d"
        )
    )

    print(
        "Rezago al momento de descarga:",
        rezago,
        "meses"
    )


    return {

        "Fuente":
            nombre,

        "Último dato":
            ultimo_dato.strftime(
                "%Y-%m-%d"
            ),

        "Fecha descarga":
            fecha_descarga.strftime(
                "%Y-%m-%d"
            ),

        "Rezago meses":
            rezago

    }


# ============================================================
# HOMICIDIOS
# ============================================================

resultado_hom = auditar_oportunidad(

    "Homicidios",

    HOM_FILE,

    "FECHA HECHO"

)


# ============================================================
# SECUESTROS
# ============================================================

resultado_sec = auditar_oportunidad(

    "Secuestros",

    SEC_FILE,

    "FECHA HECHO"

)


# ============================================================
# EXTORSIÓN
# ============================================================

resultado_ext = auditar_oportunidad(

    "Extorsión",

    EXT_FILE,

    "FECHA HECHO"

)


# ============================================================
# TERRORISMO
# ============================================================

resultado_ter = auditar_oportunidad(

    "Terrorismo",

    TER_FILE,

    "FECHA HECHO"

)


# ============================================================
# COCA
# ============================================================
#
# Coca NO tiene una columna fecha.
# Tiene columnas por año:
# 2001, 2002, ..., 2024
# ============================================================

print("\n")
print("#" * 90)
print("FUENTE: Cultivos de hoja de coca")
print("#" * 90)


coca = pd.read_excel(
    COCA_FILE
)


años_coca = []

for columna in coca.columns:

    try:

        año = int(columna)

        if 2000 <= año <= 2030:

            años_coca.append(año)

    except:

        pass


ultimo_año_coca = max(
    años_coca
)


fecha_ultimo_coca = datetime(
    ultimo_año_coca,
    12,
    31
)


fecha_descarga_coca = FECHAS_DESCARGA[
    "Coca"
]


rezago_coca = meses_rezago(

    fecha_ultimo_coca,

    fecha_descarga_coca

)


print(
    "Último año disponible:",
    ultimo_año_coca
)

print(
    "Fecha de descarga:",
    fecha_descarga_coca.strftime(
        "%Y-%m-%d"
    )
)

print(
    "Rezago al momento de descarga:",
    rezago_coca,
    "meses"
)


resultado_coca = {

    "Fuente":
        "Coca",

    "Último dato":
        str(ultimo_año_coca),

    "Fecha descarga":
        fecha_descarga_coca.strftime(
            "%Y-%m-%d"
        ),

    "Rezago meses":
        rezago_coca

}


# ============================================================
# DIVIPOLA
# ============================================================
#
# DIVIPOLA no es una serie de eventos.
# Es un catálogo territorial.
# Por tanto NO tiene sentido calcular un
# "rezago entre último hecho y descarga".
# ============================================================

print("\n")
print("#" * 90)
print("FUENTE: DIVIPOLA")
print("#" * 90)

print(
    "Tipo de fuente: catálogo territorial"
)

print(
    "Rezago temporal de eventos: N/A"
)

print(
    "Se debe evaluar su vigencia/versionamiento."
)


resultado_div = {

    "Fuente":
        "DIVIPOLA",

    "Último dato":
        "Vigente 2025",

    "Fecha descarga":
        FECHAS_DESCARGA[
            "DIVIPOLA"
        ].strftime(
            "%Y-%m-%d"
        ),

    "Rezago meses":
        "N/A"

}


# ============================================================
# RESUMEN
# ============================================================

resultados = [

    resultado_hom,

    resultado_sec,

    resultado_ext,

    resultado_ter,

    resultado_coca,

    resultado_div

]


resumen = pd.DataFrame(
    resultados
)


print("\n")
print("=" * 90)
print("RESUMEN DE OPORTUNIDAD")
print("=" * 90)

print(
    resumen.to_string(
        index=False
    )
)


# ============================================================
# EXPORTAR
# ============================================================

salida = os.path.join(

    BASE,

    "auditoria_oportunidad_rezago.xlsx"

)


resumen.to_excel(

    salida,

    index=False

)


print("\n")
print("=" * 90)
print("ARCHIVO GENERADO")
print("=" * 90)

print(salida)