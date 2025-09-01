import streamlit as st
from connection import init_connection
from st_supabase_connection import SupabaseConnection
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


def eliminar_sede(st_supabase_client):
    st.subheader("🗑️ Eliminando sede")
    
    # Traer todos los elementos disponibles
    try:
        response = st_supabase_client.table("Sede").select("id, nombre").execute()
        sedes = response.data
    except Exception as e:
        st.error(f"❌ Error al obtener sedes: {e}")
        return
    
    if not sedes:
        st.info("No hay sedes registradas.")
        return
    
    # Mostrar opciones en un selectbox
    opciones = {f"{el['nombre']}": el["id"] for el in sedes}
    seleccion = st.selectbox("Selecciona la sede a eliminar", list(opciones.keys()))
    
    id_sede = opciones[seleccion]
    
    # Confirmación
    confirmar = st.checkbox(f"⚠️ Confirmo que quiero eliminar al usuario: {seleccion}")
    
    if st.button("Eliminar definitivamente 🚨"):
        if not confirmar:
            st.warning("Debes confirmar la eliminación antes de continuar.")
            return
        
        try:
            st_supabase_client.table("Sede").delete().eq("id", id_sede).execute()
            st.success(f"✅ Usuario '{seleccion}' eliminado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
            
def editar_sede(st_supabase_client):
    st.subheader("✏️ Editando sede")

    # 1. Obtener todos los elementos
    sedes = st_supabase_client.table("Sede").select("*").execute().data

    if not sedes:
        st.info("No hay sedes para editar.")
        return

    # 2. Seleccionar cuál editar
    opciones = {e["id"]: f'{e["id"]} - {e["nombre"]}' for e in sedes}
    id_seleccionado = st.selectbox("Selecciona un elemento", options=list(opciones.keys()), format_func=lambda x: opciones[x])

    # Buscar datos actuales
    sede = next(e for e in sedes if e["id"] == id_seleccionado)

    # 3. Formulario con datos precargados
    with st.form(key="EditarElementoForm"):
        nombre = st.text_input("Nombre", value=sede["nombre"])
        direccion = st.text_input("Dirección", value=sede["direccion"])
    
        # Botón submit
        update_button = st.form_submit_button("Actualizar elemento")

        if update_button:
            try:
                # 5. Actualizar tabla Elemento
                update_data = {
                    "nombre": nombre,
                    "direccion": direccion,
                }

                st_supabase_client.table("Sede").update(update_data).eq("id", id_seleccionado).execute()
                
                st.success(f"Sede {id_seleccionado} actualizado correctamente ✅")

            except Exception as e:
                st.error(f"❌ Error al actualizar: {e}")


# Inicializar conexión y estado
st_supabase_client = init_connection()
if "accion" not in st.session_state:
    st.session_state.accion = None

st.header("Gestión de sedes")

# Botones
col1, col2, col3, col4, col5 = st.columns([1,0.1,1,0.1,1])

with col1:
    if st.button("Crear sede"):
        st.session_state.accion = "crear"
with col3:
    if st.button("Editar sede"):
        st.session_state.accion = "editar"
with col5:
    if st.button("Eliminar sede"):
        st.session_state.accion = "eliminar"


# Mostrar contenido según la acción guardada en session_state
if st.session_state.accion == "crear":
    crear_sede(st_supabase_client)
elif st.session_state.accion == "editar":
    editar_sede(st_supabase_client)
elif st.session_state.accion == "eliminar":
    eliminar_sede(st_supabase_client)