# Solución de problemas

Esta guía separa fallos de instalación de la skill, generación, validación y controles de
calidad. Empieza por reproducir el problema con el comando más pequeño posible y conserva
la salida completa.

## La skill no aparece o no se activa

### Síntomas

- Codex no reconoce `$create-mlops-project`;
- la solicitud se trata como una tarea genérica;
- los cambios de `SKILL.md` no parecen aplicarse.

### Comprobaciones

1. confirma que el archivo se llama exactamente `SKILL.md`;
2. confirma que está en la raíz de la carpeta instalada;
3. revisa que el frontmatter YAML contenga `name` y `description` válidos;
4. evita una carpeta duplicada por un clone mal ubicado;
5. abre una sesión nueva después de instalar o actualizar;
6. para una instalación personal, comprueba que la carpeta esté bajo
   `$HOME/.agents/skills`;
7. si instalaste el plugin, comprueba su estado en Codex y prueba en una conversación
   nueva.

Estructura esperada:

```text
create-mlops-project/
├── SKILL.md
├── agents/
├── references/
└── scripts/
```

## El destino ya contiene archivos

La skill está diseñada para destinos nuevos. Un directorio no vacío puede contener trabajo
del usuario y no debe sobrescribirse automáticamente.

Opciones seguras:

- elegir otra carpeta vacía;
- mover el trabajo existente mediante un proceso explícito y revisado;
- pedir una adaptación de repositorio existente, entendiendo que queda fuera del alcance
  normal de esta skill.

No resuelvas el conflicto borrando el directorio sin confirmar la ruta y la intención.

## `uv` no encuentra una versión de Python compatible

Este repositorio requiere Python 3.12 o 3.13. Comprueba:

```powershell
python --version
uv python list
```

Después instala o selecciona una versión compatible según la política de tu entorno y
repite:

```powershell
uv sync --locked --dev
```

No edites el rango de Python solo para silenciar el error sin verificar compatibilidad de
dependencias y CI.

## `uv` no puede acceder a su caché

En entornos restringidos puede aparecer un error de permisos sobre la caché global. Usa
un entorno con permisos apropiados o configura una caché permitida según tu runtime. No
desactives el lock ni cambies dependencias para resolver un problema de filesystem.

## Pytest falla al crear `tmp_path` en Windows

Síntoma frecuente:

```text
PermissionError: Access is denied ... pytest-of-user
```

Ejecuta las pruebas con una base temporal dentro del repositorio:

```powershell
uv run pytest --basetemp .pytest-tmp
```

`.pytest-tmp/` ya está ignorado por Git. Este cambio afecta la ubicación temporal, no la
lógica de las pruebas.

## La branch coverage queda por debajo de 90%

Primero revisa el reporte de líneas y branches faltantes. Agrega pruebas sobre
comportamiento y contratos, especialmente:

- resolución de perfiles;
- errores de configuración;
- reglas nuevas del validador;
- caminos del CLI;
- garantía de no modificación.

No excluyas código arbitrariamente ni agregues asserts vacíos para elevar el porcentaje.

## Ruff falla

Ejecuta por separado:

```powershell
uv run ruff check .
uv run ruff format --check .
```

Para aplicar correcciones seguras y revisar el diff:

```powershell
uv run ruff check . --fix
uv run ruff format .
git diff
```

No aceptes una corrección automática sin revisar cambios semánticos o archivos ajenos.

Si el validador reporta `ruff-config`, revisa antes de ejecutar Ruff:

- versión `ruff>=0.16.5,<0.17`;
- `target-version = "py312"`, línea 100 y `preview = false`;
- conjunto curado completo;
- ausencia de `ALL`, ignores globales y exclusiones de carpetas productivas;
- `S101`, `T201` y `N999` limitados a sus rutas autorizadas;
- builtins y namespace packages Databricks sólo en ese perfil.

Consulta [Ruff estricto](ruff.md) para la configuración completa, explicación de códigos,
política de `noqa` y migración paso a paso.

## mypy falla

Reproduce ambas variantes de CI:

```powershell
uv run mypy --no-incremental --python-version 3.12
uv run mypy --no-incremental --python-version 3.13
```

La configuración es estricta. Corrige la causa en vez de propagar `Any`, agregar casts
internos o ignorar el error globalmente. Verifica:

- tipos de colecciones y retornos;
- estrechamiento después de leer TOML;
- tipos de argumentos del CLI;
- casts justificados en fronteras dinámicas.

Si una librería carece de tipos, instala su paquete `types-*`, crea un stub local o limita
cualquier excepción a su namespace externo concreto. Si el validador informa `mypy-config`,
revisa versión, stubs de PyYAML, alcance `src`/`tests`, flags obligatorios, códigos opt-in,
exclusiones y overrides. La guía [mypy estricto](mypy.md) explica cada control, ejemplos,
migración y diagnóstico por código.

## `uv build` falla

Comprueba la sección de build en `pyproject.toml` y que el paquete `scripts` siga siendo
importable. Un build exitoso verifica packaging, no la corrección del validador; ejecuta
también la suite.

## Error `path`

La ruta suministrada no existe o no es un directorio. Usa una ruta absoluta y evita
errores de comillas:

```powershell
Resolve-Path C:\ruta\al\proyecto
uv run python skills/create-mlops-project/scripts/validate_project.py C:\ruta\al\proyecto
```

Si la ruta contiene espacios, escríbela entre comillas.

## Error `profile`

`.mlops-profile` solo admite:

```text
python-ml
mlflow-local
databricks-mlops
```

El archivo debe contener un único valor. Corregirlo no basta si la estructura todavía no
cumple el perfil seleccionado.

## Error `missing`

No crees archivos vacíos solo para pasar la comprobación. Abre
[project-contract.md](project-contract.md), identifica la responsabilidad del componente
y agrega una implementación o documento útil.

## Error `pyproject`

Valida primero la sintaxis TOML. Revisa comillas, tablas repetidas, arrays y separadores.
Después ejecuta:

```powershell
uv lock --check
uv sync --locked
```

## Error `quality-config` o `coverage-config`

El proyecto debe declarar configuración para Ruff, mypy, pytest y coverage. Copiar tablas
vacías puede satisfacer presencia sin cumplir intención; configura rutas, strictness,
testpaths, branch coverage y umbral de forma consciente.

## Error `package`

Debe existir al menos un directorio de paquete bajo `src`. Asegúrate también de que el
backend de build incluya ese paquete y que las pruebas importen el código instalado, no
rutas manipuladas manualmente.

## Error `tests`

El validador busca `test_*.py` de forma recursiva bajo `tests`. Agrega pruebas reales. Un
archivo vacío puede eliminar el issue estructural, pero no cumplirá cobertura ni calidad.

## Errores `config-layout`, `config-format` o `config-secret`

Comprueba `configs/base.yaml`, `configs/local.yaml` y, para Databricks, `dev.yaml` y
`prod.yaml`. Cada uno debe ser un mapping con `config_version: 1`. No coloques tokens,
passwords ni claves en YAML; usa variables de entorno o Secret Scopes. Si el archivo es
válido pero Pydantic falla, revisa tipos estrictos y claves desconocidas en
[Configuración](configuration.md).

## Error `python-layout`

Debe existir un único paquete principal bajo `src/`. Mueve funciones, clases,
transformaciones y reglas productivas a ese paquete. Los tests pueden mantener helpers y
fixtures bajo `tests/`; los notebooks no.

## Errores `notebook-layout` o `notebook-format`

Los notebooks productivos viven en `notebooks/databricks/`. Un `.py` necesita el marcador
Databricks en la primera línea; un `.ipynb` necesita nbformat 4, outputs vacíos y
`execution_count: null`. No conserves dos formatos con el mismo nombre base ni definas
funciones o clases dentro del notebook.

## Error `databricks-task`

Confirma que el bundle contiene al menos un `notebook_task` y que cada `notebook_path`
apunta a un archivo existente bajo `notebooks/databricks/`. Las rutas de exploración y
los notebooks inexistentes no son válidos.

## Error `mlflow-run`

Sólo `<package>/tracking/mlflow.py` puede llamar a `mlflow.start_run`. Implementa
`start_experiment_run`, activa `mlflow.autolog` dentro del run y antes de `yield`, registra
la configuración resuelta y úsalo desde cada workflow. Consulta
[Notebooks y MLflow](notebooks-mlflow.md).

## Error `mlflow-security`

El proyecto contiene una señal productiva de MLflow AI Gateway: por ejemplo
`auth_config.api_base`, `CreateGatewaySecret`, una ruta `/api/2.0/mlflow/gateway` o
`/gateway/proxy`. Los perfiles generados admiten MLflow Tracking, pero mantienen AI
Gateway deshabilitado para evitar una ruta SSRF no demostrada como segura.

Retira la configuración o el código. No resuelvas el error cambiando el nombre de la
clave, concatenando la ruta u omitiendo el validador. Si AI Gateway es un requisito real,
abre un cambio de contrato con revisión de seguridad, versión upstream verificada,
autorización administrativa, allowlist, egress y pruebas de bypass. Sigue
[Seguridad de MLflow](mlflow-security.md).

## Error `workflow-contract`

Comprueba primero el filename y el nombre público. Todos los perfiles requieren
`01-code-quality.yml` y `02-security.yml`; Databricks agrega `03-databricks.yml` y
`04-production-monitoring.yml`.

Después revisa:

- `permissions.contents: read` en la raíz;
- ausencia de `pull_request_target`;
- cada `uses:` fijado a un SHA hexadecimal completo de 40 caracteres;
- `databricks bundle validate` en el workflow 03;
- `schedule`, `workflow_dispatch` y un job de monitoreo en el workflow 04.

El comentario `# v4` ayuda a personas, pero no reemplaza el SHA inmutable. Consulta
[Workflows](ci-workflows.md) para entender triggers, credenciales y required checks.

## Pytest no reconoce un marker

La suite usa `--strict-markers`. Declara el marker en `[tool.pytest.ini_options].markers`,
explica su frontera en [Estrategia de pruebas](testing-strategy.md) y vuelve a ejecutar
`uv run pytest --markers`. No corrijas un typo agregando un segundo marker equivalente.

## Una prueba de Hypothesis excede el deadline

Primero determina si hay una regresión de rendimiento. Si la prueba toca filesystem y la
variación pertenece al sistema operativo, usa un límite explícito o `deadline=None` sólo
en esa propiedad. El timeout global de pytest debe permanecer activo.

## Error `mlflow`

El perfil requiere una dependencia cuyo nombre comience por `mlflow`. Agrégala con un
rango de versión explícito, actualiza `uv.lock` y configura tracking local aislado.

## Error `placeholder`

Busca todos los marcadores antes de reemplazar:

```powershell
rg -n "TODO|FIXME|CHANGEME|\{\{" C:\ruta\al\proyecto
```

Sustituye cada marcador por una decisión del dominio. Si el texto es documentación que
explica literalmente un marcador, considera reformularlo para no colisionar con la regla.

## Error `example-leak`

Indica que quedó un nombre específico de dataset demostrativo. Revisa no solo esa palabra,
sino también columnas, métricas, rutas y supuestos copiados que puedan no pertenecer al
problema real.

## Error `secret-file`

1. no muestres el contenido en logs;
2. retira el archivo del área de commit;
3. agrégalo a `.gitignore` cuando corresponda;
4. carga el valor desde variables o un gestor de secretos;
5. si el secreto llegó a Git, considéralo comprometido y rótalo;
6. limpia el historial solo mediante un procedimiento revisado y coordinado.

Cambiar el nombre del archivo sin retirar el secreto no soluciona el riesgo.

## El validador pasa pero el proyecto falla

Es posible y esperado: el validador comprueba estructura. Ejecuta:

```powershell
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

Después revisa datos, pipeline e integraciones específicas. Un resultado estructural
exitoso no garantiza que el modelo entrene o alcance sus umbrales.

## Databricks no puede validarse

Clasifica el estado con precisión:

- **no ejecutado:** faltan credenciales, red o workspace autorizado;
- **fallo local:** bundle, build o configuración inválida antes del workspace;
- **fallo externo:** permisos, recursos, Job, registro o endpoint falló en el workspace;
- **exitoso:** la comprobación concreta se ejecutó contra el entorno autorizado.

No reemplaces un fallo externo por un mock y lo reportes como éxito.

## Diagnóstico mínimo para solicitar ayuda

Incluye:

- sistema operativo;
- `python --version` y `uv --version`;
- comando exacto;
- perfil elegido;
- salida completa sin secretos;
- `git status --short`;
- si el fallo ocurre en local, CI o infraestructura externa.

No adjuntes `.env`, tokens, perfiles de Databricks ni claves privadas.
