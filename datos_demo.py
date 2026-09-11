"""
Datos sintéticos con la estructura real de la base Pampero.

Seminario de Actualización - Unidad 5
Tecnicatura Superior en Análisis de Sistemas

Reproduce el esquema de Pampero (pamperomssql.sql) para que los notebooks
funcionen igual con el servidor del laboratorio y sin él. Las columnas, los
tipos y los órdenes de magnitud son los mismos que los de la base real:

    Clientes          IDCliente CHAR(5), NombreEmpresa, Ciudad, Region, Pais
    Empleados         IDEmpleado, Apellido, Nombre, Puesto, Pais
    Categorias        IDCategoria, NombreCategoria
    Productos         IDProducto, NombreProducto, IDCategoria, PrecioUnitario,
                      Discontinuado
    Transportistas    IDTransportista, NombreEmpresa
    Pedidos           IDPedido, IDCliente, IDEmpleado, FechaPedido,
                      FechaRequerida, FechaEnvio, EnvioPor, Flete, ...
    Detalles Pedido   IDPedido, IDProducto, PrecioUnitario, Cantidad, Descuento

    ValoresPedido     VISTA derivada, con la misma fórmula que en la base:
                      IDPedido, IDCliente, IDEmpleado, EnvioPor, FechaPedido,
                      FechaRequerida, FechaEnvio, cantidad, val

Detalles del modelo real que conviene tener presentes, porque son fuente de
errores frecuentes:

  * IDCliente es texto de cinco caracteres ('ALFKI'), no un número.
  * Descuento es una FRACCIÓN entre 0 y 0,25. No es un porcentaje: el importe
    se calcula con (1 - Descuento) y nunca con (1 - Descuento/100).
  * La tabla [Detalles Pedido] tiene un espacio en el nombre y siempre debe ir
    entre corchetes en T-SQL.
  * Existe una tabla Region (territorios) y además una columna Region en
    Clientes y Empleados. No son lo mismo.
  * ValoresPedido NO tiene IDProducto, PrecioUnitario, Descuento ni Region:
    para llegar a esas columnas hay que ir a las tablas base.

La base real ya trae sus propios problemas de calidad, que se reproducen acá
porque son mejor material de clase que cualquier defecto inventado:

    1. Dos tercios de los clientes tienen Region nula.
    2. Una parte de los pedidos no tiene FechaEnvio: todavía no se despacharon.
    3. Algunos envíos salieron después de la fecha requerida.
    4. Hay clientes sin ningún pedido.
    5. El período tiene muchos días sin actividad: no es una serie continua.

A eso se suman tres defectos inyectados a propósito, que no ocurren solos y sin
los cuales no se podrían practicar los ejercicios correspondientes:

    6. Filas duplicadas, como si la extracción se hubiera ejecutado dos veces.
    7. FechaPedido llega como texto, no como fecha.
    8. El país del cliente aparece escrito de varias formas.

La semilla es fija, de modo que todos los estudiantes obtienen el mismo
conjunto y los resultados del perfilado son comparables entre sí.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026

# Magnitudes tomadas de la base real.
N_CLIENTES = 91
N_EMPLEADOS = 9
N_PRODUCTOS = 77
N_TRANSPORTISTAS = 3
N_PEDIDOS = 830

FECHA_INICIO = pd.Timestamp("2019-07-04")
FECHA_FIN = pd.Timestamp("2021-05-06")

CATEGORIAS = ["Bebidas", "Condimentos", "Dulces", "Lacteos",
              "Granos/Cereales", "Carnes", "Frutos", "Mariscos"]

PAISES = ["Alemania", "Argentina", "Australia", "Austria", "Bélgica", "Brasil",
          "Canadá", "Dinamarca", "España", "EE.UU.", "Finlandia", "Francia",
          "Irlanda", "Italia", "México", "Noruega", "Polonia", "Portugal",
          "Reino Unido", "Suecia", "Suiza"]

# Los once valores de descuento que existen realmente en Pampero.
DESCUENTOS = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.10, 0.15, 0.20, 0.25]
PESO_DESCUENTOS = [0.611, 0.005, 0.005, 0.005, 0.005, 0.108, 0.005,
                   0.066, 0.077, 0.070, 0.043]

PUESTOS = ["Representante de Ventas", "Gerente de Ventas",
           "Vicepresidente, Ventas", "Coordinador de Ventas"]


def _codigos_cliente(n: int, rng) -> list[str]:
    """Códigos de cinco letras mayúsculas, únicos, como los de Pampero."""
    letras = np.array(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
    codigos: set[str] = set()
    while len(codigos) < n:
        codigos.add("".join(rng.choice(letras, size=5)))
    return sorted(codigos)


def generar_clientes(semilla: int = SEMILLA) -> pd.DataFrame:
    """Clientes con IDCliente de texto y Region mayormente nula, como en la base."""
    rng = np.random.default_rng(semilla)
    ids = _codigos_cliente(N_CLIENTES, rng)

    df = pd.DataFrame({
        "IDCliente": ids,
        "NombreEmpresa": [f"Empresa {c}" for c in ids],
        "NombreContacto": [f"Contacto {i:03d}" for i in range(1, N_CLIENTES + 1)],
        "Ciudad": [f"Ciudad {i:02d}" for i in rng.integers(1, 70, size=N_CLIENTES)],
        "Region": rng.choice(["Norte", "Sur", "Centro", "RJ", "SP", "WA", "BC"],
                             size=N_CLIENTES),
        "Pais": rng.choice(PAISES, size=N_CLIENTES),
    })

    # Defecto real 1: dos tercios de los clientes no tienen región cargada.
    sin_region = rng.choice(N_CLIENTES, size=60, replace=False)
    df.loc[sin_region, "Region"] = None

    return df


def generar_empleados(semilla: int = SEMILLA) -> pd.DataFrame:
    rng = np.random.default_rng(semilla + 1)
    df = pd.DataFrame({
        "IDEmpleado": np.arange(1, N_EMPLEADOS + 1),
        "Apellido": [f"Apellido{i}" for i in range(1, N_EMPLEADOS + 1)],
        "Nombre": [f"Nombre{i}" for i in range(1, N_EMPLEADOS + 1)],
        "Puesto": rng.choice(PUESTOS, size=N_EMPLEADOS, p=[0.7, 0.1, 0.1, 0.1]),
        "Pais": rng.choice(["EE.UU.", "Reino Unido"], size=N_EMPLEADOS, p=[0.6, 0.4]),
        "JefeID": [None] + [2] * (N_EMPLEADOS - 1),
    })
    return df


def generar_categorias() -> pd.DataFrame:
    return pd.DataFrame({
        "IDCategoria": np.arange(1, len(CATEGORIAS) + 1),
        "NombreCategoria": CATEGORIAS,
    })


def generar_productos(semilla: int = SEMILLA) -> pd.DataFrame:
    rng = np.random.default_rng(semilla + 2)
    return pd.DataFrame({
        "IDProducto": np.arange(1, N_PRODUCTOS + 1),
        "NombreProducto": [f"Producto {i:02d}" for i in range(1, N_PRODUCTOS + 1)],
        "IDCategoria": rng.integers(1, len(CATEGORIAS) + 1, size=N_PRODUCTOS),
        # Los precios reales son asimétricos: mediana 19,50, media 28,87 y una
        # cola hasta 263,50. Una uniforme daría importes muy por encima.
        "PrecioUnitario": np.round(
            np.clip(rng.lognormal(mean=np.log(19.5), sigma=0.85, size=N_PRODUCTOS),
                    2.5, 263.5), 2),
        "Discontinuado": (rng.random(N_PRODUCTOS) < 0.10).astype(int),
    })


def generar_transportistas() -> pd.DataFrame:
    return pd.DataFrame({
        "IDTransportista": np.arange(1, N_TRANSPORTISTAS + 1),
        "NombreEmpresa": ["Transporte Rápido", "Envíos del Sur", "Logística Norte"],
    })


def generar_pedidos(clientes: pd.DataFrame, semilla: int = SEMILLA) -> pd.DataFrame:
    """Pedidos con la misma forma que en Pampero, incluida la hora en FechaPedido."""
    rng = np.random.default_rng(semilla + 3)

    dias = (FECHA_FIN - FECHA_INICIO).days
    # Defecto real 5: la actividad se concentra en días hábiles, así que la
    # serie diaria tiene muchos huecos. No se reindexa a propósito.
    offsets = rng.integers(0, dias + 1, size=N_PEDIDOS)
    fechas = FECHA_INICIO + pd.to_timedelta(offsets, unit="D")
    horas = pd.to_timedelta(rng.integers(8 * 60, 19 * 60, size=N_PEDIDOS), unit="m")
    fecha_pedido = fechas + horas

    # Defecto real 4: dos clientes se quedan sin ningún pedido.
    elegibles = clientes["IDCliente"].iloc[:-2].to_numpy()

    df = pd.DataFrame({
        "IDPedido": np.arange(10248, 10248 + N_PEDIDOS),
        "IDCliente": rng.choice(elegibles, size=N_PEDIDOS),
        "IDEmpleado": rng.integers(1, N_EMPLEADOS + 1, size=N_PEDIDOS),
        "FechaPedido": fecha_pedido,
        "EnvioPor": rng.integers(1, N_TRANSPORTISTAS + 1, size=N_PEDIDOS),
        "Flete": np.round(rng.uniform(0.5, 250.0, size=N_PEDIDOS), 2),
    })

    df["FechaRequerida"] = df["FechaPedido"].dt.normalize() + pd.Timedelta(days=28)

    # El envío sale entre 1 y 35 días después: parte queda fuera de término.
    demora = rng.integers(1, 36, size=N_PEDIDOS)
    df["FechaEnvio"] = df["FechaPedido"].dt.normalize() + pd.to_timedelta(demora, "D")

    # Defecto real 2: 21 pedidos todavía no se despacharon.
    sin_envio = rng.choice(N_PEDIDOS, size=21, replace=False)
    df.loc[sin_envio, "FechaEnvio"] = pd.NaT

    df["CiudadEnvio"] = clientes.set_index("IDCliente").loc[
        df["IDCliente"], "Ciudad"].to_numpy()
    df["RegionEnvio"] = None
    con_region = rng.choice(N_PEDIDOS, size=N_PEDIDOS - 507, replace=False)
    df.loc[con_region, "RegionEnvio"] = "Región"
    df["PaisEnvio"] = clientes.set_index("IDCliente").loc[
        df["IDCliente"], "Pais"].to_numpy()

    return df[["IDPedido", "IDCliente", "IDEmpleado", "FechaPedido",
               "FechaRequerida", "FechaEnvio", "EnvioPor", "Flete",
               "CiudadEnvio", "RegionEnvio", "PaisEnvio"]]


def generar_detalles(pedidos: pd.DataFrame, productos: pd.DataFrame,
                     semilla: int = SEMILLA) -> pd.DataFrame:
    """Detalles de pedido: entre 1 y 5 renglones por pedido, sin repetir producto."""
    rng = np.random.default_rng(semilla + 4)
    precios = productos.set_index("IDProducto")["PrecioUnitario"]

    # Distribución observada en Pampero: 2,6 renglones por pedido en promedio,
    # con moda en 2 y cola corta hasta 6.
    renglones = [1, 2, 3, 4, 5, 6]
    peso_renglones = [0.165, 0.341, 0.299, 0.151, 0.040, 0.004]

    filas = []
    for id_pedido in pedidos["IDPedido"]:
        cuantos = int(rng.choice(renglones, p=peso_renglones))
        elegidos = rng.choice(productos["IDProducto"].to_numpy(),
                              size=cuantos, replace=False)
        for id_producto in elegidos:
            filas.append({
                "IDPedido": int(id_pedido),
                "IDProducto": int(id_producto),
                "PrecioUnitario": float(precios.loc[id_producto]),
                # Cantidad real: mediana 20, media 23,8, máximo 130.
                "Cantidad": int(np.clip(
                    rng.lognormal(mean=np.log(20), sigma=0.75), 1, 130)),
                "Descuento": float(rng.choice(DESCUENTOS, p=PESO_DESCUENTOS)),
            })
    return pd.DataFrame(filas)


def calcular_valores_pedido(pedidos: pd.DataFrame,
                            detalles: pd.DataFrame) -> pd.DataFrame:
    """Reproduce la vista ValoresPedido con la misma fórmula que la base.

        SUM(Cantidad)                                    AS cantidad
        SUM(Cantidad * PrecioUnitario * (1 - Descuento)) AS val

    Nótese que Descuento es una fracción: se multiplica por (1 - Descuento) y
    nunca por (1 - Descuento/100). Y que la vista usa JOIN, de modo que un
    pedido sin renglones de detalle no aparecería.
    """
    agregado = (
        detalles.assign(
            importe=lambda d: d["Cantidad"] * d["PrecioUnitario"] * (1 - d["Descuento"]))
        .groupby("IDPedido", as_index=False)
        .agg(cantidad=("Cantidad", "sum"), val=("importe", "sum"))
    )
    agregado["val"] = agregado["val"].round(2)

    return (pedidos[["IDPedido", "IDCliente", "IDEmpleado", "EnvioPor",
                     "FechaPedido", "FechaRequerida", "FechaEnvio"]]
            .merge(agregado, on="IDPedido", how="inner"))


def _inyectar_defectos(vp: pd.DataFrame, clientes: pd.DataFrame,
                       semilla: int = SEMILLA):
    """Agrega los tres defectos que no aparecen solos en la base real."""
    rng = np.random.default_rng(semilla + 5)

    # Defecto 7: FechaPedido llega como texto.
    vp = vp.copy()
    vp["FechaPedido"] = vp["FechaPedido"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Defecto 6: la extracción se ejecutó dos veces para algunas filas.
    repetidas = vp.sample(n=40, random_state=semilla)
    vp = pd.concat([vp, repetidas], ignore_index=True)
    vp = vp.sample(frac=1, random_state=semilla).reset_index(drop=True)

    # Defecto 8: el país del cliente, escrito de varias formas.
    clientes = clientes.copy()
    equivalencias = {
        "EE.UU.": ["EE.UU.", "EEUU", "Estados Unidos", " EE.UU. ", "ee.uu."],
        "Reino Unido": ["Reino Unido", "REINO UNIDO", "Reino  Unido"],
    }
    for canonico, variantes in equivalencias.items():
        idx = clientes.index[clientes["Pais"] == canonico]
        if len(idx):
            clientes.loc[idx, "Pais"] = rng.choice(variantes, size=len(idx))

    return vp, clientes


def generar_todo(semilla: int = SEMILLA) -> dict[str, pd.DataFrame]:
    """Devuelve todas las tablas más la vista, ya con los defectos aplicados."""
    clientes = generar_clientes(semilla)
    empleados = generar_empleados(semilla)
    categorias = generar_categorias()
    productos = generar_productos(semilla)
    transportistas = generar_transportistas()
    pedidos = generar_pedidos(clientes, semilla)
    detalles = generar_detalles(pedidos, productos, semilla)

    valores_pedido = calcular_valores_pedido(pedidos, detalles)
    valores_pedido, clientes = _inyectar_defectos(valores_pedido, clientes, semilla)

    return {
        "Clientes": clientes,
        "Empleados": empleados,
        "Categorias": categorias,
        "Productos": productos,
        "Transportistas": transportistas,
        "Pedidos": pedidos,
        "Detalles Pedido": detalles,
        "ValoresPedido": valores_pedido,
    }


def generar_metas(empleados: pd.DataFrame, semilla: int = SEMILLA) -> pd.DataFrame:
    """Segundo origen del pipeline ETL: metas mensuales por empleado.

    Es información que en la vida real vive fuera de la base transaccional, en
    una planilla del área comercial. Se combina por IDEmpleado, Anio y Mes.
    """
    rng = np.random.default_rng(semilla + 6)
    periodos = pd.period_range(FECHA_INICIO, FECHA_FIN, freq="M")
    filas = []
    for emp in empleados["IDEmpleado"]:
        for per in periodos:
            filas.append({
                "IDEmpleado": int(emp),
                "Anio": per.year,
                "Mes": per.month,
                "MetaMensual": float(np.round(rng.uniform(8000, 60000), 2)),
            })
    return pd.DataFrame(filas)


def escribir_csv(carpeta: str | Path = ".") -> dict[str, Path]:
    """Escribe cada tabla como CSV. El nombre del archivo usa guion bajo."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)

    tablas = generar_todo()
    tablas["MetasEmpleado"] = generar_metas(tablas["Empleados"])

    archivos = {
        "Clientes": "clientes.csv",
        "Empleados": "empleados.csv",
        "Categorias": "categorias.csv",
        "Productos": "productos.csv",
        "Transportistas": "transportistas.csv",
        "Pedidos": "pedidos.csv",
        "Detalles Pedido": "detalles_pedido.csv",
        "ValoresPedido": "valores_pedido.csv",
        "MetasEmpleado": "metas_empleado.csv",
    }

    rutas = {}
    for nombre, df in tablas.items():
        ruta = carpeta / archivos[nombre]
        df.to_csv(ruta, index=False, encoding="utf-8")
        rutas[nombre] = ruta
    return rutas


if __name__ == "__main__":
    rutas = escribir_csv(Path(__file__).parent / "datos")
    for nombre, ruta in rutas.items():
        print(f"{nombre:18} -> {ruta.name}")

    tablas = generar_todo()
    vp = tablas["ValoresPedido"]
    print(f"\nValoresPedido: {len(vp)} filas x {vp.shape[1]} columnas")
    print(f"  columnas          : {list(vp.columns)}")
    print(f"  duplicados IDPedido: {vp.duplicated(subset=['IDPedido']).sum()}")
    print(f"  tipo de FechaPedido: {vp['FechaPedido'].dtype}")
    print(f"  val: mediana {vp['val'].median():,.2f}  máx {vp['val'].max():,.2f}")
    print(f"  FechaEnvio nula   : {vp['FechaEnvio'].isna().sum()}")

    cl = tablas["Clientes"]
    print(f"\nClientes: {len(cl)}  Region nula: {cl['Region'].isna().sum()} "
          f"({cl['Region'].isna().mean():.0%})")
    print(f"  países distintos (con variantes de escritura): {cl['Pais'].nunique()}")
    print(f"  sin pedidos: "
          f"{len(set(cl['IDCliente']) - set(tablas['Pedidos']['IDCliente']))}")

    det = tablas["Detalles Pedido"]
    print(f"\nDetalles Pedido: {len(det)} filas  "
          f"descuento máx {det['Descuento'].max()} (fracción)")
