import streamlit as st
from connection import init_connection
import pandas as pd


def crear_usuario(st_supabase_client):
    st.subheader("✅ Creando usuario")
    
    # Empieza el formulario
    with st.form(key="User_form"):
        st.text("Campos a llenar:")
        
        nombres = st.text_input("Nombre del usuario")
        apellidos = st.text_input("Apellido del usuario")
        correo = st.text_input("Correo")
        telefono = st.text_input("Número de teléfono")  # mejor como text_input por si hay +57, espacios, etc.
        
        # Traer todos los roles disponibles
        try:
            response = st_supabase_client.table("Rol").select("id, nombre_cargo").execute()
            cargos = response.data
        except Exception as e:
            st.error(f"❌ Error al obtener cargos: {e}")
            return
        
        if not cargos:
            st.info("⚠️ No hay roles creados.")
            return
        
        # Mapeo de opciones
        opciones = {cargo["nombre_cargo"]: cargo["id"] for cargo in cargos}
        seleccion = st.selectbox("Selecciona el rol del usuario", list(opciones.keys()))
        id_rol = opciones[seleccion]
        
        # Botón de submit
        send_button = st.form_submit_button("Agregar usuario nuevo")
        
        if send_button:
            # Validación de campos obligatorios
            if not nombres.strip() or not apellidos.strip():
                st.warning("⚠️ El nombre y apellido son obligatorios.")
            else:
                send_data = {
                    "nombres": nombres,
                    "apellidos": apellidos,
                    "correo": correo.strip(),
                    "telefono": telefono.strip(),
                    "id_rol": id_rol,
                }
                
                try:
                    st_supabase_client.table("Usuario").insert(send_data).execute()
                    st.success("Usuario agregado correctamente ✅")
                except Exception as e:
                    st.error(f"❌ Error al crear el usuario: {e}")


def eliminar_usuario(st_supabase_client):
    st.subheader("🗑️ Eliminando usuario")
    
    # Traer todos los usuarios
    try:
        response = st_supabase_client.table("Usuario").select("id, nombres, apellidos").execute()
        usuarios = response.data
    except Exception as e:
        st.error(f"❌ Error al obtener usuarios: {e}")
        return
    
    if not usuarios:
        st.info("No hay usuarios registrados.")
        return
    
    # Opciones en selectbox
    opciones = {f"{el['nombres']} {el['apellidos']}": el["id"] for el in usuarios}
    seleccion = st.selectbox("Selecciona el usuario a eliminar", sorted(opciones.keys()))
    id_usuario = opciones[seleccion]
    
    # Confirmación
    confirmar = st.checkbox(f"⚠️ Confirmo que quiero eliminar al usuario: {seleccion}")
    
    if st.button("Eliminar definitivamente 🚨"):
        if not confirmar:
            st.warning("Debes confirmar la eliminación antes de continuar.")
            return
        
        try:
            st_supabase_client.table("Usuario").delete().eq("id", id_usuario).execute()
            st.success(f"✅ Usuario '{seleccion}' eliminado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
    
    
def editar_usuario(st_supabase_client):
    st.subheader("✏️ Editando usuario")

    # 1. Obtener todos los usuarios
    usuarios = st_supabase_client.table("Usuario").select("*").execute().data

    if not usuarios:
        st.info("No hay usuarios para editar.")
        return

    # 2. Seleccionar usuario
    opciones = {e["id"]: f'{e["id"]} - {e["nombres"]} {e["apellidos"]}' for e in usuarios}
    id_seleccionado = st.selectbox("Selecciona un usuario", options=list(opciones.keys()), format_func=lambda x: opciones[x])

    # Buscar datos actuales
    usuario = next(e for e in usuarios if e["id"] == id_seleccionado)

    # 3. Formulario con datos precargados
    with st.form(key="EditarUsuarioForm"):
        nombres = st.text_input("Nombres", value=usuario["nombres"])
        apellidos = st.text_input("Apellidos", value=usuario["apellidos"])
        correo = st.text_input("Correo", value=usuario["correo"])
        telefono = st.text_input("Número de teléfono", value=usuario["telefono"])

        # 4. Traer roles disponibles
        try:
            response = st_supabase_client.table("Rol").select("id, nombre_cargo").execute()
            cargos = response.data
        except Exception as e:
            st.error(f"❌ Error al obtener cargos: {e}")
            return

        if not cargos:
            st.info("⚠️ No hay roles creados.")
            return

        # Mapeo de opciones
        opciones_roles = {cargo["nombre_cargo"]: cargo["id"] for cargo in cargos}

        # Rol actual del usuario
        rol_actual = next((cargo["nombre_cargo"] for cargo in cargos if cargo["id"] == usuario["id_rol"]), None)
        index_actual = list(opciones_roles.keys()).index(rol_actual) if rol_actual else 0

        seleccion = st.selectbox("Selecciona el rol del usuario", list(opciones_roles.keys()), index=index_actual)
        id_rol = opciones_roles[seleccion]

        # 5. Botón submit
        update_button = st.form_submit_button("Actualizar usuario")

        if update_button:
            if not nombres.strip() or not apellidos.strip() or not correo.strip():
                st.warning("⚠️ Nombre, apellidos y correo son obligatorios.")
                return

            try:
                update_data = {
                    "nombres": nombres.strip(),
                    "apellidos": apellidos.strip(),
                    "correo": correo.strip(),
                    "telefono": telefono.strip(),
                    "id_rol": id_rol,
                }

                st_supabase_client.table("Usuario").update(update_data).eq("id", id_seleccionado).execute()
                
                st.success(f"Usuario {id_seleccionado} actualizado correctamente ✅")

            except Exception as e:
                st.error(f"❌ Error al actualizar: {e}")


# Inicializar conexión y estado
st_supabase_client = init_connection()
if "accion" not in st.session_state:
    st.session_state.accion = None

st.header("Gestión de usuario")

# Botones
col1, col2, col3, col4, col5 = st.columns([1,0.1,1,0.1,1])

with col1:
    if st.button("Crear usuario"):
        st.session_state.accion = "crear"
with col3:
    if st.button("Editar usuario"):
        st.session_state.accion = "editar"
with col5:
    if st.button("Eliminar usuario"):
        st.session_state.accion = "eliminar"


# Mostrar contenido según la acción guardada en session_state
if st.session_state.accion == "crear":
    crear_usuario(st_supabase_client)
elif st.session_state.accion == "editar":
    editar_usuario(st_supabase_client)
elif st.session_state.accion == "eliminar":
    eliminar_usuario(st_supabase_client)