# Aplicación desarrollada en Streamlit para visualización de datos de biodiversidad
# Autor código fuente : Manuel Vargas (mfvargas@gmail.com)
# Estudiante que utiliza código base  : Steven Guillén Rivera 
# Fecha de creación: 2022-12-12

# Cargar bibliotecas 

import streamlit as st 
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from folium import Marker
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import math

#
# Configuración de la página
#
st.set_page_config(layout='wide')


#
# TÍTULO Y DESCRIPCIÓN DE LA APLICACIÓN
#

st.title('Visualización de datos de biodiversidad')
st.markdown('Esta aplicación presenta visualizaciones tabulares, gráficas y geoespaciales de datos de biodiversidad que siguen el estándar [Darwin Core (DwC)](https://dwc.tdwg.org/terms/).')
st.markdown('El usuario debe seleccionar un archivo CSV basado en el DwC y posteriormente elegir una de las especies con datos contenidos en el archivo. **El archivo debe estar separado por tabuladores**. Este tipo de archivos puede obtenerse, entre otras formas, en el portal de la [Infraestructura Mundial de Información en Biodiversidad (GBIF)](https://www.gbif.org/).')
st.markdown('La aplicación muestra un conjunto de tablas, gráficos y mapas correspondientes a la distribución de la especie en el tiempo y en el espacio.')



# ENTRADAS

# Carga de datos
archivo_registros_presencia = st.sidebar.file_uploader('Seleccione un archivo CSV que siga el estándar DwC')

# Se continúa con el procesamiento solo si hay un archivo de datos cargado
if archivo_registros_presencia is not None:
# Carga de registros de presencia en un dataframe
    registros_presencia = pd.read_csv(archivo_registros_presencia, delimiter='\t')
# Conversión del dataframe de registros de presencia a geodataframe
    registros_presencia = gpd.GeoDataFrame(registros_presencia, 
                                           geometry=gpd.points_from_xy(registros_presencia.decimalLongitude, 
                                                                       registros_presencia.decimalLatitude),
                                           crs='EPSG:4326')

# Carga de polígonos de cantones
    cantones = gpd.read_file("datos/Cantones.geojson")

# Limpieza de datos
# Eliminación de registros con valores nulos en la columna 'species'
    registros_presencia = registros_presencia[registros_presencia['species'].notna()]
# Cambio del tipo de datos del campo de fecha
    registros_presencia["eventDate"] = pd.to_datetime(registros_presencia["eventDate"])

# Especificación de filtros
# Especie
    lista_especies = registros_presencia.species.unique().tolist()
    lista_especies.sort()
    filtro_especie = st.sidebar.selectbox('Seleccione la especie', lista_especies)

#
# PROCESAMIENTO
#

# Filtrado
    registros_presencia = registros_presencia[registros_presencia['species'] == filtro_especie]

# Cálculo de la cantidad de registros en Cantones
# "Join" espacial de las capas de Cantones y registros de presencia
    cantones_contienen_reg = cantones.sjoin(registros_presencia, how="left", predicate="contains")
# Conteo de registros de presencia en cada Cantón
    cantones_registros = cantones_contienen_reg.groupby("CODNUM").agg(cantidad_registros_presencia = ("gbifID","count"))
    cantones_registros = cantones_registros.reset_index() # para convertir la serie a dataframe

#
# SALIDAS -----------------------------
#     

# Tablas de registros de presencia
    st.header('Registros de presencia de especies')
    st.dataframe(registros_presencia[['eventDate','species', 'stateProvince', 'locality']].rename(columns = {'eventDate':'Fecha', 'species':'Especie', 'stateProvince':'Provincia', 'locality':'Localidad'}))

# Definición de columnas

 # Definición de columnas que divide el contenido en dos para facilitar lectura
    col1, col2 = st.columns(2)
    col3 = st.columns(1)

# Gráficos de cantidad de registros de presencia por provincia
# Este "Join" es para agregar la columna con el conteo a la capa de cantón en un proceso inicial, posteriormente se utiliza provincia
    cantones_registros = cantones_registros.join(cantones.set_index('CODNUM'), on='CODNUM', rsuffix='_b')
# Dataframe con filtro para graficar
    cantones_registros_graf = cantones_registros.loc[cantones_registros['cantidad_registros_presencia'] > 0, 
                                                            ["provincia", "cantidad_registros_presencia"]].sort_values("cantidad_registros_presencia", ascending=True) 
    cantones_registros_graf = cantones_registros_graf.set_index('provincia')  

    with col1:
        # Gráficos de registros de presencia de especie por provincias
        st.header('Registros de especie por provincia')

        fig = px.bar(cantones_registros_graf, 
                    labels={'provincia':'Provincia', 'cantidad_registros_presencia':'Registros de presencia'})    

        fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig) 

# Gráficos de cantidad de registros de presencia por cantón
# Este "Join" sirve para agregar la columna con el conteo a la capa de cantón
    cantones_registros = cantones_registros.join(cantones.set_index('CODNUM'), on='CODNUM', rsuffix='_b')
# Dataframe filtrado para usar en graficación
    cantones_registros_graf = cantones_registros.loc[cantones_registros['cantidad_registros_presencia'] > 0, 
                                                            ["NCANTON", "cantidad_registros_presencia"]].sort_values("cantidad_registros_presencia")
    cantones_registros_graf = cantones_registros_graf.set_index('NCANTON')  

    with col2:
# Gráficos de registros de presencia de especie por canton
        st.header('Registros de presencia de especie por cantón')

        fig = px.bar(cantones_registros_graf, 
                    labels={'NCANTON':'Cantón', 'cantidad_registros_presencia':'a'})    

        fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig)

    with col1:

# Creación de mapas de coropletas de presencia de especies por provincia, cantón y agrupación de registros
        st.header('Mapa de registros de presencia de especies por provincia, cantón y agrupación')
       
 # Capa base
        m = folium.Map(
        location=[10, -84],
        tiles='Stamen Terrain', 
        zoom_start=5,
        control_scale=True)

# Añadir capas base adicionales para mejor visualización
        folium.TileLayer(
        tiles='CartoDB positron', 
        name='CartoDB positron').add_to(m)

# Capa de coropletas
        canton_map = folium.Choropleth(
            name="Mapa de coropletas de los registros por cantón",
            geo_data=cantones,
            data=cantones_registros,
            columns=['CODNUM', 'cantidad_registros_presencia'],
            bins=8,
            key_on='feature.properties.CODNUM',
            fill_color='Oranges', 
            fill_opacity=0.7, 
            line_opacity=1,
            legend_name='Cantidad de registros de presencia de especie por cantón en Costa Rica',
            smooth_factor=0).add_to(m)
        
        folium.GeoJsonTooltip(['NCANTON', 'provincia']).add_to(canton_map.geojson)


# Capa de registros de presencia agrupados
        mc = MarkerCluster(name='Registro de especie agrupados')
        for idx, row in registros_presencia.iterrows():
            if not math.isnan(row['decimalLongitude']) and not math.isnan(row['decimalLatitude']):
                mc.add_child(
                    Marker([row['decimalLatitude'], row['decimalLongitude'], ], 
                                    popup= "Nombre la especie: " + str(row["species"]) + "\n" + "Provincia: " + str(row["stateProvince"]) + "\n" + "Fecha: " + str(row["eventDate"]),
                                    icon=folium.Icon(color="red")))
        m.add_child(mc)

        
        provincia_mapa = folium.Choropleth(
            name="Mapa de coropletas de los registros de especie por provincia",
            geo_data=cantones,
            data=cantones_registros,
            columns=['provincia', 'cantidad_registros_presencia'],
            bins=8,
            key_on='feature.properties.provincia',
            fill_color='Blues', 
            fill_opacity=0.6, 
            line_opacity=1,
            legend_name='Cantidad de registros de especies por provincia',
            smooth_factor=0).add_to(m)

        folium.GeoJsonTooltip(['NCANTON', 'provincia']).add_to(provincia_mapa.geojson)

# Control de capas
        folium.LayerControl().add_to(m) 
        # Despliegar el mapa
        folium_static(m)   
  