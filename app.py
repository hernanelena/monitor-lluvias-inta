import streamlit as st
import pandas as pd
import requests
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, LocateControl
import locale
import altair as alt

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
        df_p['fen_raw'] = df_p['fenomeno'].astype(str).str.strip().str.lower()
        map_f = {'viento': 'Vientos fuertes', 'granizo': 'Granizo', 'tormenta': 'Tormentas eléctricas', 'sinfeno': 'Sin obs. de fenómenos'}
        df_p['Fenómeno atmosférico'] = df_p['fen_raw'].replace(map_f)
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

    # --- NUEVO CSS OPTIMIZADO PARA MÓVILES ---
    st.markdown(f"""
        <style>
            .header-container {{ 
                display: flex; 
                align-items: center; 
                margin-bottom: 15px; 
                gap: 12px; 
                width: 100%;
            }}
            .main-title {{ 
                font-weight: bold; 
                color: #1E3A8A !important; 
                margin: 0; 
                line-height: 1.2; 
                font-size: 24px;
            }}
            .header-logo {{ height: 45px; width: auto; }}
            .fecha-label {{ color: #1E3A8A; font-weight: bold; font-size: 15px; margin: 0; }}

            /* Ajustes específicos para pantallas de menos de 600px (Celulares) */
            @media (max-width: 600px) {{
                .main-title {{
                    font-size: 18px !important; /* Forzamos un tamaño pequeño en móvil */
                }}
                .header-logo {{
                    height: 35px;
                }}
            }}
        </style>
        <div class="header-container">
            <img src="{logo_url}" class="header-logo">
            <h1 class="main-title">Red Pluviométrica Salta - Jujuy</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # --- TABS ---
    tab_list = ["📍 Mapa", "📊 Listado", "📅 Mensual", "📈 Histórico"]
    t1, t2, t3, t4 = st.tabs(tab_list)

    with t1:
        fecha_f = f_hoy.strftime('%d/%m/%Y')
        col_ctrl1, col_ctrl2 = st.columns([0.55, 0.45])
        with col_ctrl1:
            st.markdown(f'<p class="fecha-label">Lluvias del {fecha_f} <span class="separador">|</span></p>', unsafe_allow_html=True)
        with col_ctrl2:
            ver_calor = st.checkbox("🔥 Activar Mapa de Calor", value=False)
        df_dia = df[df['fecha'] == f_hoy].dropna(subset=['lat', 'lon'])
        if not df_dia.empty:
            m = folium.Map(location=[df_dia['lat'].mean(), df_dia['lon'].mean()], zoom_start=7, tiles=None)
            folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google', name='Google Satélite', overlay=False).add_to(m)
            folium.TileLayer(tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png", attr='IGN', name='Argenmap (IGN)', overlay=False).add_to(m)
            if ver_calor:
                calor_data = df_dia[df_dia['mm'] > 0][['lat', 'lon', 'mm']].values.tolist()
                if calor_data: HeatMap(calor_data, radius=25, blur=18, min_opacity=0.4, control=False).add_to(m)
            LocateControl(auto_start=False, fly_to=True, strings={"title": "Mi ubicación", "popup": "Usted está aquí"}).add_to(m)
            folium.LayerControl(position='topright', collapsed=True).add_to(m)
            for _, r in df_dia.iterrows():
                c_hex = '#d32f2f' if r['mm'] > 50 else '#ef6c00' if r['mm'] > 20 else '#1a73e8'
                c_fol = 'red' if r['mm'] > 50 else 'orange' if r['mm'] > 20 else 'blue'
                icon_code = 'cloud' 
                if 'granizo' in r['fen_raw']: icon_code = 'asterisk' 
                elif 'tormenta' in r['fen_raw']: icon_code = 'flash' 
                elif 'viento' in r['fen_raw']: icon_code = 'leaf'
                html_popup = f"""<div style="font-family: sans-serif; min-width: 200px;"><h4 style="margin:0; color:{c_hex}; border-bottom:1px solid #ccc;">{r['Pluviómetro']}</h4><b>{r['mm']} mm</b><br><small>{r['Departamento']}, {r['Provincia']}</small></div>"""
                folium.Marker([r['lat'], r['lon']], popup=folium.Popup(html_popup, max_width=300), icon=folium.Icon(color=c_fol, icon=icon_code)).add_to(m)
                folium.map.Marker([r['lat'], r['lon']], icon=folium.DivIcon(icon_size=(40,20), icon_anchor=(20,-10), html=f'<div style="color:{c_hex}; font-weight:900; font-size:11pt; text-shadow:1px 1px 0 #fff;">{int(r["mm"])}</div>')).add_to(m)
            st_folium(m, width=None, height=500, key="mapa_v_final")
        else: st.warning("No hay datos para la fecha seleccionada.")

    with t2:
        st.subheader(f"Registros del {f_hoy.strftime('%d/%m/%Y')}")
        df_list = df[df['fecha'] == f_hoy][['Pluviómetro', 'mm', 'Departamento', 'Provincia', 'Fenómeno atmosférico']].sort_values('mm', ascending=False)
        st.dataframe(df_list.rename(columns={'mm': 'Lluvia (mm)'}), use_container_width=True, hide_index=True)

    with t3:
        st.subheader("📅 Acumulados Mensuales")
        df['Año'] = df['fecha_dt'].dt.year
        df['Mes_Num'] = df['fecha_dt'].dt.month
        meses_nombres = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
        sel_anio = st.selectbox("Seleccione Año:", sorted(df['Año'].unique(), reverse=True), key="sel_anio_mensual")
        df_mes = df[df['Año'] == sel_anio]
        if not df_mes.empty:
            tabla_mensual = df_mes.pivot_table(index=['Provincia', 'Departamento', 'Pluviómetro'], columns='Mes_Num', values='mm', aggfunc='sum').fillna(0)
            tabla_mensual.columns = [meses_nombres[c] for c in tabla_mensual.columns]
            tabla_mensual['TOTAL'] = tabla_mensual.sum(axis=1)
            st.dataframe(tabla_mensual.style.format("{:.1f}"), use_container_width=True)

    with t4:
        st.subheader("📈 Consulta Histórica")
        estaciones_lista = sorted(df['Pluviómetro'].unique())
        sel_estaciones = st.multiselect("Seleccione Pluviómetros:", estaciones_lista, key="ms_pluv_hist")
        
        col_f1, col_f2 = st.columns(2)
        fecha_min, fecha_max = df['fecha'].min(), df['fecha'].max()
        with col_f1: f_inicio = st.date_input("Fecha desde:", fecha_min, key="f_desde_hist")
        with col_f2: f_fin = st.date_input("Fecha hasta:", fecha_max, key="f_hasta_hist")

        if sel_estaciones and f_inicio <= f_fin:
            df_hist = df[(df['Pluviómetro'].isin(sel_estaciones)) & (df['fecha'] >= f_inicio) & (df['fecha'] <= f_fin)].copy()
            if not df_hist.empty:
                df_hist['fecha_f'] = df_hist['fecha_dt'].dt.strftime('%d/%m/%Y')
                df_hist = df_hist.sort_values('fecha_dt')
                csv = df_hist[['fecha', 'Pluviómetro', 'mm', 'Departamento', 'Provincia', 'Fenómeno atmosférico']].to_csv(index=False).encode('utf-8')
                st.download_button(label="📥 Descargar datos (CSV)", data=csv, file_name='historico_lluvias.csv', mime='text/csv')
                
                chart = alt.Chart(df_hist).mark_bar().encode(
                    x=alt.X('Pluviómetro:N', title=None, axis=alt.Axis(labels=False, ticks=False)),
                    y=alt.Y('mm:Q', title='Lluvia (mm)'),
                    color=alt.Color('Pluviómetro:N', legend=alt.Legend(orient='bottom', title="Pluviómetros Seleccionados")),
                    column=alt.Column('fecha_f:O', 
                                     title=None, 
                                     header=alt.Header(labelOrient='bottom', 
                                                       labelAngle=-45, 
                                                       labelAlign='right',
                                                       labelPadding=15)),
                    tooltip=['fecha_f', 'Pluviómetro', 'mm']
                ).configure_view(stroke=None).properties(width=alt.Step(30), height=380)
                
                st.altair_chart(chart)
            else: st.info("No hay datos en el rango seleccionado.")

    # --- INFORMACIÓN INSTITUCIONAL COMPLETA ---
    st.markdown("---")
    with st.expander("ℹ️ Información sobre la Red Pluviométrica"):
        st.write("""
        La Red Pluviométrica es una herramienta tecnológica desarrollada por el INTA Centro Regional Salta y Jujuy, cuyo objetivo es recopilar datos precisos y confiables sobre la precipitación en diversas áreas geográficas. Estos datos son esenciales no solo para la gestión agrícola, sino también para la toma de decisiones de otros actores, como los gobiernos locales, que pueden utilizarlos para la planificación y gestión de recursos hídricos, la prevención de desastres naturales y el desarrollo sostenible en sus comunidades.
        
        La Red Pluviométrica es una iniciativa que reúne el trabajo articulado y mancomunado entre INTA, productores locales y particulares que colaboran diariamente con la información registrada por sus pluviómetros.
        
        La ubicación de los pluviómetros está georreferenciada y los datos se recopilan mediante la plataforma INTA Territorios. La misma se desarrolló utilizando el software Kobo Toolbox y Kobo Collect, herramientas de código abierto que facilitan la colecta eficiente de datos y optimizan la exportación y la integración de los mismos, para su posterior análisis en sistemas de información geográfica.
        
        Los datos se registran como día pluviométrico. Día pluviométrico es un período de 24 horas, que va de una hora específica (comúnmente las 9 AM) de un día hasta la misma hora del día siguiente, utilizado para registrar la cantidad total de precipitación (lluvia) caída, estandarizando las mediciones meteorológicas. La lluvia medida a las 9 AM de un día corresponde a la acumulada desde las 9 AM del día anterior. 
        
        Se pone a disposición de la comunidad paneles de control interactivos que visualizan la red de pluviómetros. Estos paneles permiten consultar los valores diarios y mensuales de precipitaciones desde octubre de 2024 hasta la fecha actual, acompañados de gráficos comparativos que facilitan la comprensión y análisis de los datos.

        **Equipo de trabajo:**
        Lic. Inf. Hernán Elena (Lab. Teledetección y SIG - Grupo RRNN), Obs. Met. Germán Guanca (Meteorología - Grupo RRNN), Ing. Agr. Rafael Saldaño (OIT Coronel Moldes) - Ing. Agr. Daniela Moneta (AER Valle de Lerma). INTA EEA Salta - Ing. Juan Ramón Rojas (INTA-AER Santa Victoria Este) - Ing. Agr. Daniel Lamberti (INTA AER Perico) - Tec. Recursos Hídricos Fátima del Valle Miranda (INTA AER Palma Sola) - Ing. Agr. Florencia Diaz (INTA AER Palma Sola), Héctor Diaz (INTA AER J.V. Gonzalez), Carlos G. Cabrera (INTA AER J.V. Gonzalez), Lucas Diaz (INTA AER Cafayate - OIT San Carlos), Cristina Rosetto (INTA EECT Yuto).
        
        **Colaboradores:**
        Nicolás Uriburu, Nicolás Villegas, Matias Lanusse, Marcela Lopez, Martín Amado, Agustín Sanz Navamuel, Luis Fernández Acevedo, Miguel A. Boasso, Luis Zavaleta, Mario Lambrisca, Noelia Rovedatti, Matías Canonica, Alejo Alvarez, Javier Montes, Guillermo Patron Costa, Sebastián Mendilaharzu, Francisco Chehda, Jorge Robles, Gustavo Soricich, Javier Atea, Luis D. Elias, Leandro Carrizo, Daiana Núñez, Fátima González, Santiago Villalba, Juan Collado, Julio Collado, Estanislao Lara, Carlos Cruz, Daniel Espinoza, Fabian Álvarez, Lucio Señoranis, Rene Vallejos Rueda, Héctor Miranda, Emanuel Arias, Oscar Herrera, Francisca Vacaflor, Zaturnino Ceballos, Alcides Ceballos, Juan Ignacio Pearson, Pascual Erazo, Dario Romero, Luisa Andrada, Alejandro Ricalde, Odorico Romero, Lucas Campos, Sebastián Diaz, Carlos Sanz, Gabriel Brinder, Gastón Vizgarra, Diego Sulca, Alicia Tapia, Roberto Ponce, Sergio Cassinelli, María Zamboni, Andres Flores, Tomás Lienemann, Carmen Carattoni, Cecilia Carattoni, Tito Donoso, Javier Aprile, Carla Carattoni, Cuenca Renan, Luna Federico, Soloza Pedro, Aparicio Cirila, Torres Arnaldo, Torres Mergido, Sardina Ruben, Illesca Francisco, Saravia Adrian, Carabajal Jesus, Alvarado Rene, Saban Mary, Rodriguez Eleuterio, Guzman Durbal, Sajama Sergio, Miranda Dina, Pedro Quispe.
        """)
else: st.error("Error al conectar con la base de datos.")


