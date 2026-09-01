# Contrato del proyecto generado

Este documento describe las entradas que debe resolver la skill, la estructura que debe
producir y los criterios que permiten declarar una generación como completa.

## Contrato de entrada

### Identidad

| Campo | Regla |
| --- | --- |
| Nombre del proyecto | Legible para personas y apropiado para el repositorio |
| Nombre del paquete | Identificador Python válido, normalmente en `snake_case` |
| Destino | Ruta absoluta resuelta; inexistente o vacía |

El nombre del repositorio y el paquete pueden diferir. Por ejemplo,
`fraud-detection-service` puede contener `src/fraud_detection_service`.

### Problema ML

El contrato debe expresar:

- tipo de problema: clasificación, regresión, forecasting, ranking, NLP u otro;
- unidad de predicción;
- target y horizonte cuando corresponda;
- población y exclusiones relevantes;
- fuente, formato y granularidad de datos;
- estrategia de partición, especialmente para datos temporales o agrupados;
- framework y familia de modelos;
- métrica principal y métricas diagnósticas;
- umbrales y regresiones permitidas;
- requisitos de inferencia batch u online.

No toda solicitud necesita todos los campos, pero una decisión crítica no debe quedar
oculta dentro de una implementación arbitraria.

### Ingeniería y operación

- versión de Python;
- gestor de dependencias;
- cobertura mínima;
- perfil MLOps;
- restricciones de runtime;
- necesidad de tracking, registry, aprobación o serving;
- entorno donde corre cada etapa;
- credenciales disponibles para verificaciones externas.

## Valores por defecto

Cuando el usuario no indique lo contrario:

- Python 3.12;
- `uv` para dependencias y ejecución;
- branch coverage mínima de 90%;
- perfil más pequeño que satisfaga el requerimiento;
- configuración neutral al entorno;
- notebooks opcionales y finos;
- pruebas externas excluidas de la suite local por defecto.

Los valores por defecto aceleran decisiones reversibles. No deben emplearse para inventar
un target, un umbral de negocio, permisos o infraestructura.

## Estructura base

La estructura puede adaptarse al problema, pero debe preservar responsabilidades claras:

```text
proyecto_ml/
├── .github/
│   └── workflows/
│       ├── 01-code-quality.yml
│       ├── 02-security.yml
│       ├── 03-databricks.yml
│       └── 04-production-monitoring.yml
├── .gitignore
├── .mlops-profile
├── README.md
├── pyproject.toml
├── uv.lock
├── configs/
│   ├── base.yaml
│   ├── local.yaml
│   ├── dev.yaml
│   └── prod.yaml
├── notebooks/
│   ├── databricks/
│   │   ├── 10_prepare_data.py
│   │   ├── 20_train.py
│   │   ├── 30_evaluate.py
│   │   └── 40_promote.py
│   └── exploration/
├── docs/
│   ├── architecture.md
│   ├── configuration.md
│   └── testing.md
├── src/
│   └── paquete_ml/
│       ├── __init__.py
│       ├── config/
│       │   ├── models.py
│       │   ├── loader.py
│       │   └── hashing.py
│       ├── data/
│       ├── features/
│       ├── modeling/
│       ├── tracking/
│       │   └── mlflow.py
│       └── workflows/
└── tests/
    ├── unit/
    └── contract/
```

Existe exactamente un paquete principal bajo `src/`. Los submódulos del dominio pueden
adaptarse, pero `config/` y `workflows/` conservan sus responsabilidades. `dev.yaml`,
`prod.yaml`, `notebooks/databricks/` y `databricks.yml` son obligatorios para el perfil
Databricks; sus workflows `03` y `04` también son obligatorios. Los perfiles menores sólo
incluyen `01` y `02`. `notebooks/exploration/` es opcional y nunca lo ejecutan Jobs.

## Responsabilidades arquitectónicas

### Configuración

- cargar `base.yaml`, el entorno y overrides mediante `load_config`;
- validar `config_version: 1`, tipos estrictos y campos obligatorios con Pydantic;
- congelar modelos y rechazar claves adicionales;
- reemplazar listas y escalares, y fusionar mappings recursivamente;
- producir un hash SHA-256 estable y `resolved_config.yaml` sin secretos;
- no contener secretos reales;
- hacer visible qué cambia entre local, CI y producción.

La interfaz pública es `AppConfig`, `load_config(environment, overrides)` y
`config_hash(config)`. YAML nunca se lee directamente desde notebooks o workflows.

### Acceso a datos

- encapsular rutas, tablas, consultas o clientes;
- separar lectura de transformación;
- identificar el dataset o snapshot usado;
- permitir fixtures pequeños en pruebas.

### Features

- implementar transformaciones deterministas cuando sea posible;
- conservar el mismo contrato entre entrenamiento e inferencia;
- validar columnas, tipos, nulos y categorías;
- evitar lógica reusable encerrada en notebooks.

### Entrenamiento

- recibir datos y configuración explícitos;
- controlar semillas y fuentes de no determinismo;
- devolver o persistir artefactos definidos por contrato;
- no decidir promoción productiva por efecto colateral.

### Evaluación

- ejecutar sobre datos independientes del fit;
- calcular la métrica principal y diagnósticos;
- comparar con umbrales y, cuando exista, con el modelo vigente;
- producir evidencia legible por personas y automatización.

### Inferencia

- declarar esquema de entrada y salida;
- aplicar las mismas transformaciones aprobadas;
- manejar errores de validación de manera predecible;
- incluir smoke tests si existe despliegue.

### Orquestación

Los entry points coordinan componentes, pero no acumulan reglas de negocio. Un notebook,
Job o CLI debe invocar funciones del paquete y mantener poca lógica propia.

### Notebooks y tracking

Los notebooks productivos aceptan source `.py` o nbformat 4 `.ipynb`, sin formatos
duplicados, funciones, clases u outputs. El bundle apunta sólo a rutas bajo
`notebooks/databricks/` mediante `notebook_task` e instala el wheel del paquete.

En perfiles MLflow, sólo `tracking/mlflow.py` abre runs. `start_experiment_run` activa
`autolog` dentro del run antes del entrenamiento, registra configuración y tags, y
encapsula las métricas y artefactos manuales. Tuning usa runs anidados.

## Contrato de pruebas

### Unitarias

Prueban transformaciones, configuración, métricas, gates y reglas de promoción sin red,
credenciales ni estado compartido.

### De contrato

Protegen esquemas de datos, target, configuración, firmas del modelo, payloads, artefactos
y manifiestos de despliegue.

### Integración local

Ejercitan varios componentes con almacenamiento temporal. En MLflow deben usar un store
aislado y no el estado personal del desarrollador.

### Externas

Requieren infraestructura autorizada y se marcan como `external`. No se ejecutan por
defecto ni se sustituyen por mocks para afirmar que producción fue validada.

### Smoke

Invocan la versión exacta aprobada después del despliegue, verifican disponibilidad,
esquema y semántica mínima, y bloquean promoción si fallan.

## Contrato de calidad

El proyecto debe configurar y pasar, salvo una desviación documentada:

```text
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

Ruff cubre estilo, errores comunes, imports y formato mediante el contrato curado descrito
en [Ruff estricto](ruff.md): reglas estables para seguridad, anotaciones, pytest, paths,
logging y mantenibilidad, sin `ALL` ni preview. Mypy valida con rigor el código propio;
pytest aplica markers estrictos, timeout y al menos 90% de branch coverage; el build y el
smoke de instalación comprueban que el paquete puede distribuirse.

La matriz de CI cubre Python 3.12 y 3.13 sobre Linux y Windows. Las acciones se fijan a
commits completos, los permisos parten de `contents: read` y ninguna prueba externa se
ejecuta implícitamente.

## Contrato documental

Todos los perfiles incluyen:

- `README.md`: propósito, preparación, ejecución y límites;
- `docs/architecture.md`: componentes, relaciones y fronteras de runtime;
- `docs/configuration.md`: fuentes, precedencia y variables;
- `docs/testing.md`: capas, marcadores y comandos.
- primer entrenamiento local, mapa de carpetas, cambio de configuración, errores
  frecuentes y pruebas previas a un PR.

`mlflow-local` y `databricks-mlops` agregan `docs/mlflow.md`.
También agregan `docs/mlflow-security.md`: el proyecto usa Tracking, mantiene AI Gateway
deshabilitado y explica actualización de dependencias, despliegue seguro y respuesta ante
una exposición. El validador aplica este límite como error inmediato.

`databricks-mlops` agrega:

- `docs/databricks.md`;
- `docs/operations.md`;
- `docs/release-checklist.md`;
- `docs/rollback.md`.

También explica cómo ejecutar un notebook, encontrar un run de MLflow, qué funciona sin
credenciales y qué requiere un workspace Databricks.

La documentación debe decir dónde corre cada componente, cuál sistema es autoritativo,
qué funciona localmente y qué requiere credenciales.

## Contrato de seguridad

- secretos obtenidos desde el runtime;
- `.env.example` solo con valores inequívocamente ficticios;
- credenciales locales y artefactos ignorados por Git;
- permisos mínimos en CI y producción;
- versiones exactas para promoción y rollback;
- ausencia de tokens, claves privadas y perfiles locales en commits.

## Criterio de completitud

Una generación está completa cuando:

1. la estructura corresponde al perfil;
2. no quedan placeholders ni contenido heredado de ejemplos;
3. el validador estructural no informa errores;
4. los gates locales aplicables pasan;
5. el README permite reproducir el camino local;
6. los supuestos están documentados;
7. las verificaciones no ejecutadas se declaran;
8. no se afirma éxito externo sin evidencia de una ejecución autorizada.

No se considera completa si falta una credencial necesaria para una comprobación requerida,
si el build falla o si una prueba obligatoria fue omitida sin explicación.
