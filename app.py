import streamlit as st
import pandas as pd
import requests
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import locale

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Monitor PP - INTA", 
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png", 
    layout="wide"
)

# Intentar poner fecha en español (si el sistema lo permite)
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
        df_p['fen'] = df_p['fenomeno'].astype(str).str.strip().str.lower().replace(map_f)
        df_p['fen'] = df_p['fen'].replace({'none': 'Sin obs. de fenómenos', 'nan': 'Sin obs. de fenómenos'})

        res = df_c.apply(extraer_coordenadas, axis=1)
        df_c['lat'], df_c['lon'] = zip(*res)
        col_n = next((c for c in df_c.columns if 'Nombre_del_Pluviometro' in c), 'cod')
        
        df = pd.merge(df_p, df_c[['cod', 'lat', 'lon', col_n]], on='cod', how='left')
        df['estacion'] = df[col_n].fillna(df['cod'])
        return df
    except: return pd.DataFrame()

df = cargar_datos_completos()

if not df.empty:
    # --- BARRA LATERAL ---
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png"
    st.sidebar.image(logo_url, width=80)
    todas_f = sorted(df['fecha'].unique(), reverse=True)
    f_hoy = st.sidebar.date_input("Consultar otra fecha:", todas_f[0], format="DD/MM/YYYY")

    # --- CABECERA PRINCIPAL ---
    st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <img src="{logo_url}" style="height: 45px; margin-right: 15px;">
            <h1 style="font-size: 28px !important; font-weight: bold; color: #1E3A8A; margin: 0; line-height: 1.2; border: none;">
                Red Pluviométrica Salta - Jujuy
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs([
        "📍 Mapa e Intensidad", 
        "📊 Listado Diario", 
        "📅 Resumen Mensual", 
        "📈 Comparativa e Histórico"
    ])

    # 1. MAPA OPTIMIZADO
    with t1:
        # Título dinámico para el mapa
        fecha_formateada = f_hoy.strftime('%d de %B de %Y')
        st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 10px; border-left: 5px solid #1E3A8A; border-radius: 5px; margin-bottom: 15px;">
                <h3 style="margin: 0; color: #1E3A8A; font-size: 20px;">
                    ☔ Últimas lluvias registradas: <span style="color: #d32f2f;">{fecha_formateada}</span>
                </h3>
            </div>
        """, unsafe_allow_html=True)

        df_dia = df[df['fecha'] == f_hoy].dropna(subset=['lat', 'lon'])
        
        if not df_dia.empty:
            ver_calor = st.checkbox("🔥 Mostrar Mapa de Calor")
            m = folium.Map(location=[df_dia['lat'].mean(), df_dia['lon'].mean()], zoom_start=7)
            if ver_calor:
                heat_data = [[row['lat'], row['lon'], row['mm']] for _, row in df_dia.iterrows() if row['mm'] > 0]
                if heat_data: HeatMap(heat_data, radius=25, blur=15).add_to(m)
            
            for _, r in df_dia.iterrows():
                c_hex = '#d32f2f' if r['mm'] > 50 else '#ef6c00' if r['mm'] > 20 else '#1a73e8'
                c_fol = 'red' if r['mm'] > 50 else 'orange' if r['mm'] > 20 else 'blue'
                
                html_popup = f"""
                <div style="font-family: Arial; min-width: 200px; padding: 5px;">
                    <h4 style="margin: 0 0 5px 0; color: {c_hex}; white-space: nowrap;">{r['estacion']}</h4>
                    <p style="margin: 0; font-size: 13px;">Lluvia: <b>{r['mm']} mm</b><br>Obs: {r['fen']}</p>
                </div>
                """
                folium.Marker(
                    [r['lat'], r['lon']], 
                    popup=folium.Popup(html_popup, max_width=350),
                    icon=folium.Icon(color=c_fol, icon='cloud')
                ).add_to(m)

                folium.map.Marker(
                    [r['lat'], r['lon']],
                    icon=folium.DivIcon(
                        icon_size=(40,20), icon_anchor=(20,-10),
                        html=f'<div style="color: {c_hex}; font-weight: 900; font-size: 11pt; text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff; text-align: center;">{int(r["mm"])}</div>'
                    )
                ).add_to(m)
            
            st_folium(m, width=None, height=550)
        else:
            st.warning(f"No se encontraron registros para el día {fecha_formateada}.")

    # 2. LISTADO DIARIO
    with t2:
        st.subheader(f"📊 Registros del día {f_hoy.strftime('%d/%m/%Y')}")
        df_res = df[df['fecha'] == f_hoy][['estacion', 'mm', 'fen']].sort_values('mm', ascending=False)
        if not df_res.empty:
            df_chart = df_res[df_res['mm'] > 0].head(15)
            if not df_chart.empty:
                st.bar_chart(df_chart.set_index('estacion')['mm'])
            st.dataframe(df_res.style.format({"mm": "{:.1f}"}), use_container_width=True, hide_index=True)
            csv_diario = df_res.to_csv(index=False, sep=';').encode('utf-8-sig')
            st.download_button("📥 Descargar Planilla", csv_diario, f"lluvia_{f_hoy}.csv", "text/csv")

    # 3. RESUMEN MENSUAL
    with t3:
        df['Año'] = df['fecha_dt'].dt.year
        df['Mes_Num'] = df['fecha_dt'].dt.month
        meses = {1:'Ene', 2:'Feb', 3:'Mar', 4:'Abr', 5:'May', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dic'}
        año_sel = st.selectbox("📅 Año:", sorted(df['Año'].unique(), reverse=True))
        df_año = df[df['Año'] == año_sel]
        if not df_año.empty:
            tabla = df_año.groupby(['estacion', 'Mes_Num'])['mm'].sum().unstack().fillna(0)
            tabla.columns = [meses[c] for c in tabla.columns]
            tabla['TOTAL'] = tabla.sum(axis=1)
            st.dataframe(tabla.style.format("{:.1f}"), use_container_width=True)

    # 4. COMPARATIVA
    with t4:
        st.subheader("📈 Consulta Histórica")
        est_mult = st.multiselect("Seleccione estaciones:", sorted(df['estacion'].unique()))
        c_i, c_f = st.columns(2)
        f_desde = c_i.date_input("Desde:", df['fecha'].min())
        f_hasta = c_f.date_input("Hasta:", df['fecha'].max())
        if est_mult:
            df_comp = df[(df['estacion'].isin(est_mult)) & (df['fecha'] >= f_desde) & (df['fecha'] <= f_hasta)]
            if not df_comp.empty:
                chart_data = df_comp.pivot_table(index='fecha', columns='estacion', values='mm').fillna(0)
                st.area_chart(chart_data)

else:
    st.error("No se pudo conectar con la base de datos de INTA.")