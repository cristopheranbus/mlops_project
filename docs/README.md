# Documentación

Este directorio contiene las guías de uso y mantenimiento de `create-mlops-project`.

## Rutas de lectura

### Quiero usar la skill por primera vez

1. [Tutorial inicial paso a paso](beginner-tutorial.md)
2. [Guía de inicio e instalación](getting-started.md)
3. [Perfiles](profiles.md)
4. [Ejemplos](examples.md)
5. [Validación](validation.md)

### Soy ML engineer

1. [Contrato del proyecto generado](project-contract.md)
2. [Configuración tipada](configuration.md)
3. [Notebooks y MLflow](notebooks-mlflow.md)
4. [Seguridad de MLflow](mlflow-security.md)
5. [Ruff estricto](ruff.md)
6. [mypy estricto](mypy.md)
7. [Perfiles](profiles.md)
8. [Estrategia de pruebas](testing-strategy.md)

### Trabajo con Databricks

1. [Notebooks y MLflow](notebooks-mlflow.md)
2. [Configuración tipada](configuration.md)
3. [Perfil Databricks](profiles.md#perfil-databricks-mlops)
4. [Contrato del proyecto](project-contract.md)
5. [Workflows de CI y monitoreo](ci-workflows.md)

### Quiero hacer mi primera contribución

1. [Tutorial inicial](beginner-tutorial.md)
2. [Mi primera contribución](../CONTRIBUTING.md#mi-primera-contribución)
3. [Validación](validation.md)
4. [Estrategia de pruebas](testing-strategy.md)
5. [Workflows](ci-workflows.md)

### Quiero definir un proyecto correctamente

1. [Contrato del proyecto generado](project-contract.md)
2. [Perfiles](profiles.md)
3. [Ejemplos](examples.md)

### Quiero mantener o extender la skill

1. [Diseño interno](design.md)
2. [Validación](validation.md)
3. [Ruff estricto](ruff.md)
4. [mypy estricto](mypy.md)
5. [Evaluación de activación](evaluation.md)
6. [Gobernanza y revisión](governance.md)
7. [Guía de contribución](../CONTRIBUTING.md)
8. [Política de seguridad](../SECURITY.md)
9. [Migración desde v0.1.0](migration-v0.1.md)
10. [Estrategia de pruebas](testing-strategy.md)
11. [Workflows y operación](ci-workflows.md)

### Tengo un fallo

Consulta [Solución de problemas](troubleshooting.md) y reúne la salida mínima indicada
antes de solicitar ayuda.

## Documentos normativos

Los archivos de este directorio son explicativos. Las reglas que la skill consume durante
la generación viven bajo
[`skills/create-mlops-project/references/`](../skills/create-mlops-project/references/):

- [Arquitectura](../skills/create-mlops-project/references/architecture.md)
- [Configuración](../skills/create-mlops-project/references/configuration.md)
- [Calidad](../skills/create-mlops-project/references/quality.md)
- [Pruebas](../skills/create-mlops-project/references/testing.md)
- [MLflow](../skills/create-mlops-project/references/mlflow.md)
- [Seguridad de MLflow](../skills/create-mlops-project/references/mlflow-security.md)
- [Databricks](../skills/create-mlops-project/references/databricks.md)

Cuando una guía y una referencia discrepen, corrige ambas. El
[`SKILL.md`](../skills/create-mlops-project/SKILL.md) de la skill define el flujo de
ejecución y las referencias definen el estándar aplicado.
