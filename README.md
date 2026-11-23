# Create MLOps Project

Skill de Codex para diseñar y crear repositorios de machine learning orientados a
producción. Convierte el contrato de un problema ML en una base de proyecto reproducible,
verificable y operable, con una complejidad proporcional al entorno donde se ejecutará.

> Este repositorio contiene la **skill, sus estándares y su validador**. No contiene un
> dataset, un modelo entrenado ni una solución ML de dominio lista para desplegar.

## Primer resultado en cinco minutos

Necesitas Git, Python 3.12 o 3.13 y [`uv`](https://docs.astral.sh/uv/). El primer recorrido
es completamente local y no requiere Databricks ni credenciales.

```text
git clone https://github.com/cristopheranbus/mlops_project.git
cd mlops_project
uv sync --locked --dev
uv run pytest --basetemp .pytest-tmp
```

Resultado esperado: todas las pruebas pasan y la branch coverage es al menos 90%. Después pide
a Codex:

```text
Usa $create-mlops-project para crear ./first_ml_project. Es una clasificación binaria
con datos CSV, target accepted, scikit-learn, ROC AUC y perfil python-ml. Incluye un
primer entrenamiento local con datos sintéticos y sin credenciales.
```

El proyecto resultante explica cómo instalar dependencias, entrenar, cambiar configuración
y ejecutar pruebas. Si nunca has contribuido a un repositorio, sigue el
[tutorial inicial completo](docs/beginner-tutorial.md).

## Qué problema resuelve

Crear un repositorio ML serio exige tomar decisiones que suelen quedar implícitas o
distribuidas entre scripts, notebooks y conocimiento del equipo: estructura de paquetes,
fronteras entre componentes, configuración, reproducibilidad, pruebas, cobertura,
trazabilidad de experimentos, criterios de aprobación y operación.

`create-mlops-project` convierte esas decisiones en un contrato explícito y genera un
repositorio nuevo de manera adaptativa con Codex o como baseline determinista mediante CLI:

- layout `src` e imports basados en paquetes;
- separación entre configuración, acceso a datos, features, entrenamiento, evaluación e
  inferencia;
- pruebas unitarias, de contrato e integración cuando corresponda;
- matrices dinámicas con `pytest_generate_tests`, property-based testing, timeouts y
  90% de branch coverage;
- mutation testing programado con resultados auditables y fallos operativos bloqueantes;
- Ruff, mypy, pytest, cobertura y build como puertas de calidad;
- dependencias bloqueadas con `uv`;
- CI en GitHub Actions;
- workflows separados para calidad, seguridad, Databricks y monitoreo productivo;
- documentación técnica y operativa adecuada al perfil;
- manejo de integraciones externas sin versionar credenciales;
- un límite preventivo que mantiene MLflow AI Gateway deshabilitado y detecta su
  configuración con `mlflow-security`;
- un camino local que no depende de servicios productivos.

La skill está pensada para **crear proyectos nuevos**. No debe emplearse como migrador
automático de repositorios existentes ni como generador de paquetes Python genéricos.

## Qué genera

La forma exacta depende del problema y del perfil, pero el núcleo esperado es:

```text
proyecto_ml/
├── .github/workflows/
│   ├── 01-code-quality.yml
│   ├── 02-security.yml
│   ├── 03-databricks.yml
│   └── 04-production-monitoring.yml
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
│   └── exploration/
├── docs/
│   ├── architecture.md
│   ├── configuration.md
│   └── testing.md
├── src/
│   └── paquete_ml/
│       ├── config/
│       ├── data/
│       ├── features/
│       ├── modeling/
│       ├── tracking/
│       └── workflows/
└── tests/
```

Los perfiles con MLflow y Databricks agregan contratos de tracking, evaluación,
registro, despliegue y operación. La estructura detallada está en
[Contrato del proyecto generado](docs/project-contract.md).

Hay un solo paquete principal. Toda función productiva vive bajo `src/<package>/`; los
notebooks únicamente reciben parámetros e invocan workflows. La configuración se valida
con Pydantic y cada ejecución conserva el entorno, los overrides, un hash SHA-256 y
`resolved_config.yaml` sin secretos.

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

### 2. Instalar para uso personal

La [documentación oficial de Codex sobre skills](https://learn.chatgpt.com/docs/build-skills)
indica que las skills personales se descubren bajo `$HOME/.agents/skills`. Clona el
repositorio en una carpeta de desarrollo y copia o enlaza la skill contenida en
`skills/create-mlops-project/` hacia esa ubicación.

También puedes pedirle al instalador integrado que use la carpeta de la skill publicada:

```text
Usa $skill-installer para instalar create-mlops-project desde
https://github.com/cristopheranbus/mlops_project/tree/main/skills/create-mlops-project
```

Codex detecta cambios automáticamente; si la actualización no aparece, inicia una sesión
nueva. Para compartir una capacidad estable, OpenAI recomienda distribuirla como plugin.
Este repositorio incluye el manifiesto oficial `.codex-plugin/plugin.json` y la skill bajo
`skills/`, según la
[documentación oficial de plugins](https://learn.chatgpt.com/docs/build-plugins).

### 3. Invocarla

```text
Usa $create-mlops-project para crear en ./customer_churn un proyecto de clasificación.
Los datos llegan como Parquet, el target es churned, usa scikit-learn, optimiza ROC AUC,
exige al menos 0.82 en validación y aplica el perfil python-ml.
```

La skill confirma o infiere el contrato, crea el proyecto en un destino vacío, ejecuta el
validador estructural y corre los controles locales aplicables.

### 4. Usarla como CLI determinista

El paquete también expone un generador no interactivo para automatización y bootstrapping:

```powershell
uv tool install .
create-mlops-project C:\proyectos\customer_churn `
  --name customer-churn `
  --profile mlflow-local
```

Agrega `--embed-skill` para incluir la skill en
`.agents/skills/create-mlops-project/` dentro del nuevo repositorio. Así todo el equipo usa el
mismo contrato. El CLI crea un baseline genérico y reproducible; para implementar datos,
features, métricas y gates específicos del dominio, usa la generación adaptativa de la skill.
El destino debe estar vacío en ambos casos.

Consulta [Modos de distribución y generación](docs/distribution.md) para elegir entre skill
personal, skill de repositorio, plugin y CLI.

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

Si faltan datos, la skill usa por defecto Python 3.12, `uv`, 90% de branch coverage y el perfil
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
uv run python skills/create-mlops-project/scripts/validate_project.py `
  C:\ruta\al\proyecto --profile auto
```

Perfiles explícitos:

```powershell
uv run python skills/create-mlops-project/scripts/validate_project.py C:\ruta\al\proyecto --profile python-ml
uv run python skills/create-mlops-project/scripts/validate_project.py C:\ruta\al\proyecto --profile mlflow-local
uv run python skills/create-mlops-project/scripts/validate_project.py C:\ruta\al\proyecto --profile databricks-mlops
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
| [Tutorial inicial](docs/beginner-tutorial.md) | Desde instalar herramientas hasta el primer PR | Principiantes |
| [Configuración](docs/configuration.md) | Perfiles YAML, Pydantic, overrides, secretos y hash | Usuarios y ML engineers |
| [Notebooks y MLflow](docs/notebooks-mlflow.md) | Notebook-first, workflows, autolog y trazabilidad | ML engineers y Databricks |
| [Seguridad de MLflow](docs/mlflow-security.md) | Límite de AI Gateway, SSRF, despliegue y respuesta | Usuarios, seguridad y operadores |
| [Ruff estricto](docs/ruff.md) | Reglas curadas, excepciones, diagnóstico y migración | Principiantes y contribuidores |
| [Estrategia de pruebas](docs/testing-strategy.md) | Hook dinámico, capas, Mutmut, baseline y diagnóstico | Contribuidores y mantenedores |
| [mypy estricto](docs/mypy.md) | Tipado estático, códigos opt-in, stubs, adapters y migración | Principiantes, ML engineers y mantenedores |
| [Workflows](docs/ci-workflows.md) | Calidad, seguridad, Databricks y monitoreo | ML engineers y operadores |
| [Migración v0.1.0](docs/migration-v0.1.md) | Adopción del nuevo contrato | Mantenedores |
| [Perfiles](docs/profiles.md) | Selección, capacidades, fronteras y evolución | Tech leads y ML engineers |
| [Contrato del proyecto](docs/project-contract.md) | Entradas, estructura y criterios de completitud | Usuarios y revisores |
| [Diseño interno](docs/design.md) | Componentes de esta skill y flujo del validador | Mantenedores |
| [Validación](docs/validation.md) | CLI, reglas, códigos, límites y CI | Usuarios y mantenedores |
| [Distribución](docs/distribution.md) | Skill personal, repositorio, plugin y CLI | Usuarios y equipos |
| [Evaluación](docs/evaluation.md) | Casos de activación explícita, implícita y negativa | Mantenedores |
| [Ejemplos](docs/examples.md) | Solicitudes completas para casos frecuentes | Usuarios |
| [Solución de problemas](docs/troubleshooting.md) | Fallos comunes y diagnóstico | Todos |
| [Gobernanza](docs/governance.md) | Ramas, revisión, Dependabot y controles hospedados | Contribuidores y mantenedores |
| [Contribución](CONTRIBUTING.md) | Desarrollo, pruebas y cambios de reglas | Contribuidores |
| [Seguridad](SECURITY.md) | Credenciales, reportes y respuesta ante filtraciones | Todos |

Los archivos bajo
[`skills/create-mlops-project/references/`](skills/create-mlops-project/references/) son
estándares normativos consumidos por la propia skill. Los documentos bajo [`docs/`](docs/)
explican cómo usarla y mantenerla.

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

La configuración actual exige al menos 90% de branch coverage. La suite también comprueba que
los enlaces Markdown locales resuelvan y que el índice enumere todas las guías. GitHub
Actions repite lint, formato, tipado, una matriz Linux/Windows para Python 3.12/3.13,
package smoke tests y controles de seguridad en pull requests y pushes a `dev` y `main`.

El análisis programado de Mutmut tiene una baseline reproducible del 2 de septiembre de
2026: 2.406 mutantes, 1.689 eliminados y 717 sobrevivientes, equivalente a 70,20% sobre
mutantes clasificados. La puntuación todavía es informativa; una falla de ejecución,
recolección o exportación sí deja el workflow en rojo. Consulta la
[estrategia de pruebas](docs/testing-strategy.md#baseline-auditada) para interpretar y
reproducir el resultado.

La configuración versionada limita y agrupa los PR de Dependabot. Las opciones hospedadas
de GitHub —Dependabot alerts, Dependabot security updates, secret scanning y push
protection— se administran aparte y deben comprobarse al habilitar un repositorio remoto.
La [guía de gobernanza](docs/governance.md#controles-de-seguridad-hospedados) explica qué
queda en Git y qué vive en la configuración de GitHub.

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

Distribuido bajo [Apache License 2.0](LICENSE). Las contribuciones aceptadas se incorporan
bajo los términos descritos en esa licencia.
