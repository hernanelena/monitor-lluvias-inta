import streamlit as st
import pandas as pd
import requests
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
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
        df_p['Fenómeno atmosférico'] = df_p['fen_raw'].replace(map_f).replace({'none': 'Sin obs. de fenómenos', 'nan': 'Sin obs. de fenómenos'})
        res = df_c.apply(extraer_coordenadas, axis=1)
        df_c['lat'], df_c['lon'] = zip(*res)
        col_n = next((c for c in df_c.columns if 'Nombre_del_Pluviometro' in c), 'cod')
        col_depto = next((c for c in df_c.columns if 'depto' in c.lower() or 'departamento' in c.lower()), None)
        col_prov = next((c for c in df_c.columns if 'prov' in c.lower() or 'provincia' in c.lower()), None)
        col_region = next((c for c in df_c.columns if 'region' in c.lower() or 'región' in c.lower()), None)
        columnas_mapa = ['cod', 'lat', 'lon', col_n]
        if col_depto: columnas_mapa.append(col_depto)
        if col_prov: columnas_mapa.append(col_prov)
        if col_region: columnas_mapa.append(col_region)
        df = pd.merge(df_p, df_c[columnas_mapa], on='cod', how='left')
        df['Pluviómetro'] = df[col_n].fillna(df['cod'])
        df['Departamento'] = df[col_depto].fillna("S/D") if col_depto else "S/D"
        df['Provincia'] = df[col_prov].fillna("S/D") if col_prov else "S/D"
        df['Region'] = df[col_region].fillna("S/D") if col_region else "General"
        return df
    except: return pd.DataFrame()

df = cargar_datos_completos()

if not df.empty:
    # --- BARRA LATERAL ---
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png"
    st.sidebar.image(logo_url, width=80)
    st.sidebar.markdown("---")
    todas_f = sorted(df['fecha'].unique(), reverse=True)
    f_hoy = st.sidebar.date_input("Consultar otra fecha:", todas_f[0], format="DD/MM/YYYY")

    # --- CSS OPTIMIZADO (MODIFICADO PARA NO VERSE GRANDE) ---
    # --- CSS OPTIMIZADO ---
    st.markdown(f"""
        <style>
            .header-container {{ display: flex; align-items: center; margin-bottom: 15px; gap: 12px; width: 100%; }}
            .main-title {{ font-weight: bold; color: #1E3A8A !important; margin: 0; line-height: 1.2; font-size: 24px; }}
            .header-logo {{ height: 45px; width: auto; }}
            

            /* REGLA CORREGIDA PARA BORDE COMPLETO */
            .map-border {{
             
            box-shadow: 0px 0px 0px 2px #000000; 
            border-radius: 8px;
            margin: 10px 2px; /* Margen para que la sombra no se corte */
            line-height: 0;
            }}

            @media (max-width: 600px) {{
                .main-title {{ font-size: 18px !important; }}
                .header-logo {{ height: 35px; }}
            }}
        </style>
        <div class="header-container">
            <img src="{logo_url}" class="header-logo">
            <h1 class="main-title">Red Pluviométrica Salta - Jujuy</h1>
        </div>
    """, unsafe_allow_html=True)
    
    df_dia = df[df['fecha'] == f_hoy].dropna(subset=['lat', 'lon'])
    
    # --- PESTAÑAS ---
    tab_list = ["🗺️ Mapa", "📊 Día", "📅 Mes", "📈 Hist.", "📥 Desc.", "🌧️ Red"]
    t1, t2, t3, t4, t5, t6 = st.tabs(tab_list)

    with t1:
        # 1. Filtro de región ocupando menos espacio
        lista_regiones = ["Todas"] + sorted(df_dia['Region'].unique().tolist()) if not df_dia.empty else ["Todas"]
        sel_zoom = st.selectbox("🔍 Enfocar Región:", lista_regiones)
        
        if not df_dia.empty:
            df_mapa = df_dia[df_dia['Region'] == sel_zoom].copy() if sel_zoom != "Todas" else df_dia.copy()
            zoom_inicial = 9 if sel_zoom != "Todas" else 7
            centro = [df_mapa['lat'].mean(), df_mapa['lon'].mean()]
            
            m = folium.Map(location=centro, zoom_start=zoom_inicial, tiles=None)
            
            # Capas base
            folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google', name='Google Satélite', overlay=False).add_to(m)
            folium.TileLayer(tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png", attr='IGN', name='Argenmap (IGN)', overlay=False).add_to(m)
            
            # 2. LEYENDA FLOTANTE DENTRO DEL MAPA (HTML inyectado)
            legend_html = '''
            <div style="
                position: fixed; 
                top: 10px; right: 10px; width: 110px; height: auto; 
                background-color: white; border:2px solid grey; z-index:9999; font-size:11px;
                padding: 8px; border-radius: 5px; opacity: 0.85;
                font-family: sans-serif; line-height: 1.4;
                ">
                <b>Referencia:</b><br>
                <i style="background: #1a73e8; width: 10px; height: 10px; float: left; margin-right: 5px; margin-top: 3px; border-radius: 50%;"></i> 0-20 mm<br>
                <i style="background: #ef6c00; width: 10px; height: 10px; float: left; margin-right: 5px; margin-top: 3px; border-radius: 50%;"></i> 20-50 mm<br>
                <i style="background: #d32f2f; width: 10px; height: 10px; float: left; margin-right: 5px; margin-top: 3px; border-radius: 50%;"></i> +50 mm
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))

            LocateControl(auto_start=False, flyTo=True).add_to(m)
            folium.LayerControl(position='bottomright').add_to(m)
            
            # Marcadores
            for _, r in df_mapa.iterrows():
                c_hex = '#d32f2f' if r['mm'] > 50 else '#ef6c00' if r['mm'] > 20 else '#1a73e8'
                c_fol = 'red' if r['mm'] > 50 else 'orange' if r['mm'] > 20 else 'blue'
                
                icon_code = 'cloud' 
                if 'granizo' in r['fen_raw']: icon_code = 'asterisk' 
                elif 'tormenta' in r['fen_raw']: icon_code = 'flash' 
                elif 'viento' in r['fen_raw']: icon_code = 'leaf'

                html_popup = f"""
                <div style="font-family: sans-serif; min-width: 180px;">
                    <div style="margin:0; color:{c_hex}; border-bottom:2px solid {c_hex}; font-size:16px; font-weight:bold; padding-bottom:5px; margin-bottom:8px;">
                        {r['Pluviómetro']}
                    </div>
                    <div style="font-size:14px; margin-bottom:3px;"><b>Lluvia:</b> {r['mm']} mm</div>
                    <div style="font-size:13px; margin-bottom:6px;"><b>Fenómeno:</b> {r['Fenómeno atmosférico']}</div>
                    <div style="font-size:12px; color:#333; border-top:1px solid #eee; padding-top:5px;">
                        <b>{r['Departamento']}, {r['Provincia']}</b>
                    </div>
                </div>
                """
                
                folium.Marker(
                    [r['lat'], r['lon']], 
                    popup=folium.Popup(html_popup, max_width=250), 
                    icon=folium.Icon(color=c_fol, icon=icon_code)
                ).add_to(m)
                
                folium.map.Marker(
                    [r['lat'], r['lon']], 
                    icon=folium.DivIcon(
                        icon_size=(40,20), 
                        icon_anchor=(20,-10), 
                        html=f'<div style="color:{c_hex}; font-weight:900; font-size:11pt; text-shadow:1px 1px 0 #fff;">{int(r["mm"])}</div>'
                    )
                ).add_to(m)
            # AQUÍ MODIFICAR:
            st.markdown('<div class="map-border">', unsafe_allow_html=True)
            st_folium(m, width=None, height=550, use_container_width=True, key=f"mapa_{sel_zoom}")
            st.markdown('</div>', unsafe_allow_html=True)
        else: 
            st.warning("No hay datos para la fecha seleccionada.")

    with t2:
        st.subheader(f"Resumen del {f_hoy.strftime('%d/%m/%Y')}")
        if not df_dia.empty:
            avg_reg = df_dia.groupby('Region')['mm'].agg(['mean', 'max', 'count']).sort_values('mean', ascending=False).reset_index()
            rows = [avg_reg[i:i + 3] for i in range(0, len(avg_reg), 3)]
            for row_df in rows:
                cols = st.columns(3)
                for i, (_, row) in enumerate(row_df.iterrows()):
                    with cols[i]:
                        st.metric(label=f"Región: {row['Region']}", value=f"{row['mean']:.1f} mm prom.", delta=f"Máx: {row['max']} mm ({int(row['count'])} estaciones)")
            st.markdown("---")
            st.subheader("Detalle de Registros")
            st.dataframe(df_dia[['Pluviómetro', 'Region', 'mm', 'Departamento', 'Fenómeno atmosférico']].sort_values('mm', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("No hay datos para la fecha seleccionada.")

    with t3:
        st.subheader("📅 Acumulados Mensuales")
        df['Año'] = df['fecha_dt'].dt.year
        df['Mes_Num'] = df['fecha_dt'].dt.month
        meses_n = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
        sel_anio = st.selectbox("Año:", sorted(df['Año'].unique(), reverse=True))
        df_m = df[df['Año'] == sel_anio]
        if not df_m.empty:
            tabla = df_m.pivot_table(index=['Region', 'Pluviómetro'], columns='Mes_Num', values='mm', aggfunc='sum').fillna(0)
            tabla.columns = [meses_n[c] for c in tabla.columns]
            tabla['TOTAL'] = tabla.sum(axis=1)
            st.dataframe(tabla.style.format("{:.1f}").highlight_max(axis=1, props='background-color: #e3f2fd;'), use_container_width=True)

    with t4:
        st.subheader("📈 Consulta Histórica")
        col_f1, col_f2, col_f3 = st.columns([0.3, 0.4, 0.3])
        with col_f1:
            f_desde = st.date_input("Desde:", df['fecha'].min())
            f_hasta = st.date_input("Hasta:", df['fecha'].max())
        with col_f2:
            reg_h = sorted(df['Region'].unique())
            sel_reg_h = st.multiselect("Filtrar por Región:", reg_h)
            df_h_base = df if not sel_reg_h else df[df['Region'].isin(sel_reg_h)]
            sel_est_h = st.multiselect("Seleccionar Pluviómetros:", sorted(df_h_base['Pluviómetro'].unique()))
        with col_f3:
            agrupar = st.radio("Agrupar por:", ["Día", "Semana", "Mes"])
        
        if sel_est_h:
            df_p = df[(df['fecha'] >= f_desde) & (df['fecha'] <= f_hasta) & (df['Pluviómetro'].isin(sel_est_h))].copy()
            if agrupar == "Semana": df_p['f_plot'] = df_p['fecha_dt'] - pd.to_timedelta(df_p['fecha_dt'].dt.dayofweek, unit='d')
            elif agrupar == "Mes": df_p['f_plot'] = df_p['fecha_dt'].dt.to_period('M').dt.to_timestamp()
            else: df_p['f_plot'] = df_p['fecha_dt']
            
            df_res = df_p.groupby(['f_plot', 'Pluviómetro'])['mm'].sum().reset_index()
            df_res = df_res.sort_values('f_plot')
            df_res['fecha_f'] = df_res['f_plot'].dt.strftime('%d/%m/%Y')
            
            chart = alt.Chart(df_res).mark_bar().encode(
                x=alt.X('Pluviómetro:N', title=None, axis=alt.Axis(labels=False)),
                y=alt.Y('mm:Q', title='Lluvia (mm)'),
                color='Pluviómetro:N',
                column=alt.Column('fecha_f:O', title=None, sort=alt.SortField(field='f_plot', order='ascending'), header=alt.Header(labelOrient='bottom', labelAngle=-45, labelAlign='right')),
                tooltip=['fecha_f', 'Pluviómetro', 'mm']
            ).properties(width=alt.Step(45), height=350)
            st.altair_chart(chart)

    with t5:
        st.subheader("📥 Descargar")
        sel_est_desc = st.selectbox("Seleccione el Pluviómetro:", sorted(df['Pluviómetro'].unique()))
        if sel_est_desc:
            df_desc = df[df['Pluviómetro'] == sel_est_desc][['fecha', 'mm', 'Fenómeno atmosférico', 'Departamento', 'Provincia', 'Region']].sort_values('fecha', ascending=False)
            st.dataframe(df_desc, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Descargar CSV de {sel_est_desc}", df_desc.to_csv(index=False).encode('utf-8'), f'{sel_est_desc}.csv', "text/csv")

    with t6:
        st.subheader("Red")
        st.info("Este mapa muestra todos los pluviómetros incorporados a la red, independientemente de si han reportado datos en la fecha seleccionada.")
        
        # 1. Preparación de datos únicos
        df_red_completa = df.drop_duplicates(subset=['cod']).dropna(subset=['lat', 'lon']).copy()
        
        # 2. Buscador con sugerencias dinámicas
        # Usamos una lista de nombres para que Streamlit ayude al usuario a elegir
        opciones_sugeridas = sorted(df_red_completa['Pluviómetro'].unique().tolist())
        
        # El selectbox permite escribir y va filtrando la lista de sugerencias automáticamente
        seleccion = st.selectbox(
            "🔍 Busque un pluviómetro para localizarlo (escriba parte del nombre):", 
            options=["Ver todos"] + opciones_sugeridas,
            index=0,
            help="Escriba el nombre del pluviómetro y selecciónelo de la lista"
        )

        # Lógica de filtrado
        if seleccion != "Ver todos":
            df_mostrar = df_red_completa[df_red_completa['Pluviómetro'] == seleccion]
            zoom_init = 12  # Zoom cercano si elige uno específico
        else:
            df_mostrar = df_red_completa
            zoom_init = 7

        if not df_mostrar.empty:
            # Centro dinámico
            centro_red = [df_mostrar['lat'].mean(), df_mostrar['lon'].mean()]
            m_red = folium.Map(location=centro_red, zoom_start=zoom_init, tiles=None)
            
            # Capas base
            folium.TileLayer(tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                             attr='Google', name='Google Satélite').add_to(m_red)
            folium.TileLayer(tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png", 
                             attr='IGN', name='Argenmap (IGN)').add_to(m_red)
            
            # Marcadores con tus atributos específicos
            for _, r in df_mostrar.iterrows():
                # Color institucional para el diseño
                c_azul = "#1E3A8A"
                
                pop_red = f"""
                <div style="font-family: sans-serif; min-width: 180px;">
                    <div style="margin:0; color:{c_azul}; border-bottom:2px solid {c_azul}; font-size:16px; font-weight:bold; padding-bottom:5px; margin-bottom:8px;">
                        {r['Pluviómetro']}
                    </div>
                    <div style="font-size:12px; color:#333; border-top:1px solid #eee; padding-top:5px;">
                        <b>{r['Departamento']}, {r['Provincia']}</b>
                    </div>
                </div>
                """
                
                folium.CircleMarker(
                    location=[r['lat'], r['lon']],
                    radius=8,
                    popup=folium.Popup(pop_red, max_width=250),
                    color=c_azul,
                    fill=True,
                    fill_color="#3B82F6",
                    fill_opacity=0.8
                ).add_to(m_red)
            
            folium.LayerControl().add_to(m_red)
            LocateControl().add_to(m_red)
            
            # Renderizado del mapa
            # AQUÍ MODIFICAR:
            st.markdown('<div class="map-border">', unsafe_allow_html=True)
            st_folium(m_red, width=None, height=600, use_container_width=True, key=f"mapa_red_full_{seleccion}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.write(f"**Total de estaciones en vista:** {len(df_mostrar)}")
        else:
            st.warning("No se encontraron datos para mostrar.")
    
    
    # --- INFO INSTITUCIONAL COMPLETA ---
    st.markdown("---")
    with st.expander("ℹ️ Información sobre la Red Pluviométrica"):
        st.markdown("""
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
else: 
    st.error("Error al conectar con la base de datos.")
