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

# 1. CARGA DE DATOS (CORREGIDO PARA EVITAR ERRORES DE COLUMNAS)
@st.cache_data
def cargar_datos():
    data = pd.read_excel("encuestas_farmatech.xlsx")
    # Limpia espacios en blanco al inicio o final de los nombres de las columnas
    data.columns = data.columns.str.strip()
    return data

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"⚠️ Error al cargar el archivo: {e}")
    st.stop()

# 2. INICIALIZAR HISTORIAL
if 'historial' not in st.session_state:
    st.session_state.historial = []

# --- BARRA LATERAL ---
st.sidebar.image("https://www.unimilitar.edu.co/documents/10184/10227/Logo.png", width=200)
st.sidebar.title("Panel de Control")

# 3. FILTROS (CON VERIFICACIÓN)
col_canal = 'Canal Preferido'
if col_canal in df.columns:
    opciones = df[col_canal].unique()
    filtro_canal = st.sidebar.multiselect("Filtrar por Canal:", options=opciones, default=opciones)
    df_filtrado = df[df[col_canal].isin(filtro_canal)]
else:
    df_filtrado = df
    st.sidebar.error(f"No se halló la columna '{col_canal}'")

# --- BOTONES ESPECIALES ---
st.sidebar.divider()
st.sidebar.subheader("Acciones de Reporte")

if st.sidebar.button("💾 Guardar en Historial"):
    hora = datetime.now().strftime("%H:%M:%S")
    st.session_state.historial.append({"Hora": hora, "Registros": len(df_filtrado)})
    st.sidebar.success(f"Guardado a las {hora}")

if st.sidebar.button("🗑️ Vaciar Papelera"):
    st.session_state.historial = []
    st.sidebar.warning("Historial eliminado")
    st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("📊 Dashboard de Satisfacción FarmaTech")
st.info("Para tomar una captura: Usa el botón de la cámara (Camera icon) que aparece arriba a la derecha de cada gráfica al pasar el mouse.")

col1, col2 = st.columns(2)

# GRÁFICA 1: FRECUENCIA (CORREGIDA)
with col1:
    st.subheader("Frecuencia de Compra")
    col_frec = 'Frecuencia'
    if col_frec in df_filtrado.columns:
        fig1 = px.pie(df_filtrado, names=col_frec, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning(f"No se encontró la columna '{col_frec}'")

# GRÁFICA 2: GASTO (CORREGIDA)
with col2:
    st.subheader("Gasto Mensual por Cliente")
    col_gasto = 'Gasto Mer' if 'Gasto Mer' in df_filtrado.columns else 'Gasto Mensual'
    if col_gasto in df_filtrado.columns:
        fig2 = px.bar(df_filtrado, x='Nombre', y=col_gasto, color=col_gasto, color_continuous_scale='Viridis')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        # Si no encuentra el nombre, usa la columna 9 del Excel por posición
        fig2 = px.bar(df_filtrado, x=df_filtrado.columns[1], y=df_filtrado.columns[8])
        st.plotly_chart(fig2, use_container_width=True)

# --- SECCIÓN DE HISTORIAL ---
st.divider()
st.subheader("📜 Historial de Consultas")
if st.session_state.historial:
    st.table(pd.DataFrame(st.session_state.historial))
else:
    st.write("El historial está vacío.")

# --- DESCARGA DE DATOS ---
st.divider()
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name='Reporte')
    
st.download_button(
    label="📥 Descargar Excel de Datos Filtrados",
    data=buffer.getvalue(),
    file_name=f"reporte_farmatech_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.ms-excel"
)
