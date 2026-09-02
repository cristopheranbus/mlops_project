# Workflows de CI, seguridad, Databricks y monitoreo

Los nombres numerados hacen visible el orden mental del sistema en GitHub Actions. No
significa que todos se ejecuten secuencialmente: cada workflow tiene su trigger, permisos
y frontera operativa.

## Vista final

Todos los proyectos generados incluyen:

```text
01 - Code quality and package validation
02 - Repository security scanning
```

`databricks-mlops` agrega:

```text
03 - Databricks bundle validation and deployment
04 - Production model monitoring
```

Este repositorio es la fuente de la skill, no un modelo desplegado. Por eso sus workflows
`03` y `04` validan el contrato generado de manera offline y conservan la palabra
`contract`. Un proyecto real generado elimina ese sufijo y conecta sus entornos
autorizados.

## 01 — Code quality and package validation

### Propósito

Impedir que un PR rompa estilo, tipos, comportamiento, compatibilidad o packaging.

### Jobs

`branch-policy` verifica que una feature apunte a `dev`, que sólo `dev` pueda promoverse a
`main` y que Dependabot nunca abra cambios contra `main`. `static-analysis` ejecuta lock
check, Ruff, formato y smoke del CLI. Ruff se ejecuta
con `ruff check . --output-format=github` y `ruff format --check .`: CI informa hallazgos,
pero nunca aplica `--fix` ni reescribe el código.

`type-check` ejecuta mypy sin caché en una matriz Ubuntu con Python 3.12 y 3.13. Publica un
JUnit por versión incluso al fallar, y aplica el contrato explicado en [mypy estricto](mypy.md).
La ejecución se separa de `static-analysis` para que GitHub identifique claramente qué versión
falló y para no duplicar trabajo. `tests` usa una
matriz de Python 3.12/3.13 sobre Ubuntu y Windows. `package` construye el wheel, lo instala
en un entorno separado y comprueba imports. `quality` es el agregador estable que puede
configurarse como required check.

`mutation-analysis` se ejecuta de manera programada o manual. La puntuación permanece como
señal informativa y no forma parte del agregador hasta establecer una baseline y clasificar
mutantes equivalentes. El job no oculta fallos operativos: si Mutmut no puede recolectar
estadísticas o ejecutar la suite seleccionada, la ejecución programada o manual queda roja.
La selección se limita a las pruebas que ejercitan el validador para que el workspace aislado
`mutants/` no intente resolver documentación u otros archivos ajenos a la mutación. Durante
esa ejecución, pytest antepone el código copiado en `mutants/` al paquete instalado en modo
editable mediante un bootstrap condicionado por `MUTANT_UNDER_TEST`; esto garantiza que las
pruebas observan cada mutante y no el checkout original, sin alterar las ejecuciones normales.

GitHub documenta las matrices como una forma de crear variaciones de un job para varias
versiones y sistemas operativos: [matrix strategies](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations).

### Fallos habituales

- Ruff: consulta [Ruff estricto](ruff.md), corrige la primera regla y vuelve a ejecutar
  localmente. Si usas `--fix`, revisa el diff antes del commit.
- mypy: alinea el tipo público; no uses `Any` para ocultar el contrato.
- un test falla sólo en Windows: revisa paths, encoding y permisos.
- package smoke falla: el código funcionaba desde el checkout pero no fue incluido en el wheel.
- coverage falla: identifica la rama sin evidencia antes de aumentar el umbral o excluirla.

### Artefactos

Cada combinación conserva JUnit y coverage XML. El job de package conserva sdist y wheel.
Los artefactos facilitan diagnóstico; no contienen credenciales ni datasets privados.

## 02 — Repository security scanning

### CodeQL

Analiza Python y workflows de GitHub Actions. El job recibe `security-events: write` sólo
para publicar resultados; el resto del workflow conserva `contents: read`. GitHub explica
los lenguajes y modos soportados en [Code scanning con CodeQL](https://docs.github.com/en/code-security/code-scanning/introduction-to-code-scanning/about-code-scanning-with-codeql).

### Dependency Review

Se ejecuta en pull requests y bloquea dependencias vulnerables introducidas por cambios
en manifests o lockfiles. Consulta la
[documentación oficial](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-dependency-review).

### Auditoría del lock

Se exportan sólo dependencias runtime desde `uv.lock`, omitiendo el proyecto editable, y
`pip-audit` las compara con
advisories conocidos. Un finding debe investigarse; no se ignora globalmente. Una
excepción temporal documenta paquete, vulnerabilidad, exposición real, mitigación,
responsable y vencimiento.

### Acciones inmutables

Cada `uses:` apunta a un SHA completo y conserva un comentario con la versión legible.
Dependabot puede proponer el SHA nuevo. Esto evita que un tag mutable cambie código sin un
PR visible.

Dependabot agrupa los cambios periódicos por ecosistema y los propone mensualmente. Las
actualizaciones de seguridad conservan un grupo separado y prioritario. La configuración,
los límites y el procedimiento de revisión están documentados en
[Gobernanza](governance.md#dependabot-sin-avalancha-de-pull-requests).

### Permisos y triggers

La raíz de cada workflow declara:

```yaml
permissions:
  contents: read
```

Los jobs amplían únicamente lo indispensable. El validador rechaza
`pull_request_target` porque no debe combinar contexto privilegiado con ejecución de código
no confiable. GitHub reúne estas prácticas en su
[Secure use reference](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).

## 03 — Databricks bundle validation and deployment

### Pull requests

Siempre se ejecutan validaciones offline:

- estructura de configuración;
- formato de notebooks;
- imports de workflows;
- rutas de `notebook_task`;
- wheel instalable;
- ausencia de secretos;
- targets y variables declarativas.

Un proyecto real puede ejecutar `databricks bundle validate -t dev` con identidad de
corta duración. Un PR de un fork nunca recibe credenciales.

### Merge a main

Los pushes a `dev` pueden desplegar desarrollo. `main` queda reservado para publicación o
acciones productivas después de una promoción `dev → main`. El deploy de desarrollo usa:

- GitHub Environment `databricks-dev`;
- workload identity u OIDC;
- target explícito;
- concurrency para evitar despliegues superpuestos;
- smoke test del Job desplegado;
- evidencia de bundle, commit y run.

Producción usa otro environment con aprobación. Validar no equivale a desplegar y desplegar
no equivale a ejecutar correctamente. Databricks documenta `bundle validate`, targets y
deploy en la [referencia oficial de bundle commands](https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands).

## 04 — Production model monitoring

### Propósito

Detectar deterioro después del despliegue sin entrenar, aprobar o promover modelos como
efecto lateral.

### Entradas mínimas

- versión exacta del modelo;
- `config.hash` y `config.version`;
- ventana temporal y baseline;
- tabla de inferencias;
- ground truth cuando esté disponible;
- umbrales versionados;
- owner y canal de escalamiento.

### Señales

| Dimensión | Ejemplos |
| --- | --- |
| Frescura | última partición, retraso de etiquetas |
| Integridad | schema, nulos, categorías desconocidas |
| Drift | features, predicciones, slices críticos |
| Performance | métrica primaria y guardrails con ground truth |
| Serving | disponibilidad, latencia, errores, volumen |
| Trazabilidad | modelo, run, commit y hash de configuración |

Databricks Data Profiling permite seguir estadísticas, drift, inputs, predicciones y
performance sobre tablas de inferencia. Consulta la
[documentación oficial](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling).

### Resultado

Cada ejecución produce un resumen legible, métricas estructuradas y links a evidencia. Un
error técnico hace fallar el workflow. Una desviación de negocio genera la severidad y
alerta definida por política. No se oculta un incidente reintentando hasta obtener verde.

## Qué workflows bloquean un PR

| Workflow | Bloqueante en PR | Credenciales externas |
| --- | :---: | :---: |
| 01 | Sí | No |
| 02 | Sí, para checks aplicables | No |
| 03 offline | Sí en Databricks | No |
| 03 deploy | No en PR | Sí, entorno protegido |
| 04 | No | Sí, sólo operación programada/manual |

## Configuración de branch protection

Mantén nombres de jobs agregadores estables. Para este repositorio, `quality` reúne
`branch-policy`, `static-analysis`, `type-check`, `tests` y `package`, y es el check
principal en `dev` y `main`. Agrega los checks de seguridad cuando la funcionalidad esté habilitada en el
repositorio. No marques como requerido un job que se omite legítimamente en la mayoría de
los PR; usa un agregador que interprete correctamente esos estados.

## Actualizar una acción

1. Confirma el repositorio oficial de la acción.
2. Resuelve el tag aprobado a su commit actual.
3. Sustituye el SHA conservando el comentario de versión.
4. Revisa release notes y permisos.
5. Ejecuta validación YAML y CI.
6. No mezcles la actualización con cambios funcionales no relacionados.

## Diagnóstico

Abre primero el job rojo y localiza el primer comando fallido. El agregador sólo resume.
Reproduce localmente los comandos de `01`. Los resultados de CodeQL y Dependency Review
se investigan desde Security y el diff de dependencias. Los fallos Databricks deben
clasificarse como offline, autenticación, validación, deploy, run o smoke; cada categoría
tiene un owner distinto.
