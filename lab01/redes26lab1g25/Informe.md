# Laboratorio 1: Recomendador de videojuegos – Redes y Sistemas Distribuidos 2026 – FaMAF – UNC


## 1. Instrucciones de compilación y ejecución

### 1.1. Con Docker (recomendado)
```bash
make docker-build
make docker-run
```

Con la API corriendo, abrir **http://localhost:5000/docs**. Para correr solo los tests:
```bash
make docker-test
```

Para verificar tests, cobertura, lint y complejidad:
```bash
make docker-grade
```

### 1.2. Alternativa con entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
make run
make grade
```



## 2. Módulos del proyecto

- **`src/app.py`**: punto de entrada de la API. Crea la app Flask, registra todas las rutas y las conecta con los módulos de lógica. También expone `/docs` con Swagger UI y `/health` para monitoreo.
- **`src/usuarios.py`**: implementa el CRUD completo de usuarios: crear, listar, obtener por id, actualizar y eliminar.
- **`src/juegos.py`**: gestiona la lista de juegos de cada usuario. Permite agregar, listar, actualizar y eliminar juegos, con soporte para filtros por género y ordenamiento.
- **`src/sugerencias.py`**: sugiere un juego al azar entre los que el usuario tiene (`tengo=true`), con la opción de filtrar por género.
- **`src/wikidata.py`**: se conecta con la API de Wikidata para buscar videojuegos por texto u obtenerlos por id, y los guarda en el catálogo local.
- **`src/filtros.py`**: función compartida de filtrado por género y ordenamiento, usada tanto en la lista de juegos del usuario como en el catálogo global.
- **`src/store.py`**: centraliza todas las estructuras de datos (usuarios, listas, catálogo) y su persistencia en SQLite. Para empezar de cero: `make clean-db`.
- **`src/auth.py`**: maneja el registro y login de usuarios. Al registrar, guarda la contraseña como hash seguro; al hacer login, verifica el hash y genera un token con fecha de expiración. También valida el token en cada request y rechaza los vencidos con 401.
- **`src/auth_common.py`**: helpers compartidos para autenticación: parseo de bodies de registro y login, verificación de unicidad de username, extracción del token del header y consulta de datos del token en la base.
- **`tests/test_public/`**: tests provistos por la cátedra que verifican el contrato de la API. Cubren usuarios, lista de juegos, catálogo (Wikidata), sugerencia y autenticación.
- **`tests/test_private/test_juegos_casos_borde.py`**: tests propios sobre casos borde de la lista de juegos: campos obligatorios faltantes, juegos inexistentes, ordenamiento por fecha de lanzamiento.
- **`tests/test_private/test_sugerencia_por_genero.py`**: tests propios sobre el endpoint de sugerencia filtrado por género: que solo devuelva juegos del género pedido y que devuelva 404 si no hay coincidencias.
- **`openapi.yaml`**: contrato formal de la API. Define todos los endpoints, parámetros, esquemas de request y response, y códigos HTTP esperados. Es la referencia central para implementar y testear la API.



## 3. Metodología de trabajo en equipo

Para organizar el trabajo nos reunimos por videollamada en Discord y dividimos los módulos entre los integrantes. Usamos un repositorio en Bitbucket con una rama `development` como base, desde la que creamos ramas secundarias para cada tarea y luego mergeamos a `development` al terminar. Una vez finalizado el proyecto, mergeamos `development` a `main`.

La división quedó así:

- **API de usuarios** (`src/usuarios.py`) y **lista de juegos por usuario** (`src/juegos.py`): nos repartimos las funciones entre todos.
- **Integración con Wikidata** (`src/wikidata.py`): implementada por Nahuel Ontivero.
- **Autenticación básica** (`src/auth.py`): implementada por Nicolás Gerbaudo.
- **Sugerencias** (`src/sugerencias.py`): implementada por Alejo Vides.
- **Evaluación de la API** (`tests/test_private/`): implementada por Nicolás Jorge.
- **Informe**: redactado por Nahuel Ontivero, a excepción de las respuestas de la entrega parcial, que se elaboraron entre todos.
- **Guión del video**: a cargo de Nahuel Ontivero.
- **Presentación**: a cargo de [COMPLETAR].
- **Video**: cada integrante grabó su parte; la edición y unión del material estuvo a cargo de Nicolás Gerbaudo.



## 4. Video y presentación

A continuación se encuentran el video de presentación del proyecto y los slides utilizados como apoyo visual.

- **Video**: [ver video](https://www.google.com/)
- **Presentación**: [ver slides](https://www.google.com/)


## 5. Glosario

- **HTTP**: protocolo de comunicación sobre el que se construye la web y las APIs REST. Define cómo se estructuran las requests y responses entre cliente y servidor, incluyendo métodos (`GET`, `POST`, `PUT`, `DELETE`), códigos de estado (`200`, `201`, `404`, `409`, etc.) y headers.
- **JSON**: formato de texto liviano para intercambiar datos entre sistemas. En este proyecto, todos los endpoints de la API reciben y devuelven datos en formato JSON. Por ejemplo, `{"nombre": "Ana"}` es un JSON con un campo `nombre`.
- **API REST**: una API (interfaz de programación de aplicaciones) que sigue los principios de diseño del estilo arquitectónico REST (transferencia de estado representacional).
- **Recurso**: entidad identificada por una URL sobre la que se pueden realizar operaciones. En este proyecto, los recursos principales son los usuarios, los juegos del catálogo y las listas de juegos por usuario. Por ejemplo, `/usuarios/1` identifica al usuario con id 1, y `/usuarios/1/juegos` identifica la lista de juegos de ese usuario.
- **Endpoint**: un método HTTP combinado con una URL específica que expone una operación de la API. Por ejemplo, `GET /usuarios` expone la operación "listar usuarios", `POST /usuarios` expone la operación "crear usuario" y `GET /juegos/<id>` expone la operación "obtener juego por id (del catálogo o Wikidata)".
- **Parámetros**: información que se pasa en la URL. Pueden ser de dos tipos:
    - *Path params*: van dentro de la URL, como el `1` en `/usuarios/1`.
    - *Query params*: van después del `?`, como `q` y `fuente` en `/juegos?q=zelda&fuente=wikidata`.
- **Cuerpo (body)**: información que se envía dentro de la request, no en la URL. Se usa típicamente en `POST` y `PUT`. Por ejemplo, cuando creás un usuario mandás {"nombre": "Ana"} en el cuerpo.
- **Idempotencia**: propiedad de una operación que garantiza que ejecutarla una o varias veces produce el mismo resultado. Por ejemplo, `GET /usuarios/1` (obtener usuario con id 1) siempre devuelve el mismo usuario sin modificar nada; `PUT /usuarios/1` (actualizar usuario con id 1) con el mismo cuerpo siempre deja al usuario en el mismo estado, sin importar cuántas veces se ejecute. En cambio, `POST /usuarios` (crear usuario) no es idempotente: cada llamada crea un usuario nuevo.
- **Contrato de API**: especificación formal que define cómo debe comportarse la API: qué endpoints expone, qué parámetros y cuerpos recibe cada uno, y qué respuestas devuelve. En este proyecto el contrato está definido en `openapi.yaml` y es la referencia tanto para implementar la API como para escribir los tests.
- **Proxy**: intermediario entre dos sistemas. En este proyecto, nuestra API actúa como proxy entre el usuario y Wikidata: el usuario le pide juegos a nuestra API, y esta a su vez consulta Wikidata. Si Wikidata falla, la API devuelve `502 Bad Gateway`.
- **Variable de entorno**: variable definida en el sistema o en un archivo como `.env` que permite configurar el comportamiento de una aplicación sin modificar el código. Se usa para guardar valores como configuraciones, rutas o credenciales.
- **Docker**: herramienta que permite ejecutar aplicaciones en contenedores, es decir, entornos aislados que incluyen todo lo necesario para que el programa funcione (código, dependencias, configuración).
- **Flask**: framework web minimalista para Python que permite construir APIs y aplicaciones web de forma sencilla. En este proyecto se usa para definir las rutas de la API, manejar requests y responses HTTP, y servir la documentación Swagger.
- **SQLite**: motor de base de datos relacional que almacena todos los datos en un único archivo local, sin necesidad de un servidor separado. En este proyecto se usa para persistir cinco tablas: `usuarios` (id y nombre), `listas_juegos` (juegos de cada usuario con sus flags: tengo, quiero, jugado, me_gusta), `catalogo` (juegos obtenidos de Wikidata), `credenciales` (username, hash de contraseña y token de autenticación con su fecha de expiración) y `meta` (datos internos como el próximo id de usuario). Por defecto el archivo se guarda en `instance/datos.db`; para empezar de cero: `make clean-db`.
- **Wikidata**: base de conocimiento abierta y colaborativa mantenida por la Fundación Wikimedia. En este proyecto se usa como fuente de datos de videojuegos: se consulta su API para buscar juegos por nombre o por id (Q-id), y los resultados se mapean al esquema de la API y se guardan en el catálogo local.
- **requests**: librería de Python que permite hacer llamadas HTTP a APIs externas de forma sencilla. En este proyecto se usa para consultar la API de Wikidata desde `src/wikidata.py`.
- **Swagger**: herramienta que permite visualizar e interactuar con una API a partir de su especificación OpenAPI. En este proyecto, al levantar la API se puede acceder a la documentación interactiva en `http://localhost:5000/docs`, donde se pueden ver todos los endpoints y probarlos directamente desde el navegador.
- **pytest**: framework de testing para Python que permite escribir y ejecutar tests de forma sencilla. En este proyecto se usa para correr los tests públicos y privados con `make test` o `make grade`.
- **Cobertura de tests**: porcentaje de líneas de código en `src/` que son ejecutadas al correr los tests. Indica qué proporción del código está siendo efectivamente probada por los tests. En este proyecto se exige una cobertura mínima (70%) para asegurar que el código esté suficientemente probado.
- **Linter**: herramienta que analiza el código sin ejecutarlo para detectar errores, problemas de estilo y malas prácticas. En este proyecto se usa `ruff` para verificar que el código cumpla ciertas reglas.
- **Complejidad ciclomática**: medida de la cantidad de caminos posibles que puede seguir la ejecución de una función, en función de sus estructuras de control (`if`, `for`, `while`, etc.). En este proyecto ninguna función en `src/` debe superar complejidad 8.
- **Health check**: endpoint de la API (`GET /health`) que permite verificar si el servicio está funcionando correctamente. Se usa para monitoreo y para que herramientas como Docker puedan comprobar que la aplicación está activa.
- **Timeout**: límite de tiempo máximo que se espera una respuesta de una operación (por ejemplo, una llamada a una API externa). Si se supera ese tiempo, la operación se cancela y se considera un error. En este proyecto, las consultas a Wikidata usan un timeout para evitar que la API quede bloqueada indefinidamente.
- **Hash**: resultado de aplicar una función de hash a un dato, que lo transforma en una cadena de caracteres de longitud fija, de forma irreversible. Por ejemplo, `"miPassword123"` -> función de hash -> `"$2b$12$Kx8Qv3mN..."`. Si alguien ve el hash, no puede recuperar la contraseña original.
- **Autenticación**: proceso por el cual un sistema verifica la identidad de quien hace una solicitud. En este proyecto, un usuario se registra con username y contraseña, y al hacer login recibe un token que debe incluir en el header `Authorization: Token <TOKEN>` de cada request que requiera identidad válida.
- **Token**: cadena generada al autenticarse (login) que identifica al usuario en la API. Se envía en el header `Authorization: Token <TOKEN>` en cada request protegida y permite validar su identidad sin reenviar sus credenciales. En este proyecto, los tokens tienen un tiempo de expiración (TTL) y dejan de ser válidos una vez vencidos.
- **TTL (Time To Live)**: cuánto tiempo dura algo antes de considerarse vencido. En este caso, cuántos minutos es válido un token después de ser creado.



## 6. Preguntas conceptuales y reflexión

### 6.1. ¿Qué es una API REST y un contrato de API?

Una API REST es una interfaz de programación de aplicaciones que sigue los principios de diseño del estilo arquitectónico REST. Permite que aplicaciones y servicios se comuniquen entre sí a través de HTTP, intercambiando recursos identificados por URLs. A diferencia de otros estilos como SOAP, REST es flexible: se puede implementar en prácticamente cualquier lenguaje y admite distintos formatos de datos, aunque JSON es el más usado por ser legible tanto para humanos como para máquinas.

REST se basa en algunos principios clave:

- **Sin estado**: el servidor no guarda información entre requests. Cada solicitud debe incluir todo lo necesario para procesarla, ya que el servidor no recuerda nada de requests anteriores. Por ejemplo, cada request que requiere autenticación debe incluir el token en el header `Authorization: Token <TOKEN>`.
- **Separación cliente-servidor**: el cliente y el servidor son completamente independientes entre sí. El cliente solo conoce la URL del recurso que quiere acceder; el servidor solo responde con los datos solicitados.
- **Recursos identificados por URL**: cada recurso tiene un identificador único (su URL). Por ejemplo, `/usuarios/1` identifica al usuario con id 1.
- **Operaciones mediante métodos HTTP**: las operaciones sobre los recursos se expresan con métodos HTTP, siguiendo el modelo CRUD: `GET` para leer, `POST` para crear, `PUT` para actualizar y `DELETE` para eliminar.

En este proyecto, la API permite gestionar usuarios, listas de juegos y consultar el catálogo de Wikidata siguiendo estos principios. El contrato de la API está definido en `openapi.yaml`, que sigue la especificación OpenAPI (OAS): un estándar que permite describir una API de forma que cualquier desarrollador pueda entender sus endpoints, parámetros, cuerpos, respuestas y métodos de autenticación. Este contrato funciona como referencia tanto para implementar la API como para escribir los tests, y garantiza que el comportamiento de la API sea predecible y consistente.

### 6.2. ¿Para qué sirven los tests y la cobertura?

Los tests permiten verificar automáticamente que cada parte de la API se comporta como se espera. En este proyecto hay tres tipos:

- **Tests públicos** (`tests/test_public/`): provistos por la cátedra, verifican que los endpoints cumplan el contrato definido en `openapi.yaml`. Cubren el CRUD de usuarios, la lista de juegos, la integración con Wikidata, la sugerencia y la autenticación.
- **Tests privados** (`tests/test_private/`): implementados por nosotros, cubren casos borde como agregar un juego sin campos obligatorios, intentar modificar un juego inexistente, o pedir una sugerencia de un género sin coincidencias.
- **Tests de métricas** (`tests/test_metrics.py`): verifican que el código cumpla los requisitos de calidad: cobertura mínima del 70%, sin errores de linter y ninguna función con complejidad ciclomática mayor a 8.

La cobertura mide qué porcentaje de las líneas de código en `src/` son ejecutadas al correr los tests. En este proyecto alcanzamos un 91%, superando ampliamente el mínimo exigido del 70%. Los 51 tests pasan y `make grade` completa sin errores.

### 6.3. ¿Qué es la complejidad ciclomática y por qué se limita?

La complejidad ciclomática es una medida de la cantidad de caminos posibles que puede seguir la ejecución de una función, según sus estructuras de control (`if`, `for`, `while`, etc.). Cuanto mayor es, más difícil resulta entender, mantener y testear el código. Si una función supera cierto umbral, es una señal de que conviene refactorizarla dividiéndola en partes más simples. Por eso, en este proyecto ninguna función en `src/` supera complejidad 8.

### 6.4. ¿Qué es un linter?

Un linter es una herramienta que analiza el código sin ejecutarlo para detectar errores, problemas de estilo y malas prácticas. En este proyecto usamos `ruff`, que verifica que el código en `src/` cumpla ciertas reglas de calidad. Esto ayuda a mantener el código consistente y a detectar problemas antes de correr los tests.

### 6.5. ¿Para qué sirve Docker en este proyecto?

Docker permite correr la API y los tests en un entorno controlado y reproducible, sin necesidad de configurar el sistema local. Esto es útil porque garantiza que el código funcione igual en cualquier máquina, independientemente del sistema operativo o las dependencias instaladas. En este proyecto, `make docker-build` construye la imagen, `make docker-run` levanta la API, `make docker-test` corre los tests y `make docker-grade` ejecuta el grading completo (tests, cobertura, lint y complejidad) dentro de un contenedor.

### 6.6. ¿Cómo realizamos el debugging cuando algo fallaba?

Nuestro proceso de debugging se basó principalmente en los tests y su output. Cuando algo fallaba, analizábamos qué test no pasaba, qué esperaba y qué recibía, y a partir de eso deducíamos dónde podía estar el error en el código. El output de `make test` fue suficiente para identificar la mayoría de los problemas.



## 7. Decisiones de diseño y problemas encontrados

El proyecto tenía un diseño muy pautado: la estructura de módulos, las rutas, los helpers y gran parte de la lógica ya estaban definidos en el kickstarter. Nuestro trabajo fue principalmente completar las funciones pendientes siguiendo el contrato de `openapi.yaml` y los tests como guía.

Los principales problemas que encontramos fueron:

- **Persistencia de datos entre ejecuciones de `make test`**: al correr `make test` varias veces, los tests de auth fallaban porque el usuario ya existía en la base de datos de una ejecución anterior. `make clean-db` no resolvía el problema. Un compañero nos indicó que la base de datos de los tests a veces no se limpia sola entre ejecuciones; la solución fue hacer `rm :memory:` antes de volver a correr `make test`.

- **Integración con Wikidata**: el principal desafío fue entender cómo hacer correctamente una request a la API de Wikidata usando la librería `requests` de Python, combinando los parámetros que llegaban desde el cliente Flask con los que esperaba la API externa.



## 8. Autenticación básica

### 8.1. Hashing de contraseñas

Para el hashing de contraseñas se usó la librería `werkzeug.security`, que ya forma parte de las dependencias de Flask. Al registrar un usuario, la contraseña se hashea con `generate_password_hash` antes de guardarse en la base de datos. Al hacer login, se verifica con `check_password_hash`, que compara la contraseña ingresada contra el hash almacenado sin necesidad de revertirlo.

### 8.2. Expiración de tokens

Al hacer login, se genera un token único con `uuid4().hex` y se calcula su fecha de vencimiento sumando un TTL a la hora actual en UTC. Esa fecha se guarda en la columna `token_expira_en` de la tabla `credenciales` en formato ISO 8601.

En cada request autenticada, `obtener_usuario_actual` extrae el token del header `Authorization`, recupera su información desde la base de datos y verifica su fecha de expiración comparándola con la hora actual. Si el token no existe, no tiene fecha de expiración o ya venció, la función devuelve `None` y la request es rechazada con un `401 Unauthorized`.

### 8.3. Cómo probar con *curl*

**Registro:**
```bash
curl -s -X POST http://localhost:5000/auth/registro \
  -H "Content-Type: application/json" \
  -d '{"username": "ana", "nombre": "Ana", "password": "miPassword123"}' | python3 -m json.tool
```
```json
{
    "id": 1,
    "nombre": "Ana"
}
```

**Login**:
```bash
curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "ana", "password": "miPassword123"}' | python3 -m json.tool
```
```json
{
    "token": "57ad8dae05e24fdc9f5c03d5b0bbbafb"
}
```

**Uso del token**:
```bash
curl -s -X POST http://localhost:5000/usuarios/1/juegos \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 1246bd6a3cb64fd1980ff055be3dde02" \
  -d '{"juego_id": "Q610968", "tengo": true, "quiero": false, "jugado": false, "me_gusta": false}' | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin), indent=4, ensure_ascii=False))"
```
```json
{
    "descripcion": "videojuego de 1983",
    "fecha_agregado": "2026-04-04T00:55:34.496618+00:00",
    "genero": "videojuego de plataformas",
    "id": "Q610968",
    "jugado": false,
    "lanzamiento": "1984-00-00",
    "me_gusta": false,
    "nombre": "Mario Bros",
    "plataforma": "Game Boy Advance",
    "quiero": false,
    "tengo": true
}
```



## 9. Uso de IA en el proyecto

Varios integrantes del equipo utilizamos asistentes de IA a lo largo del proyecto, principalmente Claude, ChatGPT y GitHub Copilot desde VS Code.

El uso se concentró en las siguientes áreas:

- **Código**: para entender módulos y funciones del kickstarter, consultar conceptos de Flask (manejo de parámetros y body de requests), HTTP, la librería `requests` (cómo conectarse con Wikidata) y Python en general. También para debuggear errores en nuestro código.
- **Tests**: para entender qué verificaba cada test y qué significaban los errores del output de `make test`.
- **Documentación**: para mejorar la redacción y generar partes del informe.

En cuanto a los criterios de revisión: para el código, verificamos que lo generado o sugerido fuera coherente con el resto del proyecto y con el contrato de la API. Para la documentación, comparamos las definiciones y afirmaciones con el código, el enunciado u otras fuentes confiables.



## 10. Entregable de Parte 1

### 10.1. Ejemplo 1

```bash
curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=zelda&language=es&format=json" \  
| python3 -m json.tool
```

**¿Qué valor aparece en la clave *searchinfo.search*?**

El valor que aparece en la clave `searchinfo.search` es `"zelda"`.

**En la lista *search*, elegí un resultado que parezca un videojuego: ¿cuál es su *id* (Q-id), *label* y *description*?**

El segundo resultado la lista `search` tiene:

- `id` -> `"Q12395"`
- `label` -> `"The Legend of Zelda"`
- `description` -> `"1986 action-adventure video game"`

### 10.2. Ejemplo 2

```bash
curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q12395&format=json&props=labels|descriptions" \  
| python3 -m json.tool
```

**Dentro de *entities.(QID).labels*, ¿qué *value* aparece para el idioma *es* y para *en*?**

Para el Q-id `Q12395`, en el campo `labels`, obtenemos:

- `es` -> `"The Legend of Zelda"`
- `en` -> `"The Legend of Zelda"`

**Dentro de *entities.(QID).descriptions*, ¿qué descripción en *es* te devuelve para ese juego?**

En el campo `descriptions`, obtenemos:

- `en` -> `"1986 action-adventure video game"`
- `es` -> `"videojuego de 1986"`

### 10.3. Ejemplo 3

```bash
curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=mario&language=es&limit=5&format=json" \  
| python3 -m json.tool
```

**¿Cuántos elementos hay en la lista *search* cuando usás *limit=5*?**

Cuando usamos `limit=5`, en la lista `search` hay a lo sumo 5 elementos.

**¿Encontrás en los resultados algún videojuego de la saga Mario? ¿Cuál es su *id* y su *description*?**

Al limitarlo a sólo los primeros 5 resultados, lo más parecido a un juego de Mario sólo habla de la franquicia, con:

- `id` -> `"Q4803535"`
- `description` -> `"media franchise"`

Pero si sustituimos `search=mario` por `search=super%20mario` en la URL del comando `curl`, la tercera entrada de la lista `search` tiene

- `id` -> `"Q11168"`
- `description` -> `"1985 platform video game"`

### 10.4. Consignas para que redactes vos

**Ejercicio adicional 1**

***Consigna:*** Realizar una solicitud a la API de Wikidata para buscar entidades relacionadas con el término "pac-man", solicitando hasta 10 resultados en formato JSON y priorizando el idioma inglés, enviando además un encabezado User-Agent personalizado con `"LabRedes2026/1.0"`. Formatear la respuesta con Python. En la lista `search`, buscar dos resultados que parezcan videojuegos y dar sus `id`, `label` y `description`.

***Respuesta:***

El comando `curl` que ejecutamos es el siguiente:

```bash
curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=pac-man&language=en&limit=10&format=json" | python3 -m json.tool
```

En la lista `search`, el primer y el cuarto elementos se corresponden con juegos. Para el primer elemento, tenemos:

- `"id": "Q173626"`
- `"label": "Pac-Man"`
- `"description": "1980 arcade game developed by Namco"`

Y para el cuarto elemento, tenemos:

- `"id": "Q4838380"`
- `"label": "Baby Pac-Man"`
- `"description": "hybrid video game/pinball arcade game"`

**Ejercicio adicional 2**

***Consigna:*** Consultar la API de Wikidata usando la acción `wbgetentities` para obtener información de las entidades cuyos IDs se obtuvieron en el ejercicio anterior, en formato JSON, incluyendo únicamente las propiedades `info`, `labels` y `descriptions`, y priorizando los idiomas inglés y español. Enviar además un encabezado User-Agent personalizado con `"LabRedes2026/1.0"`. Formatear la respuesta con Python. Dentro de `entities.<QID>` de cada entidad, identificar los valores de:

- `modified`
- `labels.es.value`
- `labels.en.value`
- `descriptions.es.value`
- `descriptions.en.value`

***Respuesta:***

El comando `curl` que ejecutamos es el siguiente:

```bash
curl -A "LabRedes2026/1.0" "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q173626|Q4838380&format=json&props=info|labels|descriptions&languages=en|es" | python3 -m json.tool
```

| **Campo**               | **QID**  `"Q173626"`                    | **QID** `"Q4838380"`                      |
|-------------------------|-----------------------------------------|-------------------------------------------|
| *modified*              | `"2026-01-11T07:22:39Z"`                | `"2025-11-05T18:10:26Z"`                  |
| *labels.es.value*       | `"Pac-Man"`                             | `"Baby Pac-Man"`                          |
| *labels.en.value*       | `"Pac-Man"`                             | `"Baby Pac-Man"`                          |
| *descriptions.es.value* | `"videojuego de 1980"`                  | -                                         |
| *descriptions.en.value* | `"1980 arcade game developed by Namco"` | `"hybrid video game/pinball arcade game"` |

## 11. Entregable de Parte 3

### 11.1. Añadiendo usuarios a la database

***Comando:***
```bash
curl -s -X POST http://localhost:5000/usuarios -H "Content-Type: application/json" -d '{"nombre": "juan"}' | python3 -m json.tool
```
***Output:***
```json
{
    "id": 1,
    "nombre": "juan"
}
```
***Comando:***
```bash
curl -s -X POST http://localhost:5000/usuarios -H "Content-Type: application/json" -d '{"nombre": "pepe"}' | python3 -m json.tool
```
***Output:***
```json
{
    "id": 2,
    "nombre": "pepe"
}
```

### 11.2. Listando usuarios

***Comando:***
```bash
curl -s http://localhost:5000/usuarios | python3 -m json.tool
```
***Output:***
```json
[
    {
        "id": 1,
        "nombre": "juan"
    },
    {
        "id": 2,
        "nombre": "pepe"
    }
]
```

### 11.3. Actualizando un usuario y mostrando la lista actualizada

***Comando:***
```bash
curl -s -X PUT http://localhost:5000/usuarios/2 -H "Content-Type: application/json" -d '{"nombre": "juan2"}' | python3 -m json.tool
```
***Output:***
```json
{
    "id": 2,
    "nombre": "juan2"
}
```
***Comando:***
```bash
curl -s http://localhost:5000/usuarios | python3 -m json.tool
```
***Output:***
```json
[
    {
        "id": 1,
        "nombre": "juan"
    },
    {
        "id": 2,
        "nombre": "juan2"
    }
]
```

### 11.4. Eliminando un usuario y mostrando la lista actualizada

***Comando:***
```bash
curl -s -X DELETE http://localhost:5000/usuarios/1 | python3 -m json.tool
```
***Output:***
```json
{
    "mensaje": "Usuario eliminado"
}
```
***Comando:***
```bash
curl -s http://localhost:5000/usuarios | python3 -m json.tool
```
***Output:***
```json
[
    {
        "id": 2,
        "nombre": "juan2"
    }
]
```
