# Create MLOps Project

Skill de Codex para crear repositorios de machine learning orientados a producción. A
partir de los requisitos de un problema, genera una base reproducible con estructura
`src`, pruebas automatizadas, controles de calidad, integración continua y documentación
operativa.

Este repositorio contiene la **skill y sus herramientas de validación**. No es, por sí
mismo, un proyecto de entrenamiento ni incluye datasets o modelos preentrenados.

## Qué resuelve

La skill estandariza la creación de proyectos ML nuevos y permite elegir el nivel de
infraestructura necesario:

| Perfil | Uso recomendado | Componentes principales |
| --- | --- | --- |
| `python-ml` | Desarrollo y ejecución local | Paquete Python, configuración, pruebas, calidad y CI |
| `mlflow-local` | Experimentación y trazabilidad local | Todo lo anterior más MLflow, evaluación, artefactos e integración local |
| `databricks-mlops` | Flujo productivo sobre Databricks | MLflow, Unity Catalog, Asset Bundles, Jobs, aprobación, serving y smoke tests |

Cada proyecto generado debe incluir, según el perfil elegido:

- código reutilizable bajo `src/<nombre_del_paquete>`;
- separación entre datos, features, entrenamiento, evaluación e inferencia;
- pruebas unitarias, de contrato e integración aplicables;
- Ruff, mypy, pytest y cobertura mínima configurable;
- workflow de CI con controles de calidad;
- documentación de arquitectura, configuración y pruebas;
- integraciones externas aisladas detrás de adaptadores y sin secretos versionados.

## Requisitos

- Codex con soporte para skills locales.
- Python 3.12 o 3.13.
- [`uv`](https://docs.astral.sh/uv/) para instalar y ejecutar las herramientas del
  repositorio.
- Credenciales de MLflow o Databricks únicamente cuando el perfil y las validaciones
  externas las requieran.

## Instalación de la skill

Clona este repositorio dentro del directorio de skills personales de Codex, usando
`create-mlops-project` como nombre de carpeta:

```powershell
git clone https://github.com/cristopheranbus/mlops_project.git `
  "$env:CODEX_HOME\skills\create-mlops-project"
```

Si `CODEX_HOME` no está definido, utiliza el directorio de configuración de Codex de tu
entorno y conserva la estructura siguiente:

```text
skills/
└── create-mlops-project/
    ├── SKILL.md
    ├── agents/
    ├── references/
    └── scripts/
```

Reinicia Codex después de instalarla para que detecte la nueva skill.

## Cómo aplicarla

Invoca la skill por su nombre y describe el proyecto que quieres crear. Conviene indicar
el problema, los datos, la variable objetivo, el framework, la métrica principal y el
perfil deseado.

Ejemplo local:

```text
Usa $create-mlops-project para crear un proyecto de clasificación de abandono de
clientes en ./churn_prediction. Los datos provienen de archivos Parquet, el target es
churned, usa scikit-learn, optimiza ROC AUC y aplica el perfil python-ml.
```

Ejemplo con MLflow:

```text
Usa $create-mlops-project para crear en ./forecasting un proyecto de pronóstico de
demanda con LightGBM, métrica WAPE, cobertura mínima de 90% y perfil mlflow-local.
```

Ejemplo con Databricks:

```text
Usa $create-mlops-project para crear en ./fraud_detection un sistema de clasificación
con perfil databricks-mlops. Los datos están en Unity Catalog, la métrica de aprobación
es recall >= 0.85 y el despliegue debe incluir Model Serving y smoke tests.
```

Codex puede completar valores seguros por defecto —Python 3.12, `uv`, 85% de cobertura
y el perfil más pequeño que satisfaga el caso—, pero solicitará decisiones que cambien
materialmente la solución. El directorio de destino debe estar vacío para evitar que la
skill sobrescriba un proyecto existente.

## Validar un proyecto generado

El validador comprueba la estructura requerida, la configuración de calidad, las pruebas,
los documentos del perfil, placeholders pendientes y posibles archivos sensibles. No
modifica el proyecto analizado.

Desde este repositorio:

```powershell
uv sync --dev
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile auto
```

También puedes seleccionar el perfil explícitamente:

```powershell
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile python-ml
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile mlflow-local
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile databricks-mlops
```

El comando termina con código `0` cuando no encuentra errores y con código `1` cuando el
proyecto incumple alguna regla estructural.

## Desarrollo y controles de calidad

Para verificar cambios en esta skill:

```powershell
uv sync --dev
uv run ruff check .
uv run mypy
uv run pytest
```

La suite exige al menos 85% de cobertura. El workflow de GitHub Actions ejecuta los
controles automáticamente en cada cambio configurado.

## Seguridad y alcance

- No guardes tokens, contraseñas, archivos `.env`, certificados ni claves privadas en el
  repositorio.
- Las pruebas externas no se ejecutan por defecto y deben reportarse como no ejecutadas
  cuando faltan credenciales.
- Una simulación o un mock local no equivale a validar MLflow, Databricks, un registro de
  modelos o un endpoint productivo.
- La skill está diseñada para proyectos ML nuevos; no es la herramienta indicada para
  modificar repositorios existentes ni para crear paquetes Python genéricos.

## Estructura de este repositorio

```text
.
├── SKILL.md                     # Contrato y flujo principal de la skill
├── agents/openai.yaml           # Metadatos mostrados por Codex
├── references/                  # Estándares de arquitectura, calidad y operación
├── scripts/validate_project.py  # Validador estructural de proyectos generados
├── tests/                       # Pruebas del validador
├── .github/workflows/ci.yml     # Integración continua
└── pyproject.toml               # Dependencias y herramientas de calidad
```
