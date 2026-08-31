# Migración desde v0.1.0

Esta guía aplica a consumidores que copian la skill desde `main`. La release `v0.1.0` no
se modifica; el nuevo contrato introduce errores inmediatos para proyectos generados con
la versión actual.

## Cambios incompatibles del contrato

- exactamente un paquete principal bajo `src/`;
- configuración YAML en `configs/` y modelos Pydantic bajo `src/<package>/config/`;
- `config_version: 1`, tipos estrictos y ausencia de secretos;
- funciones productivas únicamente bajo el paquete;
- MLflow abierto exclusivamente por `tracking/mlflow.py`;
- notebooks productivos únicamente en `notebooks/databricks/`;
- Jobs Databricks notebook-first con rutas comprobables.
- workflows numerados de calidad y seguridad en todos los perfiles;
- workflows separados de bundle y monitoreo en `databricks-mlops`;
- 90% de branch coverage, markers estrictos y timeout finito.

## Orden recomendado

1. crea una rama y ejecuta los tests existentes;
2. consolida el código en un único paquete;
3. crea `config/models.py`, `config/loader.py` y `config/hashing.py`;
4. migra valores a `base.yaml` y perfiles por entorno;
5. mueve la orquestación a `workflows/`;
6. centraliza MLflow en `tracking/mlflow.py`;
7. convierte notebooks en adaptadores finos y limpia outputs;
8. actualiza `databricks.yml` y la librería wheel;
9. añade documentación para principiantes;
10. reemplaza el workflow único por `01` y `02`, y agrega `03`/`04` en Databricks;
11. migra casos compartidos al inventario de `pytest_generate_tests`;
12. ejecuta el validador y todos los quality gates.

## Compatibilidad por perfil

`python-ml` requiere `base.yaml`, `local.yaml`, Pydantic y PyYAML, pero no obliga a usar
MLflow ni Databricks. `mlflow-local` añade el wrapper de runs y pruebas de integración.
`databricks-mlops` añade `dev.yaml`, `prod.yaml`, notebooks y bundle.

No migres credenciales desde archivos antiguos: retíralas, rótalas si estuvieron en Git y
usa variables de entorno o Secret Scopes. Consulta [Configuración](configuration.md),
[Notebooks y MLflow](notebooks-mlflow.md) y [Validación](validation.md).

