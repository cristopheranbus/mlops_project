# Diseño interno de la skill

Este documento explica cómo colaboran los archivos de este repositorio y qué principios
deben conservarse al modificarlo.

## Objetivos de diseño

1. crear proyectos independientes, no copias rígidas de un ejemplo;
2. adaptar la arquitectura al problema y al perfil;
3. mantener un camino local reproducible;
4. aplicar controles verificables antes de declarar éxito;
5. impedir afirmaciones falsas sobre infraestructura externa;
6. proteger destinos existentes y secretos;
7. mantener las instrucciones pequeñas y delegar detalle normativo a referencias.

## Componentes

```text
Petición del usuario
       │
       ▼
SKILL.md ────────────────┐
       │                 │ carga selectiva
       ▼                 ▼
Contrato          references/*.md
       │                 │
       └────────┬────────┘
                ▼
        Proyecto generado
                │
                ▼
 scripts/validate_project.py
                │
                ▼
       Gates locales y reporte
```

### `SKILL.md`

Es el contrato ejecutivo. Define:

- cuándo debe activarse la skill;
- datos que deben confirmarse o inferirse;
- perfiles disponibles;
- reglas de seguridad del destino;
- referencias que deben leerse según el perfil;
- validaciones obligatorias;
- contenido del informe final.

Debe permanecer enfocado. Un detalle extenso que no cambie el orden de ejecución suele
pertenecer a `references/` o `docs/`.

### `references/architecture.md`

Define la arquitectura mínima de los proyectos generados: layout `src`, fronteras entre
componentes, configuración neutral, camino local y separación de etapas productivas.

### `references/quality.md`

Define reproducibilidad, packaging, gates, CI e higiene del repositorio. Es normativo: un
proyecto no debe debilitar estas reglas sin una razón explícita y documentada.

### `references/testing.md`

Describe capas de pruebas, aislamiento, marcadores y expectativas de cobertura. Protege
contra suites que solo elevan el porcentaje sin validar comportamiento.

### `references/mlflow.md`

Se carga para `mlflow-local` y `databricks-mlops`. Define tracking, artefactos, firma,
evaluación independiente, aliases y aislamiento de pruebas.

### `references/databricks.md`

Solo se necesita para `databricks-mlops`. Define bundles, targets, Unity Catalog, Jobs,
serving, aprobación, smoke tests y rollback.

### `scripts/validate_project.py`

Es un validador estructural sin efectos sobre el proyecto analizado. Recibe una raíz y un
perfil, resuelve el contrato esperado y devuelve issues tipados por severidad y código.

### `tests/test_validate_project.py`

Construye proyectos mínimos en directorios temporales. Las pruebas cubren caminos válidos,
archivos faltantes, configuración incompleta, placeholders, nombres sensibles, perfiles y
la garantía de no modificación.

### `agents/openai.yaml`

Contiene nombre visible, descripción corta y prompt sugerido. Debe permanecer alineado con
el `name` y el alcance descritos en `SKILL.md`.

## Flujo de resolución de perfil

El validador acepta un perfil explícito o `auto`.

Con `auto`:

1. busca `.mlops-profile`;
2. si contiene un valor válido, lo usa;
3. si existe `databricks.yml`, infiere `databricks-mlops`;
4. si existe `docs/mlflow.md`, infiere `mlflow-local`;
5. en otro caso, usa `python-ml`.

Un marcador inválido produce un issue `profile`; la validación continúa con el fallback
para entregar más información en una sola ejecución.

## Flujo del validador

```text
Resolver ruta
    │
    ├── ruta inexistente → issue path → finalizar
    │
    ▼
Resolver perfil
    │
    ▼
Comprobar rutas comunes
    │
    ▼
Leer pyproject.toml
    │
    ├── validar Ruff, mypy, pytest y coverage
    ├── recopilar dependencias
    └── comprobar paquete y pruebas
    │
    ▼
Aplicar requisitos del perfil
    │
    ▼
Escanear archivos y placeholders
    │
    ▼
Imprimir resumen y devolver 0 o 1
```

El validador acumula issues en lugar de detenerse en el primer fallo. Esto reduce ciclos
de corrección y facilita su uso en CI.

## Modelo de datos

`Issue` es una dataclass inmutable con:

- `severity`: `error` o `warning`;
- `code`: categoría estable para diagnóstico;
- `message`: explicación humana y ruta cuando corresponde.

Actualmente todas las detecciones son errores. La severidad `warning` permite incorporar
recomendaciones no bloqueantes sin cambiar la interfaz.

## Invariantes que deben conservarse

- `validate_project` no escribe, borra ni renombra archivos;
- el CLI devuelve `1` si existe al menos un error;
- el perfil explícito prevalece sobre la inferencia;
- los requisitos de perfiles superiores son acumulativos;
- el escaneo ignora Git, entornos virtuales y cachés conocidas;
- un archivo ilegible como UTF-8 no provoca una mutación ni un crash del escaneo textual;
- los tests no dependen de red, credenciales ni estado compartido.

## Cómo extender el diseño

### Agregar una regla

1. define qué riesgo evita;
2. decide si es común o específica de un perfil;
3. elige un código estable;
4. implementa una función pequeña;
5. agrega una prueba que pase y otra que falle;
6. documenta la regla en [validation.md](validation.md);
7. ejecuta todos los gates.

### Agregar un perfil

Un perfil nuevo cambia una interfaz pública y requiere:

1. extender el tipo `Profile` y `PROFILES`;
2. definir inferencia o exigir marcador explícito;
3. declarar rutas y dependencias requeridas;
4. agregar la referencia normativa correspondiente;
5. agregar proyectos mínimos válidos en tests;
6. cubrir perfiles incompletos;
7. actualizar README, perfiles, contrato, ejemplos y troubleshooting;
8. comprobar compatibilidad con perfiles existentes.

### Agregar placeholders detectables

Las expresiones deben ser específicas para minimizar falsos positivos. Una regla muy
amplia puede marcar documentación legítima. Agrega tests tanto del patrón rechazado como
de texto cercano que debe aceptarse.

## Decisiones deliberadas

### No existe un generador rígido

La skill dirige a Codex para crear un proyecto adaptado. Esto permite que módulos,
métricas y pruebas respondan al dominio, en vez de copiar una plantilla con nombres o
supuestos irrelevantes.

### El validador es estructural

Mantenerlo rápido, determinista y sin red permite ejecutarlo después de cada generación.
La validez estadística, la calidad de datos y los servicios externos requieren pruebas
especializadas que pertenecen al proyecto generado.

### La documentación normativa se separa de la guía

`references/` define lo que la skill debe aplicar. `docs/` explica cómo usar y mantener
el repositorio. Esta separación evita convertir `SKILL.md` en un manual difícil de seguir.

