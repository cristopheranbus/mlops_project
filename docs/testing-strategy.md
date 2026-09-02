# Estrategia de pruebas de clase mundial

Esta guía describe cómo se prueba la skill, cómo deben probarse los proyectos que genera y
por qué cada capa existe. Está escrita para que una persona principiante pueda ejecutar y
diagnosticar la suite, y para que un mantenedor pueda ampliarla sin convertirla en una
colección frágil de casos duplicados.

## Objetivos

La suite debe responder con evidencia a cinco preguntas:

1. ¿Una estructura válida es aceptada para cada perfil?
2. ¿Cada infracción produce el código y el diagnóstico correctos?
3. ¿El validador permanece determinista y de solo lectura?
4. ¿El paquete funciona una vez construido e instalado?
5. ¿Los controles que necesitan infraestructura están claramente separados?

Cobertura, número de tests y duración son señales útiles, no sustitutos de esas preguntas.

## Mapa de la suite

```text
tests/
├── conftest.py               opciones, markers y generación dinámica
├── contract_cases.py         inventario tipado de infracciones
├── project_factory.py        construcción determinista de proyectos válidos
├── test_contract_matrix.py   perfiles y mutaciones generadas
├── test_documentation.py     enlaces, índice y contratos públicos
├── test_generated_ruff.py    Ruff real sobre proyectos sintéticos
├── test_generated_mypy.py    mypy real en Python 3.12/3.13 y casos negativos
├── test_plugin_contract.py   manifiesto, metadata y workflows
├── test_properties.py        propiedades sobre entradas amplias
├── test_validate_project.py  comportamiento detallado del validador
└── test_validator_edges.py   parsers y fronteras difíciles
```

El factory crea siempre un proyecto válido. Cada test negativo modifica una sola
responsabilidad. Así un fallo de configuración no queda oculto por un notebook roto o un
workflow ausente.

`test_generated_ruff.py` no simula el linter: localiza el ejecutable de Ruff instalado por
el lock y lo ejecuta contra cada perfil sintético con su propio `pyproject.toml`. También
demuestra los límites importantes: `assert` funciona en tests, `print` falla en lógica
productiva y sólo se admite en el CLI, los builtins de Databricks funcionan en notebooks y
`RUF100` rechaza un `noqa` innecesario. Esto evita que el validador y Ruff discrepen sobre
una configuración aparentemente válida.

`test_generated_mypy.py` ejecuta el binario fijado por el lock contra los tres perfiles para
Python 3.12 y 3.13. También demuestra que el contrato rechaza funciones sin anotaciones,
`Any` explícito, ignores sin código, variables posiblemente indefinidas, awaitables olvidados,
matches incompletos y overrides sin `@override`. Así se prueba tanto la configuración como el
comportamiento real del analizador.

## Cómo usa `pytest_generate_tests`

El hook vive en `tests/conftest.py` y se ejecuta durante la colección. Parametriza dos
fixtures reservadas:

- `project_profile`: recorre `python-ml`, `mlflow-local` y `databricks-mlops`;
- `contract_case`: recorre el inventario de mutaciones compatibles con el perfil.

Ejecutar toda la matriz:

```powershell
uv run pytest
```

```bash
uv run pytest
```

Limitarla a Databricks:

```text
uv run pytest --profile databricks-mlops
```

La salida usa IDs estables como:

```text
test_every_supported_profile_is_valid[profile=python-ml]
test_each_contract_mutation_emits_its_owned_issue[missing-local-config]
```

Esto permite copiar el node ID y repetir exactamente el caso:

```text
uv run pytest "tests/test_contract_matrix.py::test_each_contract_mutation_emits_its_owned_issue[missing-local-config]" -q
```

La [documentación oficial de pytest](https://docs.pytest.org/en/stable/how-to/parametrize.html)
explica que `pytest_generate_tests` permite definir esquemas personalizados mediante
`metafunc.parametrize()`.

### Cuándo no usar el hook

Para tres entradas cercanas al test, usa `@pytest.mark.parametrize`. No ocultes datos
simples en `conftest.py`. El hook se reserva para inventarios globales, selección por CLI
o casos compartidos por varios módulos.

No combines automáticamente todos los perfiles, formatos y errores. Una explosión
cartesiana produce ruido y tiempo de CI sin aumentar evidencia. `ContractCase` representa
una combinación completa y válida.

## Capas

### Unitarias

Cubren funciones pequeñas sin filesystem compartido, red ni credenciales. Ejemplos:
normalización de nombres, detección de claves sensibles, serialización canónica o reglas
de merge.

### Contrato

Comprueban la interfaz observable de un proyecto generado: rutas, perfiles, configuración,
notebooks, MLflow y workflows. Una prueba contractual prefiere el código público
`validate_project` sobre helpers internos.

### Integración local

Ejecutan componentes reales con almacenamiento temporal. Para MLflow usan un tracking
store aislado. Se marcan `integration` y siguen funcionando sin nube.

### External

Necesitan un workspace, identidad o recurso autorizado. Se marcan `external` y se omiten
por defecto. Para ejecutarlas conscientemente:

```text
uv run pytest --run-external -m external
```

La opción no concede credenciales ni permisos: sólo elimina el skip. La persona que
ejecuta sigue siendo responsable de seleccionar el entorno correcto.

### Security

Cubren traversal de rutas, archivos malformados, límites de permisos, triggers peligrosos,
acciones no fijadas y configuraciones con secretos aparentes.

### Property-based

Hypothesis genera entradas que sería fácil olvidar manualmente. Las propiedades actuales
comprueban configuraciones seguras, claves sensibles anidadas y paths que intentan escapar
de `notebooks/databricks`.

Cuando una propiedad toca filesystem, cada ejemplo usa un directorio temporal nuevo. Un
deadline puede desactivarse si la variabilidad pertenece al sistema operativo, pero el
timeout global de pytest continúa protegiendo la suite.

## Markers

| Marker | Uso | Ejecución por defecto |
| --- | --- | :---: |
| `contract` | Contratos comunes de proyectos generados | Sí |
| `databricks_contract` | Contrato offline de notebooks y bundles | Sí |
| `integration` | Varios componentes locales | Sí |
| `monitoring_contract` | Presencia y estructura de monitoreo | Sí |
| `external` | Workspace o servicio autorizado | No |

`--strict-markers` convierte un typo en error. Nunca agregues un marker sin declararlo en
`pyproject.toml` y explicarlo aquí.

## Cobertura

La puerta actual es 90% de branch coverage sobre el código del validador. Branch coverage
cuenta decisiones, no sólo líneas visitadas. Para obtener el reporte:

```text
uv run pytest --cov-report=term-missing
```

Una línea sin cubrir no obliga automáticamente a escribir un test. Primero pregunta si
representa un comportamiento alcanzable y relevante. Tampoco uses exclusiones para
ocultar ramas difíciles de probar.

## Timeouts, flakes y `xfail`

Cada test tiene un timeout finito de 30 segundos. Las pruebas de red no pertenecen a la
suite local. No se permiten reruns automáticos para transformar una prueba inestable en
verde.

Un `xfail` debe incluir:

- razón concreta;
- issue asociado;
- condición para retirarlo;
- `strict=True` cuando un éxito inesperado deba obligar a revisar la expectativa.

## Mutation testing programado

El workflow `01` ejecuta Mutmut los miércoles y cuando se lanza manualmente. La puntuación
continúa en fase informativa mientras se construye una baseline honesta: el log muestra
mutantes detectados, sobrevivientes, timeouts y errores sospechosos. Sin embargo, un fallo
operativo de Mutmut sí deja el workflow en rojo; así, una configuración rota o una suite que
no logra recolectar estadísticas nunca se confunde con un análisis exitoso.

`source_paths` limita las mutaciones al validador. La selección
`pytest_add_cli_args_test_selection` ejecuta únicamente las pruebas que ejercitan ese código;
excluye deliberadamente pruebas documentales y de empaquetado que dependen de archivos que
Mutmut no copia a su workspace `mutants/`. El runner desactiva coverage para evitar medir
cada mutante con una instrumentación redundante. Estos nombres corresponden a la
[configuración oficial de Mutmut](https://github.com/boxed/mutmut#configuration).

Para reproducirlo:

```text
uv sync --locked --dev --group mutation
uv run --group mutation mutmut run
uv run --group mutation mutmut results
```

Mutmut no ofrece ejecución nativa en Windows. Usa WSL o Linux para estos comandos; los
demás gates continúan siendo compatibles con PowerShell. El workflow programado se
ejecuta sobre Ubuntu.

No hagas bloqueante la puntuación hasta clasificar los sobrevivientes equivalentes. La
primera meta es 70%; después de estabilizar tiempos y excepciones, el objetivo es 80–85%.
Cada exclusión necesita una justificación concreta. Esta política distingue dos resultados:

- un análisis que termina y reporta mutantes sobrevivientes es evidencia válida, aunque su
  puntuación todavía sea informativa;
- un análisis que no recolecta estadísticas, no encuentra pruebas o termina con una excepción
  es un fallo operativo y debe quedar rojo.

## Cómo agregar una regla

Ejemplo: exigir un workflow nuevo.

1. Documenta el invariante en una referencia normativa.
2. Añade el código estable y mensaje accionable al validador.
3. Actualiza `project_factory.py` para que el proyecto base siga siendo válido.
4. Añade un `ContractCase` que retire o corrompa únicamente el workflow.
5. Agrega casos detallados sólo para ramas que tengan diagnósticos distintos.
6. Actualiza validación y troubleshooting.
7. Ejecuta toda la matriz, no sólo el caso nuevo.

## Diagnóstico de fallos

Empieza por el primer error, no por el resumen de cobertura. Repite un test:

```text
uv run pytest tests/test_validate_project.py::test_actions_must_be_pinned_to_a_commit_sha -vv
```

Lista la colección sin ejecutar:

```text
uv run pytest --collect-only -q
```

Lista markers:

```text
uv run pytest --markers
```

Si Windows informa permisos sobre temporales:

```text
uv run pytest --basetemp .pytest-tmp
```

No edites el comportamiento para silenciar un error ambiental. Distingue fallo de test,
fallo de colección, fallo de cobertura y fallo de infraestructura.

## Criterio de aceptación

- Todos los perfiles válidos pasan.
- Cada regla nueva tiene caso positivo y negativo.
- La cobertura de branches alcanza al menos 90%.
- No se ejecutan servicios externos por defecto.
- La suite pasa en Python 3.12 y 3.13, Linux y Windows.
- El wheel construido se instala y puede importar el CLI.
- Los reportes JUnit y coverage quedan disponibles en CI.
- El validador no modifica el proyecto examinado.
