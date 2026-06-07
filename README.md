# Dashboard Ejecutivo Grupo Exito

Dashboard interactivo para analisis de ventas, clientes, inventarios y logistica de Grupo Exito.

## Caracteristicas

- 33 visualizaciones interactivas en 5 pestanas
- Filtros globales por ano, mes, region, canal, categoria y segmento
- Insights automaticos generados por IA
- Exportacion a PDF de reportes ejecutivos
- Analisis avanzados de rentabilidad, eficiencia, comportamiento y benchmarking

## Instalacion

```bash
pip install -r requirements.txt
```

## Uso Local

```bash
streamlit run app.py
```

## Estructura del Proyecto

```
grupo_exito_dashboard/
├── app.py                  # Aplicacion principal Streamlit
├── requirements.txt        # Dependencias
├── README.md              # Este archivo
├── data/                  # Datasets CSV
│   ├── 01_ventas_mensuales_canal_categoria_region.csv
│   ├── 02_inventarios_region_formato_categoria.csv
│   ├── 03_conversion_digital_funnel.csv
│   ├── 04_clientes_segmentos_clv_nps.csv
│   ├── 05_logistica_entregas_region_canal.csv
│   └── 06_kpis_dashboard_mensual.csv
└── utils/                 # Modulos de utilidad
    ├── load_data.py
    ├── data_processing.py
    ├── insights_generator.py
    ├── advanced_charts_2.py
    ├── drilldown_utils.py
    └── pdf_report_generator.py
```

## Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio de GitHub
4. Selecciona `app.py` como archivo principal
5. Despliega

## Datos

Los datos son sinteticos y estan basados en informes publicos de Grupo Exito para fines academicos.

## Licencia

MIT License
