# Política de seguridad

La seguridad de esta skill tiene dos dimensiones: proteger el repositorio de la skill y
evitar que los proyectos generados incorporen secretos o afirmaciones operativas falsas.

## Alcance

Reporta de forma privada problemas como:

- exposición de credenciales en el repositorio o su historial;
- instrucciones que puedan sobrescribir destinos sin autorización;
- generación de workflows con permisos excesivos;
- inclusión de secretos en configuración versionada;
- comandos que filtren tokens en logs;
- promoción o despliegue sin validar la versión exacta;
- bypass de controles de aprobación o smoke tests;
- manejo inseguro de rutas en el validador.

Los errores funcionales sin impacto de seguridad pueden tratarse como issues normales una
vez exista un repositorio remoto y un canal público definido.

## Cómo reportar

La plantilla de issues enlaza esta política en lugar de abrir un reporte público. Si el
repositorio se publica, el canal recomendado es **GitHub private vulnerability
reporting**, que debe habilitarse en su configuración de seguridad.

Cuando ese canal esté habilitado, usa `Security` → `Report a vulnerability` en GitHub. Si
el repositorio permanece privado, limita los reportes a colaboradores autorizados y
define un contacto privado para terceros antes de ampliar el acceso. No abras un issue
público para una vulnerabilidad. Mientras el repositorio remoto o el canal privado todavía
no estén disponibles:

- no publiques credenciales ni detalles explotables en un issue público;
- contacta directamente al mantenedor mediante un medio privado acordado;
- comparte la mínima evidencia necesaria y elimina secretos de capturas y logs.

Un reporte útil incluye:

- componente y versión o commit afectado;
- impacto observado o potencial;
- pasos mínimos de reproducción;
- condiciones necesarias;
- mitigación temporal, si existe;
- confirmación de que el reporte no contiene secretos activos.

## Respuesta ante un secreto expuesto

Si un secreto se añadió a Git:

1. deja de usarlo y evita copiarlo en más logs o mensajes;
2. revócalo o rótalo en el sistema emisor;
3. determina repositorios, artefactos y logs donde apareció;
4. retíralo del estado actual;
5. evalúa limpiar el historial mediante un procedimiento coordinado;
6. revisa accesos realizados durante la ventana de exposición;
7. agrega prevención: `.gitignore`, scanner, permisos mínimos o gestor de secretos.

Eliminar el archivo en un commit posterior no invalida un secreto que ya estuvo en el
historial. La rotación es la acción prioritaria.

## Reglas para proyectos generados

### Credenciales

- obtener secretos desde variables, identidades de workload o gestores autorizados;
- versionar solo nombres de variables y valores de ejemplo ficticios;
- ignorar `.env`, `.databrickscfg`, claves, certificados y stores locales;
- evitar imprimir configuración completa cuando puede contener secretos.

### CI

- declarar permisos mínimos;
- separar calidad local de despliegue;
- proteger entornos productivos;
- preferir identidades de corta duración frente a tokens estáticos;
- no ejecutar código no confiable con secretos de producción.

### MLflow

- no registrar credenciales como parámetros, tags o artefactos;
- controlar acceso al tracking server y artifact store;
- usar versiones exactas para decisiones de promoción;
- conservar evidencia auditable sin incluir datos sensibles innecesarios.
- mantener AI Gateway deshabilitado en proyectos generados; el validador rechaza gateway
  secrets, `auth_config.api_base` y rutas proxy con `mlflow-security`;
- no considerar una validación local de URL como corrección suficiente de SSRF: debe
  protegerse el destino efectivo, DNS, redirects, permisos y egress;
- revisar [la guía específica](docs/mlflow-security.md) y el advisory
  [GHSA-h7x2-h6g9-p789](https://github.com/advisories/GHSA-h7x2-h6g9-p789).

### Databricks

- usar una identidad de automatización con permisos mínimos;
- preferir federación/OIDC según el entorno autorizado;
- gobernar modelos y datos en el catálogo correspondiente;
- separar dev y prod;
- exigir aprobación cuando la política organizacional lo requiera;
- ejecutar smoke tests antes de mover el alias productivo;
- conservar un rollback conocido.

## Límites del validador

El validador detecta algunos nombres de archivos sensibles, pero no reemplaza:

- escaneo de secretos por patrones y entropía;
- análisis de dependencias;
- revisión de permisos de workflows;
- SAST;
- revisión de infraestructura;
- controles de acceso del tracking server o workspace.

Un resultado sin issues significa que no se detectaron violaciones estructurales
implementadas; no constituye una certificación de seguridad.

## Divulgación y corrección

Una vez exista un canal formal, el proceso recomendado es:

1. confirmar recepción sin solicitar secretos adicionales;
2. reproducir en un entorno aislado;
3. clasificar impacto y versiones afectadas;
4. preparar corrección y pruebas de regresión;
5. rotar cualquier credencial comprometida;
6. publicar una actualización y mitigaciones;
7. atribuir al reportante cuando lo desee y sea seguro.
