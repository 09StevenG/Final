# Universidad de Costa Rica - GF-0657 Programación en SIG 2022-II - Profesor Manuel Vargas 
## Estudiante Steven Guillén Rivera
### Registro de presencia de especies en Costa Rica.
### Proyecto final Streamlit

La aplicación resultante del código fuente muestra información de los registros de presencia de espacies en Costa Rica por medio de tablas, gráficos y mapa interactivo.

El flujo de trabajo inicial se articula con base en el manejo de datos con las bibliotecas Pandas, GeoPandas,Plotly y Folium que permite filtrar y sintetizar la información en tablas y gráficos dividiendo los registros entre provincias e incluso a una escala de análisis cantonal. En la parte final del proceso los hallazgos se integran en  la aplicación interactiva con la biblioteca Streamlit que permite publicar en la plataforma Streamlit Cloud. El usuario final tiene la capacidad de suministrar un archivo CSV y realizar la consulta de una especie en específico. 

#### La fuente de los datos 
Los datos de cantones en archivo GeoJSON utilizados para este trabajo están alojados en el Sistema Nacional de Información Territorial [SNIT](https://www.snitcr.go.cr/ico_servicios_ogc_info?k=bm9kbzo6NDA=&nombre=SINAC).

El archivo CSV con registros de presencia de especies de Costa Rica, que seleccione el usuario y siga el estándar de  [Darwin Core](https://dwc.tdwg.org/terms/).

Estos archivos CSV de presencia del registro de presencia de especies se pueden obtener en Global Biodiversity Information Facility [GBIF](https://www.gbif.org/occurrence/download/0141580-220831081235567).
 

##### Resultado final 

En el siguiente enlace se puede apreciar el trabajo llevado a cabo publicado en [Streamlit Cloud](https://09steveng-final-prin-nlv5y5.streamlit.app/).


