import streamlit as st
from connection import init_connection
import pandas as pd


def crear_sede(st_supabase_client):
    st.subheader("✅ Creando sede")
    
    # Empieza el formulario
    with st.form(key="Sede_form"):
        st.text("Campos a llenar:")
        
        nombre = st.text_input("Nombre de la sede")
        direccion = st.text_input("Dirección")
        
        # Botón de submit
        send_button = st.form_submit_button("Agregar sede nueva")
        
        if send_button:
            if not nombre.strip():  # <- valida que no esté vacío o solo espacios
                st.warning("⚠️ El nombre de la sede es obligatorio.")
            else:
                send_data = {
                    "nombre": nombre,
                    "direccion": direccion,
                }

                try:
                    st_supabase_client.table("Sede").insert(send_data).execute()
                    st.success("Sede agregada correctamente ✅")
                except Exception as e:
                    st.error(f"❌ Error al crear la sede: {e}")


def obtener_matriz_elemento(st_supabase_client):
    st_supabase_client = init_connection()
    
    response = st_supabase_client.table("Elemento").select("*").execute()
    df_elementos = response.data
    
    st.dataframe(df_elementos)

# Inicializar conexión y estado
st_supabase_client = init_connection()
if "accion" not in st.session_state:
    st.session_state.accion = None

st.header("Reportes")

# Botones
col1, col2, col3, col4, col5 = st.columns([1,0.1,1,0.1,1])

with col1:
    if st.button("Elementos"):
        st.session_state.accion = "Matriz de EPP"


# Mostrar contenido según la acción guardada en session_state
if st.session_state.accion == "Matriz de EPP":
    obtener_matriz_elemento(st_supabase_client)