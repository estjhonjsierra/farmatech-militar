import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Configuración inicial
st.set_page_config(page_title="Dashboard FarmaTech", layout="wide")

st.title("📊 FarmaTech: Control de Filtros")

# --- CARGAR DATOS (RUTA CORREGIDA PARA GITHUB) ---
try:
    # Se eliminó la ruta C:\Users\... para que funcione en la nube
    ruta = 'encuestas_farmatech.xlsx'
    df = pd.read_excel(ruta)
    df.columns = [c.strip() for c in df.columns]
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.info("Asegúrate de que el archivo 'encuestas_farmatech.xlsx' esté en la raíz de tu repositorio de GitHub.")
    st.stop()

# --- BLOQUE DE FILTROS ---
st.sidebar.header("Configuración de Filtros")

# Aseguramos que los estratos sean tratables
opciones_estrato = sorted(list(df["Estrato"].unique()))

# Multiselect con selección por defecto
estrato_sel = st.sidebar.multiselect(
    "Seleccione Estrato:", 
    options=opciones_estrato, 
    default=opciones_estrato
)

# Aplicar el filtro
df_filtrado = df[df["Estrato"].isin(estrato_sel)]

# --- BOTÓN DE DESCARGA ---
def generar_excel(df_input):
    output = io.BytesIO()
    # Usamos openpyxl como motor por defecto para compatibilidad
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_input.to_excel(writer, index=False, sheet_name='Datos_Filtrados')
    return output.getvalue()

if not df_filtrado.empty:
    st.sidebar.download_button(
        label="📥 Descargar Excel Filtrado",
        data=generar_excel(df_filtrado),
        file_name="reporte_farmatech.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- VISTA DE DATOS ---
if not df_filtrado.empty:
    st.subheader(f"Resultados para Estratos: {', '.join(map(str, estrato_sel))}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gráfica de Torta
        # Buscamos la columna que contenga la palabra 'Canal'
        columnas_canal = [c for c in df.columns if "Canal" in c]
        if columnas_canal:
            fig = px.pie(df_filtrado, names=columnas_canal[0], title="Canal de Compra")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No se encontró la columna 'Canal de Compra' para graficar.")
        
    with col2:
        # Tabla de datos para el informe
        st.write("📋 **Lista de Encuestados:**")
        # Ajusta los nombres de columnas si son diferentes en tu Excel
        columnas_visibles = ['Nombre', 'Estrato']
        # Verificamos si existe la columna de Gasto
        if 'Gasto Mensual ($)' in df_filtrado.columns:
            columnas_visibles.append('Gasto Mensual ($)')
            
        st.dataframe(df_filtrado[columnas_visibles], height=300)
else:
    st.warning("⚠️ Selecciona al menos un estrato en el menú de la izquierda para ver los datos.")
