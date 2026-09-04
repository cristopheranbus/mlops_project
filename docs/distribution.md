# Modos de distribución y generación

Todas las modalidades usan el mismo `SKILL.md`, las mismas referencias de arquitectura y el
mismo validador. La diferencia es dónde vive la skill y si el proyecto se adapta mediante
Codex o se produce como un baseline determinista.

| Modalidad | Elegir cuando | Instalación o comando | Resultado |
| --- | --- | --- | --- |
| Skill personal | Una persona genera proyectos en distintos repositorios | `$skill-installer` desde la carpeta publicada en `main` | Generación adaptativa |
| Skill de repositorio | Un equipo versiona el generador junto a su código | `.agents/skills/create-mlops-project/` | Generación adaptativa compartida |
| Plugin | Se distribuye la capacidad completa como unidad instalable | raíz con `.codex-plugin/plugin.json` | Skill y metadatos versionados |
| CLI | CI, scripts o bootstrap repetible sin conversación | `create-mlops-project DESTINO --name NOMBRE` | Baseline determinista |

## Skill personal

Solicita a Codex:

```text
Usa $skill-installer para instalar create-mlops-project desde
https://github.com/cristopheranbus/mlops_project/tree/main/skills/create-mlops-project
```

Después invoca `$create-mlops-project` desde cualquier workspace. Si no aparece tras la
instalación, inicia una sesión nueva.

## Skill versionada en el repositorio

Codex descubre skills bajo `.agents/skills`. Para generar y conservar una copia de esta skill:

```powershell
create-mlops-project C:\proyectos\risk_model `
  --name risk-model `
  --profile python-ml `
  --embed-skill
```

No crees primero `.agents/skills` en el destino: dejaría de estar vacío. Genera con
`--embed-skill` o incorpora la carpeta después con autorización explícita.

## Plugin

El manifiesto `.codex-plugin/plugin.json` distribuye la carpeta `skills/`. Antes de publicar
una versión, mantén alineadas las versiones del manifiesto y `pyproject.toml`, ejecuta la suite
completa y actualiza el changelog.

## CLI determinista

Instala desde un checkout confiable:

```powershell
uv tool install .
create-mlops-project C:\proyectos\forecasting `
  --name demand-forecasting `
  --package demand_forecasting `
  --profile mlflow-local
```

El comando ejecuta `uv lock` por defecto. `--skip-lock` permite crear archivos sin acceso al
índice, pero exige ejecutar `uv lock` antes de `uv sync --locked`. El CLI rechaza destinos no
vacíos y nunca inicializa Git, publica repositorios, cambia controles hospedados ni usa
credenciales.

El baseline contiene la estructura, configuración, pruebas y workflows comunes. No conoce el
contrato de negocio. Para implementar una fuente de datos, target, métrica, umbral, modelo o
serving concretos, invoca la skill de forma adaptativa sobre un destino vacío.

## Verificación común

Después de cualquier modalidad:

```powershell
uv run python RUTA_A_LA_SKILL\scripts\validate_project.py C:\ruta\proyecto --profile auto
cd C:\ruta\proyecto
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

La creación del remoto y la configuración del flujo `feature → dev → main` son pasos
posteriores que requieren autorización separada.
