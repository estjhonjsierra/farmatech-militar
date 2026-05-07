import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(page_title="FarmaTech - Dashboard Militar", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 1. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    # Asegúrate de que el nombre del archivo coincida exactamente con el de GitHub
    return pd.read_excel("encuestas_farmatech.xlsx")

try:
    df = cargar_datos()
except:
    st.error("⚠️ No encontré el archivo 'encuestas_farmatech.xlsx'. Asegúrate de que esté en GitHub.")
    st.stop()

# 2. INICIALIZAR HISTORIAL (Base de datos temporal)
if 'historial' not in st.session_state:
    st.session_state.historial = []

# --- BARRA LATERAL ---
st.sidebar.image("https://www.unimilitar.edu.co/documents/10184/10227/Logo.png", width=200)
st.sidebar.title("Panel de Control")

# 3. FILTROS
filtro_canal = st.sidebar.multiselect("Filtrar por Canal:", options=df["Canal Preferido"].unique(), default=df["Canal Preferido"].unique())
df_filtrado = df[df["Canal Preferido"].isin(filtro_canal)]

# --- BOTONES ESPECIALES ---
st.sidebar.divider()
st.sidebar.subheader("Acciones de Reporte")

# Botón para Guardar en Historial
if st.sidebar.button("💾 Guardar en Historial"):
    hora = datetime.now().strftime("%H:%M:%S")
    st.session_state.historial.append({"Hora": hora, "Registros": len(df_filtrado), "Canales": ", ".join(filtro_canal)})
    st.sidebar.success(f"Guardado a las {hora}")

# Botón de Papelera (Limpiar Historial)
if st.sidebar.button("🗑️ Vaciar Papelera"):
    st.session_state.historial = []
    st.sidebar.warning("Historial eliminado")

# --- CUERPO PRINCIPAL ---
st.title("📊 Dashboard de Satisfacción FarmaTech")
st.info("Para tomar una captura: Presiona **Windows + Shift + S** (en PC) o usa el botón de la cámara arriba a la derecha de cada gráfica.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Frecuencia de Compra")
    fig1 = px.pie(df_filtrado, names='Frecuencia', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Gasto Mensual por Cliente")
    fig2 = px.bar(df_filtrado, x='Nombre', y='Gasto Mensual', color='Gasto Mensual', title="Gasto por Usuario")
    st.plotly_chart(fig2, use_container_width=True)

# --- SECCIÓN DE HISTORIAL ---
st.divider()
st.subheader("📜 Historial de Consultas")
if st.session_state.historial:
    hist_df = pd.DataFrame(st.session_state.historial)
    st.table(hist_df)
else:
    st.write("El historial está vacío. Dale a 'Guardar en Historial' para ver datos aquí.")

# --- DESCARGA DE DATOS ---
st.divider()
st.subheader("📥 Exportar Datos Actuales")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name='Reporte')
    
st.download_button(
    label="Descargar Excel de Datos Filtrados",
    data=buffer.getvalue(),
    file_name=f"reporte_farmatech_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.ms-excel"
)
