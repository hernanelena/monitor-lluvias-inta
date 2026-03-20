import streamlit as st
import pandas as pd
import requests
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl
import locale
import altair as alt
from datetime import timedelta
from fpdf import FPDF
from folium.plugins import MarkerCluster

# =========================================
# CREACIÓN DE PDF (firma original, 3 parámetros)
# =========================================
def crear_pdf(df_dia, fecha_selec, cant_total):
    """Genera bytes de PDF con el resumen diario (usa col_nombre_estacion global como en tu original)."""
    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, 'Documento generado automáticamente por el Sistema de Relevamiento Pluviométrico - INTA EEA Salta', 0, 0, 'L')
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

    pdf = PDF()
    pdf.add_page()

    # --- ENCABEZADO INSTITUCIONAL ---
    pdf.set_fill_color(30, 58, 138)  # Azul INTA
    pdf.rect(0, 0, 210, 45, 'F')
    try:
        pdf.image("logo_inta.png", x=12, y=8, w=22)
    except:
        pass

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", style='B', size=16)
    pdf.set_xy(38, 12)
    pdf.cell(0, 10, "Grupo de RR.NN. - E.E.A. Salta", ln=True)

    pdf.set_font("Helvetica", style='B', size=13)
    pdf.set_x(38)
    pdf.cell(0, 8, "REPORTE DIARIO DE PRECIPITACIONES", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.set_x(38)
    #pdf.cell(0, 8, f"Fecha de consulta: {fecha_selec}", ln=True)

    pdf.ln(22)
    pdf.set_text_color(0, 0, 0)

    # --- RESUMEN DE RED ---
    pdf.set_font("Helvetica", style='B', size=12)
    pdf.cell(0, 10, "Resumen de la Red:", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(0, 7, f"Estaciones con reporte: {len(df_dia)}", ln=True)
        # Convertir fecha_selec (date) a "16 de marzo de 2026"
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    fecha_formateada = f"{fecha_selec.day} de {meses[fecha_selec.month]} de {fecha_selec.year}"

    pdf.cell(0, 8, f"Fecha de consulta: {fecha_formateada}", ln=True)
    pdf.cell(0, 7, f"Total de estaciones en base: {cant_total}", ln=True)
    # --------- BLOQUE NUEVO: Leyenda de día pluviométrico ---------
    # Format fechas en DD/MM/YYYY
    # --------- BLOQUE NUEVO: cartel sombreado ---------
    f1 = fecha_selec.strftime('%d/%m/%Y')
    f2 = (fecha_selec + timedelta(days=1)).strftime('%d/%m/%Y')

    # Guardamos posición inicial
    x0 = pdf.get_x()
    y0 = pdf.get_y()

    # Creamos caja con fondo gris suave
    pdf.set_fill_color(240, 240, 240)  # gris claro
    pdf.rect(x0, y0, 190, 12, 'F')     # ancho casi total del A4 menos márgenes

    # Texto arriba de la caja
    pdf.set_xy(x0 + 2, y0 + 2)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica",style='B', size=11)

    pdf.multi_cell(
        0, 8,
        f"Lluvia acumulada desde las 9 hs del {f1} "
        f"a las 9 hs del día {f2} - Día pluviométrico",
        align='C'
    )

    pdf.ln(6)
# ---------------------------------------------------
# ---------------------------------------------------------------
    
    
    pdf.ln(8)

    # --- TABLA DE DATOS ---
    pdf.set_font("Helvetica", style='B', size=11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(60, 10, " Estación", 1, 0, 'L', True)
    pdf.cell(50, 10, " Departamento", 1, 0, 'L', True)
    pdf.cell(50, 10, " Provincia", 1, 0, 'L', True)
    pdf.cell(30, 10, " Lluvia (mm)", 1, 1, 'C', True)

    df_ordenado = df_dia.sort_values(by='mm', ascending=False)

    # Usa variable global col_nombre_estacion (como tu original)
    for _, fila in df_ordenado.iterrows():
        nombre_val = fila.get('Pluviómetro', fila.get(col_nombre_estacion, fila.get('cod', 'S/D')))
        depto_val = fila.get('depto', fila.get('Departamento', 'S/D'))
        valor_mm = fila.get('mm', 0)

        nombre = str(nombre_val).encode('latin-1', 'replace').decode('latin-1')
        depto = str(depto_val).encode('latin-1', 'replace').decode('latin-1')

        if valor_mm >= 50:
            pdf.set_fill_color(210, 210, 210)  # gris más notable
            pdf.set_font("Helvetica", style='B', size=10)
            pintar_celda = True
        else:
            pdf.set_font("Helvetica", size=10)
            pintar_celda = False

        prov_val = fila.get('Provincia', 'S/D')
        provincia = str(prov_val).encode('latin-1', 'replace').decode('latin-1')

        pdf.cell(60, 10, f" {nombre}", 1, 0, 'L', pintar_celda)
        pdf.cell(50, 10, f" {depto}", 1, 0, 'L', pintar_celda)
        pdf.cell(50, 10, f" {provincia}", 1, 0, 'L', pintar_celda)
        pdf.cell(30, 10, f" {valor_mm} mm", 1, 1, 'C', pintar_celda)

    # === FIX ROBUSTO: normalizar a bytes sin importar la versión de fpdf ===
    data = pdf.output(dest='S')  # puede ser str, bytes o bytearray
    if isinstance(data, (bytes, bytearray)):
        return bytes(data)
    else:
        return data.encode('latin-1', errors='replace')


# =========================================
# CONFIGURACIÓN DE PÁGINA
# =========================================
st.set_page_config(
    page_title="Red Pluviométrica Salta - Jujuy",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png",
    layout="wide"
)

# Estado para carga histórica (Optimización)
if 'cargar_todo' not in st.session_state:
    st.session_state.cargar_todo = False

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
    except:
        return None, None
    return None, None


@st.cache_data(ttl=1800)
def cargar_datos_optimizados(solo_reciente=True):
    try:
        r1 = requests.get(URL_PRECIPITACIONES, headers=HEADERS)
        r2 = requests.get(URL_MAPA, headers=HEADERS)
        df_p, df_c = pd.DataFrame(r1.json()), pd.DataFrame(r2.json())

        df_p['fecha_dt'] = pd.to_datetime(df_p['Fecha_del_dato'])

        # --- FILTRO INTELIGENTE ---
        if solo_reciente:
            fecha_corte = pd.Timestamp.now() - pd.Timedelta(days=60)
            df_p = df_p[df_p['fecha_dt'] >= fecha_corte].copy()

        df_p['cod'] = df_p['Pluviometros'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_c['cod'] = df_c['Codigo_txt_del_pluviometro'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_p['fecha'] = df_p['fecha_dt'].dt.date
        df_p['mm'] = pd.to_numeric(df_p['Mil_metros_registrados'], errors='coerce').fillna(0)
        df_p['fen_raw'] = df_p['fenomeno'].astype(str).str.strip().str.lower()

        map_f = {
            'viento': 'Vientos fuertes',
            'granizo': 'Granizo',
            'tormenta': 'Tormentas eléctricas',
            'sinfeno': 'Sin obs. de fenómenos'
        }
        df_p['Fenómeno atmosférico'] = df_p['fen_raw'].replace(map_f).replace({
            'none': 'Sin obs. de fenómenos',
            'nan': 'Sin obs. de fenómenos'
        })

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

        return df, df_c, col_n  # Retornamos df_c y el nombre de columna
    except:
        return pd.DataFrame(), pd.DataFrame(), None


# --- EJECUCIÓN DE LA CARGA ---
df, df_estaciones_base, col_nombre_estacion = cargar_datos_optimizados(solo_reciente=not st.session_state.cargar_todo)


# =========================================
# APP
# =========================================
if not df.empty:
    # --- PROCESAMIENTO PREVIO PARA MÉTRICAS ---
    todas_f = sorted(df['fecha'].unique(), reverse=True)

    if 'fecha_seleccionada' not in st.session_state:
        st.session_state.fecha_seleccionada = todas_f[0]

    f_referencia = st.session_state.get('fecha_query', todas_f[0])
    df_dia = df[df['fecha'] == f_referencia].dropna(subset=['lat', 'lon'])

    # --- HEADER (columns + image) ---
    logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png"
    st.markdown(f"""
        <style>
            .header-container {{ display: flex; align-items: center; margin-bottom: 15px; gap: 12px; width: 100%; }}
            .main-title {{ font-weight: bold; color: #1E3A8A !important; margin: 0; line-height: 1.2; font-size: 24px; }}
            .header-logo {{ height: 45px; width: auto; }}
            .map-border {{ box-shadow: 0px 0px 0px 2px #000000; border-radius: 8px; margin: 10px 2px; line-height: 0; }}
            .ficha-header {{
                background-color: #1E3A8A;
                color: white;
                padding: 8px;
                border-radius: 5px 5px 0 0;
                font-weight: bold;
                text-align: center;
                font-size: 14px;
                margin-top: 10px;
                }}
            
            
            @media (max-width: 600px) {{ .main-title {{ font-size: 18px !important; }} .header-logo {{ height: 35px; }} }}
        </style>
        <div class="header-container">
            <img src="{logo_url}" class="header-logo">
            <h1 class="main-title">Red Pluviométrica Salta - Jujuy</h1>
        </div>
    """, unsafe_allow_html=True)    
    
    
    
    
    # --- CSS auxiliar ---
    st.markdown("""
    <style>
        .map-border { box-shadow: 0px 0px 0px 2px #000000; border-radius: 8px; margin: 10px 2px; line-height: 0; }
        .ficha-header {
            background-color: #1E3A8A;
            color: white;
            padding: 8px;
            border-radius: 5px 5px 0 0;
            font-weight: bold;
            text-align: center;
            font-size: 14px;
            margin-top: 10px;
        }
        @media (max-width: 600px) { h1 { font-size: 18px !important; } }
    </style>
    """, unsafe_allow_html=True)

    # --- BARRA LATERAL ---
    cant_reportes = len(df_dia)
    cant_total = len(df_estaciones_base)

    st.sidebar.markdown("""
        <div class="ficha-header">Pluviómetros Reportados</div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
        <div style="
            background-color: #ffffff;
            padding: 18px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            text-align: center;
        ">
            <div style="display: flex; align-items: baseline; justify-content: center; gap: 4px;">
                <span style="font-size: 32px; font-weight: 800; color: #1E3A8A;">{cant_reportes}</span>
                <span style="font-size: 18px; color: #94a3b8; font-weight: 600;">/ {cant_total}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.cargar_todo:
        st.sidebar.info("📂 Modo: Datos recientes (60 días)")
        if st.sidebar.button("Cargar Historial Completo"):
            st.session_state.cargar_todo = True
            st.cache_data.clear()
            st.rerun()
    else:
        st.sidebar.success("📂 Modo: Historial Completo")
        if st.sidebar.button("Volver a modo rápido"):
            st.session_state.cargar_todo = False
            st.rerun()

    st.sidebar.markdown("---")
    f_hoy = st.sidebar.date_input(
        "Consultar otra fecha:",
        value=f_referencia,
        format="DD/MM/YYYY",
        key="fecha_query"
    )

    # --- SECCIÓN DE DESCARGA (PDF) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Reportes")

    try:
        df_dia_pdf = df[df['fecha'] == f_hoy].dropna(subset=['lat', 'lon'])
        pdf_bytes = crear_pdf(df_dia_pdf, f_hoy, cant_total)  # ← firma original
        st.sidebar.download_button(
            label="📥 Reporte del dia - PDF",
            data=pdf_bytes,  # bytes directos
            file_name=f"reporte_INTA_{f_hoy}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.sidebar.error(f"No se pudo generar el PDF: {e}")

    # df del día actualizado
    df_dia = df[df['fecha'] == f_hoy].dropna(subset=['lat', 'lon'])

    # --- PESTAÑAS ---
    tab_list = ["🗺️ Mapa", "📊 Día", "📅 Mes", "🏆 Max Min", "📈 Hist.", "📥 Desc.", "🌧️ Red"]
    t1, t2, t3, t4, t5, t6, t7 = st.tabs(tab_list)

    # =========================
    # TAB 1 - MAPA (sin parpadeo)
    # =========================
    with t1:
        st.subheader(f"Lluvia del {f_hoy.strftime('%d/%m/%Y')}")
        st.info(f"Lluvia acumulada desde las 9 hs del {f_hoy.strftime('%d/%m/%Y')} a las 9 hs del día {(f_hoy + timedelta(days=1)).strftime('%d/%m/%Y')} - Día pluviométrico")

        lista_regiones = ["Todas"] + sorted(df_dia['Region'].unique().tolist()) if not df_dia.empty else ["Todas"]
        sel_zoom = st.selectbox("🔍 Enfocar Región:", lista_regiones)

        if not df_dia.empty:
            df_mapa = df_dia[df_dia['Region'] == sel_zoom].copy() if sel_zoom != "Todas" else df_dia.copy()
            zoom_inicial = 9 if sel_zoom != "Todas" else 7
            centro = [df_mapa['lat'].mean(), df_mapa['lon'].mean()]

            m = folium.Map(location=centro, zoom_start=zoom_inicial, tiles=None)
            folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                attr='Google', name='Google Satélite', overlay=False
            ).add_to(m)
            folium.TileLayer(
                tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png",
                attr='IGN', name='Argenmap (IGN)', overlay=False
            ).add_to(m)

            legend_html = '''
            <div style="position: fixed; top: 10px; right: 10px; width: 110px; background: white; border:2px solid grey; z-index:9999; font-size:11px; padding: 8px; border-radius: 5px; opacity: 0.85; font-family: sans-serif; line-height: 1.4;">
                <b>Referencia:</b><br>
                <i style="background: #1a73e8; width: 10px; height: 10px; display:inline-block; border-radius: 50%;"></i> 0-20 mm<br>
                <i style="background: #ef6c00; width: 10px; height: 10px; display:inline-block; border-radius: 50%;"></i> 20-50 mm<br>
                <i style="background: #d32f2f; width: 10px; height: 10px; display:inline-block; border-radius: 50%;"></i> +50 mm
            </div>
            '''
            m.get_root().html.add_child(folium.Element(legend_html))
            LocateControl(auto_start=False, flyTo=True).add_to(m)
            folium.LayerControl(position='bottomright').add_to(m)

            for _, r in df_mapa.iterrows():
                c_hex = '#d32f2f' if r['mm'] > 50 else '#ef6c00' if r['mm'] > 20 else '#1a73e8'
                c_fol = 'red' if r['mm'] > 50 else 'orange' if r['mm'] > 20 else 'blue'
                icon_code = 'cloud'
                if 'granizo' in r['fen_raw']: icon_code = 'asterisk'
                elif 'tormenta' in r['fen_raw']: icon_code = 'flash'
                elif 'viento' in r['fen_raw']: icon_code = 'leaf'

                html_popup = f"""
                <div style="font-family: sans-serif; min-width: 180px;">
                    <div style="margin:0; color:{c_hex}; border-bottom:2px solid {c_hex}; font-size:16px; font-weight:bold; padding-bottom:5px; margin-bottom:8px;">{r['Pluviómetro']}</div>
                    <div style="font-size:14px; margin-bottom:3px;"><b>Lluvia:</b> {r['mm']} mm</div>
                    <div style="font-size:13px; margin-bottom:6px;"><b>Fenómeno:</b> {r['Fenómeno atmosférico']}</div>
                    <div style="font-size:12px; color:#333; border-top:1px solid #eee; padding-top:5px;"><b>{r['Departamento']}, {r['Provincia']}</b></div>
                </div>
                """
                # 🔵 Leyenda de mm sobre el marcador (número grande)
                folium.map.Marker(
                    [r['lat'], r['lon']],
                    icon=folium.DivIcon(
                        icon_size=(40, 20),
                        icon_anchor=(20, -10),
                        html=f'''
                            <div style="
                                color:{c_hex};
                                font-weight:900;
                                font-size:11pt;
                                text-shadow:1px 1px 0 #fff;
                            ">{int(r["mm"])}</div>
                        '''
                    )
                ).add_to(m)

                folium.Marker(
                    [r['lat'], r['lon']],
                    popup=folium.Popup(html_popup, max_width=250),
                    icon=folium.Icon(color=c_fol, icon=icon_code),
                    
                ).add_to(m)

            st.markdown('<div class="map-border">', unsafe_allow_html=True)
            st_folium(m, width="100%", height=550, key="mapa_dia", returned_objects=[])  # sin parpadeo
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No hay datos para la fecha seleccionada.")

    # =========================
    # TAB 2 - DÍA
    # =========================
    with t2:
        st.subheader(f"Resumen del {f_hoy.strftime('%d/%m/%Y')}")
        if not df_dia.empty:
            avg_reg = df_dia.groupby('Region')['mm'].agg(['mean', 'max', 'count']).sort_values('mean', ascending=False).reset_index()
            rows = [avg_reg[i:i + 3] for i in range(0, len(avg_reg), 3)]
            for row_df in rows:
                cols = st.columns(3)
                for i, (_, row) in enumerate(row_df.iterrows()):
                    with cols[i]:
                        st.metric(label=f"Región: {row['Region']}", value=f"{row['mean']:.1f} mm prom.", delta=f"Máx: {row['max']} mm ({int(row['count'])} pluviómetros)")
            st.markdown("---")
            st.subheader("Detalle de Registros")
            st.dataframe(df_dia[['Pluviómetro', 'Region', 'mm', 'Departamento', 'Provincia','Fenómeno atmosférico']].sort_values('mm', ascending=False), use_container_width=True, hide_index=True)

    # =========================
    # TAB 3 - MES
    # =========================
    with t3:
        st.subheader("📅 Acumulados Mensuales")
        if not st.session_state.cargar_todo:
            st.warning("⚠️ Mostrando últimos 60 días. Para meses/años anteriores, active 'Cargar Historial Completo' en el lateral.")

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

    # =========================
    # TAB 4 - MÁX / MÍN
    # =========================
    with t4:
        st.subheader("🏆 Máximos y Mínimos Mensuales")
        st.info("Seleccioná un pluviómetro y un período para conocer los extremos registrados.")
        if not st.session_state.cargar_todo:
            st.warning("⚠️ Mostrando últimos 60 días. Para meses/años anteriores, active 'Cargar Historial Completo' en el lateral.")

        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            sel_anio_r = st.selectbox("Año:", sorted(df['Año'].unique(), reverse=True), key="anio_r")
        with col_r2:
            meses_n_full = {1:'Enero', 2:'Febrero', 3:'Marzo', 4:'Abril', 5:'Mayo', 6:'Junio', 7:'Julio', 8:'Agosto', 9:'Septiembre', 10:'Octubre', 11:'Noviembre', 12:'Diciembre'}
            meses_disp = sorted(df[df['Año'] == sel_anio_r]['Mes_Num'].unique())
            sel_mes_r = st.selectbox("Mes:", meses_disp, format_func=lambda x: meses_n_full[x], key="mes_r")
        with col_r3:
            sel_est_r = st.selectbox("Seleccionar Pluviómetro:", sorted(df['Pluviómetro'].unique()), key="est_r")

        df_records = df[(df['Año'] == sel_anio_r) & (df['Mes_Num'] == sel_mes_r) & (df['Pluviómetro'] == sel_est_r)].copy()
        if not df_records.empty:
            max_row = df_records.loc[df_records['mm'].idxmax()]
            df_con_lluvia = df_records[df_records['mm'] > 0]
            m1, m2 = st.columns(2)
            with m1:
                st.metric(label="Máxima Precipitación", value=f"{max_row['mm']} mm")
                st.caption(f"📅 Fecha: {max_row['fecha'].strftime('%d/%m/%Y')}")
            with m2:
                if not df_con_lluvia.empty:
                    min_row = df_con_lluvia.loc[df_con_lluvia['mm'].idxmin()]
                    st.metric(label="Mínima (Día con lluvia)", value=f"{min_row['mm']} mm")
                    st.caption(f"📅 Fecha: {min_row['fecha'].strftime('%d/%m/%Y')}")
                else:
                    st.metric(label="Mínima", value="0 mm")
            st.markdown("---")
            chart_r = alt.Chart(df_records).mark_line(point=True, color='#1E3A8A').encode(
                x=alt.X('fecha:T', title='Día'),
                y=alt.Y('mm:Q', title='Precipitación (mm)'),
                tooltip=['fecha', 'mm']
            ).properties(height=200)
            st.altair_chart(chart_r, use_container_width=True)

    # =========================
    # TAB 5 - HISTÓRICO
    # =========================
    with t5:
        st.subheader("📈 Consulta Histórica")
        if not st.session_state.cargar_todo:
            st.warning("⚠️ Mostrando últimos 60 días. Para meses/años anteriores, active 'Cargar Historial Completo' en el lateral.")

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
            df_p_filt = df[(df['fecha'] >= f_desde) & (df['fecha'] <= f_hasta) & (df['Pluviómetro'].isin(sel_est_h))].copy()
            if not df_p_filt.empty:
                if agrupar == "Semana":
                    df_p_filt['f_plot'] = df_p_filt['fecha_dt'] - pd.to_timedelta(df_p_filt['fecha_dt'].dt.dayofweek, unit='d')
                elif agrupar == "Mes":
                    df_p_filt['f_plot'] = df_p_filt['fecha_dt'].dt.to_period('M').dt.to_timestamp()
                else:
                    df_p_filt['f_plot'] = df_p_filt['fecha_dt']
                df_res = df_p_filt.groupby(['f_plot', 'Pluviómetro'])['mm'].sum().reset_index()
                df_res['fecha_f'] = df_res['f_plot'].dt.strftime('%d/%m/%Y')
                chart = alt.Chart(df_res).mark_bar().encode(
                    x=alt.X('Pluviómetro:N', title=None, axis=alt.Axis(labels=False)),
                    y=alt.Y('mm:Q', title='Lluvia (mm)'),
                    color='Pluviómetro:N',
                    column=alt.Column('fecha_f:O', title=None,
                                      sort=alt.SortField(field='f_plot', order='ascending'),
                                      header=alt.Header(labelOrient='bottom', labelAngle=-45, labelAlign='right')),
                    tooltip=['fecha_f', 'Pluviómetro', 'mm']
                ).properties(width=alt.Step(45), height=350)
                st.altair_chart(chart, use_container_width=True)

    # =========================
    # TAB 6 - DESCARGAS
    # =========================
    with t6:
        st.subheader("📥 Descargar")
        if not st.session_state.cargar_todo:
            st.warning("⚠️ Mostrando últimos 60 días. Para meses/años anteriores, active 'Cargar Historial Completo' en el lateral.")

        sel_est_desc = st.selectbox("Seleccione el Pluviómetro:", sorted(df['Pluviómetro'].unique()), key="desc_sel")
        if sel_est_desc:
            df_desc = df[df['Pluviómetro'] == sel_est_desc][['fecha', 'mm', 'Fenómeno atmosférico', 'Departamento', 'Provincia', 'Region']].sort_values('fecha', ascending=False)
            st.dataframe(df_desc, use_container_width=True, hide_index=True)
            st.download_button(f"📥 Descargar CSV de {sel_est_desc}", df_desc.to_csv(index=False).encode('utf-8'), f'{sel_est_desc}.csv', "text/csv")

    # =========================
    # TAB 7 - RED (sin parpadeo + popup móvil)
    # =========================
    with t7:
        st.subheader("Red")
        st.info("Este mapa muestra todos los pluviómetros incorporados a la red.")

        df_red_completa = df_estaciones_base.dropna(subset=['lat', 'lon']).copy()

        if col_nombre_estacion and col_nombre_estacion in df_red_completa.columns:
            df_red_completa['Pluviómetro'] = df_red_completa[col_nombre_estacion].fillna(df_red_completa['cod'])
        else:
            df_red_completa['Pluviómetro'] = df_red_completa['cod']

        col_depto_base = next((c for c in df_red_completa.columns if 'depto' in c.lower() or 'depart' in c.lower()), None)
        col_prov_base = next((c for c in df_red_completa.columns if 'prov' in c.lower()), None)

        opciones_sugeridas = sorted(df_red_completa['Pluviómetro'].unique().tolist())
        seleccion = st.selectbox("🔍 Busque un pluviómetro:", ["Ver todos"] + opciones_sugeridas, index=0)

        df_mostrar = df_red_completa if seleccion == "Ver todos" else df_red_completa[df_red_completa['Pluviómetro'] == seleccion]
        zoom_init = 7 if seleccion == "Ver todos" else 12

        if not df_mostrar.empty:
            m_red = folium.Map(location=[df_mostrar['lat'].mean(), df_mostrar['lon'].mean()],
                               zoom_start=zoom_init, tiles=None)

            folium.TileLayer(
                tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                attr='Google', name='Google Satélite'
            ).add_to(m_red)

            folium.TileLayer(
                tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png",
                attr='IGN', name='Argenmap (IGN)'
            ).add_to(m_red)

            # ⭐ A C Á   A D O P T A M O S   M A R K E R C L U S T E R ⭐
            cluster = MarkerCluster().add_to(m_red)

            for _, r in df_mostrar.iterrows():
                depto_val = r[col_depto_base] if col_depto_base and pd.notna(r[col_depto_base]) else 'S/D'
                prov_val = r[col_prov_base] if col_prov_base and pd.notna(r[col_prov_base]) else 'S/D'

                info = folium.Popup(
                    html=f"""
                    <div style="font-family: sans-serif; min-width: 180px;">
                        <div style="font-weight:700; margin-bottom:6px;">{r['Pluviómetro']}</div>
                        <div style="font-size:13px; color:#333;">
                            <b>Depto/Prov:</b> {depto_val} / {prov_val}
                        </div>
                    </div>
                    """,
                    max_width=260
                )

                folium.CircleMarker(
                    location=[r['lat'], r['lon']],
                    radius=8, color="#1E3A8A",
                    fill=True, fill_color="#3B82F6", fill_opacity=0.9,
                    tooltip=r['Pluviómetro'],
                    popup=info
                ).add_to(cluster)

            st.markdown('<div class="map-border">', unsafe_allow_html=True)
            st_folium(m_red, width="100%", height=600, key="mapa_red", returned_objects=[])
            st.markdown('</div>', unsafe_allow_html=True)

    # --- INFO INSTITUCIONAL COMPLETA ---
    INFO_MD = """
    La Red Pluviométrica es una herramienta tecnológica desarrollada por el INTA Centro Regional Salta y Jujuy, cuyo objetivo es recopilar datos precisos y confiables sobre la precipitación en diversas áreas geográficas. Estos datos son esenciales no solo para la gestión agrícola, sino también para la toma de decisiones de otros actores, como los gobiernos locales, que pueden utilizarlos para la planificación y gestión de recursos hídricos, la prevención de desastres naturales y el desarrollo sostenible en sus comunidades.

    La Red Pluviométrica es una iniciativa que reúne el trabajo articulado y mancomunado entre INTA, productores locales y particulares que colaboran diariamente con la información registrada por sus pluviómetros.

    La ubicación de los pluviómetros está georreferenciada y los datos se recopilan mediante la plataforma INTA Territorios. La misma se desarrolló utilizando el software Kobo Toolbox y Kobo Collect, herramientas de código abierto que facilitan la colecta eficiente de datos y optimizan la exportación y la integración de los mismos, para su posterior análisis en sistemas de información geográfica.

    Los datos se registran como día pluviométrico. Día pluviométrico es un período de 24 horas, que va de una hora específica (comúnmente las 9 AM) de un día hasta la misma hora del día siguiente, utilizado para registrar la cantidad total de precipitación (lluvia) caída, estandarizando las mediciones meteorológicas. La lluvia medida a las 9 AM de un día corresponde a la acumulada desde las 9 AM del día anterior.

    Se pone a disposición de la comunidad paneles de control interactivos que visualizan la red de pluviómetros. Estos paneles permiten consultar los valores diarios y mensuales de precipitaciones desde octubre de 2024 hasta la fecha actual, acompañados de gráficos comparativos que facilitan la comprensión y análisis de los datos.

    **Equipo de trabajo:**
    Lic. Inf. Hernán Elena (Lab. Teledetección y SIG - Grupo RRNN), Obs. Met. Germán Guanca (Meteorología - Grupo RRNN), Ing. Agr. Rafael Saldaño (OIT Coronel Moldes) - Ing. Agr. Daniela Moneta (AER Valle de Lerma). INTA EEA Salta - Ing. Juan Ramón Rojas (INTA-AER Santa Victoria Este) - Ing. Agr. Daniel Lamberti (INTA AER Perico) - Tec. Recursos Hídricos Fátima del Valle Miranda (INTA AER Palma Sola) - Ing. Agr. Florencia Diaz (INTA AER Palma Sola), Héctor Diaz (INTA AER J.V. Gonzalez), Carlos G. Cabrera (INTA AER J.V. Gonzalez), Lucas Diaz (INTA AER Cafayate - OIT San Carlos), Cristina Rosetto (INTA EECT Yuto), Ing. RRNN Fabian Tejerina (Grupo RRNN EEA Salta), Tec. Agr. Carlos Arias (OIT General Güemes).

    **Colaboradores:**
    Nicolás Uriburu, Nicolás Villegas, Matias Lanusse, Marcela Lopez, Martín Amado, Agustín Sanz Navamuel, Luis Fernández Acevedo, Miguel A. Boasso, Luis Zavaleta, Mario Lambrisca, Noelia Rovedatti, Matías Canonica, Alejo Alvarez, Javier Montes, Guillermo Patron Costa, Sebastián Mendilaharzu, Francisco Chehda, Jorge Robles, Gustavo Soricich, Javier Atea, Luis D. Elias, Leandro Carrizo, Daiana Núñez, Fátima González, Santiago Villalba, Juan Collado, Julio Collado, Estanislao Lara, Carlos Cruz, Daniel Espinoza, Fabian Álvarez, Lucio Señoranis, Rene Vallejos Rueda, Héctor Miranda, Emanuel Arias, Oscar Herrera, Francisca Vacaflor, Zaturnino Ceballos, Alcides Ceballos, Juan Ignacio Pearson, Pascual Erazo, Dario Romero, Luisa Andrada, Alejandro Ricalde, Odorico Romero, Lucas Campos, Sebastián Diaz, Carlos Sanz, Gabriel Brinder, Gastón Vizgarra, Diego Sulca, Alicia Tapia, Roberto Ponce, Sergio Cassinelli, María Zamboni, Andres Flores, Tomás Lienemann, Carmen Carattoni, Cecilia Carattoni, Tito Donoso, Javier Aprile, Carla Carattoni, Cuenca Renan, Luna Federico, Soloza Pedro, Aparicio Cirila, Torres Arnaldo, Torres Mergido, Sardina Ruben, Illesca Francisco, Saravia Adrian, Carabajal Jesus, Alvarado Rene, Saban Mary, Rodriguez Eleuterio, Guzman Durbal, Sajama Sergio, Miranda Dina, Pedro Quispe, Fabiana Monasterio, Raquel Araoz, Raul Alvarez, Rafael Mendoza, Lila Torfe, Samuel Aramayo.

    Para más información, podés contactarnos en: elena.hernan@inta.gob.ar
    """
    st.markdown("---")
    with st.expander("ℹ️ Información sobre la Red Pluviométrica"):
        st.markdown(INFO_MD, unsafe_allow_html=True)

else:
    st.error("Error al conectar con la base de datos.")
