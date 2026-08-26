## Resumen

Describe qué cambia y por qué es necesario.

## Tipo de cambio

- [ ] Corrección de un error
- [ ] Nueva capacidad o perfil
- [ ] Cambio de contrato o comportamiento
- [ ] Refactorización sin cambio funcional
- [ ] Documentación
- [ ] CI, packaging o mantenimiento
- [ ] Seguridad

## Evidencia

Incluye los comandos ejecutados y sus resultados. Si alguna validación no se ejecutó,
explica por qué y qué autorización, credencial o infraestructura falta.

```text
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --basetemp .pytest-tmp
uv build
```

## Impacto y compatibilidad

- ¿Cambia `skills/create-mlops-project/SKILL.md`, un perfil, un código de issue o la
  estructura generada?
- ¿Rompe compatibilidad con proyectos o consumidores existentes?
- ¿Requiere migración, actualización documental o una nueva versión?

## Checklist

- [ ] El PR tiene un alcance único y revisable.
- [ ] No incluye secretos, credenciales, datasets ni artefactos privados.
- [ ] Se agregaron pruebas positivas y negativas cuando cambió una regla.
- [ ] Ruff, formato, mypy, pytest y build pasan localmente.
- [ ] La cobertura se mantiene en al menos 85%.
- [ ] README, guías y referencias normativas están alineados.
- [ ] Las validaciones externas se distinguen de las locales.
- [ ] Los cambios incompatibles y pasos de migración están documentados.
- [ ] El PR está listo para revisión de `@cristopheranbus`.
