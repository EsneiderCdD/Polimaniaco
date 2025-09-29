# Scripts de Procesamiento - Orden de Ejecución

## Orden de los scripts:

### 1. `python run_scraper.py`
- Ejecuta el scraper principal para obtener ofertas
- Luego actualiza las descripciones completas

### 2. `python run_processing.py`
- Analiza las ofertas de la BD
- Extrae el stack tecnológico de cada descripción
- Guarda los resultados en la tabla `analisis_resultados`

### 3. `python -m scripts.calc_compatibilidad`
- Calcula la compatibilidad entre tu perfil y cada oferta
- Asigna puntajes basados en coincidencias tecnológicas
- Actualiza el campo `compatibilidad` en `analisis_resultados`

### 4. `python -m scripts.export_analisis`
- Genera el archivo JSON final con todos los análisis
- Exporta los datos procesados para revisión externa

### 5. `python -m scripts.calcular_metricas`
- Calcula métricas agregadas a partir de las ofertas procesadas
- Métricas incluidas:
  - Tecnologías más solicitadas (conteo y porcentaje)
  - Ubicaciones con más ofertas
  - Modalidad de trabajo
  - Métricas generales (total de ofertas y promedio de compatibilidad)
- Actualiza las tablas: `metricas_tecnologia`, `metricas_ubicacion`, `metricas_modalidad`, `metricas_generales`


## Resumen del flujo:
**Scraping → Procesamiento → Scoring → Exportación**