# Notebooks productivos y MLflow

Esta guía explica cómo mantener notebooks Databricks pequeños, reutilizables y
trazables. Aplica principalmente a `mlflow-local` y `databricks-mlops`.

## Notebook, módulo y workflow

| Elemento | Responsabilidad | No debe contener |
| --- | --- | --- |
| Notebook | recibir widgets, cargar configuración e invocar | funciones, clases o reglas de negocio |
| Módulo bajo `src/<package>/` | transformaciones y lógica reutilizable | estado específico de una sesión interactiva |
| Workflow | coordinar data, modelo, tracking y artefactos | implementación duplicada de componentes |

Los entry points usados por CLI y notebooks viven en `<package>.workflows`. El mismo
workflow debe poder probarse sin ejecutar la interfaz visual de Databricks.

## Notebook source `.py`

Ruta: `notebooks/databricks/20_train.py`.

```python
# Databricks notebook source
import json

from first_ml_project.config.loader import load_config
from first_ml_project.workflows.training import train

environment = dbutils.widgets.get("environment")
run_name = dbutils.widgets.get("run_name")
overrides = json.loads(dbutils.widgets.get("config_overrides_json") or "{}")
config = load_config(environment, overrides)
train(config=config, run_name=run_name)
```

No añadas `def`, `class`, entrenamiento ni transformaciones. Databricks documenta el
[formato source](https://docs.databricks.com/aws/en/notebooks/notebook-format).

## Notebook `.ipynb`

También se acepta nbformat 4. Antes de versionarlo:

- elimina todos los outputs;
- deja `execution_count: null` en cada celda de código;
- importa un workflow;
- no conserves funciones o clases;
- no mantengas a la vez `20_train.py` y `20_train.ipynb`.

La limpieza evita diffs ruidosos, resultados obsoletos y exposición accidental de datos.

## Jobs notebook-first

El flujo principal usa `notebook_task`. Cada `notebook_path` resuelve a un archivo real
bajo `notebooks/databricks/`, y el wheel del paquete se instala como librería del Job.
Las tareas wheel auxiliares son válidas, pero no reemplazan el flujo principal. Consulta
[tipos de tareas](https://docs.databricks.com/aws/en/dev-tools/bundles/job-task-types) y
[parámetros de Jobs](https://docs.databricks.com/gcp/en/dev-tools/bundles/job-parameters).

`notebooks/exploration/` es opcional, nunca se referencia desde Jobs y no contiene el
camino productivo.

## Experimento y run de MLflow

Un **experimento** agrupa ejecuciones relacionadas. Un **run** representa una ejecución
concreta y contiene parámetros, métricas, tags y artefactos. Cambiar un hiperparámetro
crea otro run dentro del mismo experimento.

Todo workflow usa el único context manager permitido:

```python
with start_experiment_run(config, run_name=run_name) as run:
    model.fit(features, target)
    mlflow.log_metric("validation_score", score)
```

Sólo `src/<package>/tracking/mlflow.py` llama a `mlflow.start_run`. Dentro del contexto,
el adaptador configura tracking y experimento, abre el run, activa `mlflow.autolog`,
registra la configuración resuelta y sólo entonces entrega el control al workflow.

## Registro automático y manual

`autolog` registra lo que soporte la integración del framework: hiperparámetros,
métricas, modelo, signature e input example según configuración. Revisa siempre la
[MLflow Tracking API](https://mlflow.org/docs/latest/ml/tracking/tracking-api), porque el
detalle depende del framework y la versión.

Registra manualmente dentro del contexto aquello que expresa el contrato propio:

- métricas de aceptación y segmentos;
- identidad o versión del dataset;
- reportes de evaluación;
- evidencia de aprobación;
- artefactos que autolog no conoce.

Tuning usa runs hijos con `nested=True`. Entrenamiento, evaluación, aprobación y
promoción siguen siendo workflows separados.

## Encontrar la configuración de un run

1. abre el experimento configurado;
2. busca por `run_name` o por el tag `config.hash`;
3. verifica `config.environment` y `config.version`;
4. descarga `resolved_config.yaml`;
5. compara su hash con el que aparece en logs o resultados.

No llames `start_run` desde un notebook o workflow: rompe el punto único de configuración,
puede dejar autolog fuera del run y dificulta garantizar tags y artefactos. El validador
lo rechaza con `mlflow-run`.

## Límite de seguridad de AI Gateway

MLflow Tracking y MLflow AI Gateway son capacidades distintas. Los proyectos generados
usan Tracking, pero no habilitan gateway secrets, `auth_config.api_base` ni rutas proxy.
El validador reporta `mlflow-security` si detecta esa superficie en código o configuración
productiva. Consulta [Seguridad de MLflow y límite de AI Gateway](mlflow-security.md) para
entender el riesgo, la mitigación y los requisitos de una futura revisión.
