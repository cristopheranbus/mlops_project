# Ruff estricto: configuración, uso y migración

Esta guía explica el estándar Ruff obligatorio de la skill. Está dirigida tanto a una
persona que ve por primera vez un código como `F401` como a quien mantiene el contrato de
proyectos generados.

## Qué problema resuelve Ruff

Ruff revisa código Python sin ejecutarlo. Detecta imports incorrectos, nombres inválidos,
errores frecuentes, prácticas inseguras, anotaciones ausentes, patrones difíciles de
mantener y convenciones específicas de pytest. También proporciona el formatter del
proyecto.

Ruff no reemplaza:

- mypy, que comprueba relaciones de tipos;
- pytest, que demuestra comportamiento;
- CodeQL, que analiza flujos de seguridad;
- `pip-audit`, que revisa vulnerabilidades conocidas;
- una revisión humana del diseño.

## Configuración obligatoria

El proyecto declara una versión reproducible y un conjunto curado de reglas:

```toml
[dependency-groups]
dev = ["ruff>=0.16.5,<0.17"]

[tool.ruff]
target-version = "py312"
line-length = 100
preview = false

[tool.ruff.lint]
select = [
    "E", "F", "W", "I", "N", "UP", "B", "A", "ANN", "ASYNC", "BLE", "C4",
    "DTZ", "EM", "ERA", "EXE", "FA", "FLY", "FURB", "G", "ICN", "INP", "INT",
    "LOG", "PIE", "PT", "PTH", "Q", "RET", "RSE", "S", "SIM", "SLOT", "T10",
    "T20", "TC", "ARG", "PERF", "PGH", "PLC", "PLE", "PLW", "RUF",
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["S101"]
"src/**/cli.py" = ["T201"]
"notebooks/databricks/**/*.py" = ["N999"]
```

No se usa `ALL`: puede incorporar reglas nuevas o incompatibles al actualizar Ruff y
convierte una actualización de herramienta en un cambio de política no revisado. Tampoco
se activan reglas preview. El contrato puede crecer de manera explícita mediante un PR.

## Qué cubre cada grupo

| Área | Selectores | Ejemplos de protección |
| --- | --- | --- |
| Errores base | `E`, `F`, `W` | sintaxis, nombres indefinidos, imports sin usar |
| Imports y modernización | `I`, `UP`, `FA`, `TC` | orden, sintaxis moderna, imports usados sólo para tipos |
| API y tipos | `N`, `ANN`, `A`, `ARG` | nombres, anotaciones, builtins ocultos, argumentos sin usar |
| Bugs y claridad | `B`, `BLE`, `C4`, `PIE`, `RET`, `RSE`, `SIM` | excepciones amplias, comprehensions y retornos confusos |
| Seguridad | `S`, `T10`, `PGH` | asserts productivos, debugger, supresiones inseguras |
| Pytest | `PT` | fixtures, imports y asserts con convenciones consistentes |
| Paths, fechas y logging | `PTH`, `DTZ`, `LOG`, `G` | pathlib, zonas horarias y mensajes de log correctos |
| Rendimiento | `PERF`, `FLY`, `FURB` | loops y construcciones innecesarias |
| Higiene | `ERA`, `EXE`, `INP`, `INT`, `ICN`, `Q` | código comentado, paquetes, gettext, aliases y comillas |
| Calidad adicional | `EM`, `SLOT`, `T20`, `PLC`, `PLE`, `PLW`, `RUF` | mensajes, clases, prints, errores de pylint y reglas propias |

Los detalles de cada código están en el
[catálogo oficial de reglas](https://docs.astral.sh/ruff/rules/).

### Familias deliberadamente fuera de esta etapa

El baseline no activa `D` (docstrings), `PLR` (diseño y complejidad) ni `TRY` (estilo de
excepciones). No se consideran reglas de menor valor: necesitan decisiones separadas
sobre API pública, umbrales de complejidad y fronteras de error. Activarlas sin esa
política produciría excepciones arbitrarias y dificultaría la primera contribución. Un PR
futuro puede incorporarlas con ejemplos, migración y pruebas propias; no deben colarse
mediante `ALL`.

## Las tres excepciones permitidas

### `S101` en tests

Pytest usa `assert` para expresar evidencia. Permitirlo bajo `tests/**/*.py` no autoriza
asserts en producción, donde pueden desaparecer con optimizaciones de Python.

### `T201` en CLI

Un entry point `src/**/cli.py` puede imprimir resultados destinados a la persona usuaria.
La lógica reusable debe usar retornos o logging; no se permite `print` en modeling, data,
features o workflows.

### `N999` en notebooks Databricks

Los notebooks productivos usan nombres ordenados como `10_prepare_data.py` y
`20_train.py`. Esos nombres no son módulos Python importables convencionales, por lo que
`N999` se ignora exclusivamente en `notebooks/databricks/**/*.py`.

No agregues una cuarta excepción sin documentar el conflicto, probar el caso positivo y
negativo, y actualizar el validador.

## Databricks

Los source notebooks pueden usar nombres que Databricks inyecta en runtime:

```toml
[tool.ruff]
builtins = ["dbutils", "display", "spark"]
namespace-packages = ["notebooks", "notebooks/databricks"]
```

Estas entradas sólo pertenecen al perfil `databricks-mlops`. Añadirlas a un proyecto local
ocultaría errores de nombres indefinidos.

## Flujo local recomendado

Primero observa los errores sin modificar archivos:

```powershell
uv run ruff check .
uv run ruff format --check .
```

Aplica únicamente fixes seguros y revisa el diff:

```powershell
uv run ruff check . --fix
uv run ruff format .
git diff
```

Después ejecuta nuevamente Ruff, mypy y pytest. No uses `--unsafe-fixes` como acción
masiva: algunos cambios necesitan juicio semántico.

## Cómo leer un error

Ejemplo:

```text
src/project/modeling/train.py:24:5: T201 `print` found
```

- `src/project/modeling/train.py` es el archivo;
- `24:5` es línea y columna;
- `T201` identifica la regla;
- el texto explica el hallazgo.

Busca `T201` en el catálogo oficial, corrige la causa y vuelve a ejecutar el comando. No
añadas `# noqa` antes de entender por qué la regla aplica.

## Política de `noqa`

Queda prohibido un comentario genérico:

```python
operation()  # noqa
```

Si una frontera excepcional requiere supresión inline, debe indicar el código exacto y
tener una explicación comprobable al lado. `PGH` rechaza supresiones genéricas y `RUF100`
rechaza códigos `noqa` que ya no son necesarios.

Antes de aceptar una supresión:

1. confirma que cambiar el código dañaría el contrato;
2. limita la supresión a una línea y un código;
3. explica la razón, no la mecánica;
4. agrega una prueba cuando la excepción protege una frontera real;
5. comprueba que Ruff no reporte `RUF100`.

## Migración desde la configuración anterior

1. crea una rama y conserva un baseline de tests;
2. actualiza Ruff y `uv.lock`;
3. copia el conjunto curado, sin `ALL` ni ignores globales;
4. agrega `__init__.py` a paquetes Python reales;
5. mueve imports usados sólo por tipos bajo `TYPE_CHECKING` cuando Ruff lo solicite;
6. agrega anotaciones faltantes y corrige argumentos sin usar;
7. reemplaza prints productivos por retornos o logging;
8. configura las tres excepciones permitidas;
9. añade builtins y namespace packages sólo para Databricks;
10. ejecuta todos los gates y revisa el diff completo.

El validador reporta `ruff-config` inmediatamente. No existe periodo de warning.

## CI

GitHub ejecuta:

```text
uv run ruff check . --output-format=github
uv run ruff format --check .
```

El primer comando crea anotaciones sobre el diff. Ningún workflow usa `--fix`; CI debe
mostrar el problema, no modificar silenciosamente el código de una contribución.

## Documentación oficial

- [Configuración de Ruff](https://docs.astral.sh/ruff/configuration/)
- [Selección de reglas](https://docs.astral.sh/ruff/linter/#rule-selection)
- [Catálogo de reglas](https://docs.astral.sh/ruff/rules/)
- [Formatter](https://docs.astral.sh/ruff/formatter/)
