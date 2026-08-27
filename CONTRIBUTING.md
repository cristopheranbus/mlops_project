# Contribuir a Create MLOps Project

Gracias por mejorar la skill. Este repositorio define una interfaz que afecta la estructura
de proyectos nuevos; por eso, una modificación pequeña en una regla puede tener impacto en
muchos repositorios generados.

## Principios de contribución

- preservar seguridad del destino y datos del usuario;
- preferir reglas explícitas y verificables;
- mantener la complejidad proporcional al perfil;
- no acoplar la skill a un dominio o dataset de ejemplo;
- mantener el camino local sin servicios productivos;
- distinguir generación, validación local y validación externa;
- acompañar cambios de comportamiento con pruebas y documentación.

## Preparar el entorno

Requisitos:

- Git;
- Python 3.12 o 3.13;
- `uv`.

Instala las dependencias bloqueadas:

```powershell
uv sync --locked --dev
```

Comprueba el entorno:

```powershell
uv run python --version
uv run pytest --version
uv run ruff --version
uv run mypy --version
```

## Flujo de trabajo

1. crea un fork o una rama con un propósito concreto;
2. revisa `skills/create-mlops-project/SKILL.md` y la referencia normativa relacionada;
3. implementa el cambio más pequeño que resuelva el problema;
4. agrega o ajusta pruebas;
5. actualiza la documentación pública;
6. ejecuta todos los gates;
7. revisa el diff completo y busca secretos;
8. usa commits enfocados y mensajes descriptivos;
9. abre un pull request hacia `main` y completa su plantilla;
10. responde la revisión y mantén el PR actualizado hasta que CI esté verde.

Antes de editar, comprueba el estado del repositorio:

```powershell
git status --short --branch
```

No descartes ni reformatees cambios ajenos que no pertenezcan a tu contribución.

`@cristopheranbus` es code owner global y debe revisar los cambios antes del merge. La
política completa está en [docs/governance.md](docs/governance.md).

## Mi primera contribución

El recorrido completo es:

```text
Fork → clone → branch → edit → test → commit → push → PR
```

1. crea un **fork**, tu copia remota del repositorio;
2. haz **clone** para obtener una copia local;
3. crea una **branch**, una línea aislada de trabajo;
4. edita una sola responsabilidad y sus pruebas;
5. ejecuta los gates;
6. crea un **commit**, una unidad versionada con un mensaje descriptivo;
7. haz **push** hacia tu fork;
8. abre un **PR** (pull request) para revisión y espera que **CI** valide el cambio.

Comandos mínimos con [GitHub CLI](https://cli.github.com/) autenticado:

```text
gh repo fork cristopheranbus/mlops_project --clone
cd mlops_project
git switch -c docs/my-first-change
uv sync --locked --dev
uv run pytest --basetemp .pytest-tmp
git add docs README.md
git commit -m "Clarify beginner documentation"
git push -u origin docs/my-first-change
```

### Glosario breve

| Concepto | Significado |
| --- | --- |
| fork | Copia remota personal desde la que propones cambios |
| branch | Línea de trabajo separada de `main` |
| commit | Snapshot revisable de cambios relacionados |
| CI | Controles automáticos ejecutados por GitHub Actions |
| PR | Solicitud para revisar e integrar una branch |
| fixture | Preparación reutilizable de datos o archivos para una prueba |
| profile | Contrato de capacidades: `python-ml`, `mlflow-local` o `databricks-mlops` |

### Quiero cambiar X: ¿dónde empiezo?

| Cambio | Archivos principales |
| --- | --- |
| Cómo actúa la skill | `skills/create-mlops-project/SKILL.md` |
| Arquitectura generada | `skills/create-mlops-project/references/architecture.md` |
| Configuración | `references/configuration.md`, `docs/configuration.md` |
| MLflow o Databricks | `references/mlflow.md`, `references/databricks.md` |
| Regla estructural | `scripts/validate_project.py`, `tests/test_validate_project.py` |
| Guía pública | `docs/` y `docs/README.md` |
| Dependencia | `pyproject.toml` y `uv.lock` |

Las rutas `references/` y `scripts/` de la tabla están dentro de
`skills/create-mlops-project/`.

### Ejemplo de una regla nueva

Supón que un archivo obligatorio debe contener `config_version: 1`:

1. define el invariante en la referencia normativa;
2. agrega un helper del validador que emita un código estable y mensaje accionable;
3. prueba el caso positivo con el fixture válido intacto;
4. prueba el caso negativo eliminando sólo `config_version`;
5. documenta el código en `docs/validation.md` y troubleshooting;
6. confirma `test_validation_does_not_modify_files`.

Una prueba positiva demuestra que una entrada válida no genera el issue. Una negativa
introduce una sola infracción y confirma el código esperado; no debe depender de red ni
credenciales.

### Leer fallos de herramientas

- **Ruff:** el código al inicio identifica la regla y la ruta/línea indica dónde corregir.
- **mypy:** compara el tipo recibido con el esperado; corrige el contrato en vez de usar
  `Any` indiscriminadamente.
- **pytest:** empieza por el primer traceback y el assert final; ejecuta una sola prueba
  con `uv run pytest ruta::test_name -q` antes de repetir la suite completa.

Si agregas una guía, enlázala desde `docs/README.md`. Antes del PR confirma: cambio
pequeño, prueba positiva y negativa cuando corresponde, documentación actualizada, gates
verdes y ausencia de secretos. Las secciones siguientes son la guía avanzada.

## Gates obligatorios

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --basetemp .pytest-tmp
uv build
```

La cobertura mínima configurada es 85%. El objetivo no es maximizar el porcentaje, sino
probar decisiones, errores y contratos relevantes.

## Cambiar `SKILL.md`

`skills/create-mlops-project/SKILL.md` debe responder con claridad:

- cuándo se activa la skill;
- qué información necesita;
- qué valores puede inferir;
- qué archivos normativos debe leer;
- qué acciones realiza;
- cómo verifica el resultado;
- qué debe reportar.

Evita convertirlo en documentación enciclopédica. Mueve estándares extensos a
`skills/create-mlops-project/references/` y explicaciones para personas a `docs/`.

Si cambia `name` o el alcance, actualiza también
`skills/create-mlops-project/agents/openai.yaml`, el manifiesto del plugin, README y
ejemplos.

## Cambiar referencias normativas

Una referencia bajo `skills/create-mlops-project/references/` guía la generación. Al
modificarla:

1. identifica los perfiles afectados;
2. confirma que la regla puede cumplirse localmente o declara su frontera externa;
3. evita requisitos que agreguen infraestructura sin necesidad;
4. actualiza el contrato público en `docs/project-contract.md` o `docs/profiles.md`;
5. agrega validación automática si la regla es estructural y estable.

No toda buena práctica necesita una regla del script. Algunas requieren juicio de dominio
y pertenecen solo a instrucciones o documentación.

## Cambiar el validador

### Agregar una regla

Una regla nueva debe tener:

- riesgo o invariante definido;
- scope común o de perfil;
- código estable y mensaje accionable;
- prueba positiva;
- prueba negativa;
- documentación en `docs/validation.md`;
- ausencia de escrituras sobre el proyecto analizado.

Prefiere helpers pequeños. La función `validate_project` debe seguir siendo fácil de leer
como secuencia de validaciones.

### Cambiar un código de issue

Los consumidores pueden usar `Issue.code` programáticamente. Cambiarlo es una ruptura de
compatibilidad. Si el cambio es imprescindible, documéntalo y considera una transición.

### Agregar un warning

Reserva warnings para recomendaciones que no invalidan el contrato. Documenta claramente
por qué no bloquean y prueba que el CLI conserva el código de salida esperado.

### Mantener la ausencia de efectos

La prueba `test_validation_does_not_modify_files` compara bytes antes y después. Una regla
no debe formatear, corregir ni crear archivos. Las correcciones se describen en mensajes;
las aplica el usuario o el flujo generador.

## Agregar o cambiar un perfil

Revisa como mínimo:

- `Profile` y `PROFILES`;
- opciones del CLI;
- resolución automática;
- rutas requeridas;
- dependencias requeridas;
- fixture `_valid_project`;
- caso completo válido;
- caso incompleto;
- `skills/create-mlops-project/SKILL.md`;
- referencias normativas;
- README;
- `docs/profiles.md`;
- `docs/project-contract.md`;
- ejemplos y troubleshooting.

Un perfil debe representar una frontera operativa coherente, no una combinación arbitraria
de librerías.

## Escribir pruebas

Las pruebas deben ser:

- deterministas;
- aisladas mediante `tmp_path`;
- independientes de red y credenciales;
- pequeñas y orientadas al comportamiento;
- legibles como ejemplos del contrato.

Para una regla nueva, usa `_valid_project` como base y modifica solo el elemento que debe
provocar el issue. Esto evita que un fallo secundario oculte la intención.

No uses el filesystem real del desarrollador ni un servicio compartido.

## Documentación

Al modificar documentación:

- conserva enlaces relativos para navegación en GitHub y clones locales;
- usa comandos ejecutables y especifica el shell;
- diferencia ejemplos de valores reales;
- no incluyas tokens ni cadenas con formato de credencial;
- alinea nombres de perfiles y códigos con el código;
- explica límites, no solo el camino feliz;
- evita prometer integraciones no verificadas.

La suite comprueba enlaces locales y que `docs/README.md` enumere todas las guías. Cuando
agregues un archivo bajo `docs/`, incorpóralo al índice y a la ruta de lectura apropiada.

## Seguridad

Antes de preparar cambios:

```powershell
git diff --check
git status --short
```

Revisa que no se incluyan:

- `.env` o perfiles locales;
- claves y certificados;
- tokens en ejemplos o logs;
- datasets privados;
- hostnames o identificadores productivos sensibles;
- artefactos, modelos o stores locales.

Si detectas una exposición, sigue [SECURITY.md](SECURITY.md).

## Checklist del pull request

- [ ] El cambio tiene un alcance claro.
- [ ] La skill sigue aplicándose solo a proyectos ML nuevos.
- [ ] Los perfiles no afectados conservan comportamiento.
- [ ] Se agregaron pruebas positivas y negativas cuando cambia una regla.
- [ ] Ruff pasa.
- [ ] El formato pasa.
- [ ] mypy pasa.
- [ ] pytest pasa con cobertura mínima.
- [ ] El paquete se construye.
- [ ] README y documentación están alineados.
- [ ] No se incluyeron secretos ni archivos generados.
- [ ] Las validaciones externas se reportan con precisión.

## Commits

Usa mensajes imperativos y enfocados, por ejemplo:

```text
Document profile selection criteria
Add validation for profile marker
Clarify external test boundaries
```

Evita mezclar una refactorización amplia, cambios de contrato y documentación no
relacionada en un solo commit cuando pueden revisarse por separado.

## Licencia de contribuciones

Salvo que una contribución se marque explícitamente de otra manera antes de su aceptación,
se incorpora bajo Apache License 2.0, de acuerdo con la sección 5 de [LICENSE](LICENSE).
