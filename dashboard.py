import streamlit as st
import pandas as pd
import plotly.express as px
import io

# Configuración inicial de la página
st.set_page_config(page_title="Dashboard FarmaTech", layout="wide")

st.title("📊 FarmaTech: Control de Filtros y Análisis")

# --- CARGAR DATOS ---
try:
    ruta = 'encuestas_farmatech.xlsx'
    df = pd.read_excel(ruta)
    # Limpiar espacios en los nombres de las columnas
    df.columns = [c.strip() for c in df.columns]
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.info("Asegúrate de que 'encuestas_farmatech.xlsx' esté en la raíz de tu repositorio de GitHub.")
    st.stop()

# --- BLOQUE DE FILTROS EN LA BARRA LATERAL ---
st.sidebar.header("⚙️ Configuración de Filtros")

# Obtener opciones únicas de estrato
opciones_estrato = sorted(list(df["Estrato"].unique()))

# Selector múltiple (por defecto todos seleccionados para mostrar los 40)
estrato_sel = st.sidebar.multiselect(
    "Seleccione Estrato:", 
    options=opciones_estrato, 
    default=opciones_estrato
)

# Aplicar el filtro al DataFrame principal
df_filtrado = df[df["Estrato"].isin(estrato_sel)]

# --- MÉTRICAS PRINCIPALES ---
st.markdown("---")
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    total_encuestados = len(df_filtrado)
    st.metric("Total Personas Filtradas", f"{total_encuestados} / {len(df)}")

with col_m2:
    if not df_filtrado.empty:
        estratos_activos = len(df_filtrado["Estrato"].unique())
        st.metric("Estratos en Vista", estratos_activos)

with col_m3:
    # Mostramos cuántas personas hay por estrato en el filtro actual
    if not df_filtrado.empty:
        conteo_estratos = df_filtrado["Estrato"].value_counts().to_dict()
        st.write("📌 **Personas por Estrato:**")
        st.caption(str(conteo_estratos).replace("{", "").replace("}", ""))

# --- BOTÓN DE DESCARGA ---
def generar_excel(df_input):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_input.to_excel(writer, index=False, sheet_name='Datos_Filtrados')
    return output.getvalue()

if not df_filtrado.empty:
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Descargar Reporte Excel",
        data=generar_excel(df_filtrado),
        file_name="reporte_farmatech_militar.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- VISUALIZACIÓN DE GRÁFICAS Y TABLAS ---
if not df_filtrado.empty:
    st.markdown("### 📈 Análisis de la Muestra")
    
    tab1, tab2 = st.tabs(["📊 Gráficas", "📋 Tabla de Datos"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            # Gráfica de Distribución de Estratos
            fig_estrato = px.bar(df_filtrado['Estrato'].value_counts().reset_index(), 
                                 x='Estrato', y='count', 
                                 title="Cantidad de Personas por Estrato",
                                 labels={'count':'Personas', 'Estrato':'Nivel de Estrato'},
                                 color='Estrato')
            st.plotly_chart(fig_estrato, use_container_width=True)
        
        with c2:
            # Gráfica de Canal de Compra
            col_canal = [c for c in df.columns if "Canal" in c]
            if col_canal:
                fig_pie = px.pie(df_filtrado, names=col_canal[0], title="Preferencia de Canal de Compra", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.write("🔍 **Detalle de la base de datos filtrada:**")
        # Mostramos la tabla completa para que puedas verificar los 40 registros
        st.dataframe(df_filtrado, use_container_width=True, height=400)
else:
    st.warning("⚠️ El filtro está vacío. Selecciona al menos un estrato en la barra lateral.")
