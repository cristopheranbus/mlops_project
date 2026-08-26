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

1. crea una rama con un propósito concreto;
2. revisa `SKILL.md` y la referencia normativa relacionada;
3. implementa el cambio más pequeño que resuelva el problema;
4. agrega o ajusta pruebas;
5. actualiza la documentación pública;
6. ejecuta todos los gates;
7. revisa el diff completo y busca secretos;
8. usa commits enfocados y mensajes descriptivos.

Antes de editar, comprueba el estado del repositorio:

```powershell
git status --short --branch
```

No descartes ni reformatees cambios ajenos que no pertenezcan a tu contribución.

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

`SKILL.md` debe responder con claridad:

- cuándo se activa la skill;
- qué información necesita;
- qué valores puede inferir;
- qué archivos normativos debe leer;
- qué acciones realiza;
- cómo verifica el resultado;
- qué debe reportar.

Evita convertirlo en documentación enciclopédica. Mueve estándares extensos a
`references/` y explicaciones para personas a `docs/`.

Si cambia `name` o el alcance, actualiza también `agents/openai.yaml`, README y ejemplos.

## Cambiar referencias normativas

Una referencia bajo `references/` guía la generación. Al modificarla:

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
- `SKILL.md`;
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
