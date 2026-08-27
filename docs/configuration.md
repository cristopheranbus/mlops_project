# Configuración tipada y reproducible

Todos los proyectos generados separan configuración, código y secretos. La interfaz
pública es `AppConfig`, `load_config(...)` y `config_hash(...)`; notebooks y workflows no
leen YAML directamente.

## Los cuatro archivos

| Archivo | Propósito | Se versiona |
| --- | --- | :---: |
| `configs/base.yaml` | Valores comunes y seguros | Sí |
| `configs/local.yaml` | Ejecución en el equipo del desarrollador | Sí |
| `configs/dev.yaml` | Recursos y comportamiento del entorno Databricks dev | Sí |
| `configs/prod.yaml` | Comportamiento productivo no secreto | Sí |

`base.yaml` y `local.yaml` existen en todos los perfiles. `dev.yaml` y `prod.yaml` son
obligatorios para `databricks-mlops`. Producción exige `environment=prod` explícito.

## Precedencia y merge

El orden, de menor a mayor prioridad, es:

1. `base.yaml`;
2. archivo del entorno;
3. overrides del runtime;
4. secretos obtenidos separadamente.

Los mappings se fusionan recursivamente. Listas y escalares se reemplazan completos.

`base.yaml`:

```yaml
config_version: 1
environment: local
training:
  max_depth: 4
  features: [age, income]
mlflow:
  tracking_uri: ./mlruns
  experiment_name: first-model
```

`local.yaml`:

```yaml
config_version: 1
training:
  max_depth: 6
```

Override `training.features=["age","tenure"]` produce conceptualmente:

```yaml
config_version: 1
environment: local
training:
  max_depth: 6
  features: [age, tenure]
mlflow:
  tracking_uri: ./mlruns
  experiment_name: first-model
```

No se concatenó la lista. Un `null` sólo es válido cuando el campo Pydantic es opcional.

## Modelo Pydantic

Los modelos usan tipos estrictos, son inmutables y rechazan claves desconocidas:

```python
from pydantic import BaseModel, ConfigDict, StrictInt


class TrainingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    max_depth: StrictInt
    features: tuple[str, ...]
```

Para agregar `training.learning_rate`:

1. añade el campo tipado a `TrainingConfig`;
2. define su valor común en `base.yaml` o hazlo opcional conscientemente;
3. ajusta sólo los entornos que difieren;
4. agrega una prueba válida y pruebas para tipo incorrecto y clave desconocida;
5. actualiza la documentación.

Pydantic no debe contener tokens, passwords, client secrets ni credenciales.

## Overrides por CLI y Databricks

CLI:

```text
project-train --environment local
project-train --environment dev --set training.max_depth=8
```

Los notebooks productivos exponen sólo estos widgets:

```text
environment
run_name
config_overrides_json
```

El notebook convierte `config_overrides_json` a un mapping y lo entrega al workflow. El
workflow llama a `load_config`; no abre los YAML por su cuenta.

## Secretos e infraestructura

Un YAML versionado permite reproducir una decisión, por lo que nunca debe contener un
secreto. Usa variables de entorno localmente y Databricks Secret Scopes en el workspace.
Los IDs y variables de infraestructura de Jobs permanecen en Declarative Automation
Bundles, no en `AppConfig`.

## Errores de validación

- `extra_forbidden`: hay una clave no declarada; corrige el nombre o amplía el modelo.
- error de tipo: el valor no cumple el tipo estricto; no confíes en coerción implícita.
- campo requerido: falta una decisión en base, entorno u override.
- `config_version`: el lector no comprende el contrato; migra antes de ejecutar.

La validación ocurre antes de abrir un run de MLflow, de modo que una configuración
inválida no produce ejecuciones vacías.

## Hash y artefacto resuelto

`config_hash(config)` serializa el modelo sin secretos a JSON canónico —claves ordenadas y
separadores estables— y calcula SHA-256. El mismo contenido produce el mismo hash sin
importar el orden original del YAML.

Cada ejecución conserva:

- entorno;
- overrides aplicados;
- hash SHA-256;
- artefacto `resolved_config.yaml` sin secretos;
- tags `config.version`, `config.environment` y `config.hash`.

Esto permite encontrar qué configuración produjo una métrica y comparar dos runs con
evidencia. La especificación normativa vive en
[`references/configuration.md`](../skills/create-mlops-project/references/configuration.md).

