import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import streamlit.components.v1 as components # Necesario para la captura real

# Configuración de la página
st.set_page_config(page_title="FarmaTech - Dashboard Militar", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #28a745; color: white; }
    
    /* Estilo para que al imprimir salga todo ordenado */
    @media print {
        .stSidebar { display: none !important; } 
        header { visibility: hidden !important; }
        footer { visibility: hidden !important; }
        .stButton { display: none !important; }
        .stDownloadButton { display: none !important; }
        [data-testid="stExpander"] { border: 1px solid #ccc !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# 1. CARGA DE DATOS
@st.cache_data
def cargar_datos():
    data = pd.read_excel("encuestas_farmatech.xlsx")
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
    
    st.sidebar.metric("Total Encuestados", f"{len(df)}")
    st.sidebar.metric("Personas en Filtro", f"{len(df_filtrado)}")
    
    if len(df_filtrado) > 0:
        st.sidebar.write("### Desglose por Estrato:")
        for est in filtro_estrato:
            cant = len(df_filtrado[df_filtrado[col_estrato] == est])
            st.sidebar.write(f"Estrato {est}: {cant} personas")
else:
    df_filtrado = df

# --- BOTONES DE ACCIÓN ---
st.sidebar.divider()
st.sidebar.subheader("Acciones de Reporte")

# --- SOLUCIÓN PARA CAPTURA REAL ---
st.sidebar.write("📸 **Captura Total:**")
# Este componente crea un botón transparente que ejecuta la impresión al hacer clic
with st.sidebar:
    components.html(
        """
        <button onclick="window.parent.print()" style="
            width: 100%; 
            height: 3em; 
            border-radius: 5px; 
            border: none; 
            background-color: #007bff; 
            color: white; 
            font-weight: bold;
            cursor: pointer;">
            📸 Capturar Reporte Completo
        </button>
        """,
        height=55,
    )
    st.info("Al presionar, elige 'Guardar como PDF'.")

if st.sidebar.button("💾 Guardar en Historial"):
    hora = datetime.now().strftime("%H:%M:%S")
    st.session_state.historial.append({"Hora": hora, "Personas": len(df_filtrado), "Estratos": ", ".join(filtro_estrato)})
    st.sidebar.success(f"Guardado a las {hora}")

if st.sidebar.button("🗑️ Vaciar Papelera"):
    st.session_state.historial = []
    st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("📊 Dashboard de Satisfacción FarmaTech")

with st.expander("📝 ¿QUIERES REGISTRAR UNA NUEVA ENCUESTA?"):
    st.write("Para mantener la base de datos segura, usa el enlace oficial:")
    st.link_button("Ir al Formulario de Registro", "https://forms.google.com", use_container_width=True)

st.info("📸 **TIP:** Usa el botón azul de la izquierda para capturar la pantalla completa en PDF.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Frecuencia de Compra")
    col_frec = next((c for c in df_filtrado.columns if 'Frecuencia' in c), None)
    if col_frec:
        fig1 = px.pie(df_filtrado, names=col_frec, hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Gasto Mensual por Cliente")
    col_gasto = next((c for c in df_filtrado.columns if 'Gasto' in c), None)
    if col_gasto:
        fig2 = px.bar(df_filtrado, x='Nombre', y=col_gasto, color=col_gasto, color_continuous_scale='Viridis')
        st.plotly_chart(fig2, use_container_width=True)

st.divider()
with st.expander(f"👤 LISTADO DE PERSONAS FILTRADAS ({len(df_filtrado)})"):
    if not df_filtrado.empty:
        st.write(", ".join(df_filtrado['Nombre'].tolist()))

st.subheader("📜 Historial de Consultas")
if st.session_state.historial:
    st.table(pd.DataFrame(st.session_state.historial))

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
