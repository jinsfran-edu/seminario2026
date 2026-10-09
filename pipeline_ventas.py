"""
Pipeline ETL de cumplimiento comercial — ejecutable desde la línea de comandos.

Seminario de Actualización - Unidad 5
Tecnicatura Superior en Análisis de Sistemas

Es la misma lógica del notebook Unidad05_04_Pipeline_ETL.ipynb, empaquetada como un
script: es la forma en que un pipeline se programa realmente, con el Programador
de tareas de Windows, cron, o un job del Agente SQL Server.

Combina dos orígenes:

    1. La vista ValoresPedido de Pampero, unida a Clientes para tener el país.
       ValoresPedido tiene IDPedido, IDCliente, IDEmpleado, EnvioPor,
       FechaPedido, FechaRequerida, FechaEnvio, cantidad y val. NO tiene Region,
       Pais, IDProducto ni Descuento: esas columnas están en otras tablas.

    2. metas_empleado.csv, la planilla de metas mensuales que el área comercial
       mantiene fuera de la base. Se combina por IDEmpleado, Anio y Mes.

El resultado es el cumplimiento mensual de meta por empleado.

Uso:

    python pipeline_ventas.py
    python pipeline_ventas.py --tabla-destino CumplimientoMensual --carpeta datos
    python pipeline_ventas.py --simulacion      # no escribe en la base

Códigos de salida:

    0  el pipeline terminó correctamente
    1  el pipeline falló (la traza queda en el log)

Ese código de salida es lo que permite que el programador de tareas detecte la
falla: por eso el manejo de errores registra la excepción y la vuelve a lanzar,
en lugar de silenciarla.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

import config_conexion
import datos_demo

log = logging.getLogger("pipeline_ventas")

TABLA_DESTINO_POR_DEFECTO = "CumplimientoMensualU05"

CONSULTA_PEDIDOS = """
    SELECT v.IDPedido, v.IDCliente, v.IDEmpleado, v.EnvioPor,
           v.FechaPedido, v.FechaRequerida, v.FechaEnvio,
           v.cantidad, v.val,
           c.NombreEmpresa, c.Ciudad, c.Region, c.Pais
    FROM ValoresPedido AS v
      JOIN Clientes AS c
        ON c.IDCliente = v.IDCliente
"""

EQUIVALENCIAS_PAIS = {
    "EEUU": "EE.UU.",
    "ESTADOS UNIDOS": "EE.UU.",
    "REINO  UNIDO": "REINO UNIDO",
}


# ---------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------
def extraer_pedidos(engine, carpeta: Path) -> pd.DataFrame:
    """Origen 1: ValoresPedido unida a Clientes, o su respaldo en CSV."""
    if engine is not None:
        log.info("Extrayendo pedidos desde SQL Server")
        return pd.read_sql(CONSULTA_PEDIDOS, engine)

    log.warning("SQL Server no disponible: se leen los pedidos desde los CSV de respaldo")
    pedidos = pd.read_csv(carpeta / "valores_pedido.csv", encoding="utf-8")
    clientes = pd.read_csv(carpeta / "clientes.csv", encoding="utf-8")
    return pedidos.merge(
        clientes[["IDCliente", "NombreEmpresa", "Ciudad", "Region", "Pais"]],
        on="IDCliente", how="inner")


def extraer_metas(carpeta: Path) -> pd.DataFrame:
    """Origen 2: las metas mensuales por empleado, mantenidas fuera de la base."""
    ruta = carpeta / "metas_empleado.csv"
    log.info("Extrayendo metas comerciales desde %s", ruta)
    return pd.read_csv(ruta, encoding="utf-8")


# ---------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------
def transformar(pedidos: pd.DataFrame, metas: pd.DataFrame) -> pd.DataFrame:
    """Limpia, agrega por empleado y mes, y combina con las metas."""
    log.info("Transformando %d filas de pedidos", len(pedidos))

    pedidos = pedidos.copy()
    pedidos["FechaPedido"] = pd.to_datetime(pedidos["FechaPedido"], errors="coerce")
    pedidos["FechaEnvio"] = pd.to_datetime(pedidos["FechaEnvio"], errors="coerce")
    pedidos["val"] = pd.to_numeric(pedidos["val"], errors="coerce")

    antes = len(pedidos)
    pedidos = pedidos.drop_duplicates(subset=["IDPedido"], keep="first")
    log.info("Duplicados eliminados: %d", antes - len(pedidos))

    pedidos = pedidos.dropna(subset=["IDCliente", "val", "FechaPedido"])

    pedidos["Pais"] = (pedidos["Pais"].str.strip().str.upper()
                       .replace(EQUIVALENCIAS_PAIS))

    antes = len(pedidos)
    pedidos = pedidos[(pedidos["val"] > 0) &
                      (pedidos["FechaPedido"] <= pd.Timestamp.today())]
    log.info("Filas descartadas por reglas de negocio: %d", antes - len(pedidos))

    # El grano de las metas es empleado-mes: hay que agregar antes de combinar.
    pedidos["Anio"] = pedidos["FechaPedido"].dt.year
    pedidos["Mes"] = pedidos["FechaPedido"].dt.month
    mensual = (pedidos.groupby(["IDEmpleado", "Anio", "Mes"], as_index=False)
                      .agg(Pedidos=("IDPedido", "count"),
                           Unidades=("cantidad", "sum"),
                           Ventas=("val", "sum")))
    mensual["Ventas"] = mensual["Ventas"].round(2)

    resultado = mensual.merge(metas, on=["IDEmpleado", "Anio", "Mes"], how="left")

    sin_meta = int(resultado["MetaMensual"].isna().sum())
    if sin_meta:
        log.warning("%d meses sin meta cargada", sin_meta)

    resultado["CumplimientoMeta"] = (
        resultado["Ventas"] / resultado["MetaMensual"]).round(3)
    resultado["TicketPromedio"] = (
        resultado["Ventas"] / resultado["Pedidos"]).round(2)

    log.info("Transformación finalizada: %d filas resultantes", len(resultado))
    return resultado


# ---------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------
def cargar(datos: pd.DataFrame, engine, tabla: str, carpeta: Path,
           simulacion: bool = False) -> None:
    """Carga idempotente: reemplazo completo de la tabla destino.

    Ejecutar el pipeline dos veces produce exactamente el mismo resultado, que es
    la condición para poder programarlo sin supervisión.
    """
    if simulacion:
        log.info("[simulación] Se habrían cargado %d filas en %s", len(datos), tabla)
        return

    if engine is not None:
        log.info("Cargando %d filas en %s", len(datos), tabla)
        datos.to_sql(tabla, engine, if_exists="replace", index=False, chunksize=1000)
        return

    salida = carpeta / f"{tabla}.csv"
    log.warning("Sin servidor: el resultado se escribe en %s", salida)
    datos.to_csv(salida, index=False, encoding="utf-8")


# ---------------------------------------------------------------------
# Orquestación
# ---------------------------------------------------------------------
def ejecutar_pipeline(tabla: str, carpeta: Path, simulacion: bool = False) -> pd.DataFrame:
    """Ejecuta las tres etapas en orden. Registra y relanza cualquier excepción."""
    try:
        log.info("=== Inicio del pipeline ===")

        engine = config_conexion.crear_engine() if config_conexion.probar_conexion() else None
        if engine is None:
            carpeta.mkdir(parents=True, exist_ok=True)
            if not (carpeta / "valores_pedido.csv").exists():
                log.info("Generando datos de respaldo en %s", carpeta)
                datos_demo.escribir_csv(carpeta)

        pedidos = extraer_pedidos(engine, carpeta)
        metas = extraer_metas(carpeta)
        resultado = transformar(pedidos, metas)
        cargar(resultado, engine, tabla, carpeta, simulacion)

        log.info("=== Pipeline finalizado correctamente: %d filas ===", len(resultado))
        return resultado

    except Exception:
        # No se silencia el error: se registra con la traza completa y se relanza,
        # para que el proceso que invocó al pipeline reciba un código distinto de cero.
        log.exception("El pipeline falló")
        raise


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pipeline ETL de cumplimiento comercial (Unidad 5, clase 24)")
    parser.add_argument("--tabla-destino", default=TABLA_DESTINO_POR_DEFECTO,
                        help="Nombre de la tabla destino en SQL Server")
    parser.add_argument("--carpeta", default="datos", type=Path,
                        help="Carpeta de archivos planos de origen y respaldo")
    parser.add_argument("--simulacion", action="store_true",
                        help="Ejecuta todo el proceso sin escribir el resultado")
    parser.add_argument("--verboso", action="store_true",
                        help="Muestra también los mensajes de nivel DEBUG")
    return parser.parse_args()


def main() -> int:
    args = parsear_argumentos()

    logging.basicConfig(
        level=logging.DEBUG if args.verboso else logging.INFO,
        format="%(asctime)s  %(levelname)-8s %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        ejecutar_pipeline(args.tabla_destino, args.carpeta, args.simulacion)
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
