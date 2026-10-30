# Unidad 6

## Bases de datos No Relacionales (NoSQL) y Bases de Datos para IA
Las cinco unidades anteriores trabajaron sobre un mismo supuesto: los datos viven en tablas, se consultan con SQL y se protegen con las garantías transaccionales de un motor relacional como SQL Server. Ese modelo sigue siendo el corazón de la mayoría de los sistemas de gestión, pero no es el único. Desde mediados de la década de 2000, el crecimiento de las aplicaciones web, las redes sociales y los dispositivos conectados impulsó una familia de motores que guardan los datos de otra manera: como documentos, pares clave-valor, familias de columnas o grafos. A ese conjunto se lo conoce como NoSQL.
La segunda mitad de la unidad avanza sobre una necesidad todavía más reciente. Los modelos de lenguaje (Large Language Models, LLM) no buscan coincidencias de texto sino significado, y para eso necesitan representar la información como vectores numéricos. Las bases de datos vectoriales, los embeddings y las arquitecturas RAG (Retrieval Augmented Generation) son la respuesta del mundo de las bases de datos a esa necesidad. SQL Server 2025, el motor que usamos en el laboratorio, incorpora por primera vez un tipo de dato y funciones específicas para trabajar con vectores.
El objetivo de la unidad no es reemplazar el modelo relacional, sino ampliar el criterio: saber qué modelo de datos conviene para cada problema y cómo una base de datos puede convertirse en la memoria confiable de una aplicación de Inteligencia Artificial.

### Big Data: el contexto que dio origen a NoSQL
Meier y Kaufmann definen Big Data como volúmenes de datos que superan los límites del software convencional. No hay una definición única, pero existe consenso en caracterizarlo con tres V, a las que suelen sumarse dos más:
- Dimensión: Volumen; Qué describe: Cantidades de datos que van de terabytes a zettabytes.; Ejemplo: Registros de navegación de un sitio de comercio electrónico.
- Dimensión: Variedad; Qué describe: Datos estructurados, semiestructurados y no estructurados: texto, imágenes, audio, video.; Ejemplo: Publicaciones en redes sociales con fotos, etiquetas y comentarios.
- Dimensión: Velocidad; Qué describe: Flujos de datos que deben procesarse en tiempo real, a medida que llegan.; Ejemplo: Lecturas de sensores de tránsito o de medidores inteligentes.
- Dimensión: Valor; Qué describe: El dato como activo: se invierte donde genera beneficio para la organización.; Ejemplo: Recomendaciones de productos que aumentan las ventas.
- Dimensión: Veracidad; Qué describe: Mucha información es imprecisa; más datos no significa mejores análisis.; Ejemplo: Reseñas falsas o duplicadas en un sitio de opiniones.
Las cinco dimensiones se relacionan directamente con lo trabajado en la Unidad 5: la etapa de perfilado y calidad de datos es, en esencia, una respuesta al problema de la veracidad.

### Las limitaciones del modelo relacional
Sadalage y Fowler (NoSQL Distilled) identifican dos tensiones que empujaron a buscar alternativas al modelo relacional.
- Desajuste de impedancia: los objetos de una aplicación no coinciden con las tablas. Un pedido, con sus líneas, el cliente y la dirección de envío, es una sola unidad para el programa, pero se reparte en varias tablas normalizadas y debe volver a armarse con JOIN en cada lectura.
- Escalado: un servidor relacional escala bien hacia arriba (scale up, un equipo más potente) pero mal hacia los costados (scale out, un clúster de muchos equipos económicos). Las aplicaciones web de gran tráfico necesitan lo segundo, y repartir tablas relacionadas entre servidores rompe las garantías que hacen valioso al modelo relacional.
Ninguna de estas tensiones invalida a SQL. Señalan, en cambio, que hay problemas en los que otro modelo resulta más natural o más económico.

### Recorrido de la unidad
- Bases NoSQL: definición, modelos de datos, consistencia en sistemas distribuidos y el teorema CAP.
- Bases documentales con MongoDB: documentos, colecciones, operaciones CRUD, agregaciones, índices y modelado.
- Embeddings y búsqueda semántica: cómo se representa el significado como vectores y cómo se mide la similitud.
- Bases de datos vectoriales: índices de búsqueda aproximada y el soporte vectorial de SQL Server 2025.
- Arquitecturas RAG: cómo una base vectorial le da contexto a un modelo de lenguaje.

## Bases de datos NoSQL

### Qué es NoSQL
Meier y Kaufmann llaman NoSQL a todo enfoque no relacional de gestión de datos que cumple dos criterios: los datos no se almacenan en tablas y el lenguaje de consulta no es SQL. El término también se interpreta como Not only SQL, para remarcar que estas tecnologías conviven con las bases relacionales en lugar de reemplazarlas.
Más allá de las diferencias entre productos, un sistema NoSQL suele compartir estas características:
- Los datos se guardan como pares clave-valor, documentos, familias de columnas o grafos.
- La arquitectura es distribuida: los datos se reparten y se replican entre varios nodos.
- Las consultas pueden ejecutarse en paralelo, por ejemplo con el modelo MapReduce.
- La consistencia es configurable, de débil a fuerte, según lo que necesite la aplicación.
- El esquema es flexible: no hace falta definir la estructura antes de insertar datos.

### Modelos orientados a agregados
Sadalage y Fowler introducen un concepto que ordena todo el panorama NoSQL: el agregado. Un agregado es un conjunto de datos relacionados que la aplicación trata como una unidad: se lee entero, se modifica entero y se guarda junto. Un pedido con sus líneas y su dirección de envío es un agregado típico.
Pensar en agregados tiene una consecuencia práctica: si cada agregado se almacena completo en un mismo nodo del clúster, la base puede repartir los datos entre muchos servidores sin necesidad de reunirlos con JOIN. Tres de los cuatro modelos NoSQL están orientados a agregados; el cuarto, el de grafos, pone el foco en las relaciones.
- Modelo: Clave-valor; Unidad de dato: Un valor opaco asociado a una clave. Solo se accede por clave.; Casos de uso: Sesiones de usuario, caché, carritos de compra.; Ejemplos: Redis, Amazon DynamoDB
- Modelo: Documental; Unidad de dato: Un documento JSON o BSON con estructura anidada. Se consulta por cualquier campo.; Casos de uso: Catálogos de productos, perfiles, gestión de contenidos.; Ejemplos: MongoDB, CouchDB
- Modelo: Familia de columnas; Unidad de dato: Filas con columnas agrupadas en familias, optimizadas para escrituras masivas.; Casos de uso: Series de tiempo, registros de eventos, IoT.; Ejemplos: Apache Cassandra, HBase
- Modelo: Grafos; Unidad de dato: Nodos y aristas, ambos con propiedades.; Casos de uso: Redes sociales, recomendaciones, detección de fraude.; Ejemplos: Neo4j

### Consistencia en sistemas distribuidos: ACID y BASE
En la Unidad 2 vimos que una transacción relacional cumple las propiedades ACID: atomicidad, consistencia, aislamiento y durabilidad. Garantizar ACID en un único servidor es relativamente sencillo; garantizarlo entre decenas de servidores replicados, separados por una red que puede fallar, es costoso y reduce la disponibilidad.
Por eso muchos sistemas distribuidos adoptan un criterio más flexible, conocido como BASE: Basically Available, Soft state, Eventually consistent. El sistema prioriza seguir respondiendo, acepta que las réplicas tengan por un tiempo versiones distintas del mismo dato y garantiza que, si no hay nuevas escrituras, todas terminarán convergiendo al mismo valor (consistencia eventual).
- Aspecto: Prioridad; ACID: Consistencia; BASE: Disponibilidad
- Aspecto: Transacciones; ACID: Estrictas, con bloqueos o control optimista; BASE: Relajadas, con versiones múltiples
- Aspecto: Escalado; ACID: Principalmente vertical; BASE: Horizontal
- Aspecto: Lectura después de escribir; ACID: Siempre ve el último valor; BASE: Puede ver un valor anterior por un tiempo
- Aspecto: Uso típico; ACID: Finanzas, inventario, facturación; BASE: Redes sociales, catálogos, registros

### El teorema CAP
En el año 2000, Eric Brewer planteó que un sistema distribuido masivo no puede garantizar al mismo tiempo tres propiedades. La conjetura fue demostrada en 2002 por Gilbert y Lynch, del MIT, y se conoce como teorema CAP:
- Consistencia (C): toda lectura obtiene el último valor escrito, sin importar a qué nodo se consulte.
- Disponibilidad (A, availability): el sistema responde siempre, en un tiempo aceptable.
- Tolerancia a particiones (P): el sistema sigue funcionando aunque fallen nodos o se corte la comunicación entre ellos.
Solo dos de las tres pueden asegurarse simultáneamente. Meier y Kaufmann ilustran las tres combinaciones posibles con ejemplos concretos:
- Combinación: CA; Ejemplo: Bolsa de valores; Justificación: Requiere datos exactos y respuesta inmediata; se resuelve con bases relacionales ACID.
- Combinación: CP; Ejemplo: Red nacional de cajeros automáticos; Justificación: Prefiere demorar una operación antes que mostrar un saldo incorrecto.
- Combinación: AP; Ejemplo: DNS (sistema de nombres de dominio); Justificación: Debe estar siempre disponible; un cambio puede tardar en propagarse.
En la práctica, las particiones de red ocurren y no pueden evitarse en un sistema distribuido. La decisión real, entonces, es qué hacer cuando ocurren: priorizar la consistencia (y dejar de responder algunas consultas) o priorizar la disponibilidad (y aceptar datos momentáneamente desactualizados).

### Consistencia ajustable: el quórum
Muchos motores NoSQL permiten ajustar la consistencia operación por operación. Meier y Kaufmann lo explican con tres parámetros:
- N: cantidad de réplicas de cada dato.
- W: cantidad de réplicas que deben confirmar una escritura para considerarla exitosa.
- R: cantidad de réplicas que se leen para responder una consulta.
Si W + R > N, toda lectura toca al menos una réplica que tiene la última escritura: hay consistencia por quórum. Si W + R ≤ N, la consistencia es eventual. Por ejemplo, con N = 3, escribir en 2 réplicas y leer de 2 garantiza consistencia (2 + 2 > 3); escribir en 1 y leer de 1 es más rápido, pero puede devolver un valor viejo.
Regla general de esta sección: NoSQL no es "mejor" ni "peor" que SQL. Cada modelo resuelve un problema distinto, y una misma aplicación puede combinar varios motores, cada uno para lo que mejor hace. Sadalage y Fowler llaman a esto persistencia políglota.

#### Ejercicios
- Para cada uno de los cuatro modelos NoSQL, proponer un caso de uso distinto de los mencionados en el apunte y justificar la elección.
- Un sistema de reservas de hoteles con sucursales en varios países, ¿debería priorizar CP o AP? Justificar en términos del teorema CAP.
- Con N = 5 réplicas, indicar tres combinaciones de W y R que garanticen consistencia y una que no lo haga.

## Bases documentales: MongoDB
Una base documental es, en su primer nivel, un almacén clave-valor: cada documento se identifica por una clave. La diferencia es que el valor no es opaco, sino que tiene estructura propia, formada por pares atributo-valor que pueden anidarse (Meier y Kaufmann). Esa estructura permite consultar por cualquier campo, crear índices y agregar datos, algo que un almacén clave-valor puro no ofrece. MongoDB es el motor documental más difundido y el que usamos en la práctica de la clase 28.

### Documentos, colecciones y BSON
La terminología de MongoDB tiene un equivalente directo en el modelo relacional:
- SQL Server: Base de datos; MongoDB: Base de datos; Observación: Contenedor lógico.
- SQL Server: Tabla; MongoDB: Colección; Observación: No exige que todos los documentos tengan los mismos campos.
- SQL Server: Fila; MongoDB: Documento; Observación: Puede contener subdocumentos y arrays.
- SQL Server: Columna; MongoDB: Campo; Observación: Se define al insertar, no antes.
- SQL Server: Clave primaria; MongoDB: Campo _id; Observación: Si no se indica, MongoDB genera un ObjectId.
- SQL Server: JOIN; MongoDB: Documento embebido o $lookup; Observación: Se prefiere embeber lo que se lee junto.
- SQL Server: GROUP BY; MongoDB: Framework de agregación ($group); Observación: Ver la sección de agregación.
Un documento se escribe en notación JSON y se almacena en BSON (JSON binario), un formato que agrega tipos que JSON no tiene: fechas, enteros de 32 y 64 bits, decimales de alta precisión (Decimal128) y el identificador ObjectId (Sarasa, cap. II). El tamaño máximo de un documento es de 16 MB.
El documento reúne en una sola estructura lo que en SQL Server requeriría al menos tres tablas: alumnos, materias cursadas y domicilios. Otro alumno de la misma colección podría no tener el campo materias o tener un campo becado que este no tiene: el esquema es flexible y la responsabilidad de mantener la estructura pasa a la aplicación.

### La shell de MongoDB
La forma más directa de trabajar con MongoDB es mongosh, una consola interactiva basada en JavaScript. Allí, db representa la base de datos activa y cada colección se accede como una propiedad: db.alumnos. El cliente gráfico MongoDB Compass ofrece las mismas operaciones con una interfaz visual, y la extensión de MongoDB para Visual Studio Code permite ejecutar scripts desde el mismo editor que usamos en la Unidad 5. Las instrucciones de instalación están en el Anexo.

### Operaciones CRUD: inserción

Si la colección no existe, MongoDB la crea con la primera inserción. Con ordered: true (valor por defecto), insertMany se detiene ante el primer error; con ordered: false, continúa con los documentos restantes.

### Operaciones CRUD: consulta

El primer argumento de find() es un documento de filtro, equivalente a la cláusula WHERE; el segundo, opcional, es la proyección, equivalente a la lista de columnas del SELECT. Los métodos sort, skip y limit cumplen el papel de ORDER BY y de OFFSET-FETCH, vistos en la Unidad 1.
Los operadores de consulta comienzan con el signo $ y tienen un equivalente directo en SQL (Sarasa, cap. IV):
- Operador MongoDB: $eq, $ne; Equivalente SQL: =, <>; Ejemplo: { carrera: { $ne: "Contador" } }
- Operador MongoDB: $gt, $gte, $lt, $lte; Equivalente SQL: >, >=, <, <=; Ejemplo: { edad: { $gte: 18 } }
- Operador MongoDB: $in, $nin; Equivalente SQL: IN, NOT IN; Ejemplo: { codigo: { $in: ["SEM", "BD2"] } }
- Operador MongoDB: $and, $or, $not; Equivalente SQL: AND, OR, NOT; Ejemplo: { $or: [ {...}, {...} ] }
- Operador MongoDB: $exists; Equivalente SQL: IS NOT NULL (aproximado); Ejemplo: { becada: { $exists: true } }
- Operador MongoDB: $regex; Equivalente SQL: LIKE; Ejemplo: { apellido: { $regex: "^P" } }

### Operaciones CRUD: actualización

La actualización se expresa con modificadores, que indican qué cambiar sin reemplazar el documento completo:
- Modificador: $set; Efecto: Asigna un valor a un campo; lo crea si no existe.; Equivalente aproximado en SQL: SET campo = valor
- Modificador: $unset; Efecto: Elimina un campo del documento.; Equivalente aproximado en SQL: SET campo = NULL
- Modificador: $inc; Efecto: Suma un valor numérico.; Equivalente aproximado en SQL: SET campo = campo + n
- Modificador: $push; Efecto: Agrega un elemento a un array.; Equivalente aproximado en SQL: INSERT en la tabla hija
- Modificador: $pull; Efecto: Quita de un array los elementos que cumplen una condición.; Equivalente aproximado en SQL: DELETE en la tabla hija
- Modificador: $addToSet; Efecto: Agrega un elemento al array solo si no existe.; Equivalente aproximado en SQL: INSERT ... WHERE NOT EXISTS
La opción upsert: true combina actualización e inserción: si ningún documento cumple el filtro, se inserta uno nuevo (Sarasa, cap. III). Cumple un papel similar a la sentencia MERGE de T-SQL.

### Operaciones CRUD: borrado

### El framework de agregación
Para agrupar, calcular y transformar datos, MongoDB ofrece el framework de agregación: una tubería (pipeline) de etapas en la que cada una recibe los documentos que produjo la anterior (Sarasa, cap. V). El concepto es muy similar al encadenamiento de operaciones de pandas visto en la Unidad 5.

- Etapa: $match; Equivalente SQL: WHERE / HAVING; Función: Filtra documentos.
- Etapa: $project; Equivalente SQL: SELECT; Función: Elige, renombra o calcula campos.
- Etapa: $group; Equivalente SQL: GROUP BY; Función: Agrupa y calcula acumuladores: $sum, $avg, $min, $max, $count.
- Etapa: $sort; Equivalente SQL: ORDER BY; Función: Ordena los resultados.
- Etapa: $limit, $skip; Equivalente SQL: TOP, OFFSET-FETCH; Función: Pagina los resultados.
- Etapa: $unwind; Equivalente SQL: Sin equivalente directo; Función: Genera un documento por cada elemento de un array.
- Etapa: $lookup; Equivalente SQL: LEFT OUTER JOIN; Función: Trae documentos relacionados de otra colección.
La consulta equivalente en T-SQL, sobre un modelo relacional con una tabla MateriasCursadas, sería:

### Índices
Sin índices, MongoDB debe recorrer todos los documentos de la colección (collection scan), igual que un table scan en SQL Server. Los índices se crean sobre uno o varios campos, incluso sobre campos de subdocumentos y elementos de arrays, y el método explain() muestra el plan de ejecución (Sarasa, caps. VI y IX).

### Modelado: embeber o referenciar
En el modelo relacional se diseña a partir de la normalización. En MongoDB se diseña a partir de cómo la aplicación lee los datos. La decisión central es si los datos relacionados se guardan dentro del documento (embebidos) o en otra colección, guardando solo su _id (referenciados).
- Criterio: Tipo de relación; Embeber: Uno a pocos, del tipo "pertenece a".; Referenciar: Uno a muchos grandes o muchos a muchos.
- Criterio: Lectura; Embeber: Una sola consulta trae todo.; Referenciar: Requiere $lookup o una segunda consulta.
- Criterio: Actualización; Embeber: Si el dato se repite en muchos documentos, hay que actualizarlo en todos.; Referenciar: Se actualiza en un solo lugar.
- Criterio: Límite; Embeber: El documento no puede superar los 16 MB.; Referenciar: Sin límite práctico.
- Criterio: Ejemplo; Embeber: Domicilio de un alumno, líneas de un pedido.; Referenciar: Alumnos y cursos, autores y libros.

### Replicación y sharding
MongoDB implementa las dos estrategias de distribución descriptas por Sadalage y Fowler:
- Replicación (replica set): un nodo primario recibe todas las escrituras y los nodos secundarios copian sus operaciones. Si el primario falla, los secundarios eligen uno nuevo automáticamente (Sarasa, cap. VII).
- Fragmentación (sharding): una colección se reparte entre varios servidores según una clave de sharding*. Una buena clave distribuye la carga en forma pareja; una mala concentra todas las escrituras en un único servidor (Sarasa, cap. VIII).

### MongoDB desde Python
La integración con Python sigue la misma lógica que la conexión con SQL Server de la Unidad 5. El controlador oficial es pymongo, y los resultados pueden llevarse directamente a un DataFrame de pandas.
Regla general de esta sección: en una base documental se modela para la consulta. Si dos datos se leen siempre juntos, conviene embeberlos; si se actualizan por separado o crecen sin límite, conviene referenciarlos. MongoDB admite transacciones multidocumento, pero su modelo rinde mejor cuando cada operación toca un solo documento.

#### Ejercicios
- Crear la base instituto y la colección alumnos con al menos 10 documentos; algunos con el array materias y otros sin él.
- Listar los alumnos de una carrera mostrando solo nombre y legajo, ordenados por apellido.
- Escribir en MongoDB el equivalente de: SELECT nombre FROM alumnos WHERE edad > 21 ORDER BY nombre.
- Agregar una materia a un alumno con $push y subir 1 punto todas las notas de una materia con updateMany.
- Calcular el promedio por materia con aggregate y comparar el resultado con la consulta equivalente en T-SQL.
- Crear un índice único por legajo y comparar la salida de explain() antes y después.

## Embeddings y búsqueda semántica
Hasta ahora, todas las búsquedas de texto del seminario se basaron en coincidencias literales: el operador LIKE de la Unidad 1, los filtros de pandas o el operador $regex de MongoDB. Ese enfoque falla cuando dos textos dicen lo mismo con palabras distintas. La frase "el estudiante pasó el examen" no contiene la palabra "aprobó", pero significa lo mismo que "el alumno aprobó el parcial". Los embeddings permiten buscar por significado.

### Del texto al vector
Un embedding es un vector de números reales que representa el significado de un contenido (un texto, una imagen, un audio), de modo que contenidos parecidos quedan ubicados cerca en el espacio vectorial. Lo genera un modelo de embeddings, una red neuronal entrenada con grandes volúmenes de datos.
Cada modelo produce vectores de una dimensión fija, que suele ir de 384 a 3072 valores. Ninguna dimensión tiene un significado legible por sí sola: lo que importa es la posición relativa de los vectores. Algunos modelos habituales son text-embedding-3-small (OpenAI, 1536 dimensiones), nomic-embed-text (abierto, 768 dimensiones, se ejecuta localmente con Ollama) y all-MiniLM-L6-v2 (abierto, 384 dimensiones, disponible en la biblioteca sentence-transformers de Python).
Un vector generado con un modelo no es comparable con un vector generado con otro, aunque tengan la misma dimensión. Documentos y consultas deben vectorizarse siempre con el mismo modelo; si se cambia de modelo, hay que regenerar todos los embeddings.

### Medidas de similitud
Para decidir qué tan parecidos son dos vectores a y b se usan tres medidas. Joshi (2025) menciona la similitud coseno y la distancia euclidiana como las más habituales en las bases vectoriales.
- Similitud coseno: mide el ángulo entre los vectores, sin importar su longitud: cos(θ) = (a · b) / (‖a‖ × ‖b‖). Va de −1 (direcciones opuestas) a 1 (misma dirección). La distancia coseno es 1 − cos(θ).
- Distancia euclidiana: la distancia en línea recta entre los dos puntos: d = √Σ(aᵢ − bᵢ)².
- Producto punto: la suma de los productos componente a componente: a · b = Σ aᵢbᵢ. Si los vectores están normalizados (longitud 1), ordena los resultados igual que el coseno y es más barato de calcular.
- Medida: Coseno; Mejor resultado: Distancia cercana a 0; Cuándo se usa: Texto; es la opción por defecto en la mayoría de los casos.
- Medida: Euclidiana; Mejor resultado: Distancia cercana a 0; Cuándo se usa: Cuando la magnitud del vector tiene significado.
- Medida: Producto punto; Mejor resultado: Valor más alto; Cuándo se usa: Vectores normalizados; sistemas de recomendación.
Ejemplo. Sean a = (3, 4) y b = (4, 3). El producto punto es 3 × 4 + 4 × 3 = 24. Ambos vectores tienen longitud √(9 + 16) = 5. La similitud coseno es 24 / (5 × 5) = 0,96: los vectores apuntan casi en la misma dirección. La distancia coseno es 1 − 0,96 = 0,04.

### Búsqueda semántica
La búsqueda semántica sigue siempre los mismos cuatro pasos:
- Se generan los embeddings de todos los documentos y se guardan junto al texto original.
- Cuando llega una consulta, se genera su embedding con el mismo modelo.
- Se buscan los k vectores más cercanos al de la consulta (k-nearest neighbors, kNN).
- Se devuelven los documentos asociados, ordenados por similitud.
La búsqueda semántica no reemplaza a la búsqueda por palabras clave: cada una cubre las debilidades de la otra.
- Característica: Encuentra; Palabras clave (LIKE, full-text): Coincidencias literales; Semántica (vectores): Coincidencias de significado
- Característica: Sinónimos y paráfrasis; Palabras clave (LIKE, full-text): No; Semántica (vectores): Sí
- Característica: Códigos, legajos, siglas; Palabras clave (LIKE, full-text): Muy bien; Semántica (vectores): Mal
- Característica: Explicabilidad del resultado; Palabras clave (LIKE, full-text): Alta; Semántica (vectores): Baja
Por eso los sistemas reales suelen aplicar búsqueda híbrida: ejecutan ambas búsquedas y combinan los rankings.

### Generar embeddings desde Python
Antes de llevar los vectores a una base de datos conviene experimentar con ellos en Python. La biblioteca sentence-transformers descarga un modelo abierto y lo ejecuta localmente, sin servicios externos:
# Con vectores normalizados, el producto punto es la similitud coseno

#### Ejercicios
- Calcular a mano la similitud coseno entre (1, 0) y (1, 1).
- Ejecutar el script anterior con diez frases propias y verificar que las de significado parecido obtengan mayor similitud.
- Buscar un ejemplo en el que la búsqueda por palabras clave funcione mejor que la semántica y explicar por qué.

## Bases de datos vectoriales
Una base de datos vectorial almacena embeddings y resuelve de forma eficiente la pregunta "¿cuáles son los vectores más parecidos a este?" sobre millones de registros. Joshi (2025) destaca tres capacidades: almacenamiento de vectores de cientos o miles de dimensiones, búsqueda por similitud y escalabilidad ante grandes volúmenes de datos y de consultas.

### Por qué no alcanza con un índice tradicional
Los índices B-tree de SQL Server, estudiados en las unidades anteriores, ordenan valores en una sola dimensión. Sirven para encontrar un legajo o un rango de fechas, pero no para encontrar el punto más cercano en un espacio de 768 dimensiones. La búsqueda exacta (kNN) compara la consulta contra todos los vectores: es precisa, pero su costo crece en forma lineal con la cantidad de filas. Joshi señala esta limitación de las bases relacionales tradicionales como el origen de las bases vectoriales especializadas.

### Búsqueda aproximada e índices vectoriales
Los índices ANN (Approximate Nearest Neighbors) aceptan perder algo de precisión a cambio de responder en milisegundos. La métrica de calidad es el recall: qué proporción de los vecinos verdaderos devuelve el índice. Un recall de 0,95 significa que, de cada 100 vecinos que encontraría la búsqueda exacta, el índice devuelve 95.
- Índice: HNSW (Hierarchical Navigable Small World); Idea: Grafo de varias capas; la búsqueda va de lo general a lo particular.; Ventaja: Muy rápido y con alto recall.; Costo: Usa mucha memoria RAM.
- Índice: IVF (Inverted File); Idea: Agrupa los vectores en clusters y busca solo en los más cercanos.; Ventaja: Simple y económico.; Costo: El recall depende de cuántos clusters se revisan.
- Índice: DiskANN; Idea: Grafo optimizado para residir en disco SSD.; Ventaja: Escala a miles de millones de vectores con poca RAM.; Costo: Algo más lento que HNSW en memoria.
- Índice: PQ (Product Quantization); Idea: Comprime cada vector en códigos cortos.; Ventaja: Reduce el almacenamiento.; Costo: Pierde precisión; suele combinarse con IVF.
Como regla práctica, con pocos miles de filas la búsqueda exacta es suficiente; con cientos de miles o millones, se necesita un índice ANN.

### Panorama de soluciones
Joshi (2025) agrupa la oferta actual en cuatro familias:
- Familia: Bases vectoriales especializadas; Ejemplos: Pinecone, Qdrant, Milvus; Característica: Máximo rendimiento a gran escala; un sistema más para administrar.
- Familia: Servicios en la nube; Ejemplos: Vertex AI Vector Search, Azure Cosmos DB, Amazon Aurora; Característica: Administrados por el proveedor e integrados con sus servicios de IA.
- Familia: Soporte vectorial en plataformas existentes; Ejemplos: PostgreSQL con pgvector, AlloyDB AI, Databricks, Snowflake Cortex, SQL Server 2025; Característica: Los vectores conviven con los datos relacionales.
- Familia: Frameworks de integración; Ejemplos: LangChain, Semantic Kernel, Spring AI; Característica: Conectan bases vectoriales con modelos de lenguaje.
Una base especializada rinde más a gran escala. Una base relacional con soporte vectorial, en cambio, evita copiar los datos a otro sistema y permite combinar en una sola consulta filtros SQL, permisos y búsqueda semántica. En el seminario usamos la segunda opción, con SQL Server 2025.

### Vectores en SQL Server 2025
SQL Server 2025 incorpora el tipo de dato VECTOR y un conjunto de funciones para trabajar con él desde T-SQL. Algunas funciones (el índice vectorial, VECTOR_SEARCH y la generación de embeddings) pueden requerir habilitar las características en vista previa, según la versión instalada:

#### El tipo de dato VECTOR

El siguiente ejemplo didáctico usa vectores de solo tres dimensiones, que representan cuánto tiene cada película de acción, romance y humor. Así se puede seguir el cálculo sin necesidad de un modelo de embeddings:

#### VECTOR_DISTANCE: búsqueda exacta

El resultado devuelve Duro de matar (distancia ≈ 0,01), Rocky (≈ 0,05) y Shrek (≈ 0,34). La búsqueda puede combinarse con cualquier filtro relacional, por ejemplo WHERE Genero <> N'Romance', algo que una base vectorial especializada resuelve con mayor dificultad.

#### Funciones principales
- Función o instrucción: VECTOR(n); Qué hace: Tipo de dato de n dimensiones.
- Función o instrucción: VECTOR_DISTANCE(métrica, v1, v2); Qué hace: Distancia exacta entre dos vectores: 'cosine', 'euclidean' o 'dot'.
- Función o instrucción: VECTOR_NORM(v, tipo) / VECTOR_NORMALIZE(v, tipo); Qué hace: Longitud de un vector / vector normalizado a longitud 1.
- Función o instrucción: CREATE VECTOR INDEX; Qué hace: Crea un índice de búsqueda aproximada basado en DiskANN.
- Función o instrucción: VECTOR_SEARCH(...); Qué hace: Búsqueda aproximada que utiliza el índice vectorial.
- Función o instrucción: CREATE EXTERNAL MODEL; Qué hace: Registra un modelo de embeddings externo (Azure OpenAI, OpenAI, Ollama).
- Función o instrucción: AI_GENERATE_EMBEDDINGS(texto USE MODEL modelo); Qué hace: Genera el embedding de un texto desde T-SQL.

#### Generar embeddings con un modelo externo

#### Índice vectorial y VECTOR_SEARCH

Un embedding generado a partir de datos personales sigue siendo un dato sensible. Todo lo visto en la Unidad 4 aplica también a las columnas vectoriales: control de acceso, cifrado, enmascaramiento y gobernanza. Además, enviar texto a un servicio externo de embeddings implica sacar esos datos de la organización.

### Desafíos de las bases vectoriales
Joshi (2025) identifica un conjunto de desafíos abiertos:
- Escalabilidad y rendimiento: mantener baja latencia a medida que crecen los datos y las consultas.
- Actualización de datos: si cambian los documentos o el modelo, los embeddings quedan desactualizados y deben regenerarse.
- Integración y estandarización: cada producto expone su propia API, lo que dificulta la portabilidad.
- Seguridad y privacidad: control de acceso, cifrado y anonimización de los datos vectorizados.
- Costo: generar embeddings con servicios pagos y mantener índices en memoria tiene un costo que crece con el volumen.

#### Ejercicios
- Crear la tabla Peliculas, agregar cinco películas más con sus vectores y buscar las tres más cercanas a distintos vectores de consulta.
- Repetir la búsqueda con 'cosine' y con 'euclidean'. ¿Cambia el orden de los resultados? ¿Por qué?
- Calcular a mano la distancia coseno entre dos vectores de la tabla y verificarla con VECTOR_DISTANCE.
- Si el laboratorio tiene un modelo configurado, generar los embeddings de 20 frases y buscar por significado.

## Arquitecturas RAG
Los modelos de lenguaje generan texto de una calidad sorprendente, pero tienen tres limitaciones que los hacen poco confiables para responder sobre datos de una organización:
- Conocimiento desactualizado: solo conocen lo que vieron durante su entrenamiento, hasta una fecha de corte.
- Sin acceso a datos privados: no conocen el reglamento del instituto, los tickets de la mesa de ayuda ni las ventas de la empresa.
- Alucinaciones: cuando no saben una respuesta, pueden inventar una con apariencia convincente.
Reentrenar un modelo cada vez que cambian los datos es caro y lento. La alternativa es dejar el conocimiento en una base de datos y entregárselo al modelo en el momento de responder.

### Qué es RAG
Definición clave: Retrieval Augmented Generation (RAG)
RAG, o generación aumentada por recuperación, es una arquitectura que primero recupera de una base de datos los fragmentos de información más relevantes para una pregunta, luego aumenta el prompt del modelo con esos fragmentos y finalmente le pide que genere la respuesta usando ese contexto. Joshi (2025) la presenta como el caso de uso central de las bases vectoriales, porque fundamenta las respuestas del LLM en datos verificables.
Figura: arquitectura RAG. La fase de indexación llena la base vectorial; cada consulta la lee antes de llamar al LLM.

### Fase de indexación
La indexación se ejecuta una vez y se repite cada vez que cambian los documentos de origen:
- Carga: se extrae el texto de las fuentes (PDF, páginas web, tablas). Es la etapa de extracción del pipeline ETL de la Unidad 5.
- Fragmentación (chunking): el texto se divide en fragmentos de unos cientos de palabras, con un solapamiento de entre el 10% y el 20% para no cortar ideas a la mitad.
- Embeddings: se genera el vector de cada fragmento.
- Almacenamiento: se guardan el fragmento, su vector y sus metadatos (fuente, fecha, área, permisos).

### Fase de consulta
En cada pregunta del usuario se ejecutan cuatro pasos: se genera el embedding de la pregunta con el mismo modelo; se recuperan los k fragmentos más similares; se arma el prompt aumentado con instrucciones, contexto y pregunta; y el LLM genera la respuesta, idealmente citando los fragmentos que usó.
Las instrucciones del prompt cumplen un papel clave: pedir que el modelo responda solo con el contexto y que admita cuando no sabe reduce las alucinaciones, y pedir citas permite verificar cada afirmación.

### Implementación con SQL Server 2025 y Python
La recuperación se resuelve con la consulta vectorial de la sección anterior; la generación, con una llamada al modelo de lenguaje desde Python, reutilizando la conexión con SQLAlchemy de la Unidad 5:
Nótese que la pregunta se pasa como parámetro (:pregunta) y nunca se concatena en el texto de la consulta: es la misma defensa contra la inyección SQL que vimos en la Unidad 4. La llamada al LLM también puede hacerse desde T-SQL con el procedimiento sp_invoke_external_rest_endpoint.

### Decisiones de diseño
- Decisión: Tamaño del fragmento; Opciones: Chico (100 a 200 palabras) o grande (500 a 1000); Efecto: Chico: más preciso pero con poco contexto. Grande: más contexto pero con ruido.
- Decisión: Solapamiento; Opciones: 10% a 20% del fragmento; Efecto: Evita perder ideas que quedan en el borde.
- Decisión: Cantidad de fragmentos (k); Opciones: 3 a 10; Efecto: Pocos: puede faltar información. Muchos: más costo y más ruido.
- Decisión: Tipo de búsqueda; Opciones: Vectorial, palabras clave o híbrida; Efecto: La híbrida suele dar los mejores resultados.
- Decisión: Filtros por metadatos; Opciones: Fecha, área, permisos del usuario; Efecto: Restringen la búsqueda a lo que corresponde.
- Decisión: Re-ranking; Opciones: Un segundo modelo reordena los resultados; Efecto: Mejora la precisión a costa de latencia.

### Evaluación de un sistema RAG
Un sistema RAG se evalúa con un conjunto de preguntas de prueba cuyas respuestas y fragmentos correctos se conocen de antemano. Se miden cuatro dimensiones:
- Recuperación: ¿los fragmentos devueltos contienen la información necesaria?
- Fidelidad: ¿la respuesta se apoya solo en el contexto, o agrega afirmaciones que no estaban?
- Relevancia: ¿la respuesta contesta lo que se preguntó?
- Costo y latencia: cantidad de tokens enviados al modelo y tiempo de respuesta.

### Riesgos y buenas prácticas
- Permisos: el sistema solo debe recuperar fragmentos que el usuario tiene derecho a ver. Se resuelve filtrando por metadatos o con seguridad a nivel de fila.
- Datos personales: aplicar enmascaramiento antes de enviar contexto a un servicio externo.
- Actualización: reindexar cuando cambian las fuentes y registrar la fecha de cada fragmento.
- Inyección de prompt: un documento cargado en la base puede contener instrucciones maliciosas, como "ignorá las reglas anteriores".
Regla general de esta sección: la inyección de prompt es la inyección SQL de la era de la IA. En ambos casos, un texto que debería tratarse como dato termina interpretado como instrucción. La defensa es la misma idea vista en la Unidad 4: separar siempre las instrucciones de los datos y no confiar en el contenido recuperado.

#### Ejercicios
- Cargar en dbo.Apuntes los fragmentos de este apunte (un párrafo por fila) y generar sus embeddings.
- Escribir la consulta T-SQL que devuelve los cinco fragmentos más cercanos a una pregunta.
- Armar el prompt aumentado y enviarlo a un LLM desde Python.
- Probar una pregunta cuya respuesta no está en el apunte y verificar que el sistema responda "No lo sé".
- Variar k (3, 5 y 10) y comparar la calidad de las respuestas.
Anexo - Entorno de trabajo: MongoDB y modelos de embeddings
Antes de la clase 28 es necesario contar con un servidor de MongoDB y su consola, y antes de las clases 29 y 30, con un modelo de embeddings al que SQL Server 2025 pueda acceder. Las siguientes instrucciones usan herramientas gratuitas y se ejecutan en el equipo local. Como en la Unidad 5, se recomienda instalar las bibliotecas de Python dentro del entorno virtual del seminario.

## 1. MongoDB Community Server
Descargar e instalar MongoDB Community Server desde el sitio oficial de MongoDB. En Windows, el instalador ofrece registrarlo como servicio, de modo que el servidor queda escuchando en el puerto 27017. Como alternativa, si el equipo tiene Docker:

## 2. Clientes: mongosh, Compass y Visual Studio Code
- mongosh: la consola de comandos. Se instala por separado y se ejecuta con mongosh desde la terminal.
- MongoDB Compass: cliente gráfico para explorar colecciones, ejecutar consultas y ver planes de ejecución.
- MongoDB for VS Code: extensión que permite conectarse y ejecutar scripts desde Visual Studio Code.

## 3. Bibliotecas de Python
Con el entorno virtual activado:

## 4. Modelo de embeddings local con Ollama
Ollama permite ejecutar modelos abiertos en el equipo local y exponerlos mediante una API HTTP, a la que SQL Server 2025 puede acceder con CREATE EXTERNAL MODEL. Luego de instalar Ollama desde su sitio oficial, descargar el modelo de embeddings:
(Nota: las funciones de IA de SQL Server 2025 pueden requerir habilitar las características en vista previa y configurar el acceso a puntos de conexión externos. Verificar la configuración de la instancia del laboratorio antes de la clase 29.)
