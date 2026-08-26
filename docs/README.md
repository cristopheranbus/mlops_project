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
3. [Gobernanza y revisión](governance.md)
4. [Guía de contribución](../CONTRIBUTING.md)
5. [Política de seguridad](../SECURITY.md)

### Tengo un fallo

Consulta [Solución de problemas](troubleshooting.md) y reúne la salida mínima indicada
antes de solicitar ayuda.

## Documentos normativos

Los archivos de este directorio son explicativos. Las reglas que la skill consume durante
la generación viven bajo [`references/`](../references/):

- [Arquitectura](../references/architecture.md)
- [Calidad](../references/quality.md)
- [Pruebas](../references/testing.md)
- [MLflow](../references/mlflow.md)
- [Databricks](../references/databricks.md)

Cuando una guía y una referencia discrepen, corrige ambas. `SKILL.md` define el flujo de
ejecución y las referencias definen el estándar aplicado.
