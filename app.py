import streamlit as st
import pandas as pd
import requests
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import locale
import altair as alt # Se añade para el gráfico de barras no apilado

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Red Pluviométrica Salta - Jujuy", 
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png", 
    layout="wide"
)

try:
    locale.setlocale(locale.LC_TIME, "es_AR.UTF-8")
except:
    pass

# --- CREDENCIALES ---
URL_PRECIPITACIONES = "https://territorios.inta.gob.ar/assets/aYqLUVvU3EYiDa7NoJbPKF/submissions/?format=json"
URL_MAPA = "https://territorios.inta.gob.ar/assets/aFwWKNGXZKppgNYKa33wC8/submissions/?format=json"
TOKEN = st.secrets["INTA_TOKEN"]


HEADERS = {'Authorization': f'Token {TOKEN}'}

# --- PROCESAMIENTO DE DATOS ---
def extraer_coordenadas(row):
    try:
        valor = row.get('Ubicaci_in') or row.get('ubicaci_in') or row.get('_Ubicaci_in')
        if isinstance(valor, str):
            partes = valor.split()
            return float(partes[0]), float(partes[1])
        elif isinstance(valor, list):
            return float(valor[0]), float(valor[1])
    except: return None, None
    return None, None

@st.cache_data(ttl=300)
def cargar_datos_completos():
    try:
        r1, r2 = requests.get(URL_PRECIPITACIONES, headers=HEADERS), requests.get(URL_MAPA, headers=HEADERS)
        df_p, df_c = pd.DataFrame(r1.json()), pd.DataFrame(r2.json())
        
        df_p['cod'] = df_p['Pluviometros'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_c['cod'] = df_c['Codigo_txt_del_pluviometro'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
        df_p['fecha_dt'] = pd.to_datetime(df_p['Fecha_del_dato'])
        df_p['fecha'] = df_p['fecha_dt'].dt.date
        df_p['mm'] = pd.to_numeric(df_p['Mil_metros_registrados'], errors='coerce').fillna(0)
        
        map_f = {'viento': 'Vientos fuertes', 'granizo': 'Granizo', 'tormenta': 'Tormentas eléctricas', 'sinfeno': 'Sin obs. de fenómenos'}
        df_p['Fenómeno atmosférico'] = df_p['fenomeno'].astype(str).str.strip().str.lower().replace(map_f)
        df_p['Fenómeno atmosférico'] = df_p['Fenómeno atmosférico'].replace({'none': 'Sin obs. de fenómenos', 'nan': 'Sin obs. de fenómenos'})

        res = df_c.apply(extraer_coordenadas, axis=1)
        df_c['lat'], df_c['lon'] = zip(*res)
        col_n = next((c for c in df_c.columns if 'Nombre_del_Pluviometro' in c), 'cod')
        
        col_depto = next((c for c in df_c.columns if 'depto' in c.lower() or 'departamento' in c.lower()), None)
        col_prov = next((c for c in df_c.columns if 'prov' in c.lower() or 'provincia' in c.lower()), None)
        
        columnas_mapa = ['cod', 'lat', 'lon', col_n]
        if col_depto: columnas_mapa.append(col_depto)
        if col_prov: columnas_mapa.append(col_prov)

        df = pd.merge(df_p, df_c[columnas_mapa], on='cod', how='left')
        df['Pluviómetro'] = df[col_n].fillna(df['cod'])
        
        if col_depto: df = df.rename(columns={col_depto: 'Departamento'})
        else: df['Departamento'] = "S/D"
            
        if col_prov: df = df.rename(columns={col_prov: 'Provincia'})
        else: df['Provincia'] = "S/D"

        return df
    except: return pd.DataFrame()

df = cargar_datos_completos()

if not df.empty:
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png"
    st.sidebar.image(logo_url, width=80)
    todas_f = sorted(df['fecha'].unique(), reverse=True)
    f_hoy = st.sidebar.date_input("Consultar otra fecha:", todas_f[0], format="DD/MM/YYYY")

    # --- CSS Y CABECERA ---
    st.markdown(f"""
        <style>
            .main-title {{
                font-weight: bold; 
                color: #1E3A8A !important; 
                margin: 0; 
                line-height: 1.1;
                font-size: 24px;
            }}
            .header-container {{
                display: flex; 
                align-items: center; 
                margin-bottom: 15px;
                gap: 12px;
            }}
            .fecha-label {{
                color: #1E3A8A;
                font-weight: bold;
                font-size: 15px;
                margin: 0;
            }}
            .separador {{
                color: #CCC;
                font-weight: normal;
            }}
            @media (max-width: 640px) {{
                .main-title {{ font-size: 18px !important; }}
                .header-logo {{ height: 35px !important; }}
                .fecha-label {{ font-size: 13px; }}
            }}
            div[data-testid="stCheckbox"] {{
                margin-bottom: 0px;
                margin-top: -5px;
            }}
        </style>
        <div class="header-container">
            <img src="{logo_url}" class="header-logo" style="height: 45px;">
            <h1 class="main-title">Red Pluviométrica Salta - Jujuy</h1>
        </div>
    """, unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["📍 Mapa", "📊 Listado", "📅 Mensual", "📈 Histórico"])

    # 1. MAPA
    with t1:
        fecha_f = f_hoy.strftime('%d/%m/%Y')
        col_ctrl1, col_ctrl2 = st.columns([0.55, 0.45])
        
        with col_ctrl1:
            st.markdown(f'<p class="fecha-label">Lluvias del {fecha_f} <span class="separador">|</span></p>', unsafe_allow_html=True)
        with col_ctrl2:
            ver_calor = st.checkbox("🔥 Calor", value=False)
        
        df_dia = df[df['fecha'] == f_hoy].dropna(subset=['lat', 'lon'])
        
        if not df_dia.empty:
            m = folium.Map(location=[df_dia['lat'].mean(), df_dia['lon'].mean()], zoom_start=7)
            
            if ver_calor:
                datos_calor = df_dia[['lat', 'lon', 'mm']].values.tolist()
                HeatMap(datos_calor, radius=20, blur=15, min_opacity=0.3).add_to(m)

            for _, r in df_dia.iterrows():
                c_hex = '#d32f2f' if r['mm'] > 50 else '#ef6c00' if r['mm'] > 20 else '#1a73e8'
                c_fol = 'red' if r['mm'] > 50 else 'orange' if r['mm'] > 20 else 'blue'
                
                html_popup = f"""
                <div style="font-family: sans-serif; min-width: 200px;">
                    <h4 style="margin:0; color:{c_hex}; border-bottom:1px solid #ccc;">{r['Pluviómetro']}</h4>
                    <b>{r['mm']} mm</b><br>
                    <small>{r['Departamento']}, {r['Provincia']}</small><br>
                    <i style="color:gray;">{r['Fenómeno atmosférico']}</i>
                </div>
                """
                folium.Marker([r['lat'], r['lon']], popup=folium.Popup(html_popup, max_width=300), 
                              icon=folium.Icon(color=c_fol, icon='cloud')).add_to(m)
                
                folium.map.Marker([r['lat'], r['lon']], icon=folium.DivIcon(icon_size=(40,20), icon_anchor=(20,-10),
                    html=f'<div style="color:{c_hex}; font-weight:900; font-size:11pt; text-shadow:1px 1px 0 #fff;">{int(r["mm"])}</div>')).add_to(m)
            
            st_folium(m, width=None, height=500)
        else: 
            st.warning("No hay datos.")

    with t2:
        st.subheader(f"Registros del {f_hoy.strftime('%d/%m/%Y')}")
        df_list = df[df['fecha'] == f_hoy][['Pluviómetro', 'mm', 'Departamento', 'Provincia', 'Fenómeno atmosférico']].sort_values('mm', ascending=False)
        st.dataframe(df_list.rename(columns={'mm': 'Lluvia (mm)'}), use_container_width=True, hide_index=True)

    with t3:
        st.subheader("📅 Acumulados Mensuales")
        df['Año'] = df['fecha_dt'].dt.year
        df['Mes_Num'] = df['fecha_dt'].dt.month
        meses_nombres = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
        anios = sorted(df['Año'].unique(), reverse=True)
        sel_anio = st.selectbox("Seleccione Año:", anios)
        df_mes = df[df['Año'] == sel_anio]
        if not df_mes.empty:
            tabla_mensual = df_mes.pivot_table(index=['Provincia', 'Departamento', 'Pluviómetro'], columns='Mes_Num', values='mm', aggfunc='sum').fillna(0)
            tabla_mensual.columns = [meses_nombres[c] for c in tabla_mensual.columns]
            tabla_mensual['TOTAL'] = tabla_mensual.sum(axis=1)
            st.dataframe(tabla_mensual.style.format("{:.1f}"), use_container_width=True)
            csv = tabla_mensual.to_csv(sep=';').encode('utf-8-sig')
            st.download_button(f"📥 Descargar {sel_anio}", csv, f"resumen_{sel_anio}.csv", "text/csv")

    with t4:
        st.subheader("📈 Evolución Temporal")
        estaciones_lista = sorted(df['Pluviómetro'].unique())
        sel_estaciones = st.multiselect("Seleccione Pluviómetros:", estaciones_lista)
        col1, col2 = st.columns(2)
        d_desde = col1.date_input("Desde:", df['fecha'].min())
        d_hasta = col2.date_input("Hasta:", df['fecha'].max())
        
        if sel_estaciones:
            df_hist = df[(df['Pluviómetro'].isin(sel_estaciones)) & (df['fecha'] >= d_desde) & (df['fecha'] <= d_hasta)].copy()
            df_hist = df_hist[df_hist['mm'] > 0]

            if not df_hist.empty:
                df_hist = df_hist.sort_values('fecha')
                df_hist['fecha_texto'] = df_hist['fecha_dt'].dt.strftime('%d/%m/%Y')

                barras = alt.Chart(df_hist).mark_bar().encode(
                    x=alt.X('fecha_texto:N', title='Fecha (Días con registro)', sort=None, axis=alt.Axis(labelAngle=-45)), 
                    y=alt.Y('mm:Q', title='Lluvia (mm)', stack=None),
                    color=alt.Color('Pluviómetro:N', title='Pluviómetro'),
                    xOffset='Pluviómetro:N'
                ).properties(height=400).interactive()
                
                st.altair_chart(barras, use_container_width=True)
                
                df_hist_view = df_hist[['fecha', 'Pluviómetro', 'mm', 'Departamento', 'Fenómeno atmosférico']].sort_values('fecha', ascending=False)
                st.dataframe(df_hist_view.rename(columns={'fecha': 'Fecha', 'mm': 'Lluvia (mm)'}), use_container_width=True, hide_index=True)

    # --- BOTÓN DE INFORMACIÓN AL FINAL DE LA PÁGINA ---
    st.markdown("---")
    with st.expander("ℹ️ Información sobre la Red Pluviométrica"):
        st.write("""
        La Red Pluviométrica es una herramienta tecnológica desarrollada por el INTA Centro Regional Salta y Jujuy, cuyo objetivo es recopilar datos precisos y confiables sobre la precipitación en diversas áreas geográficas. Estos datos son esenciales no solo para la gestión agrícola, sino también para la toma de decisiones de otros actores, como los gobiernos locales, que pueden utilizarlos para la planificación y gestión de recursos hídricos, la prevención de desastres naturales y el desarrollo sostenible en sus comunidades.
        
        La Red Pluviométrica es una iniciativa que reúne el trabajo articulado y mancomunado entre INTA, productores locales y particulares que colaboran diariamente con la información registrada por sus pluviómetros.
        
        La ubicación de los pluviómetros está georreferenciada y los datos se recopilan mediante la plataforma INTA Territorios. La misma se desarrolló utilizando el software Kobo Toolbox y Kobo Collect, herramientas de código abierto que facilitan la colecta eficiente de datos y optimizan la exportación y la integración de los mismos, para su posterior análisis en sistemas de información geográfica.
        Se pone a disposición de la comunidad paneles de control interactivos que visualizan la red de pluviómetros. Estos paneles permiten consultar los valores diarios y mensuales de precipitaciones desde octubre de 2024 hasta la fecha actual, acompañados de gráficos comparativos que facilitan la comprensión y análisis de los datos.

        **Equipo de trabajo:**
        Lic. Inf. Hernán Elena (Lab. Teledetección y SIG - Grupo RRNN), Obs. Met. Germán Guanca (Meteorología - Grupo RRNN), Ing. Agr. Rafael Saldaño (OIT Coronel Moldes) - Ing. Agr. Daniela Moneta (AER Valle de Lerma). INTA EEA Salta - Ing. Juan Ramón Rojas (INTA-AER Santa Victoria Este) - Ing. Agr. Daniel Lamberti (INTA AER Perico) - Tec. Recursos Hídricos Fátima del Valle Miranda (INTA AER Palma Sola) - Ing. Agr. Florencia Diaz (INTA AER Palma Sola), Héctor Diaz (INTA AER J.V. Gonzalez), Carlos G. Cabrera (INTA AER J.V. Gonzalez), Lucas Diaz (INTA AER Cafayate - OIT San Carlos).
        
        **Colaboradores:**
        Nicolás Uriburu, Nicolás Villegas, Matias Lanusse, Marcela Lopez, Martín Amado, Agustín Sanz Navamuel, Luis Fernández Acevedo, Miguel A. Boasso, Luis Zavaleta, Mario Lambrisca, Noelia Rovedatti, Matías Canonica, Alejo Alvarez, Javier Montes, Guillermo Patron Costa, Sebastián Mendilaharzu, Francisco Chehda, Jorge Robles, Gustavo Soricich, Javier Atea, Luis D. Elias, Leandro Carrizo, Daiana Núñez, Fátima González, Santiago Villalba, Juan Collado, Julio Collado, Estanislao Lara, Carlos Cruz, Daniel Espinoza, Fabian Álvarez, Lucio Señoranis, Rene Vallejos Rueda, Héctor Miranda, Emanuel Arias, Oscar Herrera, Francisca Vacaflor, Zaturnino Ceballos, Alcides Ceballos, Juan Ignacio Pearson, Pascual Erazo, Dario Romero, Luisa Andrada, Alejandro Ricalde, Odorico Romero, Lucas Campos, Sebastián Diaz, Carlos Sanz, Gabriel Brinder, Gastón Vizgarra, Diego Sulca, Alicia Tapia, Roberto Ponce, Sergio Cassinelli, María Zamboni, Andres Flores, Tomás Lienemann, Carmen Carattoni, Cecilia Carattoni, Tito Donoso, Javier Aprile, Carla Carattoni.
        """)

else:

    st.error("No se pudo conectar con la base de datos.")
