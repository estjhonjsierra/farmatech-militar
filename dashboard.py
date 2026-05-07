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

# 1. CARGA DE DATOS (MEJORADO PARA QUE APAREZCAN LAS GRÁFICAS)
@st.cache_data
def cargar_datos():
    data = pd.read_excel("encuestas_farmatech.xlsx")
    # CORRECCIÓN: Limpia espacios vacíos al inicio y final de los títulos de las columnas
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

# 3. FILTROS POR ESTRATO
col_estrato = 'Estrato'
if col_estrato in df.columns:
    df[col_estrato] = df[col_estrato].astype(str)
    opciones_estrato = sorted(df[col_estrato].unique())
    
    filtro_estrato = st.sidebar.multiselect("Filtrar por Estrato:", options=opciones_estrato, default=opciones_estrato)
    df_filtrado = df[df[col_estrato].isin(filtro_estrato)]
    
    # MOSTRAR CANTIDAD DE PERSONAS
    total_encuestados = len(df)
    seleccionados = len(df_filtrado)
    
    st.sidebar.metric("Total Encuestados", f"{total_encuestados}")
    st.sidebar.metric("Personas en Filtro", f"{seleccionados}")
    
    if seleccionados > 0:
        st.sidebar.write("### Desglose por Estrato:")
        for est in filtro_estrato:
            cant = len(df_filtrado[df_filtrado[col_estrato] == est])
            st.sidebar.write(f"Estrato {est}: {cant} personas")
else:
    df_filtrado = df
    st.sidebar.error(f"No se halló la columna '{col_estrato}'")

# --- BOTONES DE ACCIÓN ---
st.sidebar.divider()
st.sidebar.subheader("Acciones de Reporte")

if st.sidebar.button("💾 Guardar en Historial"):
    hora = datetime.now().strftime("%H:%M:%S")
    st.session_state.historial.append({"Hora": hora, "Personas": len(df_filtrado), "Estratos": ", ".join(filtro_estrato)})
    st.sidebar.success(f"Guardado a las {hora}")

if st.sidebar.button("🗑️ Vaciar Papelera"):
    st.session_state.historial = []
    st.sidebar.warning("Historial eliminado")
    st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("📊 Dashboard de Satisfacción FarmaTech")
st.info("📸 **PARA DESCARGAR GRÁFICAS:** Pasa el mouse sobre la gráfica y haz clic en el icono de la **CÁMARA** (Download plot as a png).")

col1, col2 = st.columns(2)

# CORRECCIÓN: GRÁFICA 1 CON BUSQUEDA INTELIGENTE DE COLUMNA
with col1:
    st.subheader("Frecuencia de Compra")
    # Busca la columna aunque se llame 'Frecuencia ' o similar
    col_frec = next((c for c in df_filtrado.columns if 'Frecuencia' in c), None)
    if col_frec:
        fig1 = px.pie(df_filtrado, names=col_frec, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("⚠️ No se encontró la columna de 'Frecuencia' para graficar.")

# CORRECCIÓN: GRÁFICA 2 CON BUSQUEDA INTELIGENTE DE COLUMNA
with col2:
    st.subheader("Gasto Mensual por Cliente")
    # Busca columnas que contengan 'Gasto' (como 'Gasto Mer' o 'Gasto Mensual')
    col_gasto = next((c for c in df_filtrado.columns if 'Gasto' in c), None)
    if col_gasto:
        fig2 = px.bar(df_filtrado, x='Nombre', y=col_gasto, color=col_gasto, color_continuous_scale='Viridis')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ No se encontró la columna de 'Gasto' para graficar.")

# --- SECCIÓN DE HISTORIAL ---
st.divider()
st.subheader("📜 Historial de Consultas")
if st.session_state.historial:
    st.table(pd.DataFrame(st.session_state.historial))

# --- DESCARGA DE EXCEL ---
st.divider()
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False, sheet_name='Reporte_Filtrado')
    
st.download_button(
    label="📥 Descargar Excel de Datos Filtrados",
    data=buffer.getvalue(),
    file_name=f"reporte_estratos_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.ms-excel"
)
