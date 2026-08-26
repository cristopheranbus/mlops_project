# Validación y diagnóstico

`skills/create-mlops-project/scripts/validate_project.py` comprueba que un proyecto
generado cumpla el contrato
estructural mínimo de su perfil. Es rápido, determinista, no usa red y no modifica el
directorio analizado.

## Uso del CLI

```text
python skills/create-mlops-project/scripts/validate_project.py PROJECT_ROOT [--profile PROFILE]
```

Valores de `PROFILE`:

- `auto` — valor por defecto; usa marcador o inferencia;
- `python-ml`;
- `mlflow-local`;
- `databricks-mlops`.

Ejemplo desde este repositorio:

```powershell
uv run python skills/create-mlops-project/scripts/validate_project.py `
  C:\proyectos\risk_model --profile auto
```

Salida exitosa:

```text
Profile: python-ml
Result: 0 error(s), 0 warning(s)
```

Salida con fallos:

```text
Profile: mlflow-local
ERROR [missing] Required path is missing: docs/mlflow.md
ERROR [mlflow] MLflow profile requires an mlflow dependency
Result: 2 error(s), 0 warning(s)
```

## Códigos de salida

| Código | Significado |
| --- | --- |
| `0` | No se detectaron errores estructurales |
| `1` | Se detectó al menos un error o la ruta no existe |

Los warnings, si se incorporan en el futuro, se muestran en el resumen pero no cambian el
código mientras no exista también un error.

## Resolución automática del perfil

Con `--profile auto` se aplica este orden:

1. valor válido de `.mlops-profile`;
2. presencia de `databricks.yml`;
3. presencia de `docs/mlflow.md`;
4. fallback a `python-ml`.

Se recomienda versionar `.mlops-profile` porque expresa intención y evita inferencias
ambiguas.

## Reglas comunes

Todos los perfiles requieren:

```text
pyproject.toml
uv.lock
src/
tests/
README.md
.gitignore
.github/workflows/ci.yml
docs/architecture.md
docs/configuration.md
docs/testing.md
```

Además:

- `pyproject.toml` debe ser TOML válido;
- deben existir tablas de configuración para Ruff, mypy, pytest y coverage;
- debe haber al menos un directorio de paquete bajo `src`;
- debe existir al menos un archivo `test_*.py` bajo `tests`.

## Reglas de `mlflow-local`

Además de las comunes:

- alguna dependencia declarada debe comenzar por `mlflow`;
- debe existir `docs/mlflow.md`;
- debe existir `tests/integration`.

La búsqueda de dependencias cubre `project.dependencies`, grupos opcionales y
`dependency-groups`.

## Reglas de `databricks-mlops`

Incluye todas las reglas de MLflow y agrega:

```text
databricks.yml
docs/databricks.md
docs/operations.md
docs/release-checklist.md
docs/rollback.md
tests/external
```

El script solo comprueba la presencia estructural. No interpreta el bundle ni llama al
workspace.

## Escaneo textual

El validador recorre archivos con extensiones de texto conocidas y busca:

- marcadores de trabajo pendiente como `TODO`, `FIXME` o `CHANGEME`;
- expresiones de plantilla con llaves dobles;
- placeholders comunes de nombres de paquete, proyecto o target;
- una referencia específica a un dataset de demostración que puede indicar contenido no
  adaptado.

Ignora `.git`, `.venv`, `.pytest_cache`, `.mypy_cache` y `.ruff_cache`.

## Nombres de archivos sensibles

Se reporta `secret-file` para:

- `.env`;
- `.databrickscfg`;
- extensiones `.pem`, `.key`, `.p12` y `.pfx`.

Esta comprobación se basa en el nombre, no en un análisis criptográfico ni en detección de
entropía. Un token dentro de un archivo Python o YAML podría no detectarse. Usa además un
escáner de secretos apropiado para tu organización.

## Catálogo de issues

| Código | Causa | Corrección habitual |
| --- | --- | --- |
| `path` | La raíz no existe o no es un directorio | Corregir la ruta absoluta |
| `profile` | `.mlops-profile` contiene un valor desconocido | Usar uno de los tres perfiles soportados |
| `missing` | Falta una ruta requerida | Crear el componente correcto, no un archivo vacío sin contrato |
| `pyproject` | TOML inválido o ilegible | Corregir sintaxis y volver a resolver dependencias |
| `quality-config` | Falta Ruff, mypy o pytest en `[tool]` | Agregar configuración y ejecutar la herramienta |
| `coverage-config` | Falta `[tool.coverage]` | Definir fuente, branch coverage y reporte |
| `package` | No hay directorio importable bajo `src` | Crear el paquete y configurar el build |
| `tests` | No existe ningún `test_*.py` | Agregar pruebas que validen comportamiento |
| `mlflow` | El perfil necesita MLflow pero no está declarado | Agregar dependencia restringida y actualizar lock |
| `placeholder` | Quedó contenido sin adaptar | Sustituirlo por valores del dominio |
| `example-leak` | Se detectó un nombre específico de ejemplo | Eliminar supuestos heredados y adaptar el caso |
| `secret-file` | Hay un archivo cuyo nombre sugiere credenciales | Retirarlo de Git y cargar secretos desde runtime |

## Uso programático

El módulo expone:

```python
from pathlib import Path

from scripts.validate_project import validate_project

profile, issues = validate_project(Path("C:/proyectos/risk_model"), "auto")
for issue in issues:
    print(issue.severity, issue.code, issue.message)
```

La función devuelve el perfil resuelto y una lista de `Issue`. No lanza una excepción por
errores de contrato normales; los acumula para que el consumidor pueda presentar todos a
la vez.

## Uso en CI

Ejemplo de step para un repositorio generado:

```yaml
- name: Validate generated project contract
  run: uv run python path/to/validate_project.py . --profile auto
```

En la práctica conviene distribuir o copiar el validador de forma controlada, fijando la
versión que define el contrato. Consumir siempre una versión remota mutable puede cambiar
las reglas sin revisión del repositorio generado.

## Qué no valida

El script no valida:

- exactitud estadística o utilidad del modelo;
- calidad, frescura, sesgo o leakage de datos;
- ejecución de Ruff, mypy, pytest o build;
- cobertura realmente alcanzada;
- validez semántica completa de `pyproject.toml`;
- contenido de workflows de CI;
- firmas MLflow, artefactos o aliases;
- sintaxis o despliegue de Asset Bundles;
- permisos, identidades o secretos del workspace;
- disponibilidad de endpoints;
- ausencia total de secretos.

Estas comprobaciones se cubren mediante gates locales, pruebas del proyecto, scanners y
validaciones externas autorizadas.

## Pruebas del validador

```powershell
uv run pytest --basetemp .pytest-tmp
```

La suite usa `tmp_path`, construye proyectos mínimos y verifica que la validación no
modifique archivos. En entornos Windows restringidos, `--basetemp .pytest-tmp` evita
problemas de permisos en la carpeta temporal global.
