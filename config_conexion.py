"""
Conexión al SQL Server del laboratorio.

Seminario de Actualización - Unidad 5
Tecnicatura Superior en Análisis de Sistemas

Centraliza la configuración de conexión para que los notebooks no repitan la
cadena en cada archivo y, sobre todo, para que ninguna credencial quede escrita
dentro del código.

Soporta los dos controladores que presenta el apunte:

    pyodbc          dialecto mssql+pyodbc       (por defecto)
                    Requiere el ODBC Driver 18 for SQL Server instalado en el
                    sistema operativo, además del paquete de Python.

    mssql-python    dialecto mssql+mssqlpython
                    Controlador oficial de Microsoft, DB-API 2.0 sobre Direct
                    Database Connectivity (DDBC): no depende de un administrador
                    ODBC externo. Requiere Python 3.10 o posterior y, para usarlo
                    con SQLAlchemy, la serie preliminar 2.1 (>= 2.1.0b2).

Se usa pyodbc por defecto porque SQLAlchemy 2.1 todavía es una serie preliminar.
Para probar el controlador nuevo alcanza con definir U05_CONTROLADOR=mssqlpython.

Configuración por variables de entorno (todas opcionales):

    U05_SERVIDOR      nombre o dirección del servidor   (por defecto: localhost)
    U05_BASE          nombre de la base de datos        (por defecto: Pampero)
    U05_CONTROLADOR   pyodbc | mssqlpython              (por defecto: pyodbc)
    U05_DRIVER        controlador ODBC, solo con pyodbc (por defecto: ODBC Driver 18 for SQL Server)
    U05_USUARIO       usuario de SQL Server             (opcional)
    U05_CLAVE         contraseña de SQL Server          (opcional)

Cómo definirlas:

    PowerShell (solo para la sesión actual)
        $env:U05_SERVIDOR    = "localhost\\SQLEXPRESS"
        $env:U05_CONTROLADOR = "mssqlpython"

    CMD
        set U05_SERVIDOR=localhost\\SQLEXPRESS

    Linux / macOS
        export U05_SERVIDOR=localhost

Si no se define U05_USUARIO se utiliza autenticación integrada de Windows, que
es la opción preferible: no hay contraseña que administrar ni que filtrar.

Recordatorio de la Unidad 4: las credenciales nunca van escritas en el código
fuente. Autenticación integrada cuando se pueda; variables de entorno o un
gestor de secretos cuando no.
"""

import os
from urllib.parse import quote_plus

SERVIDOR = os.getenv("U05_SERVIDOR", "localhost")
BASE = os.getenv("U05_BASE", "Pampero")
CONTROLADOR = os.getenv("U05_CONTROLADOR", "pyodbc").lower()
DRIVER = os.getenv("U05_DRIVER", "ODBC Driver 18 for SQL Server")
USUARIO = os.getenv("U05_USUARIO")
CLAVE = os.getenv("U05_CLAVE")

CONTROLADORES_VALIDOS = {"pyodbc", "mssqlpython"}


def controladores_disponibles() -> dict[str, bool]:
    """Informa qué controladores están instalados en este entorno."""
    disponibles = {}
    for modulo, nombre in (("pyodbc", "pyodbc"), ("mssql_python", "mssqlpython")):
        try:
            __import__(modulo)
            disponibles[nombre] = True
        except ImportError:
            disponibles[nombre] = False
    return disponibles


def controlador_efectivo() -> str:
    """Devuelve el controlador que se va a usar realmente.

    Respeta U05_CONTROLADOR si ese controlador está instalado. Si no lo está,
    cae al otro antes que fallar, e informa el cambio.
    """
    if CONTROLADOR not in CONTROLADORES_VALIDOS:
        raise ValueError(
            f"U05_CONTROLADOR={CONTROLADOR!r} no es válido. "
            f"Valores admitidos: {sorted(CONTROLADORES_VALIDOS)}"
        )

    disponibles = controladores_disponibles()
    if disponibles.get(CONTROLADOR):
        return CONTROLADOR

    alternativa = "mssqlpython" if CONTROLADOR == "pyodbc" else "pyodbc"
    if disponibles.get(alternativa):
        print(f"Aviso: {CONTROLADOR} no está instalado; se usa {alternativa} en su lugar.")
        return alternativa

    return CONTROLADOR  # ninguno instalado: que falle con un mensaje claro


def cadena_conexion(controlador: str | None = None) -> str:
    """Devuelve la URL de conexión de SQLAlchemy para el laboratorio.

    Encrypt=yes es el valor por defecto desde el ODBC Driver 18.
    TrustServerCertificate=yes se agrega porque el servidor del laboratorio usa
    un certificado autofirmado; en un entorno productivo NO debe usarse, porque
    desactiva la validación del certificado del servidor.
    """
    controlador = (controlador or controlador_efectivo()).lower()

    if controlador == "mssqlpython":
        opciones = "encrypt=yes&TrustServerCertificate=yes"
        if USUARIO:
            usuario, clave = quote_plus(USUARIO), quote_plus(CLAVE or "")
            return f"mssql+mssqlpython://{usuario}:{clave}@{SERVIDOR}:1433/{BASE}?{opciones}"
        return f"mssql+mssqlpython://@{SERVIDOR}:1433/{BASE}?trusted_connection=yes&{opciones}"

    # pyodbc
    opciones = f"driver={quote_plus(DRIVER)}&Encrypt=yes&TrustServerCertificate=yes"
    if USUARIO:
        usuario, clave = quote_plus(USUARIO), quote_plus(CLAVE or "")
        return f"mssql+pyodbc://{usuario}:{clave}@{SERVIDOR}/{BASE}?{opciones}"
    return f"mssql+pyodbc://@{SERVIDOR}/{BASE}?{opciones}&trusted_connection=yes"


def crear_engine(echo: bool = False):
    """Crea el engine de SQLAlchemy. Lanza ImportError si faltan dependencias.

    fast_executemany es una optimización específica de pyodbc: acelera to_sql
    agrupando los parámetros por lotes. Con mssql-python no corresponde.
    """
    from sqlalchemy import create_engine

    controlador = controlador_efectivo()
    parametros = {"echo": echo}
    if controlador == "pyodbc":
        parametros["fast_executemany"] = True

    return create_engine(cadena_conexion(controlador), **parametros)


def probar_conexion() -> bool:
    """Devuelve True si se puede abrir una conexión y ejecutar SELECT 1.

    No lanza excepción: está pensada para que los notebooks decidan si trabajan
    contra el servidor real o contra los datos sintéticos de datos_demo.py.
    """
    try:
        from sqlalchemy import text

        engine = crear_engine()
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        return True
    except Exception as error:  # noqa: BLE001 - queremos capturar cualquier fallo
        print(f"No se pudo conectar a SQL Server: {type(error).__name__}: {error}")
        return False


def resumen() -> None:
    """Imprime la configuración vigente, sin exponer la contraseña."""
    disponibles = controladores_disponibles()
    print("Configuración de conexión")
    print(f"  servidor              : {SERVIDOR}")
    print(f"  base                  : {BASE}")
    print(f"  controlador pedido    : {CONTROLADOR}")
    print(f"  controlador efectivo  : {controlador_efectivo()}")
    print(f"  autenticación         : "
          f"{'SQL Server (' + USUARIO + ')' if USUARIO else 'Integrada de Windows'}")
    print("  instalados            : " +
          ", ".join(f"{k}={'sí' if v else 'no'}" for k, v in disponibles.items()))
    if disponibles.get("pyodbc"):
        import pyodbc
        print(f"  controladores ODBC    : {pyodbc.drivers()}")


if __name__ == "__main__":
    resumen()
    print()
    print("Conexión OK" if probar_conexion() else "Conexión fallida")
