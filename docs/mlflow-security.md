# Seguridad de MLflow y límite de AI Gateway

Esta guía explica el riesgo que cubre la regla `mlflow-security`, qué queda protegido por
el proyecto generado y qué debe hacer una persona que necesite MLflow AI Gateway. Está
escrita para poder seguirse sin conocimientos previos de SSRF o seguridad de red.

## Respuesta corta

Los perfiles `mlflow-local` y `databricks-mlops` usan **MLflow Tracking**, pero la skill
no genera ni permite configurar **MLflow AI Gateway**. El validador rechaza:

- creación programática de gateway secrets;
- rutas REST de gateway secrets;
- rutas `/gateway/proxy`;
- configuración de `auth_config.api_base` asociada a MLflow AI Gateway;
- imports o referencias productivas que activen el gateway.

Este límite mitiga el escenario descrito en
[GHSA-h7x2-h6g9-p789](https://github.com/advisories/GHSA-h7x2-h6g9-p789): un destino
`api_base` controlado podría hacer que el servidor solicite recursos internos y devuelva
la respuesta al llamador. La regla no afirma corregir MLflow upstream; impide introducir
esa superficie en el scaffold hasta que exista una solución revisada y el contrato se
actualice con evidencia.

## Tracking y AI Gateway no son lo mismo

| Capacidad | Para qué se usa | Estado en proyectos generados |
| --- | --- | --- |
| MLflow Tracking | Registrar runs, parámetros, métricas, modelos y artefactos | Permitido y estandarizado |
| Model Registry | Gestionar versiones y aliases con controles explícitos | Opcional según el perfil |
| AI Gateway | Guardar configuración de proveedores y reenviar solicitudes HTTP | Deshabilitado por contrato |

Un proyecto puede entrenar, evaluar y comparar modelos con MLflow Tracking sin exponer
AI Gateway. Por eso el primer entrenamiento local sigue funcionando sin credenciales ni
infraestructura externa.

## Qué es SSRF

SSRF significa *Server-Side Request Forgery*. Aparece cuando una entrada controlable por
un usuario determina hacia dónde hace una solicitud HTTP el servidor. El peligro no es
sólo acceder a `localhost`: el servidor puede alcanzar redes privadas, servicios internos
o endpoints de metadata de la nube que no son accesibles desde el equipo del atacante.

Validar únicamente que el valor “parezca una URL” no basta. Una defensa completa debe
considerar esquema, hostname, resolución DNS, IPv4, IPv6, redirects, cambios de DNS,
userinfo y cada destino efectivo de conexión.

## Qué hace el validador

El validador inspecciona archivos productivos y de despliegue bajo `src/`, `configs/`,
`resources/`, `notebooks/`, además de `pyproject.toml` y `databricks.yml`. No bloquea una
mención educativa dentro de `docs/` ni una prueba de seguridad bajo `tests/`.

Ejemplo rechazado:

```yaml
mlflow:
  gateway:
    auth_config:
      api_base: http://169.254.169.254
```

Resultado esperado:

```text
ERROR [mlflow-security] MLflow AI Gateway configuration is not allowed ...
```

La corrección normal es retirar esa configuración. No cambies el nombre de la clave, no
codifiques la URL para ocultarla y no desactives la regla: eso conservaría el riesgo sin
resolverlo.

## Qué sí puedes hacer con el proyecto

Sin AI Gateway puedes:

1. ejecutar entrenamiento local;
2. abrir un run mediante `start_experiment_run`;
3. usar `mlflow.autolog` dentro del run;
4. registrar configuración resuelta, hash, métricas y artefactos;
5. evaluar el modelo y aplicar umbrales;
6. usar tracking remoto si el servidor está autorizado y protegido;
7. registrar y promover versiones cuando el perfil y la gobernanza lo requieran.

## Dependencias y versiones

Mantén MLflow con un rango limitado en `pyproject.toml` y una resolución reproducible en
`uv.lock`. Antes de actualizar:

```powershell
uv lock --upgrade-package mlflow
uv run pip-audit
uv run pytest
```

En Bash se usan los mismos comandos. Revisa además el changelog y los advisories de la
versión resuelta. Un número de versión, una rama o la palabra `latest` no constituyen por
sí solos evidencia de que este flujo SSRF esté corregido. La fuente vigente para la
situación concreta es el advisory enlazado arriba.

## Despliegue seguro de Tracking

Aunque AI Gateway esté deshabilitado, un servidor de Tracking necesita controles:

- autenticación y autorización explícitas;
- TLS en tránsito;
- permisos mínimos sobre artefactos y base de datos;
- aislamiento de red y reglas de egress;
- límites de tamaño y tiempo de solicitud;
- logs de acceso sin tokens ni cuerpos sensibles;
- backups y restauración probada;
- actualización y auditoría periódica de dependencias;
- no exponer el servidor directamente a Internet sin una arquitectura revisada.

Consulta la [documentación oficial de seguridad de MLflow](https://mlflow.org/docs/latest/self-hosting/security/)
y la [documentación oficial de autenticación](https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/).

## Si el negocio necesita AI Gateway

Trátalo como un cambio de seguridad independiente. Antes de modificar la regla deben
existir, como mínimo:

1. una versión upstream revisada que corrija el camino completo de creación y proxy;
2. autorización administrativa específica para crear o modificar secrets;
3. allowlist HTTPS de destinos permitidos;
4. bloqueo de loopback, redes privadas, link-local, metadata, direcciones reservadas,
   multicast y unspecified, en IPv4 e IPv6;
5. revalidación del destino después de resolver DNS y en cada redirect;
6. política de egress que aplique aunque falle la validación de aplicación;
7. límites del cuerpo de respuesta y timeouts;
8. pruebas negativas de bypass y una revisión de seguridad;
9. propietario, versión revisada, fecha, evidencia y rollback documentados.

No implementes una función local de “validar URL” y la consideres suficiente: el control
debe proteger la solicitud que realmente sale del servidor.

## Pruebas de regresión esperadas

Una futura habilitación debe probar al menos:

- `127.0.0.1`, `::1` y nombres que resuelven a loopback;
- rangos RFC1918 y direcciones IPv6 privadas;
- `169.254.169.254` y endpoints de metadata equivalentes;
- representación decimal, octal, hexadecimal y direcciones IPv4 embebidas en IPv6;
- URL con userinfo, fragmentos y puertos no permitidos;
- redirects desde un host autorizado hacia uno bloqueado;
- DNS rebinding entre validación y conexión;
- permisos de una cuenta de sólo lectura;
- respuesta excesiva, timeout y error del upstream.

Estas pruebas deben ejecutarse contra servicios controlados de laboratorio, nunca contra
metadata real o recursos internos de terceros.

## Respuesta ante una exposición existente

Si ya existe un gateway desplegado:

1. restringe o deshabilita inmediatamente sus rutas externas;
2. limita egress y bloquea metadata y redes internas;
3. identifica quién pudo crear o modificar gateway secrets;
4. revisa logs de destinos, redirects y respuestas sin volver a exponer secretos;
5. rota credenciales potencialmente alcanzables;
6. actualiza a una corrección upstream verificada cuando esté disponible;
7. ejecuta pruebas de regresión en un entorno aislado;
8. documenta alcance, decisiones y evidencia de cierre.

## Enlaces oficiales y de referencia

- [MLflow: Security](https://mlflow.org/docs/latest/self-hosting/security/)
- [MLflow: Basic HTTP Authentication](https://mlflow.org/docs/latest/self-hosting/security/basic-http-auth/)
- [MLflow Tracking API](https://mlflow.org/docs/latest/ml/tracking/tracking-api/)
- [Advisory GHSA-h7x2-h6g9-p789](https://github.com/advisories/GHSA-h7x2-h6g9-p789)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
