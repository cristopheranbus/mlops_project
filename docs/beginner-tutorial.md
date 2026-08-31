# Tutorial inicial: de cero a la primera prueba

Esta guía usa un proyecto pequeño con perfil `python-ml`. El primer resultado es local:
no requiere MLflow remoto, Databricks, nube ni credenciales.

## 1. Instalar las herramientas

**Objetivo:** disponer de Git, Python 3.12 o 3.13 y `uv`.

PowerShell y Bash:

```text
git --version
python --version
uv --version
```

**Salida esperada:** tres números de versión. Si `uv` no existe, instálalo siguiendo la
[documentación oficial](https://docs.astral.sh/uv/getting-started/installation/).

**Error habitual:** `python` no se reconoce. Instala Python y abre una terminal nueva;
no continúes con una versión anterior a 3.12.

## 2. Clonar este repositorio

**Objetivo:** obtener la skill y su validador.

```text
git clone https://github.com/cristopheranbus/mlops_project.git
cd mlops_project
```

**Salida esperada:** una carpeta con `README.md`, `pyproject.toml`, `skills/` y `tests/`.

**Error habitual:** `destination path ... already exists`. Entra en la copia existente o
elige otra carpeta; no borres archivos sin revisar qué contienen.

## 3. Instalar las dependencias

**Objetivo:** crear un entorno reproducible usando el lock versionado.

```text
uv sync --locked --dev
```

**Salida esperada:** un entorno `.venv` sincronizado sin cambios en `uv.lock`.

**Error habitual:** el lock está desactualizado. En una contribución intencional ejecuta
`uv lock`, revisa el diff y vuelve a usar `uv sync --locked --dev`.

## 4. Ejecutar las pruebas

**Objetivo:** comprobar que la copia funciona antes de modificarla.

```text
uv run pytest --basetemp .pytest-tmp
```

**Salida esperada:** todos los tests pasan y la branch coverage total es al menos 90%.

**Error habitual en Windows:** permiso denegado en la carpeta temporal. Conserva
`--basetemp .pytest-tmp`; esa ruta está ignorada por Git.

## 5. Invocar la skill

**Objetivo:** generar un proyecto mínimo en una carpeta vacía.

En Codex escribe:

```text
Usa $create-mlops-project para crear ./first_ml_project. Es una clasificación binaria
con datos CSV, target accepted, scikit-learn, ROC AUC como métrica principal y perfil
python-ml. El primer ejemplo debe usar datos sintéticos y ejecutarse sin credenciales.
```

**Salida esperada:** Codex confirma el contrato, crea el proyecto, ejecuta el validador y
los controles locales, y distingue cualquier validación externa no ejecutada.

**Error habitual:** la skill no aparece. Revisa la instalación en
[Guía de inicio](getting-started.md) y abre una conversación nueva.

## 6. Abrir el proyecto generado

**Objetivo:** reconocer el mapa básico.

PowerShell:

```powershell
Set-Location ..\first_ml_project
Get-ChildItem
Get-ChildItem src -Recurse
```

Bash:

```bash
cd ../first_ml_project
find src -type f
```

**Salida esperada:** un solo paquete bajo `src/`, perfiles YAML en `configs/`, pruebas y
documentación. Consulta el README generado antes de ejecutar un comando.

**Error habitual:** aparecen dos paquetes principales. No elijas uno al azar: la
generación incumple el contrato y debe corregirse.

## 7. Cambiar configuración

**Objetivo:** modificar un valor sin editar el código.

Abre `configs/local.yaml`, cambia un parámetro no sensible como `training.max_depth`, y
ejecuta el comando de entrenamiento indicado por el README, por ejemplo:

```text
uv run project-train --environment local --set training.max_depth=8
```

**Salida esperada:** el log muestra `environment=local`, los overrides y un hash de
configuración. Las listas se reemplazan completas; los mappings se fusionan.

**Error habitual:** escribir `"8"` cuando el modelo exige entero. Pydantic lo rechaza de
forma deliberada porque los tipos son estrictos.

## 8. Ejecutar el primer entrenamiento local

**Objetivo:** obtener un artefacto o métrica reproducible sin servicios externos.

```text
uv sync --locked
uv run project-train --environment local
```

**Salida esperada:** el proceso termina con código `0`, informa la métrica principal y
guarda o registra la configuración resuelta. El comando exacto y la salida concreta
pertenecen al README del proyecto generado.

**Error habitual:** falta el dataset real. El primer camino debe usar un fixture o datos
sintéticos pequeños; la conexión productiva se configura después.

## 9. Interpretar un error del validador

**Objetivo:** convertir un código estable en una corrección concreta.

```text
ERROR [config-format] configs/local.yaml must contain config_version: 1
```

Lee primero el código entre corchetes, después el archivo y la corrección. No crees un
archivo vacío sólo para ocultar el error. El catálogo completo está en
[Validación y diagnóstico](validation.md).

## 10. Preparar una contribución pequeña

**Objetivo:** proponer un cambio revisable.

```text
git switch -c docs/clarify-local-training
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --basetemp .pytest-tmp
git add docs README.md
git commit -m "Clarify local training instructions"
git push -u origin docs/clarify-local-training
```

Abre un pull request (PR), describe la motivación y copia la evidencia de pruebas. Si `origin` apunta al
repositorio original y no tienes permisos, crea un fork y cambia el remote. Continúa con
[Mi primera contribución](../CONTRIBUTING.md#mi-primera-contribución).
