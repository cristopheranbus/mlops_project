# Documentación

Este directorio contiene las guías de uso y mantenimiento de `create-mlops-project`.

## Rutas de lectura

### Quiero usar la skill por primera vez

1. [Guía de inicio](getting-started.md)
2. [Perfiles](profiles.md)
3. [Ejemplos](examples.md)
4. [Validación](validation.md)

### Quiero definir un proyecto correctamente

1. [Contrato del proyecto generado](project-contract.md)
2. [Perfiles](profiles.md)
3. [Ejemplos](examples.md)

### Quiero mantener o extender la skill

1. [Diseño interno](design.md)
2. [Validación](validation.md)
3. [Evaluación de activación](evaluation.md)
4. [Gobernanza y revisión](governance.md)
5. [Guía de contribución](../CONTRIBUTING.md)
6. [Política de seguridad](../SECURITY.md)

### Tengo un fallo

Consulta [Solución de problemas](troubleshooting.md) y reúne la salida mínima indicada
antes de solicitar ayuda.

## Documentos normativos

Los archivos de este directorio son explicativos. Las reglas que la skill consume durante
la generación viven bajo
[`skills/create-mlops-project/references/`](../skills/create-mlops-project/references/):

- [Arquitectura](../skills/create-mlops-project/references/architecture.md)
- [Calidad](../skills/create-mlops-project/references/quality.md)
- [Pruebas](../skills/create-mlops-project/references/testing.md)
- [MLflow](../skills/create-mlops-project/references/mlflow.md)
- [Databricks](../skills/create-mlops-project/references/databricks.md)

Cuando una guía y una referencia discrepen, corrige ambas. El
[`SKILL.md`](../skills/create-mlops-project/SKILL.md) de la skill define el flujo de
ejecución y las referencias definen el estándar aplicado.
