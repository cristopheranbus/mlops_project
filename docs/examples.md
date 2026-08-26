# Ejemplos de uso

Los ejemplos muestran cómo expresar intención, restricciones y criterios de éxito. No son
plantillas rígidas: adapta métricas, fuentes y arquitectura a tu dominio.

## Patrón recomendado

Una solicitud robusta suele seguir esta forma:

```text
Usa $create-mlops-project para crear [destino].

Problema: [tipo, población y unidad de predicción].
Datos: [fuente, formato, target y reglas relevantes].
Modelo: [framework o restricciones].
Evaluación: [métrica principal, diagnósticos, partición y umbrales].
Operación: [batch/online, frecuencia, latencia y perfil].
Calidad: [Python, cobertura y controles adicionales].
```

Los corchetes aquí explican el patrón; en una solicitud real se reemplazan por contenido
concreto.

## Clasificación binaria local

```text
Usa $create-mlops-project para crear ./customer_churn.

Problema: clasificación binaria para predecir si una cuenta activa abandonará durante
los próximos 30 días. La unidad de predicción es una cuenta al cierre de cada semana.

Datos: archivos Parquet locales; target churned_30d. Separa entrenamiento y validación
por fecha para evitar fuga temporal. Las columnas customer_id y snapshot_date identifican
la observación y no deben entrar directamente como features.

Modelo: scikit-learn con un baseline simple y una implementación extensible.

Evaluación: ROC AUC principal; average precision, recall y precision como diagnósticos.
Aceptar si ROC AUC >= 0.82 y recall >= 0.65. Incluir métricas por segmento de plan.

Operación: scoring batch semanal, sin MLflow ni despliegue online. Usa perfil python-ml,
Python 3.12 y cobertura mínima de 90%.
```

Una buena salida debe incluir partición temporal, contrato de esquema, baseline,
evaluación segmentada y un entry point batch. No necesita registry ni serving.

## Regresión con restricciones de negocio

```text
Usa $create-mlops-project para crear ./vehicle_price_model.

Problema: regresión para estimar precio de publicación de vehículos usados. La predicción
se genera por anuncio.

Datos: CSV versionados externamente; target listing_price. Valida precios positivos,
antigüedad coherente y categorías desconocidas. Excluye identificadores y texto libre en
la primera versión.

Modelo: scikit-learn. Incluye un baseline de mediana por categoría y un pipeline para el
modelo candidato.

Evaluación: MAE principal, RMSE y error porcentual por rango de precio. El candidato debe
mejorar el MAE del baseline al menos 8% y no superar un error absoluto mediano de 10% en
ningún rango con suficiente muestra.

Operación: ejecución local y predicción batch. Perfil python-ml, Python 3.12, cobertura
85%. Documenta claramente unidades monetarias y tratamiento de outliers.
```

## Forecasting con backtesting

```text
Usa $create-mlops-project para crear ./demand_forecasting.

Problema: pronóstico diario de unidades por tienda y SKU con horizonte de 28 días.

Datos: tablas Parquet con ventas, inventario, precio y calendario. No uses información
posterior a la fecha de corte. Distingue demanda cero de quiebre de stock.

Modelo: LightGBM con features temporales y baseline estacional ingenuo.

Evaluación: WAPE principal, bias y cobertura de intervalos como diagnósticos. Implementa
backtesting con al menos tres ventanas y agrega métricas por tienda. Aceptar si WAPE
mejora al baseline en 5% relativo y el bias absoluto global es menor a 3%.

Operación: entrenamiento semanal y tracking local con MLflow. Guarda identidad del
dataset, parámetros, métricas por ventana, gráficos y modelo con firma. Perfil
mlflow-local, Python 3.12 y cobertura 90%.
```

La arquitectura debería dar responsabilidades propias a splits temporales, backtesting y
agregación de métricas, en vez de forzar el patrón de clasificación.

## Clasificación de texto

```text
Usa $create-mlops-project para crear ./ticket_routing.

Problema: clasificación multiclase de tickets hacia el equipo responsable.

Datos: JSON Lines con subject, body, locale y assigned_team. Elimina duplicados antes del
split y agrupa por thread_id para impedir que mensajes de la misma conversación aparezcan
en train y validación.

Modelo: comienza con TF-IDF y regresión logística. Diseña interfaces que permitan agregar
otro encoder después, pero no incluyas servicios externos ahora.

Evaluación: macro F1 principal; F1 por clase y matriz de confusión. Exige macro F1 >= 0.72
y recall >= 0.60 para cada clase con al menos 100 ejemplos.

Operación: batch diario, perfil python-ml, Python 3.12 y cobertura 90%. Incluye validación
del idioma y política para clases desconocidas.
```

## MLflow con evaluación y promoción

```text
Usa $create-mlops-project para crear ./credit_risk_experiments.

Problema: clasificación binaria de incumplimiento a 90 días. Usa datos Parquet y target
default_90d. La partición debe ser temporal y las métricas deben incluir ROC AUC, average
precision, Brier score y resultados por cohortes definidas en configuración.

Modelo: scikit-learn. Registra en MLflow parámetros, hash o versión del dataset, métricas,
curvas, firma, input example y artefactos de evaluación.

Promoción: entrenamiento y evaluación son pasos separados. Un candidato se acepta con
ROC AUC >= 0.78, Brier score <= 0.16 y sin caída de ROC AUC mayor a 0.02 frente al
Champion. Usa versiones exactas y aliases Challenger/Champion.

Operación: MLflow local con backend SQLite y artefactos en disco. Las pruebas de
integración deben crear stores temporales. Perfil mlflow-local, Python 3.12, cobertura
mínima 90%.
```

## Databricks con despliegue gobernado

```text
Usa $create-mlops-project para crear ./fraud_detection_platform.

Problema: clasificación online de transacciones. Datos y features residen en Unity
Catalog. Target confirmed_fraud. La métrica principal es recall a un false-positive rate
máximo de 1%; también reporta average precision y métricas por canal.

Arquitectura: paquete Python compartido, notebooks finos, MLflow y modelos registrados en
Unity Catalog. Define Asset Bundles con targets dev y prod. Separa Jobs de preparación,
entrenamiento, evaluación y promoción.

Aprobación: aceptar solo versiones con recall >= 0.85 bajo el límite de falsos positivos,
sin regresión mayor a 0.02 frente al Champion y con todas las pruebas de contrato verdes.

Despliegue: Model Serving. Despliega la versión exacta aprobada, espera readiness, ejecuta
smoke tests de esquema y semántica, y solo entonces mueve el alias Champion. Conserva el
Champion anterior para rollback.

Seguridad: GitHub OIDC y service principal de producción; no uses tokens estáticos.
Marca las pruebas de workspace como external y no las ejecutes por defecto.

Usa perfil databricks-mlops, Python 3.12 y cobertura mínima 90%. Incluye documentación de
operación, release, rollback y controles que requieren credenciales.
```

## Proyecto sin target tabular directo

```text
Usa $create-mlops-project para crear ./anomaly_detection.

Problema: detección no supervisada de anomalías en mediciones de sensores por equipo y
minuto. No existe target confiable para entrenamiento; hay una tabla pequeña de incidentes
confirmados que solo se usa para evaluación retrospectiva.

Datos: Parquet particionado por fecha. Valida continuidad temporal, unidades y rangos por
tipo de sensor. Evita usar información posterior a cada timestamp.

Modelo: baseline robusto por mediana y MAD, con interfaz para algoritmos posteriores.

Evaluación: precision de alertas sobre incidentes conocidos, alertas por equipo/día y
tiempo de anticipación. No inventes un umbral universal: hazlo configurable y documenta
cómo calibrarlo.

Operación: batch horario y perfil python-ml. Incluye pruebas de ventanas, orden temporal y
comportamiento sin historial suficiente.
```

Este ejemplo demuestra por qué la skill debe adaptar el contrato y no asumir siempre un
target supervisado tradicional.

## Solicitudes de seguimiento útiles

Después de la generación puedes pedir, por separado:

```text
Revisa el proyecto generado contra el contrato y enumera desviaciones con evidencia.
```

```text
Ejecuta todos los controles locales, corrige los fallos atribuibles al proyecto y reporta
qué validaciones externas quedaron pendientes.
```

```text
Agrega una fuente de datos nueva detrás del contrato existente sin acoplar entrenamiento
al cliente externo.
```

```text
Inicializa Git y prepara un primer commit. No crees un repositorio remoto todavía.
```

Las acciones remotas, credenciales, despliegues y publicación deben solicitarse de manera
explícita porque cambian estado fuera del proyecto local.

## Antipatrones de solicitud

### Demasiado vaga

```text
Hazme un MLOps completo.
```

No define problema, destino, métrica, entorno ni significado de “completo”. La skill debe
preguntar por decisiones materiales o elegir el perfil mínimo si el contexto basta.

### Impone complejidad sin necesidad

```text
Crea una prueba local de regresión y agrega Unity Catalog, serving y producción.
```

Si no existe una necesidad real de plataforma, conviene separar el experimento local de
una fase posterior de industrialización.

### Pide afirmar evidencia inexistente

```text
Genera el bundle y confirma que producción funciona sin conectarte al workspace.
```

Se puede generar y validar localmente la estructura, pero no confirmar recursos, permisos
ni endpoints sin una ejecución autorizada.

