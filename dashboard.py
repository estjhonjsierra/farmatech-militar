import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# Configuración de la página
st.set_page_config(page_title="FarmaTech - Dashboard Militar", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    # Cargamos el excel
    data = pd.read_excel("encuestas_farmatech.xlsx")
    # ESTO ARREGLA EL ERROR: Limpia espacios raros en los nombres de las columnas
    data.columns = data.columns.str.strip()
    return data

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"⚠️ Error al cargar el Excel: {e}")
    st.stop()

# --- INICIALIZAR HISTORIAL ---
if 'historial' not in st.session_state:
    st.session_state.historial = []

# --- BARRA LATERAL ---
st.sidebar.title("Panel de Control")

# Filtro dinámico (usamos 'Canal Preferido' según tu Excel)
col_canal = 'Canal Preferido'
if col_canal in df.columns:
    opciones = df[col_canal].unique()
    filtro_canal = st.sidebar.multiselect("Filtrar por Canal:", options=opciones, default=opciones)
    df_filtrado = df[df[col_canal].isin(filtro_canal)]
else:
    df_filtrado = df
    st.sidebar.warning(f"No encontré la columna '{col_canal}'")

# Botones de historial
st.sidebar.divider()
if st.sidebar.button("💾 Guardar en Historial"):
    hora = datetime.now().strftime("%H:%M:%S")
    st.session_state.historial.append({"Hora": hora, "Registros": len(df_filtrado)})
    st.sidebar.success("Guardado")

if st.sidebar.button("🗑️ Vaciar Papelera"):
    st.session_state.historial = []
    st.sidebar.rerun()

# --- CUERPO PRINCIPAL ---
st.title("📊 Dashboard FarmaTech")
st.info("💡 Tip: Pasa el mouse sobre las gráficas y dale a la CÁMARA para descargar la imagen.")

# Verificamos que la columna 'Frecuencia' exista antes de graficar
col_grafica = 'Frecuencia'
if col_grafica in df_filtrado.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución de Frecuencia")
        fig1 = px.pie(df_filtrado, names=col_grafica, hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col2:
        st.subheader("Gasto por Cliente")
        # Usamos 'Gasto Mensual' o la columna que tengas de dinero
        col_gasto = 'Gasto Mensual' if 'Gasto Mensual' in df.columns else df.columns[8] 
        fig2 = px.bar(df_filtrado, x='Nombre', y=col_gasto)
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.error(f"No se pudo crear la gráfica porque no existe la columna '{col_grafica}' en tu Excel.")
    st.write("Columnas detectadas:", list(df.columns))

# --- TABLA DE HISTORIAL ---
st.divider()
st.subheader("📜 Historial de Consultas")
if st.session_state.historial:
    st.table(pd.DataFrame(st.session_state.historial))

# --- DESCARGA ---
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, index=False)
st.download_button("📥 Descargar Excel Filtrado", buffer.getvalue(), "reporte.xlsx")
