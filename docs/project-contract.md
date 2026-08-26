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
- cobertura mínima de 85%;
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
│       └── ci.yml
├── .gitignore
├── .mlops-profile
├── README.md
├── pyproject.toml
├── uv.lock
├── configs/
│   ├── base.yaml
│   └── local.yaml
├── docs/
│   ├── architecture.md
│   ├── configuration.md
│   └── testing.md
├── src/
│   └── paquete_ml/
│       ├── __init__.py
│       ├── config.py
│       ├── data.py
│       ├── features.py
│       ├── train.py
│       ├── evaluate.py
│       └── predict.py
└── tests/
    ├── unit/
    └── contract/
```

Los nombres de módulos son orientativos. Por ejemplo, un problema de forecasting puede
necesitar `splits.py` y `backtesting.py`; una librería de features quizá no necesite
`predict.py`.

## Responsabilidades arquitectónicas

### Configuración

- cargar valores versionados y overrides del entorno;
- validar tipos y campos obligatorios;
- no contener secretos reales;
- hacer visible qué cambia entre local, CI y producción.

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

Ruff cubre estilo, errores comunes, imports y formato; mypy valida con rigor el código
propio; pytest aplica la cobertura configurada; el build comprueba que el paquete puede
distribuirse.

## Contrato documental

Todos los perfiles incluyen:

- `README.md`: propósito, preparación, ejecución y límites;
- `docs/architecture.md`: componentes, relaciones y fronteras de runtime;
- `docs/configuration.md`: fuentes, precedencia y variables;
- `docs/testing.md`: capas, marcadores y comandos.

`mlflow-local` y `databricks-mlops` agregan `docs/mlflow.md`.

`databricks-mlops` agrega:

- `docs/databricks.md`;
- `docs/operations.md`;
- `docs/release-checklist.md`;
- `docs/rollback.md`.

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

