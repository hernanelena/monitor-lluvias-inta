import streamlit as st
import pandas as pd
import requests
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Monitor PP - INTA", page_icon="🌧️", layout="wide")

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
    st.title("🌧️ Monitor Pluviométrico INTA Salta-Jujuy")
    
    todas_f = sorted(df['fecha'].unique(), reverse=True)
    f_hoy = st.sidebar.date_input("Fecha de consulta diaria:", todas_f[0], format="DD/MM/YYYY")
    
    t1, t2, t3, t4 = st.tabs([
        "📍 Mapa e Intensidad", 
        "📊 Listado Diario", 
        "📅 Resumen Mensual", 
        "📈 Comparativa e Histórico"
    ])

    # 1. MAPA OPTIMIZADO
    with t1:
        df_dia = df[df['fecha'] == f_hoy].dropna(subset=['lat', 'lon'])
        if not df_dia.empty:
            ver_calor = st.checkbox("🔥 Mostrar Mapa de Calor")
            m = folium.Map(location=[df_dia['lat'].mean(), df_dia['lon'].mean()], zoom_start=8)
            if ver_calor:
                heat_data = [[row['lat'], row['lon'], row['mm']] for _, row in df_dia.iterrows() if row['mm'] > 0]
                if heat_data: HeatMap(heat_data, radius=25, blur=15).add_to(m)
            
            for _, r in df_dia.iterrows():
                c_hex = '#d32f2f' if r['mm'] > 50 else '#ef6c00' if r['mm'] > 20 else '#1a73e8'
                c_fol = 'red' if r['mm'] > 50 else 'orange' if r['mm'] > 20 else 'blue'
                
                html_popup = f"""
                <div style="font-family: Arial; min-width: 200px; padding: 5px;">
                    <h4 style="margin: 0 0 5px 0; color: {c_hex}; white-space: nowrap;">
                        {r['estacion']}
                    </h4>
                    <p style="margin: 0; font-size: 13px;">
                        Lluvia: <b>{r['mm']} mm</b><br>
                        Obs: <span style="color: #666;">{r['fen']}</span>
                    </p>
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
                        icon_size=(40,20),
                        icon_anchor=(20,-10),
                        html=f"""<div class="zoom-label" style="
                            color: {c_hex}; font-weight: 900; font-size: 11pt;
                            text-shadow: -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff;
                            text-align: center;">{int(r['mm'])}</div>"""
                    )
                ).add_to(m)
            
            st.markdown("<style>.zoom-label { display: none; } .leaflet-zoom-10 .zoom-label, .leaflet-zoom-11 .zoom-label, .leaflet-zoom-12 .zoom-label, .leaflet-zoom-13 .zoom-label, .leaflet-zoom-14 .zoom-label, .leaflet-zoom-15 .zoom-label, .leaflet-zoom-16 .zoom-label, .leaflet-zoom-17 .zoom-label, .leaflet-zoom-18 .zoom-label { display: block !important; }</style>", unsafe_allow_html=True)
            st_folium(m, width=None, height=500)

    # 2. LISTADO DIARIO CON GRÁFICO DE BARRAS
    with t2:
        st.subheader(f"Registros del día {f_hoy.strftime('%d/%m/%Y')}")
        df_res = df[df['fecha'] == f_hoy][['estacion', 'mm', 'fen']].sort_values('mm', ascending=False)
        
        if not df_res.empty:
            # --- NUEVO: GRÁFICO DE BARRAS ---
            # Filtramos solo estaciones con lluvia para el gráfico
            df_chart = df_res[df_res['mm'] > 0].head(15) # Top 15 para no saturar
            
            if not df_chart.empty:
                st.write("### 📊 Top estaciones con mayores precipitaciones (mm)")
                # Asignar colores para el gráfico
                df_chart['color'] = df_chart['mm'].apply(lambda x: '#d32f2f' if x > 50 else '#ef6c00' if x > 20 else '#1a73e8')
                
                st.bar_chart(df_chart.set_index('estacion')['mm'], color=None) 
                # Nota: streamlit bar_chart básico no soporta colores dinámicos por fila fácilmente sin altair, 
                # pero muestra la tendencia perfectamente.
            
            st.write("### 📋 Detalle General")
            st.dataframe(df_res.style.format({"mm": "{:.1f}"}), use_container_width=True, hide_index=True)
            
            csv_diario = df_res.to_csv(index=False, sep=';').encode('utf-8-sig')
            st.download_button(f"📥 Descargar Planilla {f_hoy}", csv_diario, f"lluvia_{f_hoy}.csv", "text/csv")
        else:
            st.info("No hay registros para la fecha seleccionada.")

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
            csv_anual = tabla.reset_index().to_csv(index=False, sep=';').encode('utf-8-sig')
            st.download_button(f"📥 Descargar Planilla Anual {año_sel}", csv_anual, f"anual_{año_sel}.csv", "text/csv")

    # 4. COMPARATIVA Y RANGO
    with t4:
        st.subheader("Consulta Histórica por Pluviómetro")
        est_mult = st.multiselect("Seleccione una o más estaciones:", sorted(df['estacion'].unique()))
        c_i, c_f = st.columns(2)
        f_desde = c_i.date_input("Fecha Inicio:", df['fecha'].min(), format="DD/MM/YYYY")
        f_hasta = c_f.date_input("Fecha Fin:", df['fecha'].max(), format="DD/MM/YYYY")
        
        if est_mult:
            df_comp = df[(df['estacion'].isin(est_mult)) & (df['fecha'] >= f_desde) & (df['fecha'] <= f_hasta)]
            if not df_comp.empty:
                chart_data = df_comp.pivot_table(index='fecha', columns='estacion', values='mm').fillna(0)
                st.area_chart(chart_data)
                
                st.write("---")
                st.write("### 📥 Descarga de Datos Filtrados")
                df_download = df_comp[['fecha', 'estacion', 'mm', 'fen']].sort_values(['estacion', 'fecha'])
                csv_rango = df_download.to_csv(index=False, sep=';').encode('utf-8-sig')
                st.download_button("📥 Descargar Período Seleccionado", csv_rango, "historico_lluvias.csv", "text/csv", use_container_width=True)
                st.dataframe(df_download, use_container_width=True, hide_index=True)

else:
    st.error("Error al obtener datos.")