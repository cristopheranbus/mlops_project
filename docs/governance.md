# Gobernanza y revisión de contribuciones

Este proyecto acepta contribuciones mediante pull requests. El objetivo es permitir que
otras personas propongan cambios sin perder trazabilidad ni control sobre `main`.

## Responsabilidad de revisión

El archivo [`.github/CODEOWNERS`](../.github/CODEOWNERS) asigna todo el repositorio a
`@cristopheranbus`. Cuando `CODEOWNERS` está en la rama base, GitHub solicita
automáticamente su revisión en los pull requests no draft que modifican archivos
alcanzados por la regla.

La solicitud automática de revisión sirve como aviso y asignación. Para impedir merges sin
esa aprobación también debe activarse en GitHub una regla de protección o ruleset que
requiera revisión de code owners.

## Flujo de contribución

1. crear un fork o una rama según los permisos disponibles;
2. realizar un cambio enfocado;
3. ejecutar todos los gates locales;
4. abrir un pull request hacia `main`;
5. completar la plantilla y declarar verificaciones no ejecutadas;
6. esperar CI y revisión del propietario;
7. corregir observaciones mediante commits adicionales;
8. resolver todas las conversaciones;
9. hacer merge solo después de cumplir revisiones y checks.

## Política recomendada para `main`

Una vez creado el repositorio remoto, configurar una regla para `main` con:

- pull request obligatorio antes del merge;
- al menos una aprobación;
- aprobación requerida de code owners;
- invalidación de aprobaciones obsoletas cuando cambia el diff;
- resolución obligatoria de conversaciones;
- check requerido del job `quality`;
- prohibición de force push;
- prohibición de eliminar la rama;
- aplicación de la regla a administradores cuando el plan de GitHub lo permita;
- historial lineal si se adopta squash merge o rebase como política.

El check requerido debe usar un nombre único. El workflow actual contiene el job
`quality`, que ejecuta lint, formato, tipado y pruebas.

## Estrategia de merge

Se recomienda **squash merge** para mantener un commit enfocado por contribución. El título
final debe describir el cambio en modo imperativo. Antes de hacer merge:

- revisar el diff completo;
- confirmar que CI corresponde al último commit;
- comprobar cambios de contrato y documentación;
- verificar que no existan secretos;
- confirmar que las validaciones externas estén descritas con precisión.

## Cómo mantenerse informado

Hay dos mecanismos complementarios:

1. **Review requests:** `CODEOWNERS` solicita automáticamente la revisión del propietario.
2. **Watch del repositorio:** en GitHub, seleccionar `Watch` → `Custom` →
   `Pull requests` para recibir actividad de PR mediante las vías habilitadas en la cuenta.

En la configuración personal de notificaciones se puede habilitar entrega en GitHub y por
correo electrónico para actividad observada o participada. La elección de correo es
personal y no se versiona en este repositorio.

## Draft pull requests

GitHub no solicita automáticamente revisión de code owners mientras un PR permanece como
draft. La solicitud ocurre cuando el PR está listo para revisión. Los contribuidores deben
usar draft durante trabajo incompleto y marcar `Ready for review` cuando hayan ejecutado
los controles aplicables.

## Cambios sensibles

Los siguientes cambios requieren atención adicional:

- modificación de `SKILL.md` o su descripción de activación;
- cambios en perfiles o rutas requeridas;
- cambios de códigos de issue del validador;
- permisos de GitHub Actions;
- nuevas dependencias o integraciones externas;
- cambios incompatibles;
- procesamiento de credenciales;
- publicación, despliegue o promoción.

Un PR sensible debe explicar impacto, mitigaciones, migración y evidencia de pruebas.

## Incidentes de seguridad

Las vulnerabilidades no deben publicarse como issues. La configuración de issues dirige a
[SECURITY.md](../SECURITY.md), donde se distingue el canal aplicable a repositorios
públicos y privados.

## Referencias oficiales de GitHub

- [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Configuring notifications](https://docs.github.com/en/subscriptions-and-notifications/get-started/configuring-notifications)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Configuring private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository)
