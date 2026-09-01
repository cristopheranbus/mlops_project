# Perfiles y criterios de elección

Los perfiles controlan la cantidad de infraestructura, documentación y pruebas que debe
tener un proyecto generado. No representan niveles de madurez obligatorios: un proyecto
`python-ml` bien operado puede ser más apropiado que una plataforma compleja innecesaria.

## Regla de selección

Elige el perfil más pequeño que responda afirmativamente a tus necesidades actuales:

```text
¿Necesitas recursos gobernados y despliegue en Databricks?
├── Sí  → databricks-mlops
└── No
    └── ¿Necesitas tracking, artefactos o registry mediante MLflow?
        ├── Sí  → mlflow-local
        └── No  → python-ml
```

No elijas `databricks-mlops` solo porque Databricks exista en la organización. Debe haber
un requisito concreto de Jobs, Unity Catalog, bundles, serving, promoción u operación en
ese entorno.

## Comparación completa

| Capacidad | `python-ml` | `mlflow-local` | `databricks-mlops` |
| --- | :---: | :---: | :---: |
| Layout `src` | Sí | Sí | Sí |
| Configuración YAML + Pydantic | Sí | Sí | Sí |
| Ruff, mypy, pytest, cobertura y build | Sí | Sí | Sí |
| CI localizable en GitHub Actions | Sí | Sí | Sí |
| Workflows 01 calidad y 02 seguridad | Sí | Sí | Sí |
| Workflows 03 Databricks y 04 monitoreo | No | No | Sí |
| Documentación base | Sí | Sí | Sí |
| Tracking de experimentos | No obligatorio | Sí | Sí |
| Artefactos y firma del modelo | Según necesidad | Sí | Sí |
| Evaluación independiente | Recomendable | Sí | Sí |
| Registry | No | Opcional | Unity Catalog |
| Pruebas de integración local | Según componentes | Sí | Sí |
| Databricks Asset Bundles | No | No | Sí |
| Jobs y targets por entorno | No | No | Sí |
| Aprobación de producción | No implícita | Según flujo | Explícita cuando se requiera |
| Model Serving y smoke test | No | No obligatorio | Sí cuando hay despliegue |
| Documentación operativa y rollback | Según operación | Recomendable | Obligatoria |
| Credenciales externas para desarrollo básico | No | No, si MLflow es local | No para unitarias; sí para validar workspace |

## Perfil `python-ml`

### Cuándo elegirlo

- prototipos que deben conservar calidad de software;
- entrenamiento batch local o en un runtime Python genérico;
- librerías de features o scoring sin tracking centralizado;
- equipos que todavía no necesitan registry ni serving administrado;
- casos donde la simplicidad operativa es una restricción explícita.

### Contrato mínimo

- `pyproject.toml` y `uv.lock`;
- paquete importable bajo `src`;
- configuración separada del código;
- pruebas bajo `tests`;
- README y documentos de arquitectura, configuración y pruebas;
- CI con los controles locales;
- matriz Python 3.12/3.13 sobre Linux y Windows, branch coverage y package smoke;
- marcador `.mlops-profile` con `python-ml`.
- `configs/base.yaml`, `configs/local.yaml` y un modelo Pydantic estricto.

### Frontera de ejecución

Todo el camino principal debe poder ejecutarse sin MLflow, Databricks ni credenciales de
producción. Las fuentes externas se encapsulan en adaptadores y se prueban mediante
contratos o dobles controlados.

### Señales para evolucionar

Considera `mlflow-local` cuando comparar ejecuciones manualmente se vuelva frágil, cuando
los artefactos deban quedar trazados o cuando exista una decisión formal de promoción.

## Perfil `mlflow-local`

### Cuándo elegirlo

- seguimiento reproducible de experimentos;
- comparación de métricas y parámetros entre ejecuciones;
- almacenamiento de modelos, firmas y ejemplos de entrada;
- evaluación independiente del entrenamiento;
- necesidad de lifecycle o aliases sin adoptar Databricks completo;
- pruebas de integración con un tracking store temporal o SQLite.

### Contrato adicional

- dependencia de MLflow declarada;
- `docs/mlflow.md`;
- `docs/mlflow-security.md`;
- pruebas en `tests/integration`;
- URI de tracking y nombre de experimento configurables por entorno;
- registro de parámetros, métricas, identidad del dataset, tags y artefactos útiles;
- firma del modelo y ejemplo de entrada;
- separación entre entrenamiento, evaluación y decisión de promoción.
- `start_experiment_run` como único dueño de `start_run` y `autolog`.

### Reproducibilidad local

La integración debe funcionar con almacenamiento temporal o SQLite, sin depender del
estado MLflow personal del desarrollador. Las pruebas crean recursos aislados y no deben
leer experimentos previos del equipo.

### Registry y aliases

El registry se agrega solo si aporta un lifecycle versionado. Cuando existe promoción, las
decisiones usan versiones exactas y aliases explícitos como `Challenger` y `Champion`.
Una referencia mutable sin evidencia de evaluación dificulta auditoría y rollback.

### Señales para evolucionar

Considera `databricks-mlops` cuando la ejecución deba administrarse mediante Jobs, el
modelo deba gobernarse en Unity Catalog, el despliegue use Model Serving o existan límites
claros entre dev y prod.

## Perfil `databricks-mlops`

### Cuándo elegirlo

- datos y modelos gobernados por Unity Catalog;
- entrenamiento o evaluación ejecutados como Databricks Jobs;
- infraestructura declarada mediante Asset Bundles;
- despliegue a Model Serving;
- aprobación y promoción por versión exacta;
- necesidad explícita de smoke tests y rollback operativo.

### Contrato adicional

- `databricks.yml` como fuente de verdad de recursos del workspace;
- targets diferenciados, al menos `dev` y `prod`;
- wheel del paquete compartido;
- notebooks bajo `notebooks/databricks/` que delegan lógica a `workflows/`;
- `notebook_task` como flujo principal del bundle;
- documentos `databricks.md`, `operations.md`, `release-checklist.md` y `rollback.md`;
- pruebas externas separadas en `tests/external`;
- tareas independientes para evaluación, aprobación, despliegue, smoke test y promoción;
- identidad de automatización y permisos mínimos.
- workflows separados para validación/deploy y monitoreo productivo.

### Fronteras de validación

Hay tres niveles que nunca deben confundirse:

1. **Local:** lint, tipado, unitarias, contratos, build y validación de archivos.
2. **Bundle:** validación de la definición contra tooling y configuración disponible.
3. **Workspace:** despliegue, permisos, Jobs, registro, endpoint y smoke tests reales.

Pasar el primer nivel no demuestra los otros dos. Si faltan credenciales, las pruebas
externas se reportan como no ejecutadas.

### Promoción segura

La promoción ocurre después de que la versión exacta aprobada esté desplegada, el endpoint
se encuentre listo y el smoke test valide esquema y semántica. El flujo conserva la
referencia del Champion anterior y documenta cómo regresar a él.

## Cambiar de perfil

El perfil se registra en `.mlops-profile`. Cambiar solo ese texto no migra el proyecto:
también deben agregarse dependencias, documentos, módulos, pruebas y configuración.

### `python-ml` a `mlflow-local`

1. agregar MLflow con restricción de versión;
2. definir tracking URI y experimento por entorno;
3. instrumentar entrenamiento y evaluación;
4. registrar firma, ejemplo, métricas y artefactos;
5. añadir pruebas de integración aisladas;
6. documentar el flujo en `docs/mlflow.md`;
7. cambiar `.mlops-profile` y ejecutar el validador.

### `mlflow-local` a `databricks-mlops`

1. definir recursos con Asset Bundles;
2. separar targets de dev y prod;
3. adaptar registro a Unity Catalog;
4. empaquetar el código como wheel;
5. definir Jobs y límites entre etapas;
6. implementar despliegue, readiness y smoke tests;
7. documentar operación, release y rollback;
8. agregar pruebas externas marcadas;
9. validar localmente y luego contra un workspace autorizado.

## Antipatrones

- seleccionar Databricks sin un caso operativo concreto;
- usar notebooks como única fuente de lógica;
- registrar un modelo durante entrenamiento y promoverlo en la misma función;
- tratar una ejecución local simulada como despliegue validado;
- guardar tokens en archivos versionados;
- usar siempre la última versión de una dependencia crítica sin restricción;
- hacer que las pruebas dependan de un tracking store compartido;
- cambiar de perfil sin actualizar el contrato documental.
