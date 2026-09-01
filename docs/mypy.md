# Tipado estricto con mypy

Esta guía explica el contrato de análisis estático que aplica la skill y que hereda cada
proyecto generado. Está pensada para quien comienza con tipos en Python, pero también
documenta las decisiones normativas que debe revisar un mantenedor.

## Qué problema resuelve

Python valida muchos errores recién al ejecutar una línea. mypy analiza el programa antes
de ejecutarlo y comprueba que los valores usados sean compatibles con las anotaciones. Por
ejemplo, detecta una función que promete `str` pero devuelve `None`, un parámetro obligatorio
omitido o un resultado asíncrono olvidado sin `await`.

mypy no reemplaza otras capas:

| Herramienta | Pregunta principal |
| --- | --- |
| Pydantic | ¿Los datos recibidos en runtime cumplen el esquema? |
| mypy | ¿Las conexiones entre módulos son coherentes antes de ejecutar? |
| Ruff | ¿El código incumple reglas de calidad, seguridad o estilo? |
| pytest | ¿El comportamiento observado cumple los casos esperados? |

Un proyecto sano necesita las cuatro. Un tipo correcto no garantiza una fórmula correcta y
un test exitoso sólo cubre la ruta que ejecutó.

## Inicio rápido

Después de `uv sync --locked`, ejecuta lo mismo en PowerShell y Bash:

```bash
uv run mypy --no-incremental
```

La salida esperada es similar a:

```text
Success: no issues found in 24 source files
```

Para reproducir la matriz de CI:

```bash
uv run mypy --no-incremental --python-version 3.12
uv run mypy --no-incremental --python-version 3.13
```

`--no-incremental` evita que una caché local oculte diferencias durante una comprobación
reproducible. No cambia las reglas.

## Configuración obligatoria

Los proyectos generados contienen:

```toml
[tool.mypy]
python_version = "3.12"
files = ["src", "tests"]
strict = true
warn_unused_configs = true
disallow_any_explicit = true
disallow_any_unimported = true
strict_bytes = true
strict_equality_for_none = true
show_error_codes = true
show_error_code_links = true
enable_error_code = [
    "deprecated",
    "explicit-override",
    "exhaustive-match",
    "ignore-without-code",
    "mutable-override",
    "possibly-undefined",
    "redundant-expr",
    "redundant-self",
    "truthy-bool",
    "truthy-iterable",
    "unused-awaitable",
]
```

El repositorio de la skill usa el mismo contrato, pero su alcance es
`skills/create-mlops-project/scripts` y `tests` porque allí vive su código Python.

### Explicación línea por línea

- `python_version`: interpreta sintaxis y biblioteca estándar desde el mínimo soportado.
- `files`: impide una ejecución accidental que omita producción o pruebas.
- `strict`: activa el conjunto estricto mantenido por mypy. Ese conjunto puede crecer entre
  versiones; por eso la versión está acotada y se revisa al actualizarla.
- `warn_unused_configs`: informa una sección por módulo que nunca coincide, típico síntoma de
  un nombre mal escrito.
- `disallow_any_explicit`: rechaza anotaciones que escriben `Any` para escapar del contrato.
- `disallow_any_unimported`: rechaza `Any` propagado por imports que mypy no pudo analizar.
- `strict_bytes`: mantiene separados `bytes`, `bytearray` y `memoryview`.
- `strict_equality_for_none`: detecta comparaciones imposibles con `None`.
- `show_error_codes`: agrega códigos como `[arg-type]`, necesarios para diagnóstico preciso.
- `show_error_code_links`: enlaza el código con su referencia oficial cuando el terminal lo
  soporta.
- `enable_error_code`: activa controles opt-in descritos en la sección siguiente.

`strict = true` ya reúne controles importantes: exige anotaciones completas, revisa cuerpos
tipados, evita `Optional` implícito, informa ignores y casts innecesarios, limita genéricos sin
parámetros y aplica igualdad estricta. No copiamos su expansión interna porque la fuente de
verdad es `mypy --help` para la versión fijada.

## Códigos opt-in, uno por uno

### `deprecated`

Rechaza APIs marcadas como obsoletas. La corrección es migrar a la alternativa indicada, no
silenciar el aviso indefinidamente.

### `explicit-override`

Exige `@override` cuando una subclase redefine un método. Así un cambio de nombre en la clase
base no convierte silenciosamente el método hijo en otro método independiente.

```python
from typing import override


class Trainer(BaseTrainer):
    @override
    def fit(self) -> Model: ...
```

### `exhaustive-match`

Comprueba que un `match` cubra todos los miembros conocidos de un `Literal` o enum. Para una
rama deliberadamente imposible usa `assert_never`; no agregues un comodín que oculte nuevos
estados.

### `ignore-without-code`

Prohíbe `# type: ignore` sin motivo acotado. La forma mínima es
`# type: ignore[import-untyped]`, acompañada de una razón cuando no sea evidente.

### `mutable-override`

Evita redefinir un atributo mutable con un tipo más estrecho. Aunque parezca cómodo, una
referencia de la clase base podría escribir un valor válido para la base e inválido para la
subclase. Prefiere propiedades de sólo lectura o conserva el mismo tipo.

### `possibly-undefined`

Detecta una variable asignada sólo en algunas ramas:

```python
# Incorrecto: value no existe cuando enabled es False.
if enabled:
    value = train()
publish(value)

# Correcto: todas las rutas definen el valor.
value = train() if enabled else load_current()
publish(value)
```

### `redundant-expr`

Marca condiciones que son siempre verdaderas o falsas según los tipos. Suelen revelar una
rama muerta o una unión mal modelada.

### `redundant-self`

Evita anotar `self: Self` cuando el uso de `Self` en el retorno ya entrega toda la información.

### `truthy-bool`

Rechaza usar como condición un objeto cuyo tipo no declara `__bool__` ni `__len__`. Obliga a
expresar la propiedad real que se quiere comprobar.

### `truthy-iterable`

Un `Iterable` puede ser generador y siempre evaluar como verdadero. Si necesitas conocer si
está vacío, recibe `Collection[T]` o consume el iterador de forma explícita.

### `unused-awaitable`

Detecta objetos awaitable descartados. Una llamada asíncrona normalmente necesita
`await operation()`; crear la corrutina no ejecuta el trabajo.

## `object` no es `Any`

`object` representa un valor desconocido que debe estrecharse antes de usarlo. `Any` desactiva
la comprobación y además contamina expresiones posteriores.

```python
def normalize(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    raise TypeError("value must be a string")
```

Usa `isinstance`, una comprobación de clave, `TypeGuard` o un parser Pydantic para convertir
datos de frontera en tipos de dominio.

## `Optional`, unions y narrowing

`str | None` significa que ambos estados son válidos. Antes de llamar métodos de `str`, trata
el caso ausente:

```python
def experiment_name(value: str | None) -> str:
    if value is None:
        return "default"
    return value.strip()
```

El narrowing también funciona con `isinstance`, `type`, `callable`, discriminantes de
`TypedDict`, `TypeGuard` y `TypeIs`. Prefiere estas comprobaciones ejecutables a un cast.

## Herramientas de modelado

- `TypedDict`: describe mappings con claves conocidas, útil para respuestas JSON internas.
- `Protocol`: expresa comportamiento estructural, ideal para adapters y dobles de prueba.
- `TypeGuard`: encapsula una validación que estrecha una colección heterogénea.
- genéricos: preservan la relación entre entrada y salida sin duplicar implementaciones.
- `Self`: expresa métodos que devuelven la instancia o una instancia de la subclase.

Ejemplo de un adapter testeable:

```python
from typing import Protocol


class MetricLogger(Protocol):
    def log_metric(self, name: str, value: float) -> None: ...


def report_accuracy(logger: MetricLogger, value: float) -> None:
    logger.log_metric("accuracy", value)
```

La prueba puede usar una clase pequeña que cumpla el protocolo sin importar MLflow.

## YAML y JSON recursivos

Los parsers externos devuelven estructuras dinámicas. Modela la frontera y valida antes de
crear `AppConfig`:

```python
from typing import TypeAlias

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
```

No fuerces el resultado completo con `cast(AppConfig, yaml.safe_load(...))`: un cast no valida
datos. Primero comprueba que la raíz sea un mapping y luego usa Pydantic.

## MLflow y Databricks

Las librerías externas pueden tener cobertura de tipos parcial. Encierra esa incertidumbre en
adapters bajo `tracking/`, `data/` o `workflows/` y devuelve tipos propios. Los notebooks no
entran al alcance directo de mypy porque los globals `dbutils`, `display` y `spark` aparecen
sólo en el runtime. Toda lógica productiva del notebook debe delegarse a un workflow tipado
bajo `src/<package>/`.

## `py.typed`, paquetes `types-*` y stubs

Orden de preferencia cuando una dependencia carece de tipos:

1. usa una versión que publique `py.typed`;
2. instala el paquete de stubs oficial o mantenido, como `types-PyYAML`;
3. crea un adapter tipado y un stub local mínimo bajo `typings/`;
4. como último recurso, agrega un override exacto para el namespace externo.

Si declaras `mypy_path = "typings"`, el directorio debe existir y versionarse. Un `.pyi` debe
describir sólo la superficie realmente usada. Si controla una biblioteca instalada, valida su
correspondencia con `stubtest` cuando sea viable.

Override excepcional permitido:

```toml
[[tool.mypy.overrides]]
module = ["vendor_package", "vendor_package.*"]
ignore_missing_imports = true
```

No se permite apuntar a `*`, al paquete propio ni a `tests`; tampoco activar `ignore_errors`,
`follow_imports = "skip"` o deshabilitar códigos. El adapter debe impedir que `Any` escape a la
aplicación.

## Política de casts

`cast(T, value)` afirma algo a mypy, pero no lo comprueba en runtime. Sólo es legítimo después
de una validación que mypy no puede representar o en una frontera externa estrecha. No se usa
para esconder una incompatibilidad entre módulos propios. Agrega una prueba de la validación
que justifica el cast.

## Política de `type: ignore`

Antes de ignorar:

1. lee el código del error;
2. intenta corregir la anotación o estrechar el valor;
3. busca stubs o actualiza la dependencia;
4. aísla el proveedor en un adapter;
5. si no hay alternativa, usa un código exacto y explica el defecto externo.

Un ignore innecesario también falla por `warn_unused_ignores`; esto evita excepciones fósiles
después de actualizar un paquete.

## `reveal_type` para investigar

Durante el diagnóstico agrega temporalmente `reveal_type(value)`. mypy mostrará el tipo
inferido. Elimina la llamada antes del commit: no existe como función normal en runtime y no es
documentación permanente.

## Cómo leer un error

```text
src/package/workflows/train.py:42: error: Argument 1 has incompatible type ... [arg-type]
```

Lee de izquierda a derecha: archivo, línea, descripción y código. Abre la definición de la
función receptora y compara su contrato con el tipo entregado. Corrige primero el primer error;
los posteriores pueden ser consecuencias.

## Errores frecuentes

- `import-untyped`: instala stubs, usa un paquete tipado o crea un adapter; no habilites el
  ignore global.
- `no-untyped-def`: anota todos los parámetros y el retorno, incluso `-> None`.
- `union-attr`: trata cada miembro de la unión antes de usar el atributo.
- `arg-type`: corrige el productor o el consumidor; evita un cast automático.
- `unused-ignore`: elimina la excepción que ya no se necesita.
- distinto resultado local/CI: ejecuta `uv sync --locked`, confirma la misma revisión de
  `uv.lock` y reproduce ambas versiones de Python.

## Migración de un proyecto existente

1. actualiza a `mypy>=2.3.1,<2.4` y `types-pyyaml>=6.0.12,<7`;
2. copia la configuración obligatoria;
3. confirma que `files` contiene `src` y `tests`;
4. ejecuta mypy y clasifica errores por frontera, modelo y consumidor;
5. sustituye `Any` explícito por tipos de dominio u `object` con narrowing;
6. instala stubs y crea adapters para proveedores externos;
7. elimina ignores globales, exclusiones y overrides amplios;
8. ejecuta Python 3.12 y 3.13;
9. actualiza documentación y evidencia del PR.

La adopción del contrato es inmediata en la rama de desarrollo: el validador emite
`mypy-config` ante una configuración antigua o debilitada.

## Checklist antes del PR

- [ ] `uv lock --check` pasa.
- [ ] mypy pasa sin caché en Python 3.12 y 3.13.
- [ ] no se introdujo `Any` explícito.
- [ ] cada ignore tiene código y justificación legítima.
- [ ] los overrides apuntan sólo a namespaces externos concretos.
- [ ] la lógica de notebooks permanece en workflows tipados.
- [ ] tests, Ruff, build y validadores siguen verdes.
- [ ] el PR apunta a `dev`, nunca directamente a `main`.

## Referencias oficiales

- [Documentación estable de mypy](https://mypy.readthedocs.io/en/stable/)
- [Archivo de configuración](https://mypy.readthedocs.io/en/stable/config_file.html)
- [Códigos de error](https://mypy.readthedocs.io/en/stable/error_codes.html)
- [Type narrowing y TypeGuard](https://mypy.readthedocs.io/en/stable/type_narrowing.html)
- [TypedDict](https://mypy.readthedocs.io/en/stable/typed_dict.html)
- [Stub files](https://mypy.readthedocs.io/en/stable/stubs.html)
- [stubtest](https://mypy.readthedocs.io/en/stable/stubtest.html)
