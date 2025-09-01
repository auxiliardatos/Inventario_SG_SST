import streamlit as st
from connection import init_connection

st.set_page_config(layout="wide")

# Inicializar conexión
st_supabase_client = init_connection()


def validar_usuario(st_supabase_client, username, password):
    try:
        response = (
            st_supabase_client.table("Usuarios_Admin")
            .select("id, nombre_usuario, contrasena")
            .eq("nombre_usuario", username)
            .execute()
        )

        if not response.data:
            return False, None

        user = response.data[0]

        # Comparación simple (texto plano)
        if password == user["contrasena"]:
            return True, user
        else:
            return False, None

    except Exception as e:
        st.error(f"❌ Error en validación de usuario: {e}")
        return False, None


def login():
    st.title("🔐 Login")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_button = st.button("Iniciar sesión")

    if login_button:
        valido, user = validar_usuario(st_supabase_client, username, password)
        if valido:
            st.session_state["logged_in"] = True
            st.session_state["user"] = user
            st.success(f"✅ Bienvenido {user['nombre_usuario']}")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")


def logout():
    st.session_state["logged_in"] = False
    st.session_state.pop("user", None)


def main_app():
    st.sidebar.write(f"👤 Usuario: {st.session_state['user']['nombre_usuario']}")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    # Aquí va tu navegación
    pages = {
        "Inicio": [
            st.Page("inicio.py", title="🏠 Inicio"),  # 🔥 Nueva página
        ],
        "Gestión de inventario": [
            st.Page("Inventario/gestion_elementos.py", title="Elementos"),
            st.Page("Inventario/actividad_inventario.py", title="Movimientos de inventario"),
        ],
        "Gestión de sedes": [
            st.Page("Sedes/gestion_sedes.py", title="Sedes"),
        ],
        "Gestión de usuarios": [
            st.Page("Usuarios/gestion_usuarios.py", title="Usuarios"),
        ],
        "Reportes": [
            st.Page("Reportes/reportes.py", title="Reportes"),
        ],
    }

    pg = st.navigation(pages)
    pg.run()


def main():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        # 🔥 Ocultar sidebar con CSS
        hide_sidebar_style = """
            <style>
                [data-testid="stSidebar"] {display: none;}
            </style>
        """
        st.markdown(hide_sidebar_style, unsafe_allow_html=True)

        login()
    else:
        main_app()


if __name__ == "__main__":
    main()