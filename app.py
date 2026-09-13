# ==============================================================
# RED PLUVIOMÉTRICA SALTA - JUJUY
# Navegación estable por Sidebar (SIN TABS)
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl, MarkerCluster
from datetime import timedelta
from fpdf import FPDF
import locale
import xml.etree.ElementTree as ET
from io import BytesIO


# =====================================================
# INFO INSTITUCIONAL COMPLETA
# =====================================================
INFO_MD = """
La **Red Pluviométrica** es una herramienta tecnológica desarrollada por el
**INTA Centro Regional Salta y Jujuy**, cuyo objetivo es recopilar datos precisos
y confiables sobre la precipitación en diversas áreas geográficas.

Estos datos son fundamentales para la gestión agrícola, la planificación
territorial, la gestión de recursos hídricos y la prevención de eventos
hidrometeorológicos extremos.

La Red Pluviométrica es una iniciativa que reúne el trabajo articulado y
mancomunado entre **INTA**, productores locales y colaboradores particulares
que aportan diariamente la información registrada por sus pluviómetros.

La ubicación de los pluviómetros se encuentra georreferenciada y los datos
son recopilados mediante la plataforma **INTA Territorios**, desarrollada
sobre herramientas de código abierto como **Kobo Toolbox** y **Kobo Collect**,
optimizando la carga, exportación y análisis de la información.

Los datos se registran como **día pluviométrico**, definido como el período de
24 horas comprendido entre las **9:00 h de un día y las 9:00 h del día
siguiente**. La precipitación registrada a las 9:00 h corresponde a la lluvia
acumulada desde las 9:00 h del día anterior.

El sistema pone a disposición de la comunidad **paneles de control
interactivos**, que permiten la consulta de precipitaciones **diarias y
mensuales** desde octubre de 2024 a la fecha.

### 👥 Equipo de trabajo
Lic. Inf. **Hernán Elena** (EEA Salta)  
Obs. Met. **Germán Guanca** (EEA Salta)     
Ing. Agr. **Rafael Saldaño** (OIT Coronel Moldes)   
Ing. Agr. **Daniela Moneta** (AER Valle de Lerma)   
Ing. **Juan Ramón Rojas** (AER Santa Victoria Este)    
Ing. Agr. **Daniel Lamberti** (AER Perico)     
Tec. Recursos Hídricos **Fátima del Valle Miranda** (AER Palma Sola)   
Ing. Agr. **Florencia Diaz** (AER Palma Sola)  
Ing. Agr. **Héctor Diaz** (AER J.V. Gonzalez)  
Ing. Agr. **Carlos G. Cabrera** (AER J.V. Gonzalez)    
**Lucas Diaz** (AER Cafayate - OIT San Carlos)     
Med. Vet. **Cristina Rosetto** (EECT Yuto)     
Ing. RRNN **Fabian Tejerina** (EEA Salta)    
Tec. Agr. **Carlos Arias** (OIT General Güemes)    
Ing. Agr. **Diego Kalman** (AER Cafayate)    


### 🤝 Red de colaboradores territoriales

Nicolás Uriburu, Nicolás Villegas, Matías Lanusse, Marcela López, Martín Amado, Agustín Sanz Navamuel, Luis Fernández Acevedo, Miguel A. Boasso, Luis Zavaleta, Mario Lambrisca, Noelia Rovedatti, Matías Canonica, Alejo Álvarez, Javier Montes, Guillermo Patrón Costa, Sebastián Mendilaharzu, Francisco Chehda, Jorge Robles, Gustavo Soricich, Javier Atea, Luis D. Elías, Leandro Carrizo, Daiana Núñez, Fátima González, Santiago Villalba, Juan Collado, Julio Collado, Estanislao Lara, Carlos Cruz, Daniel Espinoza, Fabián Álvarez, Lucio Señoranis, René Vallejos Rueda, Héctor Miranda, Emanuel Arias, Oscar Herrera, Francisca Vacaflor, Zaturnino Ceballos, Alcides Ceballos, Juan Ignacio Pearson, Pascual Erazo, Darío Romero, Luisa Andrada, Alejandro Ricalde, Odorico Romero, Lucas Campos, Sebastián Díaz, Carlos Sanz, Gabriel Brinder, Gastón Vizgarra, Diego Sulca, Alicia Tapia, Sergio Cassinelli, María Zamboni, Andrés Flores, Tomás Lienemann, Carmen Carattoni, Cecilia Carattoni, Tito Donoso, Javier Aprile, Carla Carattoni, Cuenca Renán, Luna Federico, Soloza Pedro, Aparicio Cirila, Torres Arnaldo, Torres Mergido, Sardina Rubén, Illesca Francisco, Saravia Adrián, Carabajal Jesús, Alvarado René, Saban Mary, Rodríguez Eleuterio, Guzmán Durbal, Sajama Sergio, Miranda Dina, Pedro Quispe, Fabiana Monasterio, Raquel Araoz, Raúl Álvarez, Rafael Mendoza, Lila Torfe, Samuel Aramayo, Jose Maidana, Hernan Terceros, Maria Sulca, Paulino Sulca, Nadia Ríos, Matías Copa, Marcos Aurelio Rodríguez, Horacio Hoyo, Alejandro Romero, Carlos Ruiz.


📧 **Contacto:** elena.hernan@inta.gob.ar


"""


# ==============================================================
# CONFIGURACIÓN GENERAL
# ==============================================================

st.set_page_config(
    page_title="Red Pluviométrica Salta - Jujuy",
    page_icon="logo_inta.png",
    layout="wide"
)

st.markdown(
    """
    <style>
    /* Elimina espacio superior general */
    section.main > div {
        padding-top: 0rem !important;
    }

    /* A veces Streamlit agrega margen extra al primer bloque */
    .block-container {
        padding-top: 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)




try:
    locale.setlocale(locale.LC_TIME, "es_AR.UTF-8")
except:
    pass

st.markdown("""
<style>
/* ==============================
   RESALTAR DATE INPUT SIDEBAR (COMPATIBLE LIGHT & DARK)
   ============================== */

/* Caja/Input de la fecha */
section[data-testid="stSidebar"] div[data-baseweb="input"] {
    background-color: #DBEAFE !important;
    border-radius: 8px !important;
    border: 2px solid #1E3A8A !important;
    padding: 2px !important;
}

/* Texto interno de la fecha */
section[data-testid="stSidebar"] div[data-baseweb="input"] input {
    font-weight: 700 !important;
    color: #1E3A8A !important;
    text-align: center !important;
    background-color: transparent !important;
}

/* Label (título) adaptable al tema activo */
section[data-testid="stSidebar"] [data-testid="stDateInput"] label {
    font-weight: 600 !important;
    color: inherit !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>

/* ===== FORZAR VISUAL DE TABLAS (DARK & LIGHT SAFE) ===== */

/* Contenedor principal de Streamlit */
section.main table {
    background-color: #ffffff !important;
    color: #111111 !important;
}

/* Encabezados */
section.main thead tr th {
    background-color: #e5e7eb !important;
    color: #111111 !important;
    font-weight: 600 !important;
    border-bottom: 2px solid #9ca3af !important;
}

/* Celdas */
section.main tbody tr td {
    background-color: #ffffff !important;
    color: #111111 !important;
}

/* Filas alternadas */
section.main tbody tr:nth-child(even) td {
    background-color: #f3f4f6 !important;
}

/* Hover */
section.main tbody tr:hover td {
    background-color: #dbeafe !important;
}

/* Caption */
section.main .stCaption {
    color: #374151 !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* ===============================
   TABLAS - COMPATIBLE DARK MODE
   =============================== */

/* Dataframe background */
[data-testid="stDataFrame"] {
    background-color: #ffffff;
    color: #111111;
}

/* Header */
[data-testid="stDataFrame"] thead tr th {
    background-color: #e5e7eb !important;
    color: #111111 !important;
    font-weight: 600;
}

/* Body cells */
[data-testid="stDataFrame"] tbody tr td {
    background-color: #ffffff !important;
    color: #111111 !important;
}

/* Zebra rows */
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background-color: #f3f4f6 !important;
}

/* Hover */
[data-testid="stDataFrame"] tbody tr:hover td {
    background-color: #dbeafe !important;
}

/* Caption text */
.stCaption {
    color: #374151 !important;
}
</style>
""", unsafe_allow_html=True)




# =================================================
# ENCABEZADO INSTITUCIONAL PRINCIPAL
# =================================================
logo_url = "https://raw.githubusercontent.com/hernanelena/monitor-lluvias-inta/0d313b923de444081402a86286afc7d2e7169406/Logo_INTA.svg.png"

st.markdown(f"""
<style>
.header-container {{
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 0px;
    margin-bottom: 12px;
}}
.header-logo {{
    height: 55px;
    width: auto;
}}
.header-title {{
    font-size: 28px;
    font-weight: 800;
    color: #1E3A8A;
    margin: 0;
    line-height: 1.2;
}}
.header-subtitle {{
    font-size: 14px;
    color: #475569;
    font-weight: 500;
}}
</style>

<div class="header-container">
    <img src="{logo_url}" class="header-logo">
    <div>
        <div class="header-title">Red Pluviométrica Salta – Jujuy</div>
        <div class="header-subtitle">
            Sistema de Relevamiento de Precipitaciones · INTA EEA Salta
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")




# ==============================================================
# ESTADO GLOBAL
# ==============================================================

if "cargar_todo" not in st.session_state:
    st.session_state.cargar_todo = False

# ==============================================================
# CREDENCIALES Y URLS
# ==============================================================

URL_PRECIPITACIONES = "https://territorios.inta.gob.ar/assets/aYqLUVvU3EYiDa7NoJbPKF/submissions/?format=json"
URL_MAPA = "https://territorios.inta.gob.ar/assets/aFwWKNGXZKppgNYKa33wC8/submissions/?format=json"

TOKEN = st.secrets["INTA_TOKEN"]


HEADERS = {"Authorization": f"Token {TOKEN}"}

# ==============================================================
# FUNCIONES AUXILIARES
# ==============================================================

def parse_coordenada_rapido(v):
    if isinstance(v, str):
        parts = v.split()
        if len(parts) >= 2:
            try:
                return float(parts[0]), float(parts[1])
            except ValueError:
                pass
    elif isinstance(v, (list, tuple)) and len(v) >= 2:
        try:
            return float(v[0]), float(v[1])
        except (ValueError, TypeError):
            pass
    return np.nan, np.nan


@st.cache_data(ttl=86400, show_spinner="Actualizando base de pluviómetros...")
def cargar_estaciones():
    try:
        r2 = requests.get(URL_MAPA, headers=HEADERS, timeout=30)
        r2.raise_for_status()
        df_c = pd.DataFrame(r2.json())
    except Exception as e:
        st.error(f"Error al conectar con la base de pluviómetros: {e}")
        return pd.DataFrame(), "cod"

    if df_c.empty:
        return pd.DataFrame(), "cod"

    col_u = next((c for c in ["Ubicaci_in", "ubicaci_in", "_Ubicaci_in"] if c in df_c.columns), None)
    if col_u:
        coords = [parse_coordenada_rapido(v) for v in df_c[col_u]]
        df_c["lat"] = [c[0] for c in coords]
        df_c["lon"] = [c[1] for c in coords]
    else:
        df_c["lat"] = np.nan
        df_c["lon"] = np.nan

    if "Codigo_txt_del_pluviometro" in df_c.columns:
        df_c["cod"] = df_c["Codigo_txt_del_pluviometro"].astype(str).str.replace(".0", "", regex=False).str.strip()
    else:
        df_c["cod"] = df_c.index.astype(str)

    col_n = next((c for c in df_c.columns if "Nombre_del_Pluviometro" in c), "cod")
    col_depto = next((c for c in df_c.columns if "depto" in c.lower()), None)
    col_prov = next((c for c in df_c.columns if "prov" in c.lower()), None)
    col_region = next((c for c in df_c.columns if "reg" in c.lower()), None)

    cols_deseadas = ["cod", "lat", "lon", col_n]
    if col_depto and col_depto not in cols_deseadas:
        cols_deseadas.append(col_depto)
    if col_prov and col_prov not in cols_deseadas:
        cols_deseadas.append(col_prov)
    if col_region and col_region not in cols_deseadas:
        cols_deseadas.append(col_region)

    df_est = df_c[cols_deseadas].copy()
    df_est["Pluviómetro"] = df_est[col_n].fillna(df_est["cod"])
    df_est["Departamento"] = df_est[col_depto].fillna("S/D") if col_depto else "S/D"
    df_est["Provincia"] = df_est[col_prov].fillna("S/D") if col_prov else "S/D"
    df_est["Region"] = df_est[col_region].fillna("General") if col_region else "General"

    return df_est, col_n


@st.cache_data(ttl=1800, show_spinner="Descargando registros de precipitaciones...")
def cargar_precipitaciones(solo_reciente=True):
    try:
        r1 = requests.get(URL_PRECIPITACIONES, headers=HEADERS, timeout=60)
        r1.raise_for_status()
        raw_items = r1.json()
    except Exception as e:
        st.error(f"Error al descargar datos de precipitaciones: {e}")
        return pd.DataFrame()

    if not raw_items:
        return pd.DataFrame()

    filas = []
    for it in raw_items:
        filas.append({
            "Fecha_del_dato": it.get("Fecha_del_dato"),
            "Mil_metros_registrados": it.get("Mil_metros_registrados"),
            "fenomeno": it.get("fenomeno"),
            "Pluviometros": it.get("Pluviometros")
        })

    df_p = pd.DataFrame(filas)
    df_p["fecha_dt"] = pd.to_datetime(df_p["Fecha_del_dato"], errors="coerce")
    df_p = df_p.dropna(subset=["fecha_dt"])

    if solo_reciente:
        corte = pd.Timestamp.now() - pd.Timedelta(days=60)
        df_p = df_p[df_p["fecha_dt"] >= corte]

    df_p["fecha"] = df_p["fecha_dt"].dt.date
    df_p["mm"] = pd.to_numeric(df_p["Mil_metros_registrados"], errors="coerce").fillna(0.0)

    fen_clean = df_p["fenomeno"].astype(str).str.strip().str.lower()
    df_p["fen_raw"] = fen_clean
    map_fen = {
        "viento": "Vientos fuertes",
        "granizo": "Granizo",
        "tormenta": "Tormentas eléctricas",
        "sinfeno": "Sin obs. de fenómenos"
    }
    df_p["Fenómeno atmosférico"] = fen_clean.map(map_fen).fillna("Sin obs. de fenómenos")
    df_p["Fenómeno atmosférico"] = df_p["Fenómeno atmosférico"].replace({
        "none": "Sin obs. de fenómenos",
        "nan": "Sin obs. de fenómenos",
        "": "Sin obs. de fenómenos"
    })

    df_p["cod"] = df_p["Pluviometros"].astype(str).str.replace(".0", "", regex=False).str.strip()

    return df_p[["fecha_dt", "fecha", "mm", "fen_raw", "Fenómeno atmosférico", "cod"]]


@st.cache_data(ttl=1800, show_spinner=False)
def obtener_datos(solo_reciente=True):
    df_est, col_n = cargar_estaciones()
    df_p = cargar_precipitaciones(solo_reciente=solo_reciente)

    if df_p.empty or df_est.empty:
        return pd.DataFrame(), df_est, col_n

    cols_est = ["cod", "lat", "lon", "Pluviómetro", "Departamento", "Provincia", "Region"]
    df = df_p.merge(df_est[cols_est], on="cod", how="left")

    df["Pluviómetro"] = df["Pluviómetro"].fillna(df["cod"])
    df["Departamento"] = df["Departamento"].fillna("S/D")
    df["Provincia"] = df["Provincia"].fillna("S/D")
    df["Region"] = df["Region"].fillna("General")

    return df, df_est, col_n

# ==============================================================
# PDF DIARIO
# ==============================================================

@st.cache_data(show_spinner=False)
def crear_pdf(df_dia, fecha_selec, cant_total):
    """Genera bytes de PDF con el resumen diario."""

    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(
                0, 10,
                'Documento generado automáticamente por el Sistema de Relevamiento Pluviométrico - INTA EEA Salta',
                0, 0, 'L'
            )
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

    pdf = PDF()
    pdf.add_page()

    # =================================================
    # ENCABEZADO INSTITUCIONAL
    # =================================================
    pdf.set_fill_color(30, 58, 138)  # Azul INTA
    pdf.rect(0, 0, 210, 45, 'F')

    try:
        pdf.image("logo_inta.png", x=12, y=8, w=22)
    except:
        pass

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", 'B', 16)
    pdf.set_xy(38, 12)
    pdf.cell(0, 10, "CENTRO REGIONAL SALTA - JUJUY", ln=True)

    pdf.set_font("Helvetica", 'B', 13)
    pdf.set_x(38)
    pdf.cell(0, 8, "REPORTE DIARIO DE PRECIPITACIONES", ln=True)

    pdf.ln(22)
    pdf.set_text_color(0, 0, 0)

    # =================================================
    # RESUMEN GENERAL
    # =================================================
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Resumen del día:", ln=True)

    pdf.set_font("Helvetica", size=11)

    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }

    fecha_formateada = (
        f"{fecha_selec.day} de "
        f"{meses[fecha_selec.month]} de "
        f"{fecha_selec.year}"
    )

    pdf.cell(0, 8, f"Fecha de consulta: {fecha_formateada}", ln=True)
    pdf.cell(0, 7, f"Estaciones con reporte: {len(df_dia)}", ln=True)
    pdf.cell(0, 7, f"Total de estaciones en base: {cant_total}", ln=True)

    # =================================================
    # DÍA PLUVIOMÉTRICO
    # =================================================
    f1 = fecha_selec.strftime('%d/%m/%Y')
    f2 = (fecha_selec + timedelta(days=1)).strftime('%d/%m/%Y')

    x0 = pdf.get_x()
    y0 = pdf.get_y()

    pdf.set_fill_color(240, 240, 240)
    pdf.rect(x0, y0, 190, 12, 'F')

    pdf.set_xy(x0 + 2, y0 + 2)
    pdf.set_font("Helvetica", 'B', 11)

    pdf.multi_cell(
        0, 8,
        f"Lluvia acumulada desde las 9 hs del {f1} "
        f"a las 9 hs del día {f2} - Día pluviométrico",
        align='C'
    )

    pdf.ln(8)

    # =================================================
    # TABLA DE DATOS
    # =================================================
    pdf.set_font("Helvetica", 'B', 11)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(60, 10, "Pluviómetro", 1, 0, 'L', True)
    pdf.cell(45, 10, "Departamento", 1, 0, 'L', True)
    pdf.cell(45, 10, "Provincia", 1, 0, 'L', True)
    pdf.cell(30, 10, "Lluvia (mm)", 1, 1, 'C', True)

    pdf.set_font("Helvetica", size=10)
    df_ord = df_dia.sort_values("mm", ascending=False)

    for _, r in df_ord.iterrows():
        pdf.cell(60, 10, r["Pluviómetro"], 1)
        pdf.cell(45, 10, r["Departamento"], 1)
        pdf.cell(45, 10, r["Provincia"], 1)
        pdf.cell(30, 10, f"{r['mm']} mm", 1, 1, 'C')
        
        
    # =================================================
    # PÁGINA FINAL – EQUIPO DE TRABAJO Y COLABORADORES
    # =================================================
    pdf.add_page()

    pdf.set_text_color(0, 0, 0)

    # --- Equipo de trabajo ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Equipo de trabajo - INTA:", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0, 7,
        "Lic. Inf. Hernán Elena (EEA Salta), "
        "Obs. Met. Germán Guanca (Meteorología - EEA Salta), "
        "Ing. Agr. Rafael Saldaño (OIT Coronel Moldes), "
        "Ing. Agr. Daniela Moneta (AER Valle de Lerma), "
        "Ing. Juan Ramón Rojas (AER Santa Victoria Este), "
        "Ing. Agr. Daniel Lamberti (AER Perico), "
        "Tec. Recursos Hídricos Fátima del Valle Miranda (AER Palma Sola), "
        "Ing. Agr. Florencia Diaz (AER Palma Sola), "
        "Ing. Agr. Héctor Diaz (AER J.V. Gonzalez), "
        "Ing. Agr. Carlos G. Cabrera (AER J.V. Gonzalez), "
        "Lucas Diaz (AER Cafayate - OIT San Carlos), "
        "Med. Vet. Cristina Rosetto (EECT Yuto), "
        "Ing. RRNN Fabian Tejerina (EEA Salta), "
        "Tec. Agr. Carlos Arias (OIT General Güemes)."
    )

    pdf.ln(4)

    # --- Colaboradores ---
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Colaboradores:", ln=True)

    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(
        0, 6,
        "Nicolás Uriburu, Nicolás Villegas, Matías Lanusse, Marcela López, Martín Amado, Agustín Sanz Navamuel, Luis Fernández Acevedo, Miguel A. Boasso, Luis Zavaleta, Mario Lambrisca, Noelia Rovedatti, Matías Canonica, Alejo Álvarez, Javier Montes, Guillermo Patrón Costa, Sebastián Mendilaharzu, Francisco Chehda, Jorge Robles, Gustavo Soricich, Javier Atea, Luis D. Elías, Leandro Carrizo, Daiana Núñez, Fátima González, Santiago Villalba, Juan Collado, Julio Collado, Estanislao Lara, Carlos Cruz, Daniel Espinoza, Fabián Álvarez, Lucio Señoranis, René Vallejos Rueda, Héctor Miranda, Emanuel Arias, Oscar Herrera, Francisca Vacaflor, Zaturnino Ceballos, Alcides Ceballos, Juan Ignacio Pearson, Pascual Erazo, Darío Romero, Luisa Andrada, Alejandro Ricalde, Odorico Romero, Lucas Campos, Sebastián Díaz, Carlos Sanz, Gabriel Brinder, Gastón Vizgarra, Diego Sulca, Alicia Tapia, Sergio Cassinelli, María Zamboni, Andrés Flores, Tomás Lienemann, Carmen Carattoni, Cecilia Carattoni, Tito Donoso, Javier Aprile, Carla Carattoni, Cuenca Renán, Luna Federico, Soloza Pedro, Aparicio Cirila, Torres Arnaldo, Torres Mergido, Sardina Rubén, Illesca Francisco, Saravia Adrián, Carabajal Jesús, Alvarado René, Saban Mary, Rodríguez Eleuterio, Guzmán Durbal, Sajama Sergio, Miranda Dina, Pedro Quispe, Fabiana Monasterio, Raquel Araoz, Raúl Álvarez, Rafael Mendoza, Lila Torfe, Samuel Aramayo, Jose Maidana, Hernan Terceros, Maria Sulca, Paulino Sulca, Nadia Ríos, Matías Copa, Marcos Aurelio Rodríguez, Horacio Hoyo, Alejandro Romero, Carlos Ruiz."
    )

    pdf.ln(4)

    # --- Contacto ---
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 8, "Contacto:", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.cell(
        0, 8,
        "Para más información, podés contactarnos en: elena.hernan@inta.gob.ar",
        ln=True
    )    

    # =================================================
    # SALIDA ROBUSTA
    # =================================================
    data = pdf.output(dest='S')
    return bytes(data) if isinstance(data, (bytes, bytearray)) else data.encode('latin-1', errors='replace')
    
    

# ==============================================================
# PDF MENSUAL POR REGIÓN / DEPARTAMENTO
# ==============================================================

@st.cache_data(show_spinner=False)
def crear_pdf_mensual_region(df, region, fecha_desde, fecha_hasta):
    """
    Genera PDF mensual acumulado.
    Divide automáticamente en semestres si hay más de 6 meses.
    Incluye encabezado institucional y página final de créditos.
    """

    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(
                0, 10,
                'Documento generado automáticamente por el Sistema de Relevamiento Pluviométrico - INTA EEA Salta',
                0, 0, 'L'
            )
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

    # =================================================
    # CONFIGURACIÓN DE ANCHOS (OPTIMIZADOS)
    # =================================================
    ANCHO_EST = 58       # Pluviómetro
    ANCHO_DEP = 38       # Departamento (reducido)
    ANCHO_PROV = 28      # Provincia (reducido)
    ANCHO_MES = 18       # Mes
    ANCHO_TOTAL = 18    # Total

    # =================================================
    # PREPARACIÓN DE DATOS
    # =================================================
    df = df.copy()
    df["Mes"] = df["fecha_dt"].dt.to_period("M")

    tabla = (
        df.groupby(["Pluviómetro", "Departamento", "Provincia", "Mes"])["mm"]
        .sum()
        .reset_index()
    )

    pivot = tabla.pivot_table(
        index=["Pluviómetro", "Departamento", "Provincia"],
        columns="Mes",
        values="mm",
        aggfunc="sum"
    )

    # Ordenar meses cronológicamente
    meses = sorted(pivot.columns.tolist())
    pivot = pivot[meses]

    # Total anual
    pivot["TOTAL"] = pivot.sum(axis=1)

    # Dividir meses en bloques de hasta 6
    bloques = [meses[i:i+6] for i in range(0, len(meses), 6)]

    pdf = PDF(orientation="L")

    # =================================================
    # PÁGINAS DE TABLA (1 por bloque)
    # =================================================
    for i, bloque in enumerate(bloques):

        pdf.add_page()

        # ---------- ENCABEZADO INSTITUCIONAL ----------
        pdf.set_fill_color(30, 58, 138)
        pdf.rect(0, 0, 297, 45, 'F')

        try:
            pdf.image("logo_inta.png", x=12, y=8, w=22)
        except:
            pass

        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 16)
        pdf.set_xy(38, 12)
        pdf.cell(0, 10, "CENTRO REGIONAL SALTA - JUJUY", ln=True)

        pdf.set_font("Helvetica", 'B', 13)
        pdf.set_x(38)
        pdf.cell(0, 8, "REPORTE MENSUAL DE PRECIPITACIONES", ln=True)

        pdf.ln(22)
        pdf.set_text_color(0, 0, 0)

        # ---------- DESCRIPCIÓN ----------
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, f"Región: {region}", ln=True)

        pdf.set_font("Helvetica", size=11)
        pdf.cell(
            0, 8,
            f"Período: {fecha_desde.strftime('%m/%Y')} a {fecha_hasta.strftime('%m/%Y')}",
            ln=True
        )

        if len(bloques) > 1:
            pdf.cell(
                0, 8,
                f"Bloque: meses {i*6 + 1} a {i*6 + len(bloque)}",
                ln=True
            )

        pdf.ln(4)

        # ---------- ENCABEZADO DE TABLA ----------
        pdf.set_font("Helvetica", 'B', 9)
        pdf.set_fill_color(230, 230, 230)

        pdf.cell(ANCHO_EST, 8, "Pluviómetro", 1, 0, 'L', True)
        pdf.cell(ANCHO_DEP, 8, "Departamento", 1, 0, 'L', True)
        pdf.cell(ANCHO_PROV, 8, "Provincia", 1, 0, 'L', True)

        for mes in bloque:
            pdf.cell(ANCHO_MES, 8, mes.strftime("%m/%Y"), 1, 0, 'C', True)

        if i == len(bloques) - 1:
            pdf.cell(ANCHO_TOTAL, 8, "TOTAL", 1, 0, 'C', True)

        pdf.ln()

        # ---------- CUERPO DE TABLA ----------
        pdf.set_font("Helvetica", size=9)

        for idx, fila in pivot.iterrows():
            pdf.cell(ANCHO_EST, 8, idx[0], 1)
            pdf.cell(ANCHO_DEP, 8, idx[1], 1)
            pdf.cell(ANCHO_PROV, 8, idx[2], 1)

            for mes in bloque:
                valor = fila[mes]

                if pd.notna(valor) and valor >= 1:
                    texto = f"{valor:.1f}"
                else:
                    texto = ""

                pdf.cell(ANCHO_MES, 8, texto, 1, 0, 'C')

            if i == len(bloques) - 1:
                total = fila["TOTAL"]

                if pd.notna(total) and total >= 1:
                    texto_total = f"{total:.1f}"
                else:
                    texto_total = ""

                pdf.cell(ANCHO_TOTAL, 8, texto_total, 1, 0, 'C')

            pdf.ln()

    # =================================================
    # AVISO CELDAS EN BLANCO
    # =================================================
    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        0, 6,
        "Las celdas en blanco indican ausencia de registro de precipitación.\n"
        
    )
    
    
    # =================================================
    # PÁGINA FINAL – EQUIPO Y COLABORADORES
    # =================================================
    pdf.add_page()

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Equipo de trabajo - INTA:", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0, 7,
        "Lic. Inf. Hernán Elena (EEA Salta), "
        "Obs. Met. Germán Guanca (Meteorología - EEA Salta), "
        "Ing. Agr. Rafael Saldaño (OIT Coronel Moldes), "
        "Ing. Agr. Daniela Moneta (AER Valle de Lerma), "
        "Ing. Juan Ramón Rojas (AER Santa Victoria Este), "
        "Ing. Agr. Daniel Lamberti (AER Perico), "
        "Tec. Recursos Hídricos Fátima del Valle Miranda (AER Palma Sola), "
        "Ing. Agr. Florencia Diaz (AER Palma Sola), "
        "Ing. Agr. Héctor Diaz (AER J.V. Gonzalez), "
        "Ing. Agr. Carlos G. Cabrera (AER J.V. Gonzalez), "
        "Lucas Diaz (AER Cafayate - OIT San Carlos), "
        "Med. Vet. Cristina Rosetto (EECT Yuto), "
        "Ing. RRNN Fabian Tejerina (EEA Salta), "
        "Tec. Agr. Carlos Arias (OIT General Güemes)."
    )

    pdf.ln(4)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Colaboradores:", ln=True)

    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(
        0, 6,
        "Nicolás Uriburu, Nicolás Villegas, Matías Lanusse, Marcela López, Martín Amado, Agustín Sanz Navamuel, Luis Fernández Acevedo, Miguel A. Boasso, Luis Zavaleta, Mario Lambrisca, Noelia Rovedatti, Matías Canonica, Alejo Álvarez, Javier Montes, Guillermo Patrón Costa, Sebastián Mendilaharzu, Francisco Chehda, Jorge Robles, Gustavo Soricich, Javier Atea, Luis D. Elías, Leandro Carrizo, Daiana Núñez, Fátima González, Santiago Villalba, Juan Collado, Julio Collado, Estanislao Lara, Carlos Cruz, Daniel Espinoza, Fabián Álvarez, Lucio Señoranis, René Vallejos Rueda, Héctor Miranda, Emanuel Arias, Oscar Herrera, Francisca Vacaflor, Zaturnino Ceballos, Alcides Ceballos, Juan Ignacio Pearson, Pascual Erazo, Darío Romero, Luisa Andrada, Alejandro Ricalde, Odorico Romero, Lucas Campos, Sebastián Díaz, Carlos Sanz, Gabriel Brinder, Gastón Vizgarra, Diego Sulca, Alicia Tapia, Sergio Cassinelli, María Zamboni, Andrés Flores, Tomás Lienemann, Carmen Carattoni, Cecilia Carattoni, Tito Donoso, Javier Aprile, Carla Carattoni, Cuenca Renán, Luna Federico, Soloza Pedro, Aparicio Cirila, Torres Arnaldo, Torres Mergido, Sardina Rubén, Illesca Francisco, Saravia Adrián, Carabajal Jesús, Alvarado René, Saban Mary, Rodríguez Eleuterio, Guzmán Durbal, Sajama Sergio, Miranda Dina, Pedro Quispe, Fabiana Monasterio, Raquel Araoz, Raúl Álvarez, Rafael Mendoza, Lila Torfe, Samuel Aramayo, Jose Maidana, Hernan Terceros, Maria Sulca, Paulino Sulca, Nadia Ríos, Matías Copa, Marcos Aurelio Rodríguez, Horacio Hoyo, Alejandro Romero, Carlos Ruiz."
    )

    pdf.ln(4)
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 8, "Contacto:", ln=True)

    pdf.set_font("Helvetica", size=10)
    pdf.cell(
        0, 8,
        "Para más información, podés contactarnos en: elena.hernan@inta.gob.ar",
        ln=True
    )

    # =================================================
    # SALIDA ROBUSTA
    # =================================================
    data = pdf.output(dest="S")
    return bytes(data) if isinstance(data, (bytes, bytearray)) else data.encode("latin-1", errors="replace")



# ==============================================================
# KML DIARIO
# ==============================================================

@st.cache_data(show_spinner=False)
def generar_kml(df):
    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, "Document")

    for _, r in df.iterrows():
        pm = ET.SubElement(doc, "Placemark")
        ET.SubElement(pm, "name").text = str(r["Pluviómetro"])

        desc = ET.SubElement(pm, "description")
        desc.text = f"""
        <b>Pluviómetro:</b> {r['Pluviómetro']}<br>
        <b>Lluvia:</b> {r['mm']:.1f} mm<br>
        <b>Departamento:</b> {r['Departamento']}<br>
        <b>Provincia:</b> {r['Provincia']}
        """

        p = ET.SubElement(pm, "Point")
        ET.SubElement(p, "coordinates").text = f"{r['lon']},{r['lat']},0"

    return ET.tostring(kml, encoding="utf-8", xml_declaration=True)


@st.cache_data(show_spinner=False)
def exportar_excel(df_export):
    buffer = BytesIO()
    df_export.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()

# ==============================================================
# CARGA DE DATOS PRINCIPAL
# ==============================================================

df, df_estaciones, col_nombre_est = obtener_datos(
    solo_reciente=not st.session_state.cargar_todo
)

# ==============================================================
# SIDEBAR – NAVEGACIÓN Y AJUSTES GLOBALES
# ==============================================================

st.sidebar.markdown(
    """
    <div style="
        background-color:#1E3A8A;
        color:white;
        padding:12px 14px;
        border-radius:10px;
        margin-bottom:12px;
        font-size:18px;
        font-weight:700;
        text-align:center;
        box-shadow:0 2px 6px rgba(0,0,0,0.25);
    ">
        📊 Panel de Control
    </div>
    """,
    unsafe_allow_html=True
)

seccion = st.sidebar.radio(
    "📌 Navegación",
    [
        "📅 Monitor Diario",
        "📊 Acumulados Mensuales",
        "🏆 Récords y Extremos",
        "📈 Consulta Histórica",
        "📑 Reportes (PDF)",
        "🌧️ Red de Pluviómetros",
        "ℹ️ Información"
    ]
)

st.sidebar.markdown("---")

# MODO DE DATOS (RÁPIDO VS COMPLETO)
total_pluvios = df_estaciones.shape[0] if not df_estaciones.empty else 0
total_registros = df.shape[0] if not df.empty else 0

st.sidebar.markdown(f"**📡 Red de pluviómetros:** {total_pluvios} estaciones")
st.sidebar.markdown(f"**📋 Registros cargados:** {total_registros:,}".replace(",", "."))

if not st.session_state.cargar_todo:
    st.sidebar.caption("⚡ *Modo Rápido activo (últimos 60 días)*")
    if st.sidebar.button("📂 Cargar historial completo", use_container_width=True):
        st.session_state.cargar_todo = True
        st.cache_data.clear()
        st.rerun()
else:
    st.sidebar.caption("📂 *Historial completo activo (+5.000 registros)*")
    if st.sidebar.button("⚡ Volver a modo rápido", use_container_width=True):
        st.session_state.cargar_todo = False
        st.cache_data.clear()
        st.rerun()

st.sidebar.markdown("---")

if df.empty:
    st.error("No se pudieron cargar datos de precipitaciones. Verifique la conexión o credenciales.")
    st.stop()


# ==============================================================
# 1. MONITOR DIARIO (UNIFICA MAPA, TABLA Y RESUMEN)
# ==============================================================
if seccion == "📅 Monitor Diario":

    fecha_defecto = df["fecha"].max() if not df.empty else date.today()
    fecha_minima = df["fecha"].min() if not df.empty else date.today()

    col_f1, col_f2 = st.columns([0.4, 0.6])
    with col_f1:
        f_hoy = st.date_input(
            "📅 Seleccione fecha de consulta:",
            value=fecha_defecto,
            min_value=fecha_minima,
            max_value=fecha_defecto
        )

    df_dia = df[df["fecha"] == f_hoy].copy()
    reportados = df_dia["cod"].nunique()

    with col_f2:
        st.info(
            f"**Día pluviométrico:** Acumulado desde las 9:00 h del {f_hoy.strftime('%d/%m/%Y')} "
            f"a las 9:00 h del {(f_hoy + timedelta(days=1)).strftime('%d/%m/%Y')}.  \n"
            f"**Reportaron:** {reportados} de {total_pluvios} pluviómetros."
        )

    if df_dia.empty:
        st.warning(f"No hay registros de precipitación para la fecha {f_hoy.strftime('%d/%m/%Y')}.")
    else:
        tab_mapa, tab_resumen, tab_descargas = st.tabs([
            "🗺️ Mapa Interactivo",
            "📊 Resumen Regional y Tabla",
            "📥 Descargas del Día"
        ])

        with tab_mapa:
            df_dia_mapa = df_dia.dropna(subset=["lat", "lon"])
            if df_dia_mapa.empty:
                st.warning("No hay registros georreferenciados para graficar en el mapa.")
            else:
                centro = [df_dia_mapa["lat"].mean(), df_dia_mapa["lon"].mean()]
                m = folium.Map(location=centro, zoom_start=7, tiles=None)

                folium.TileLayer(
                    tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
                    attr="Google",
                    name="Google Satélite",
                    overlay=False,
                ).add_to(m)

                folium.TileLayer(
                    tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png",
                    attr="IGN",
                    name="Argenmap (IGN)",
                    overlay=False,
                ).add_to(m)

                legend_html = """
                <div style="
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    width: 130px;
                    background-color: rgba(255, 255, 255, 0.92);
                    border: 2px solid #111827;
                    z-index: 9999;
                    font-size: 12px;
                    padding: 8px;
                    border-radius: 6px;
                    font-family: sans-serif;
                    line-height: 1.4;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                    color: #111111;
                ">
                    <b>Referencia</b><br>
                    <span style="display:inline-block;width:10px;height:10px;background:#1a73e8;border-radius:50%;margin-right:6px;"></span>0–20 mm<br>
                    <span style="display:inline-block;width:10px;height:10px;background:#ef6c00;border-radius:50%;margin-right:6px;"></span>20–50 mm<br>
                    <span style="display:inline-block;width:10px;height:10px;background:#d32f2f;border-radius:50%;margin-right:6px;"></span>+50 mm
                </div>
                """
                m.get_root().html.add_child(folium.Element(legend_html))
                LocateControl(auto_start=False, flyTo=True).add_to(m)
                folium.LayerControl(position="bottomright").add_to(m)

                for _, r in df_dia_mapa.iterrows():
                    val_mm = r["mm"]
                    if val_mm > 50:
                        c_hex, c_fol = "#d32f2f", "red"
                    elif val_mm > 20:
                        c_hex, c_fol = "#ef6c00", "orange"
                    else:
                        c_hex, c_fol = "#1a73e8", "blue"

                    fen = str(r.get("fen_raw", "")).lower()
                    icon_code = "cloud"
                    if "granizo" in fen:
                        icon_code = "asterisk"
                    elif "tormenta" in fen:
                        icon_code = "flash"
                    elif "viento" in fen:
                        icon_code = "leaf"

                    popup_html = f"""
                    <div style="font-family:sans-serif;min-width:180px;">
                        <div style="margin:0;color:{c_hex};border-bottom:2px solid {c_hex};font-size:15px;font-weight:bold;padding-bottom:4px;margin-bottom:6px;">
                            {r['Pluviómetro']}
                        </div>
                        <div style="font-size:14px;"><b>Lluvia:</b> {val_mm:.1f} mm</div>
                        <div style="font-size:13px;margin-top:3px;"><b>Fenómeno:</b> {r.get('Fenómeno atmosférico', 'S/D')}</div>
                        <div style="font-size:12px;color:#444;border-top:1px solid #eee;padding-top:4px;margin-top:6px;">
                            <b>{r['Departamento']}, {r['Provincia']}</b>
                        </div>
                    </div>
                    """

                    folium.map.Marker(
                        [r["lat"], r["lon"]],
                        icon=folium.DivIcon(
                            icon_size=(40, 20),
                            icon_anchor=(20, -10),
                            html=f"""
                            <div style="color:{c_hex};font-weight:900;font-size:11pt;text-shadow:1px 1px 0 #fff;">
                                {int(round(val_mm))}
                            </div>
                            """
                        )
                    ).add_to(m)

                    folium.Marker(
                        [r["lat"], r["lon"]],
                        popup=folium.Popup(popup_html, max_width=260),
                        icon=folium.Icon(color=c_fol, icon=icon_code),
                    ).add_to(m)

                st_folium(m, width="100%", height=580, key="mapa_diario", returned_objects=[])

        with tab_resumen:
            st.markdown("#### 📌 Resumen por Región")
            resumen_reg = (
                df_dia.groupby("Region")["mm"]
                .agg(["mean", "max", "count"])
                .sort_values("mean", ascending=False)
                .reset_index()
            )

            filas_reg = [resumen_reg[i:i+3] for i in range(0, len(resumen_reg), 3)]
            for fila_r in filas_reg:
                cols_r = st.columns(3)
                for idx, (_, reg) in enumerate(fila_r.iterrows()):
                    with cols_r[idx]:
                        st.metric(
                            label=f"Región: {reg['Region']}",
                            value=f"{reg['mean']:.1f} mm prom.",
                            delta=f"Máx: {reg['max']:.1f} mm ({int(reg['count'])} pluviómetros)"
                        )

            st.markdown("---")
            st.markdown("#### 📋 Detalle de Registros del Día")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                provincias_dia = ["Todas"] + sorted(df_dia["Provincia"].dropna().unique().tolist())
                sel_prov_dia = st.selectbox("Filtrar por Provincia:", provincias_dia)
            with col_b2:
                if sel_prov_dia != "Todas":
                    deptos_disp = ["Todos"] + sorted(df_dia[df_dia["Provincia"] == sel_prov_dia]["Departamento"].dropna().unique().tolist())
                else:
                    deptos_disp = ["Todos"] + sorted(df_dia["Departamento"].dropna().unique().tolist())
                sel_depto_dia = st.selectbox("Filtrar por Departamento:", deptos_disp)

            df_dia_tabla = df_dia.copy()
            if sel_prov_dia != "Todas":
                df_dia_tabla = df_dia_tabla[df_dia_tabla["Provincia"] == sel_prov_dia]
            if sel_depto_dia != "Todos":
                df_dia_tabla = df_dia_tabla[df_dia_tabla["Departamento"] == sel_depto_dia]

            df_dia_mostrar = (
                df_dia_tabla[[
                    "Pluviómetro",
                    "Region",
                    "Departamento",
                    "Provincia",
                    "mm",
                    "Fenómeno atmosférico"
                ]]
                .sort_values("mm", ascending=False)
                .rename(columns={"mm": "Lluvia (mm)"})
            )

            st.dataframe(
                df_dia_mostrar,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Lluvia (mm)": st.column_config.NumberColumn(format="%.1f mm")
                }
            )

        with tab_descargas:
            st.markdown("#### 📥 Descargas Oficiales del Día")
            st.write("Exporte el reporte oficial en formato PDF institucional o el archivo geográfico KML para Google Earth.")

            col_d1, col_d2 = st.columns(2)
            with col_d1:
                pdf_dia_bytes = crear_pdf(df_dia, f_hoy, total_pluvios)
                st.download_button(
                    label="📄 Descargar Reporte Diario (PDF)",
                    data=pdf_dia_bytes,
                    file_name=f"reporte_diario_{f_hoy}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            with col_d2:
                kml_dia_bytes = generar_kml(df_dia.dropna(subset=["lat", "lon"]))
                st.download_button(
                    label="📍 Descargar KML del Día (Google Earth)",
                    data=kml_dia_bytes,
                    file_name=f"lluvia_{f_hoy}.kml",
                    mime="application/vnd.google-earth.kml+xml",
                    use_container_width=True
                )


# ------------------------- MES -------------------------

# ------------------------- MES -------------------------
# ==============================================================
# 2. ACUMULADOS MENSUALES
# ==============================================================
elif seccion == "📊 Acumulados Mensuales":

    st.subheader("📊 Acumulados Mensuales por Pluviómetro")

    if not st.session_state.cargar_todo:
        st.warning(
            "⚠️ Mostrando actualmente los últimos 60 días. "
            "Para consultar el año completo o meses anteriores, active **«Cargar historial completo»** en el panel lateral."
        )

    df_mes = df.copy()
    df_mes["Año"] = df_mes["fecha_dt"].dt.year
    df_mes["Mes_Num"] = df_mes["fecha_dt"].dt.month

    meses_n = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    anios_disponibles = sorted(df_mes["Año"].unique(), reverse=True)
    sel_anio = st.selectbox("Seleccione Año:", anios_disponibles)

    df_anio = df_mes[df_mes["Año"] == sel_anio].copy()

    if df_anio.empty:
        st.warning("No hay datos para el año seleccionado.")
    else:
        tabla = (
            df_anio
            .pivot_table(
                index=["Pluviómetro", "Departamento", "Provincia"],
                columns="Mes_Num",
                values="mm",
                aggfunc="sum"
            )
            .fillna(0.0)
        )

        tabla.columns = [meses_n[c] for c in tabla.columns]
        tabla["TOTAL"] = tabla.sum(axis=1)

        tabla_mostrar = tabla.sort_index(level=0).round(1)

        st.dataframe(
            tabla_mostrar,
            use_container_width=True,
            column_config={
                c: st.column_config.NumberColumn(format="%.1f") for c in tabla_mostrar.columns
            }
        )
        st.caption("Valores expresados en milímetros (mm). Celdas en 0 indican ausencia de registro en ese período.")

        st.markdown("---")
        st.markdown("#### 📄 Reporte Mensual Completo (PDF)")

        pdf_mensual = crear_pdf_mensual_region(
            df_anio,
            region=f"Todas las regiones - Año {sel_anio}",
            fecha_desde=df_anio["fecha_dt"].min().date(),
            fecha_hasta=df_anio["fecha_dt"].max().date()
        )

        st.download_button(
            label=f"📥 Descargar Reporte Mensual {sel_anio} (PDF)",
            data=pdf_mensual,
            file_name=f"reporte_mensual_{sel_anio}.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ==============================================================
# 3. RÉCORDS Y EXTREMOS MENSUALES
# ==============================================================
elif seccion == "🏆 Récords y Extremos":

    st.subheader("🏆 Máxima precipitación diaria registrada en el mes")

    col1, col2 = st.columns(2)
    with col1:
        anios = sorted(df["fecha_dt"].dt.year.unique(), reverse=True)
        sel_anio = st.selectbox("Año:", anios)

    meses_n = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }

    with col2:
        meses_disp = sorted(
            df[df["fecha_dt"].dt.year == sel_anio]["fecha_dt"].dt.month.unique()
        )
        sel_mes = st.selectbox(
            "Mes:",
            meses_disp,
            format_func=lambda x: meses_n[x]
        )

    df_mes_ext = df[
        (df["fecha_dt"].dt.year == sel_anio) &
        (df["fecha_dt"].dt.month == sel_mes) &
        (df["mm"] >= 1.0)
    ].copy()

    if df_mes_ext.empty:
        st.warning("No hay registros válidos de precipitación (≥ 1 mm) para el mes seleccionado.")
    else:
        max_reg = df_mes_ext.loc[df_mes_ext["mm"].idxmax()]

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(
                "Récord del mes",
                f"{max_reg['mm']:.1f} mm",
                f"{max_reg['Pluviómetro']}"
            )
        with m2:
            st.metric(
                "Fecha del récord",
                max_reg["fecha_dt"].strftime("%d/%m/%Y"),
                f"{max_reg['Departamento']}"
            )
        with m3:
            st.metric(
                "Estaciones con lluvia ≥ 1mm",
                f"{df_mes_ext['Pluviómetro'].nunique()} estaciones"
            )

        st.markdown("---")
        st.markdown("#### 📋 Mayor precipitación individual por pluviómetro")

        idx_max = df_mes_ext.groupby("Pluviómetro")["mm"].idxmax()
        df_max = df_mes_ext.loc[idx_max].copy()

        df_max["Año"] = sel_anio
        df_max["Mes"] = meses_n[sel_mes]
        df_max["Fecha"] = df_max["fecha_dt"].dt.strftime("%d/%m/%Y")

        tabla_max = df_max[[
            "Año",
            "Mes",
            "Pluviómetro",
            "Provincia",
            "Departamento",
            "mm",
            "Fecha"
        ]].rename(columns={
            "mm": "Máxima (mm)"
        }).sort_values("Máxima (mm)", ascending=False)

        st.dataframe(
            tabla_max,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Máxima (mm)": st.column_config.NumberColumn(format="%.1f mm")
            }
        )

        st.caption(
            "Se muestra, para cada pluviómetro, el evento de mayor precipitación registrado "
            "durante el mes seleccionado y la fecha exacta en que ocurrió."
        )


# ==============================================================
# 4. CONSULTA HISTÓRICA (OPTIMIZADA)
# ==============================================================
elif seccion == "📈 Consulta Histórica":

    st.subheader("📈 Consulta Histórica de Precipitaciones")

    col_f_izq, col_f_der = st.columns([0.65, 0.35])

    with col_f_izq:
        provincias_hist = ["Todas"] + sorted(df["Provincia"].dropna().unique().tolist())
        sel_prov_hist = st.selectbox("Filtrar lista de pluviómetros por provincia:", provincias_hist)

        if sel_prov_hist != "Todas":
            estaciones_disp = sorted(df[df["Provincia"] == sel_prov_hist]["Pluviómetro"].unique())
        else:
            estaciones_disp = sorted(df["Pluviómetro"].unique())

        sel_est = st.multiselect(
            "Seleccione Pluviómetro(s):",
            estaciones_disp,
            placeholder="Escriba o elija una o más estaciones..."
        )

    with col_f_der:
        f_desde = st.date_input("Fecha Desde:", df["fecha"].min())
        f_hasta = st.date_input("Fecha Hasta:", df["fecha"].max())
        modo = st.radio("Agrupación:", ["Diario", "Mensual"], horizontal=True)

    if not sel_est:
        st.info("💡 Seleccione uno o más pluviómetros en el desplegable superior para ver los registros.")
        st.stop()

    df_filt = df[
        (df["Pluviómetro"].isin(sel_est)) &
        (df["fecha"] >= f_desde) &
        (df["fecha"] <= f_hasta) &
        (df["mm"] >= 1.0)
    ].copy()

    if df_filt.empty:
        st.warning("No se encontraron registros de precipitación (≥ 1 mm) para los filtros seleccionados.")
        st.stop()

    if modo == "Diario":
        tabla_hist = (
            df_filt[
                [
                    "fecha_dt",
                    "Pluviómetro",
                    "Departamento",
                    "Provincia",
                    "mm",
                    "Fenómeno atmosférico"
                ]
            ]
            .rename(columns={
                "fecha_dt": "Fecha",
                "mm": "Lluvia (mm)"
            })
            .sort_values("Fecha", ascending=False)
        )
        tabla_hist["Fecha"] = tabla_hist["Fecha"].dt.strftime("%d/%m/%Y")

        st.dataframe(
            tabla_hist,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Lluvia (mm)": st.column_config.NumberColumn(format="%.1f mm")
            }
        )
    else:
        df_filt["Año"] = df_filt["fecha_dt"].dt.year
        df_filt["Mes_Num"] = df_filt["fecha_dt"].dt.month

        meses = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }

        tabla_hist = (
            df_filt
            .groupby(["Año", "Mes_Num", "Pluviómetro", "Departamento", "Provincia"])["mm"]
            .sum()
            .reset_index()
        )
        tabla_hist["Mes"] = tabla_hist["Mes_Num"].map(meses)
        tabla_hist = (
            tabla_hist[["Año", "Mes", "Pluviómetro", "Departamento", "Provincia", "mm"]]
            .rename(columns={"mm": "Lluvia acumulada (mm)"})
            .sort_values(["Pluviómetro", "Año", "Mes"])
        )

        st.dataframe(
            tabla_hist,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Lluvia acumulada (mm)": st.column_config.NumberColumn(format="%.1f mm")
            }
        )

    st.markdown("---")
    st.markdown("#### 📥 Exportar Resultados")
    col_csv, col_xls = st.columns(2)

    with col_csv:
        st.download_button(
            "⬇️ Descargar CSV",
            tabla_hist.to_csv(index=False).encode("utf-8"),
            file_name="historico_precipitaciones.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_xls:
        excel_bytes = exportar_excel(tabla_hist)
        st.download_button(
            "⬇️ Descargar Excel (.xlsx)",
            excel_bytes,
            file_name="historico_precipitaciones.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ==============================================================
# 5. GENERADOR DE REPORTES (PDF)
# ==============================================================
elif seccion == "📑 Reportes (PDF)":

    st.subheader("📑 Reporte Mensual Formal por Provincia / Departamento")

    provincia = st.selectbox(
        "Provincia:",
        sorted(df["Provincia"].dropna().unique())
    )

    deptos_prov = sorted(
        df[df["Provincia"] == provincia]["Departamento"].dropna().unique()
    )
    opciones_deptos = ["Todos los departamentos"] + deptos_prov

    departamentos_sel = st.multiselect(
        "Departamento(s):",
        opciones_deptos,
        default=["Todos los departamentos"],
        help="Puede seleccionar uno, varios o todos los departamentos de la provincia."
    )

    col1, col2 = st.columns(2)
    with col1:
        f_desde = st.date_input("Desde:", df["fecha"].min())
    with col2:
        f_hasta = st.date_input("Hasta:", df["fecha"].max())

    if not st.session_state.cargar_todo:
        st.info(
            "ℹ️ Para generar reportes que abarquen períodos mayores a 60 días, "
            "es necesario activar previamente **«Cargar historial completo»** desde el panel lateral."
        )

    if st.button("📄 Generar reporte PDF", use_container_width=True):
        fecha_ini = pd.to_datetime(f_desde).replace(day=1)
        fecha_fin = pd.to_datetime(f_hasta).replace(day=1) + pd.offsets.MonthEnd(1)

        df_r = df[
            (df["Provincia"] == provincia) &
            (df["fecha_dt"] >= fecha_ini) &
            (df["fecha_dt"] <= fecha_fin)
        ].copy()

        if "Todos los departamentos" in departamentos_sel:
            titulo_deptos = "Todos los departamentos"
        else:
            titulo_deptos = ", ".join(departamentos_sel)
            df_r = df_r[df_r["Departamento"].isin(departamentos_sel)]

        if df_r.empty:
            st.warning("No hay datos para el período y territorio seleccionados.")
        else:
            descripcion_reporte = f"Provincia: {provincia} - Departamentos: {titulo_deptos}"
            pdf_m = crear_pdf_mensual_region(
                df_r,
                region=descripcion_reporte,
                fecha_desde=fecha_ini.date(),
                fecha_hasta=fecha_fin.date()
            )

            st.download_button(
                "📥 Descargar PDF Mensual Generado",
                pdf_m,
                file_name="reporte_mensual_provincia_departamentos.pdf",
                mime="application/pdf",
                use_container_width=True
            )


# ==============================================================
# 6. RED COMPLETA DE PLUVIÓMETROS
# ==============================================================
elif seccion == "🌧️ Red de Pluviómetros":

    st.subheader("🌧️ Directorio y Mapa de la Red Pluviométrica")
    st.info("Ubicación geográfica de todos los pluviómetros registrados en el sistema del INTA.")

    df_red = df_estaciones.dropna(subset=["lat", "lon"]).copy()

    if col_nombre_est and col_nombre_est in df_red.columns:
        df_red["Pluviómetro"] = df_red[col_nombre_est].fillna(df_red["cod"])
    else:
        df_red["Pluviómetro"] = df_red.get("cod", "S/D")

    col_depto_base = next((c for c in df_red.columns if "depto" in c.lower() or "depart" in c.lower()), None)
    col_prov_base = next((c for c in df_red.columns if "prov" in c.lower()), None)

    opciones = ["Ver todos"] + sorted(df_red["Pluviómetro"].dropna().unique().tolist())
    seleccion = st.selectbox("🔍 Buscar un pluviómetro específico:", opciones, index=0)

    if seleccion == "Ver todos":
        df_mostrar = df_red
        zoom_init = 7
    else:
        df_mostrar = df_red[df_red["Pluviómetro"] == seleccion]
        zoom_init = 12

    if df_mostrar.empty:
        st.warning("No hay estaciones con coordenadas para mostrar.")
    else:
        centro = [df_mostrar["lat"].mean(), df_mostrar["lon"].mean()]
        m_red = folium.Map(location=centro, zoom_start=zoom_init, tiles=None)

        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google",
            name="Google Satélite",
            overlay=False
        ).add_to(m_red)

        folium.TileLayer(
            tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png",
            attr="IGN",
            name="Argenmap (IGN)",
            overlay=False
        ).add_to(m_red)

        pluvios = folium.FeatureGroup(name="Pluviómetros", overlay=False, control=False)
        cluster = MarkerCluster().add_to(pluvios)
        m_red.add_child(pluvios)

        for _, r in df_mostrar.iterrows():
            depto_val = r[col_depto_base] if col_depto_base and pd.notna(r.get(col_depto_base)) else "S/D"
            prov_val = r[col_prov_base] if col_prov_base and pd.notna(r.get(col_prov_base)) else "S/D"

            popup_html = f"""
            <div style="font-family: sans-serif; min-width: 180px;">
                <div style="font-weight:700; margin-bottom:6px; color:#1E3A8A; font-size:14px;">{r['Pluviómetro']}</div>
                <div style="font-size:13px; color:#333;">
                    <b>Depto:</b> {depto_val}<br>
                    <b>Provincia:</b> {prov_val}
                </div>
            </div>
            """

            folium.CircleMarker(
                location=[r["lat"], r["lon"]],
                radius=8,
                color="#1E3A8A",
                fill=True,
                fill_color="#3B82F6",
                fill_opacity=0.9,
                tooltip=str(r["Pluviómetro"]),
                popup=folium.Popup(popup_html, max_width=260)
            ).add_to(cluster)

        LocateControl(auto_start=False, flyTo=True).add_to(m_red)
        folium.LayerControl(position="bottomright").add_to(m_red)

        st.markdown(
            '<div style="box-shadow:0 0 0 2px #000;border-radius:8px;margin:10px 2px;line-height:0;">',
            unsafe_allow_html=True
        )
        st_folium(m_red, width="100%", height=600, key="mapa_red", returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================
# 7. INFORMACIÓN INSTITUCIONAL
# ==============================================================
elif seccion == "ℹ️ Información":
    st.subheader("ℹ️ Información Institucional y Créditos")
    st.markdown(INFO_MD, unsafe_allow_html=True)
