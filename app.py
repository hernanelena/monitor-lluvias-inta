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
   RESALTAR DATE INPUT SIDEBAR
   ============================== */

/* Contenedor completo del input de fecha */
section[data-testid="stSidebar"] div:has(input[type="date"]),
section[data-testid="stSidebar"] div:has(input[aria-haspopup="dialog"]) {
    background-color: #DBEAFE !important;
    border-radius: 10px !important;
    padding: 6px 8px !important;
    border: 2px solid #1E3A8A !important;
    margin-bottom: 8px !important;
}

/* Input interno */
section[data-testid="stSidebar"] input {
    font-weight: 600 !important;
    color: #1E3A8A !important;
    text-align: center !important;
    background-color: white !important;
}

/* Label */
section[data-testid="stSidebar"] label {
    font-weight: 600 !important;
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
logo_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Logo_INTA.svg/1200px-Logo_INTA.svg.png"

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

def extraer_coordenadas(row):
    try:
        v = row.get("Ubicaci_in") or row.get("ubicaci_in") or row.get("_Ubicaci_in")
        if isinstance(v, str):
            p = v.split()
            return float(p[0]), float(p[1])
        if isinstance(v, list):
            return float(v[0]), float(v[1])
    except:
        pass
    return None, None

@st.cache_data(ttl=1800)
def cargar_datos(solo_reciente=True):
    r1 = requests.get(URL_PRECIPITACIONES, headers=HEADERS)
    r2 = requests.get(URL_MAPA, headers=HEADERS)

    df_p = pd.DataFrame(r1.json())
    df_c = pd.DataFrame(r2.json())

    df_p["fecha_dt"] = pd.to_datetime(df_p["Fecha_del_dato"])
    if solo_reciente:
        corte = pd.Timestamp.now() - pd.Timedelta(days=60)
        df_p = df_p[df_p["fecha_dt"] >= corte]

    df_p["fecha"] = df_p["fecha_dt"].dt.date
    df_p["mm"] = pd.to_numeric(df_p["Mil_metros_registrados"], errors="coerce").fillna(0)
    df_p["fen_raw"] = df_p["fenomeno"].astype(str).str.lower()
    
    # =================================================
# NORMALIZACIÓN DE FENÓMENOS ATMOSFÉRICOS
# =================================================
    df_p["fen_raw"] = (
        df_p["fenomeno"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    map_fen = {
        "viento": "Vientos fuertes",
        "granizo": "Granizo",
        "tormenta": "Tormentas eléctricas",
        "sinfeno": "Sin obs. de fenómenos"
    }

    df_p["Fenómeno atmosférico"] = (
        df_p["fen_raw"]
        .replace(map_fen)
        .replace({
            "none": "Sin obs. de fenómenos",
            "nan": "Sin obs. de fenómenos",
            "": "Sin obs. de fenómenos"
        })
    )
        
    

    df_p["cod"] = df_p["Pluviometros"].astype(str).str.replace(".0", "", regex=False)
    df_c["cod"] = df_c["Codigo_txt_del_pluviometro"].astype(str).str.replace(".0", "", regex=False)

    res = df_c.apply(extraer_coordenadas, axis=1)
    df_c["lat"], df_c["lon"] = zip(*res)

    col_n = next((c for c in df_c.columns if "Nombre_del_Pluviometro" in c), "cod")
    col_depto = next((c for c in df_c.columns if "depto" in c.lower()), None)
    col_prov = next((c for c in df_c.columns if "prov" in c.lower()), None)
    col_region = next((c for c in df_c.columns if "reg" in c.lower()), None)

    columnas = ["cod", "lat", "lon", col_n, col_depto, col_prov, col_region]
    columnas = [c for c in columnas if c]

    df = df_p.merge(df_c[columnas], on="cod", how="left")
    df["Pluviómetro"] = df[col_n]
    df["Departamento"] = df[col_depto].fillna("S/D") if col_depto else "S/D"
    df["Provincia"] = df[col_prov].fillna("S/D") if col_prov else "S/D"
    df["Region"] = df[col_region].fillna("General") if col_region else "General"

    return df, df_c, col_n

# ==============================================================
# PDF DIARIO
# ==============================================================

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

def generar_kml(df):
    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, "Document")

    for _, r in df.iterrows():
        pm = ET.SubElement(doc, "Placemark")
        ET.SubElement(pm, "name").text = r["Pluviómetro"]

        desc = ET.SubElement(pm, "description")
        desc.text = f"""
        <b>Pluviómetro:</b> {r['Pluviómetro']}<br>
        <b>Lluvia:</b> {r['mm']} mm<br>
        <b>Departamento:</b> {r['Departamento']}<br>
        <b>Provincia:</b> {r['Provincia']}
        """

        p = ET.SubElement(pm, "Point")
        ET.SubElement(p, "coordinates").text = f"{r['lon']},{r['lat']},0"

    return ET.tostring(kml, encoding="utf-8", xml_declaration=True)

# ==============================================================
# SIDEBAR – NAVEGACIÓN
# ==============================================================

st.sidebar.markdown(
    """
    <div style="
        background-color:#1E3A8A;
        color:white;
        padding:12px 14px;
        border-radius:10px;
        margin-bottom:12px;
        font-size:20px;
        font-weight:700;
        text-align:center;
        box-shadow:0 2px 6px rgba(0,0,0,0.25);
    ">
        📊 Panel de control
    </div>
    """,
    unsafe_allow_html=True
)

seccion = st.sidebar.radio(
    "📌 Navegación",
    [
        "🗺️ Mapa",
        "📊 Día",
        "📅 Mes",
        "🏆 Máx / Mín",
        "📈 Histórico",
        "📑 Reportes",        
        "🌧️ Red",
        "ℹ️ Info"
    ]
)

st.sidebar.markdown("---")

# ==============================================================
# CARGA DE DATOS
# ==============================================================

df, df_estaciones, col_nombre_est = cargar_datos(
    solo_reciente=not st.session_state.cargar_todo
)

# ==============================================================
# CONTROLES GLOBALES
# ==============================================================

f_hoy = st.sidebar.date_input(
    "Seleccione fecha de consulta:",
    value=df["fecha"].max()
)

# =====================================================
# PLUVIÓMETROS REPORTADOS (SIDEBAR)
# =====================================================
# Total de pluviómetros de la red
total_pluvios = df_estaciones.shape[0]

# Pluviómetros con registro en la fecha seleccionada
reportados = (
    df[df["fecha"] == f_hoy]["cod"]
    .nunique()
)

st.sidebar.markdown(
    f"**Pluviómetros reportados:** {reportados} / {total_pluvios}"
)

if not st.session_state.cargar_todo:
    if st.sidebar.button("📂 Cargar historial completo"):
        st.session_state.cargar_todo = True
        st.cache_data.clear()
        st.rerun()
else:
    if st.sidebar.button("⚡ Volver a modo rápido"):
        st.session_state.cargar_todo = False
        st.cache_data.clear()
        st.rerun()

# ==============================================================
# SECCIONES PRINCIPALES
# ==============================================================

# ------------------------- MAPA DIARIO -------------------------
# ------------------------- MAPA DIARIO -------------------------
if seccion == "🗺️ Mapa":
    st.subheader(f"🗺️ Lluvia del {f_hoy.strftime('%d/%m/%Y')}")
    st.info(
        f"Lluvia acumulada desde las 9 hs del "
        f"{f_hoy.strftime('%d/%m/%Y')} a las 9 hs del día "
        f"{(f_hoy + timedelta(days=1)).strftime('%d/%m/%Y')} "
        f"- Día pluviométrico"
    )

    df_dia = df[df["fecha"] == f_hoy].dropna(subset=["lat", "lon"])

    if df_dia.empty:
        st.warning("No hay datos para la fecha seleccionada.")
    else:
        centro = [df_dia["lat"].mean(), df_dia["lon"].mean()]

        m = folium.Map(location=centro, zoom_start=7, tiles=None)

        # === CAPAS BASE ===
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attr="Google",
            name="Google Satélite",
            overlay=False,
        ).add_to(m)

        folium.TileLayer(
            tiles="https://wms.ign.gob.ar/geoserver/gwc/service/tms/"
                  "1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png",
            attr="IGN",
            name="Argenmap (IGN)",
            overlay=False,
        ).add_to(m)

        # === LEYENDA ===
        legend_html = """
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            width: 130px;
            background-color: rgba(255, 255, 255, 0.9);
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
            <span style="display:inline-block;width:10px;height:10px;
                background:#1a73e8;border-radius:50%;margin-right:6px;"></span>
            0–20 mm<br>
            <span style="display:inline-block;width:10px;height:10px;
                background:#ef6c00;border-radius:50%;margin-right:6px;"></span>
            20–50 mm<br>
            <span style="display:inline-block;width:10px;height:10px;
                background:#d32f2f;border-radius:50%;margin-right:6px;"></span>
            +50 mm
        </div>
        """
        
        
        
        m.get_root().html.add_child(folium.Element(legend_html))

        LocateControl(auto_start=False, flyTo=True).add_to(m)
        folium.LayerControl(position="bottomright").add_to(m)

        # === PUNTOS ===
        for _, r in df_dia.iterrows():

            # Color según lluvia
            if r["mm"] > 50:
                c_hex = "#d32f2f"
                c_fol = "red"
            elif r["mm"] > 20:
                c_hex = "#ef6c00"
                c_fol = "orange"
            else:
                c_hex = "#1a73e8"
                c_fol = "blue"

            # Ícono según fenómeno
            icon_code = "cloud"
            if "granizo" in r["fen_raw"]:
                icon_code = "asterisk"
            elif "tormenta" in r["fen_raw"]:
                icon_code = "flash"
            elif "viento" in r["fen_raw"]:
                icon_code = "leaf"

            popup_html = f"""
            <div style="font-family:sans-serif;min-width:180px;">
                <div style="
                    margin:0;
                    color:{c_hex};
                    border-bottom:2px solid {c_hex};
                    font-size:16px;
                    font-weight:bold;
                    padding-bottom:5px;
                    margin-bottom:8px;">
                    {r['Pluviómetro']}
                </div>
                <div style="font-size:14px;">
                    <b>Lluvia:</b> {r['mm']} mm
                </div>
                <div style="font-size:13px;margin-top:4px;">
                    <b>Fenómeno:</b> {r.get('Fenómeno atmosférico', 'S/D')}
                </div>
                <div style="
                    font-size:12px;
                    color:#333;
                    border-top:1px solid #eee;
                    padding-top:5px;
                    margin-top:6px;">
                    <b>{r['Departamento']}, {r['Provincia']}</b>
                </div>
            </div>
            """

            # Número grande (mm)
            folium.map.Marker(
                [r["lat"], r["lon"]],
                icon=folium.DivIcon(
                    icon_size=(40, 20),
                    icon_anchor=(20, -10),
                    html=f"""
                    <div style="
                        color:{c_hex};
                        font-weight:900;
                        font-size:11pt;
                        text-shadow:1px 1px 0 #fff;">
                        {int(r['mm'])}
                    </div>
                    """
                )
            ).add_to(m)

            # Marcador principal
            folium.Marker(
                [r["lat"], r["lon"]],
                popup=folium.Popup(popup_html, max_width=260),
                icon=folium.Icon(color=c_fol, icon=icon_code),
            ).add_to(m)

        st_folium(m, width="100%", height=560)


# ------------------------- DÍA -------------------------
# ------------------------- DÍA -------------------------
elif seccion == "📊 Día":

    st.subheader(f"📊 Resumen del {f_hoy.strftime('%d/%m/%Y')}")

    df_dia = df[df["fecha"] == f_hoy]

    if df_dia.empty:
        st.warning("No hay datos para la fecha seleccionada.")
    else:
        # =================================================
        # RESUMEN POR REGIÓN (máx / prom / cantidad)
        # =================================================
        resumen_reg = (
            df_dia
            .groupby("Region")["mm"]
            .agg(["mean", "max", "count"])
            .sort_values("mean", ascending=False)
            .reset_index()
        )

        st.markdown("### 📌 Resumen por Región")

        filas = [resumen_reg[i:i+3] for i in range(0, len(resumen_reg), 3)]

        for fila in filas:
            cols = st.columns(3)
            for i, (_, r) in enumerate(fila.iterrows()):
                with cols[i]:
                    st.metric(
                        label=f"Región: {r['Region']}",
                        value=f"{r['mean']:.1f} mm prom.",
                        delta=f"Máx: {r['max']} mm ({int(r['count'])} pluviómetros)"
                    )

        # =================================================
        # TABLA DETALLADA DEL DÍA
        # =================================================
        st.markdown("---")
        st.markdown("### 📋 Detalle de Registros")

        st.dataframe(
            df_dia[
                [
                    "Pluviómetro",
                    "Region",
                    "Departamento",
                    "Provincia",
                    "mm",
                    "Fenómeno atmosférico"
                ]
            ]
            .sort_values("mm", ascending=False)
            .rename(columns={"mm": "Lluvia (mm)"}),
            use_container_width=True,
            hide_index=True
        )

        # =================================================
        # DESCARGAS DEL DÍA
        # =================================================
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            pdf_dia = crear_pdf(df_dia, f_hoy, df_estaciones.shape[0])
            st.download_button(
                "📥 Descargar PDF diario",
                pdf_dia,
                file_name=f"reporte_diario_{f_hoy}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with col2:
            kml_dia = generar_kml(df_dia.dropna(subset=["lat", "lon"]))
            st.download_button(
                "📍 Descargar KML del día",
                kml_dia,
                file_name=f"lluvia_{f_hoy}.kml",
                mime="application/vnd.google-earth.kml+xml",
                use_container_width=True
            )


# ------------------------- MES -------------------------

# ------------------------- MES -------------------------
elif seccion == "📅 Mes":

    st.subheader("📅 Acumulados Mensuales")

    if not st.session_state.cargar_todo:
        st.warning(
            "⚠️ Mostrando últimos 60 días. "
            "Para meses/años anteriores, active «Cargar Historial Completo» en el panel lateral."
        )

    # =================================================
    # PREPARACIÓN DE DATOS
    # =================================================
    df_mes = df.copy()
    df_mes["Año"] = df_mes["fecha_dt"].dt.year
    df_mes["Mes_Num"] = df_mes["fecha_dt"].dt.month

    meses_n = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    # =================================================
    # SELECTOR DE AÑO
    # =================================================
    anios_disponibles = sorted(df_mes["Año"].unique(), reverse=True)
    sel_anio = st.selectbox("Año:", anios_disponibles)

    df_anio = df_mes[df_mes["Año"] == sel_anio].copy()

    if df_anio.empty:
        st.warning("No hay datos para el año seleccionado.")
    else:
        # =================================================
        # TABLA PIVOTE
        # =================================================
        tabla = (
            df_anio
            .pivot_table(
                index=["Pluviómetro", "Departamento", "Provincia"],
                columns="Mes_Num",
                values="mm",
                aggfunc="sum"
            )
            .fillna(0)
        )

        # Renombrar columnas de meses
        tabla.columns = [meses_n[c] for c in tabla.columns]

        # Total anual
        tabla["TOTAL"] = tabla.sum(axis=1)

        # Ordenar por Pluviómetro (alfabético)
        st.dataframe(
            tabla
            .sort_index(level=0)
            .style
            .format(
                lambda x: f"{x:.1f}" if pd.notna(x) and x >= 1 else ""
            ),
            use_container_width=True
        )
        st.caption(
            "Las celdas vacías indican ausencia de registro. "
            "Solo se muestran valores con datos válidos de precipitación."
        )

        # =================================================
        # PDF MENSUAL (MISMO FORMATO INSTITUCIONAL)
        # =================================================
        st.markdown("---")
        st.subheader("📄 Reporte mensual (PDF)")

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


# ------------------------- MAX / MIN -------------------------


# ------------------------- MÁXIMO MENSUAL POR PLUVIÓMETRO -------------------------
elif seccion == "🏆 Máx / Mín":

    st.subheader("🏆 Máxima precipitación mensual por pluviómetro")

    # ============================
    # SELECTORES
    # ============================
    col1, col2 = st.columns(2)

    with col1:
        anios = sorted(df["fecha_dt"].dt.year.unique(), reverse=True)
        sel_anio = st.selectbox("Año:", anios)

    with col2:
        meses_n = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }

        meses_disp = sorted(
            df[df["fecha_dt"].dt.year == sel_anio]["fecha_dt"].dt.month.unique()
        )

        sel_mes = st.selectbox(
            "Mes:",
            meses_disp,
            format_func=lambda x: meses_n[x]
        )

    # ============================
    # FILTRAR MES Y VALORES VÁLIDOS
    # ============================
    df_mes = df[
        (df["fecha_dt"].dt.year == sel_anio) &
        (df["fecha_dt"].dt.month == sel_mes) &
        (df["mm"] >= 1)
    ].copy()

    if df_mes.empty:
        st.warning("No hay registros válidos de precipitación para el mes seleccionado.")
    else:
        # ============================
        # MÁXIMO POR PLUVIÓMETRO
        # ============================
        idx_max = df_mes.groupby("Pluviómetro")["mm"].idxmax()
        df_max = df_mes.loc[idx_max].copy()

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
        }).sort_values("Pluviómetro")

        #st.markdown("### 📋 Máxima mensual registrada en cada pluviómetro")

        st.dataframe(
            tabla_max.style.format(
                {"Máxima (mm)": lambda x: f"{x:.1f}" if x >= 1 else ""}
            ),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Se muestra, para cada pluviómetro, la mayor precipitación registrada "
            "durante el mes seleccionado y la fecha en que ocurrió. "
            "Solo se consideran valores válidos (≥ 1 mm)."
        )








# ------------------------- HISTÓRICO -------------------------
# ------------------------- HISTÓRICO -------------------------
elif seccion == "📈 Histórico":

    st.subheader("📈 Consulta histórica de precipitaciones")

    # ============================
    # FILTROS
    # ============================
    col1, col2, col3 = st.columns([0.35, 0.35, 0.3])

    with col1:
        sel_est = st.multiselect(
            "Pluviómetro(s):",
            sorted(df["Pluviómetro"].unique())
        )

    with col2:
        f_desde = st.date_input(
            "Desde:",
            df["fecha"].min()
        )
        f_hasta = st.date_input(
            "Hasta:",
            df["fecha"].max()
        )

    with col3:
        modo = st.radio(
            "Modo:",
            ["Diario", "Mensual"]
        )

    if not sel_est:
        st.info("Seleccione uno o más pluviómetros para visualizar el histórico.")
        st.stop()

    # ============================
    # FILTRADO BASE
    # ============================
    df_filt = df[
        (df["Pluviómetro"].isin(sel_est)) &
        (df["fecha"] >= f_desde) &
        (df["fecha"] <= f_hasta) &
        (df["mm"] >= 1)
    ].copy()

    if df_filt.empty:
        st.warning("No hay datos válidos para los filtros seleccionados.")
        st.stop()

    # ============================
    # VISTA DIARIA
    # ============================
    if modo == "Diario":

        tabla = (
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

        tabla["Fecha"] = tabla["Fecha"].dt.strftime("%d/%m/%Y")

        st.dataframe(
            tabla.style.format(
                {"Lluvia (mm)": lambda x: f"{x:.1f}"}
            ),
            use_container_width=True,
            hide_index=True
        )

    # ============================
    # VISTA MENSUAL
    # ============================
    else:
        df_filt["Año"] = df_filt["fecha_dt"].dt.year
        df_filt["Mes_Num"] = df_filt["fecha_dt"].dt.month

        meses = {
            1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril",
            5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto",
            9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"
        }

        tabla = (
            df_filt
            .groupby(
                ["Año", "Mes_Num", "Pluviómetro", "Departamento", "Provincia"]
            )["mm"]
            .sum()
            .reset_index()
        )

        tabla["Mes"] = tabla["Mes_Num"].map(meses)

        tabla = (
            tabla[
                ["Año", "Mes", "Pluviómetro", "Departamento", "Provincia", "mm"]
            ]
            .rename(columns={"mm": "Lluvia acumulada (mm)"})
            .sort_values(["Pluviómetro", "Año", "Mes"])
        )

        st.dataframe(
            tabla.style.format(
                {"Lluvia acumulada (mm)": lambda x: f"{x:.1f}" if x >= 1 else ""}
            ),
            use_container_width=True,
            hide_index=True
        )

    # ============================
    # DESCARGA
    # ============================
    st.markdown("---")
    st.markdown("### 📥 Descargar datos")

    col_csv, col_xls = st.columns(2)

    with col_csv:
        st.download_button(
            "⬇️ Descargar CSV",
            tabla.to_csv(index=False).encode("utf-8"),
            file_name="historico_precipitaciones.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_xls:
        buffer = BytesIO()
        tabla.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            "⬇️ Descargar Excel",
            buffer,
            file_name="historico_precipitaciones.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    st.caption(
        "Las celdas vacías indican ausencia de registro. "
        "Solo se incluyen valores válidos de precipitación (≥ 1 mm)."
    )




# ------------------------- REPORTES -------------------------
elif seccion == "📑 Reportes":

    st.subheader("📑 Reporte mensual por Provincia / Departamento")

    # ============================
    # SELECCIÓN TERRITORIAL
    # ============================
    provincia = st.selectbox(
        "Provincia:",
        sorted(df["Provincia"].dropna().unique())
    )

    deptos_prov = sorted(
        df[df["Provincia"] == provincia]["Departamento"].dropna().unique()
    )

    # Agregamos opción explícita "Todos"
    opciones_deptos = ["Todos los departamentos"] + deptos_prov

    departamentos_sel = st.multiselect(
        "Departamento(s):",
        opciones_deptos,
        default=["Todos los departamentos"],
        help=(
            "Puede seleccionar uno, varios o todos los departamentos "
            "de la provincia."
        )
    )

    # ============================
    # PERÍODO
    # ============================
    col1, col2 = st.columns(2)
    with col1:
        f_desde = st.date_input("Desde:", df["fecha"].min())
    with col2:
        f_hasta = st.date_input("Hasta:", df["fecha"].max())

    # ============================
    # AVISO HISTÓRICO
    # ============================
    st.info(
        "ℹ️ Para generar reportes que abarquen períodos mayores a 60 días, "
        "es necesario activar previamente la opción "
        "**«Cargar historial completo»** desde el panel lateral."
    )

    # ============================
    # GENERAR REPORTE
    # ============================
    if st.button("📄 Generar reporte"):

        # --- normalización mensual ---
        fecha_ini = pd.to_datetime(f_desde).replace(day=1)
        fecha_fin = (
            pd.to_datetime(f_hasta)
            .replace(day=1)
            + pd.offsets.MonthEnd(1)
        )

        # --- filtro base por provincia y período ---
        df_r = df[
            (df["Provincia"] == provincia) &
            (df["fecha_dt"] >= fecha_ini) &
            (df["fecha_dt"] <= fecha_fin)
        ].copy()

        # --- lógica de departamentos ---
        if "Todos los departamentos" in departamentos_sel:
            departamentos_usados = deptos_prov
            titulo_deptos = "Todos los departamentos"
        else:
            departamentos_usados = departamentos_sel
            titulo_deptos = ", ".join(departamentos_sel)

            df_r = df_r[df_r["Departamento"].isin(departamentos_usados)]

        if df_r.empty:
            st.warning("No hay datos para el período y territorio seleccionados.")
        else:
            # Texto ASCII (sin caracteres Unicode)
            descripcion_reporte = (
                f"Provincia: {provincia} - Departamentos: {titulo_deptos}"
            )

            pdf_m = crear_pdf_mensual_region(
                df_r,
                region=descripcion_reporte,
                fecha_desde=fecha_ini.date(),
                fecha_hasta=fecha_fin.date()
            )

            st.download_button(
                "📄 Descargar PDF mensual",
                pdf_m,
                file_name="reporte_mensual_provincia_departamentos.pdf",
                mime="application/pdf",
                use_container_width=True
            )



# ------------------------- RED COMPLETA -------------------------
# ------------------------- RED COMPLETA -------------------------
elif seccion == "🌧️ Red":
    st.subheader("🌧️ Red completa de pluviómetros")
    st.info("Este mapa muestra todos los pluviómetros incorporados a la red.")

    # ============================
    # BASE DE ESTACIONES (lat/lon)
    # ============================
    df_red = df_estaciones.dropna(subset=["lat", "lon"]).copy()

    # Nombre visible de estación
    if col_nombre_est and col_nombre_est in df_red.columns:
        df_red["Pluviómetro"] = df_red[col_nombre_est].fillna(df_red["cod"])
    else:
        df_red["Pluviómetro"] = df_red.get("cod", "S/D")

    # Detección tolerante de columnas Depto/Prov (por si varían los nombres)
    col_depto_base = next(
        (c for c in df_red.columns if "depto" in c.lower() or "depart" in c.lower()),
        None
    )
    col_prov_base = next(
        (c for c in df_red.columns if "prov" in c.lower()),
        None
    )

    # ============================
    # BUSCADOR SIMPLE (opcional)
    # ============================
    opciones = ["Ver todos"] + sorted(df_red["Pluviómetro"].dropna().unique().tolist())
    seleccion = st.selectbox("🔍 Buscar un pluviómetro:", opciones, index=0)

    if seleccion == "Ver todos":
        df_mostrar = df_red
        zoom_init = 7
    else:
        df_mostrar = df_red[df_red["Pluviómetro"] == seleccion]
        zoom_init = 12

    if df_mostrar.empty:
        st.warning("No hay estaciones con coordenadas para mostrar.")
        st.stop()

    # ============================
    # MAPA FOLIUM (sin parpadeo)
    # ============================
    centro = [df_mostrar["lat"].mean(), df_mostrar["lon"].mean()]
    m_red = folium.Map(location=centro, zoom_start=zoom_init, tiles=None)

    # Capas base
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

    # Cluster de marcadores (mejor performance)
    
    #cluster = MarkerCluster().add_to(m_red)
    pluvios = folium.FeatureGroup(
        name="Pluviómetros",
        overlay=False,   # 👈 CLAVE: no aparece en el control
        control=False
    )

    cluster = MarkerCluster().add_to(pluvios)
    m_red.add_child(pluvios)

    # ============================
    # POPUPS (Pluviómetro / Depto / Prov.)
    # ============================
    for _, r in df_mostrar.iterrows():
        depto_val = r[col_depto_base] if col_depto_base and pd.notna(r.get(col_depto_base)) else "S/D"
        prov_val  = r[col_prov_base]  if col_prov_base  and pd.notna(r.get(col_prov_base))  else "S/D"

        popup_html = f"""
        <div style="font-family: sans-serif; min-width: 180px;">
            <div style="font-weight:700; margin-bottom:6px;">{r['Pluviómetro']}</div>
            <div style="font-size:13px; color:#333;">
                <b>Depto/Prov:</b> {depto_val} / {prov_val}
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
            tooltip=r["Pluviómetro"],
            popup=folium.Popup(popup_html, max_width=260)
        ).add_to(cluster)

    # Controles
    LocateControl(auto_start=False, flyTo=True).add_to(m_red)
    folium.LayerControl(position="bottomright").add_to(m_red)

    # Marco/estilo (opcional)
    st.markdown(
        '<div style="box-shadow:0 0 0 2px #000;border-radius:8px;margin:10px 2px;line-height:0;">',
        unsafe_allow_html=True
    )
    st_folium(m_red, width="100%", height=600, key="mapa_red", returned_objects=[])
    st.markdown('</div>', unsafe_allow_html=True)
    
# ------------------------- INFO -------------------------
elif seccion == "ℹ️ Info":
    st.subheader("ℹ️ Información institucional")

    st.markdown(INFO_MD, unsafe_allow_html=True)
