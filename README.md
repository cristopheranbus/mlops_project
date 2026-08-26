# Create MLOps Project

Skill de Codex para diseñar y crear repositorios de machine learning orientados a
producción. Convierte el contrato de un problema ML en una base de proyecto reproducible,
verificable y operable, con una complejidad proporcional al entorno donde se ejecutará.

> Este repositorio contiene la **skill, sus estándares y su validador**. No contiene un
> dataset, un modelo entrenado ni una solución ML de dominio lista para desplegar.

## Contenido

- [Qué problema resuelve](#qué-problema-resuelve)
- [Qué genera](#qué-genera)
- [Perfiles disponibles](#perfiles-disponibles)
- [Inicio rápido](#inicio-rápido)
- [Cómo formular una solicitud útil](#cómo-formular-una-solicitud-útil)
- [Flujo de trabajo](#flujo-de-trabajo)
- [Validación](#validación)
- [Documentación detallada](#documentación-detallada)
- [Desarrollo de la skill](#desarrollo-de-la-skill)
- [Seguridad y límites](#seguridad-y-límites)

## Qué problema resuelve

Crear un repositorio ML serio exige tomar decisiones que suelen quedar implícitas o
distribuidas entre scripts, notebooks y conocimiento del equipo: estructura de paquetes,
fronteras entre componentes, configuración, reproducibilidad, pruebas, cobertura,
trazabilidad de experimentos, criterios de aprobación y operación.

`create-mlops-project` convierte esas decisiones en un contrato explícito y genera un
repositorio nuevo con:

- layout `src` e imports basados en paquetes;
- separación entre configuración, acceso a datos, features, entrenamiento, evaluación e
  inferencia;
- pruebas unitarias, de contrato e integración cuando corresponda;
- Ruff, mypy, pytest, cobertura y build como puertas de calidad;
- dependencias bloqueadas con `uv`;
- CI en GitHub Actions;
- documentación técnica y operativa adecuada al perfil;
- manejo de integraciones externas sin versionar credenciales;
- un camino local que no depende de servicios productivos.

La skill está pensada para **crear proyectos nuevos**. No debe emplearse como migrador
automático de repositorios existentes ni como generador de paquetes Python genéricos.

## Qué genera

La forma exacta depende del problema y del perfil, pero el núcleo esperado es:

```text
proyecto_ml/
├── .github/workflows/ci.yml
├── .gitignore
├── .mlops-profile
├── README.md
├── pyproject.toml
├── uv.lock
├── configs/
├── docs/
│   ├── architecture.md
│   ├── configuration.md
│   └── testing.md
├── src/
│   └── paquete_ml/
└── tests/
```

Los perfiles con MLflow y Databricks agregan contratos de tracking, evaluación,
registro, despliegue y operación. La estructura detallada está en
[Contrato del proyecto generado](docs/project-contract.md).

## Perfiles disponibles

| Perfil | Elegir cuando | Servicios externos | Complejidad operativa |
| --- | --- | --- | --- |
| `python-ml` | El modelo se desarrolla y ejecuta localmente o en un runtime Python simple | Ninguno obligatorio | Baja |
| `mlflow-local` | Se necesita trazabilidad de experimentos, artefactos, evaluación o registro local | MLflow local; remoto solo si se solicita | Media |
| `databricks-mlops` | Se requiere un flujo gobernado en Databricks con promoción y serving | Databricks, Unity Catalog y MLflow | Alta |

Regla práctica: elegir el perfil más pequeño que satisfaga el caso real. Agregar
infraestructura antes de necesitarla aumenta el costo de mantenimiento y la superficie de
fallo.

Consulta [Perfiles y criterios de elección](docs/profiles.md) para ver requisitos,
fronteras de ejecución, artefactos y caminos de evolución.

## Inicio rápido

### 1. Requisitos

- Codex con soporte para skills locales.
- Git para obtener y actualizar el repositorio.
- Python 3.12 o 3.13 para desarrollar y probar esta skill.
- [`uv`](https://docs.astral.sh/uv/) para resolver dependencias y ejecutar los controles.
- Credenciales externas únicamente si se solicita validar infraestructura real.

### 2. Instalar la skill

Clona el repositorio en la carpeta de skills personales de Codex y conserva
`create-mlops-project` como nombre del directorio:

```powershell
git clone https://github.com/cristopheranbus/mlops_project.git `
  "$env:CODEX_HOME\skills\create-mlops-project"
```

Si tu instalación no define `CODEX_HOME`, usa el directorio de configuración de Codex
correspondiente a tu entorno. El archivo `SKILL.md` debe quedar en la raíz de la carpeta:

```text
skills/
└── create-mlops-project/
    ├── SKILL.md
    ├── agents/
    ├── references/
    ├── scripts/
    └── tests/
```

Después de instalar o actualizar la skill, inicia una nueva sesión de Codex para que el
entorno vuelva a descubrir sus instrucciones.

### 3. Invocarla

```text
Usa $create-mlops-project para crear en ./customer_churn un proyecto de clasificación.
Los datos llegan como Parquet, el target es churned, usa scikit-learn, optimiza ROC AUC,
exige al menos 0.82 en validación y aplica el perfil python-ml.
```

La skill confirma o infiere el contrato, crea el proyecto en un destino vacío, ejecuta el
validador estructural y corre los controles locales aplicables.

Consulta [Guía de inicio](docs/getting-started.md) para la instalación, primera ejecución,
inspección del resultado y actualización de la skill.

## Cómo formular una solicitud útil

Una buena solicitud indica la intención y los límites, no una estructura de archivos
completa. Siempre que sea posible incluye:

| Dato | Ejemplo | Por qué importa |
| --- | --- | --- |
| Nombre y destino | `customer_churn` en `./customer_churn` | Define carpeta, paquete y alcance de escritura |
| Tipo de problema | clasificación binaria | Determina contratos, métricas y pruebas |
| Fuente de datos | Parquet en almacenamiento local | Define el adaptador y el camino reproducible |
| Target | `churned` | Evita ambigüedad en entrenamiento y evaluación |
| Framework | scikit-learn | Condiciona dependencias y serialización |
| Métrica principal | ROC AUC | Define evaluación y criterio de comparación |
| Umbral de aceptación | ROC AUC >= 0.82 | Convierte calidad en una puerta verificable |
| Perfil | `python-ml` | Limita infraestructura y documentación |
| Python y cobertura | Python 3.12; 90% | Ajusta toolchain y quality gates |

Si faltan datos, la skill usa por defecto Python 3.12, `uv`, 85% de cobertura y el perfil
más pequeño compatible. Debe preguntar cuando una decisión cambia materialmente el
resultado.

Hay solicitudes completas para distintos casos en [Ejemplos de uso](docs/examples.md).

## Flujo de trabajo

```text
Solicitud del usuario
        │
        ▼
Contrato del problema
        │  nombre, destino, datos, target, framework,
        │  métrica, umbrales, Python, cobertura y perfil
        ▼
Selección del perfil
        │
        ▼
Generación segura en un destino vacío
        │
        ▼
Validación estructural ──► errores accionables
        │
        ▼
Ruff + formato + mypy + pytest + build
        │
        ▼
Informe de componentes, supuestos y verificaciones
```

Los principios del flujo son:

1. **Contrato antes que código.** Las decisiones del problema deben ser explícitas o
   inferidas de forma segura.
2. **Destino protegido.** No se sobrescribe ni reutiliza un directorio no vacío sin
   autorización explícita.
3. **Complejidad proporcional.** No se agregan MLflow, Databricks, registry o serving si
   el problema no los necesita.
4. **Lógica reusable.** Los notebooks pueden explorar u orquestar, pero el código probado
   vive en el paquete.
5. **Evidencia honesta.** Una prueba local o un mock no se presenta como validación de
   infraestructura productiva.
6. **Secretos fuera de Git.** La configuración versionada es neutral al entorno; las
   credenciales llegan desde el runtime.

## Validación

El repositorio incluye un validador de solo lectura para comprobar invariantes
estructurales de un proyecto generado:

```powershell
uv sync --dev
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile auto
```

Perfiles explícitos:

```powershell
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile python-ml
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile mlflow-local
uv run python scripts/validate_project.py C:\ruta\al\proyecto --profile databricks-mlops
```

El validador revisa rutas requeridas, configuración de herramientas, paquete bajo `src`,
pruebas, requisitos propios del perfil, placeholders y nombres de archivos potencialmente
sensibles. Devuelve código `0` sin errores y código `1` si existe al menos uno.

No ejecuta el pipeline del proyecto, no inspecciona servicios externos, no demuestra que
un modelo sea correcto y no sustituye Ruff, mypy, pytest, build ni pruebas de datos. Su
alcance completo y cada código de error están documentados en
[Validación y diagnóstico](docs/validation.md).

## Documentación detallada

| Documento | Contenido | Audiencia principal |
| --- | --- | --- |
| [Guía de inicio](docs/getting-started.md) | Instalación, primera generación y actualización | Usuarios nuevos |
| [Perfiles](docs/profiles.md) | Selección, capacidades, fronteras y evolución | Tech leads y ML engineers |
| [Contrato del proyecto](docs/project-contract.md) | Entradas, estructura y criterios de completitud | Usuarios y revisores |
| [Diseño interno](docs/design.md) | Componentes de esta skill y flujo del validador | Mantenedores |
| [Validación](docs/validation.md) | CLI, reglas, códigos, límites y CI | Usuarios y mantenedores |
| [Ejemplos](docs/examples.md) | Solicitudes completas para casos frecuentes | Usuarios |
| [Solución de problemas](docs/troubleshooting.md) | Fallos comunes y diagnóstico | Todos |
| [Gobernanza](docs/governance.md) | PRs, revisión, protección de `main` y notificaciones | Contribuidores y mantenedores |
| [Contribución](CONTRIBUTING.md) | Desarrollo, pruebas y cambios de reglas | Contribuidores |
| [Seguridad](SECURITY.md) | Credenciales, reportes y respuesta ante filtraciones | Todos |

Los archivos bajo [`references/`](references/) son estándares normativos consumidos por
la propia skill. Los documentos bajo [`docs/`](docs/) explican cómo usarla y mantenerla.

## Desarrollo de la skill

Instala el entorno bloqueado y ejecuta todos los gates locales:

```powershell
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --basetemp .pytest-tmp
uv build
```

La configuración actual exige al menos 85% de cobertura. La suite también comprueba que
los enlaces Markdown locales resuelvan y que el índice enumere todas las guías. GitHub
Actions repite lint, formato, tipado y pruebas en pull requests y pushes a `main`.

Antes de cambiar una regla del validador, documenta el contrato esperado, agrega pruebas
positivas y negativas, y confirma que el script continúa sin modificar el proyecto
analizado. Consulta [CONTRIBUTING.md](CONTRIBUTING.md).

## Seguridad y límites

- No versiones `.env`, `.databrickscfg`, certificados, claves privadas, tokens ni
  configuración productiva sensible.
- Usa valores ficticios inequívocos en ejemplos; nunca credenciales con formato real.
- Las pruebas externas requieren infraestructura y autorización reales. Si no se ejecutan,
  deben declararse como **no ejecutadas**, no como exitosas.
- El validador detecta algunos nombres de archivos sensibles, pero no es un escáner de
  secretos completo.
- El perfil `databricks-mlops` genera contratos y recursos, pero solo una ejecución
  autorizada contra el workspace puede validar permisos, identidades, bundles, Jobs,
  registry o serving.
- La publicación remota y el despliegue no forman parte implícita de la generación; se
  realizan solo cuando el usuario los solicita por separado.

Para reportar una vulnerabilidad o una exposición accidental, sigue
[SECURITY.md](SECURITY.md).

## Contribuciones

Las contribuciones se realizan mediante pull requests. `@cristopheranbus` figura como code
owner global para recibir solicitudes de revisión. Antes de abrir un PR, consulta
[CONTRIBUTING.md](CONTRIBUTING.md) y la [política de gobernanza](docs/governance.md).

## Licencia

El repositorio todavía no incluye un archivo de licencia. Antes de distribuirlo o aceptar
contribuciones externas, define y agrega una licencia compatible con el uso previsto.
