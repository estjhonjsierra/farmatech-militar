import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Configuración inicial
st.set_page_config(page_title="Dashboard FarmaTech", layout="wide")

st.title("📊 FarmaTech: Control de Filtros")

# --- CARGAR DATOS CON RUTA FIJA ---
try:
    # Ruta corregida según tu Ledger de correcciones
    ruta = r'C:\Users\Jhon Marin\Desktop\Proyecto_FarmaTech\encuestas_farmatech.xlsx'
    df = pd.read_excel(ruta)
    df.columns = [c.strip() for c in df.columns]
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# --- BLOQUE DE FILTROS (AQUÍ ESTÁ LA SOLUCIÓN) ---
st.sidebar.header("Configuración de Filtros")

# Aseguramos que los estratos sean tratables
opciones_estrato = sorted(list(df["Estrato"].unique()))

# Multiselect con selección por defecto para que la página no inicie vacía
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
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_input.to_excel(writer, index=False, sheet_name='Datos_Filtrados')
        # Insertar texto de control
        writer.sheets['Datos_Filtrados'].write('K1', f'Filtro aplicado: {estrato_sel}')
    return output.getvalue()

if not df_filtrado.empty:
    st.sidebar.download_button(
        label="📥 Descargar Excel Filtrado",
        data=generar_excel(df_filtrado),
        file_name="reporte_farmatech.xlsx",
        mime="application/vnd.ms-excel"
    )

# --- VISTA DE DATOS ---
if not df_filtrado.empty:
    st.subheader(f"Resultados para Estratos: {', '.join(map(str, estrato_sel))}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Gráfica de Torta
        col_canal = [c for c in df.columns if "Canal" in c][0]
        fig = px.pie(df_filtrado, names=col_canal, title="Canal de Compra")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Tabla de nombres para tu informe de la Militar
        st.write("📋 **Lista de Encuestados:**")
        st.dataframe(df_filtrado[['Nombre', 'Estrato', 'Gasto Mensual ($)']], height=300)
else:
    st.warning("⚠️ Selecciona al menos un estrato en el menú de la izquierda para ver los datos.")