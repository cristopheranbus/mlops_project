# Guía de inicio

Esta guía lleva desde una copia limpia de la skill hasta un primer proyecto generado y
verificado. Para comprender las diferencias entre perfiles, consulta
[profiles.md](profiles.md). Para conocer exactamente qué estructura se espera, consulta
[project-contract.md](project-contract.md).

## 1. Entender qué se instala

La instalación agrega a Codex una skill llamada `create-mlops-project`. La skill contiene:

- `SKILL.md`: contrato de activación y procedimiento principal;
- `references/`: estándares que guían la arquitectura, calidad, pruebas e integraciones;
- `scripts/validate_project.py`: verificador estructural de los proyectos generados;
- `tests/`: pruebas del verificador;
- `agents/openai.yaml`: metadatos de presentación.

La skill no instala MLflow o Databricks globalmente y no crea recursos externos durante
su instalación. Las dependencias específicas pertenecen al proyecto que se genere.

## 2. Preparar el entorno

Para usar la skill solo se necesita una instalación de Codex que descubra skills locales.
Para modificarla o ejecutar sus pruebas también se necesita:

```powershell
python --version
uv --version
git --version
```

Este repositorio admite Python desde 3.12 hasta antes de 3.14. El archivo `uv.lock`
conserva las versiones resueltas de las dependencias de desarrollo.

## 3. Instalar desde Git

Clona el repositorio de forma que `SKILL.md` quede directamente dentro de la carpeta
`create-mlops-project`:

```powershell
git clone https://github.com/cristopheranbus/mlops_project.git `
  "$env:CODEX_HOME\skills\create-mlops-project"
```

La forma esperada es:

```text
create-mlops-project/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── tests/
```

Una anidación accidental como `create-mlops-project/mlops_project/SKILL.md` puede impedir
que el entorno encuentre el archivo en el nivel esperado.

Si `CODEX_HOME` no está definido, localiza el directorio de configuración de Codex usado
por tu instalación y coloca allí la carpeta bajo `skills/`. Después abre una sesión nueva
para forzar un nuevo descubrimiento.

## 4. Actualizar una instalación existente

Desde la carpeta instalada:

```powershell
git pull --ff-only
```

Usar `--ff-only` evita crear un merge implícito sobre cambios locales. Si modificaste la
skill, revisa primero:

```powershell
git status --short
git diff
```

No descartes cambios locales automáticamente. Conserva un fork o una rama si mantienes
personalizaciones.

## 5. Preparar la solicitud

Antes de invocar la skill, define el contrato mínimo:

1. nombre del proyecto y directorio de destino;
2. tipo de problema;
3. fuente y formato de datos;
4. columna objetivo o definición del resultado;
5. framework preferido;
6. métrica principal;
7. criterio cuantitativo de aceptación;
8. perfil de infraestructura;
9. versión de Python y cobertura, si difieren de los valores por defecto.

Ejemplo:

```text
Usa $create-mlops-project para crear ./lead_scoring. Es una clasificación binaria con
datos Parquet, target converted, scikit-learn y average precision como métrica principal.
El modelo se acepta con average precision >= 0.40 y sin una caída de recall superior a
0.03 frente al baseline. Usa Python 3.12, cobertura mínima de 90% y perfil mlflow-local.
```

### Decisiones que pueden inferirse

La skill puede usar:

- Python 3.12;
- `uv` como gestor;
- 85% de cobertura;
- el perfil más pequeño que cumpla la solicitud;
- un nombre de paquete normalizado a partir del nombre del proyecto.

### Decisiones que conviene declarar

Declara explícitamente cualquier decisión que afecte arquitectura o aceptación:

- batch frente a online;
- frecuencia de entrenamiento;
- latencia máxima;
- tratamiento de datos sensibles;
- grupos para métricas segmentadas;
- restricciones de regresión frente al modelo vigente;
- necesidad de registry, aprobación humana, serving o rollback.

## 6. Elegir un destino seguro

El destino debe estar vacío. Esta restricción protege archivos existentes y deja claro qué
contenido fue generado por la skill.

Antes de ejecutar, puedes comprobarlo en PowerShell:

```powershell
Test-Path C:\ruta\destino
Get-ChildItem -Force C:\ruta\destino
```

Si el directorio no existe, la skill puede crearlo. Si existe y contiene archivos, elige
otro destino o autoriza explícitamente una estrategia compatible con esos archivos. La
skill no debe borrar, sobrescribir ni reutilizar un repositorio no vacío por inferencia.

## 7. Revisar la respuesta de la skill

Al finalizar, la respuesta debe distinguir:

- componentes creados;
- supuestos adoptados;
- perfil seleccionado;
- comandos ejecutados;
- controles exitosos;
- controles fallidos;
- verificaciones externas no ejecutadas;
- próximos pasos que dependan de credenciales o infraestructura.

Una respuesta que solo enumera archivos no demuestra que el proyecto funcione. Busca
evidencia de lint, formato, tipado, pruebas, cobertura y build.

## 8. Inspeccionar el proyecto generado

Verifica primero el marcador del perfil:

```powershell
Get-Content C:\ruta\destino\.mlops-profile
```

Después revisa:

```powershell
Get-Content C:\ruta\destino\README.md
Get-Content C:\ruta\destino\pyproject.toml
Get-ChildItem -Recurse C:\ruta\destino\src
Get-ChildItem -Recurse C:\ruta\destino\tests
Get-ChildItem -Recurse C:\ruta\destino\docs
```

Confirma que los nombres y reglas corresponden a tu problema y no a un ejemplo genérico.
El validador detecta la palabra de un dataset de demostración conocida, pero una revisión
de dominio sigue siendo necesaria para encontrar supuestos irrelevantes.

## 9. Ejecutar las comprobaciones

Dentro del proyecto generado, el conjunto habitual es:

```powershell
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

Ejecuta además el validador desde este repositorio:

```powershell
uv run python scripts/validate_project.py C:\ruta\destino --profile auto
```

El validador confirma estructura, no comportamiento. Consulta
[validation.md](validation.md) para interpretar los resultados.

## 10. Próximos pasos recomendados

Después de una generación exitosa:

1. revisa el contrato de datos con quien sea responsable de la fuente;
2. reemplaza datos sintéticos o fixtures de demostración por fixtures representativos y
   pequeños;
3. configura variables de entorno mediante el mecanismo de tu runtime;
4. ejecuta el camino local end-to-end;
5. inicializa Git solo si el usuario lo solicita;
6. configura el repositorio remoto por separado;
7. habilita infraestructura externa únicamente con autorización y credenciales válidas;
8. documenta cualquier desviación del contrato generado.

## 11. Desinstalar

La desinstalación consiste en retirar la carpeta instalada de skills. Antes de hacerlo,
comprueba la ruta exacta y conserva cambios propios si existen. Eliminar la skill no borra
los proyectos que ella haya generado: son repositorios independientes.

