import streamlit as st
from connection import init_connection
import pandas as pd


def calcular_inventario(st_supabse_cliente):
    try:
        response = st_supabase_client.table("MovimientoInventario").select("*").execute()
    except Exception as e:
        st.error(f"❌ Error al crear el movimiento de inventario: {e}")
        return
    
    # DataFrames de movimientos y elementos
    df_activity_inventory = pd.DataFrame(response.data)
    df_elements = pd.DataFrame(
        st_supabase_client.table("Elemento").select("*").execute().data
    )

    if not df_activity_inventory.empty:
        # Ajustar cantidades según el tipo de movimiento
        df_activity_inventory["cantidad"] = df_activity_inventory.apply(
            lambda row: -row["cantidad"]
            if row["tipo_movimiento"] in ["Salida", "De baja", "Entrega a sede"]
            else row["cantidad"],
            axis=1,
        )

        # Agrupar por elemento
        df_summary = df_activity_inventory.groupby("id_elemento", as_index=False)["cantidad"].sum()
        df_summary.rename(columns={"cantidad": "Stock_Final"}, inplace=True)
    else:
        # Si no hay movimientos, creamos un df vacío
        df_summary = pd.DataFrame(columns=["id_elemento", "Stock_Final"])

    # Hacer merge con todos los elementos (outer join garantiza que todos estén)
    df_final = pd.merge(
        df_elements.rename(columns={"nombre": "Elemento"}),
        df_summary,
        left_on="id",
        right_on="id_elemento",
        how="left"
    )
    
    df_final["Stock_Final"] = df_final["Stock_Final"].fillna(0).astype(int)
    return df_final[["id", "Elemento", "Stock_Final"]]


def crear_movimiento_inventario(st_supabase_client):
    st.subheader("✅ Creando movimiento de inventario")
    
    try:
        response = st_supabase_client.table("Elemento").select("id, nombre").execute()
        elementos = response.data
    except Exception as e:
        st.error(f"❌ Error al obtener elementos: {e}")
        return
        
    if not elementos:
            st.info("⚠️ No hay elementos creados.")
            return
        
    try:
        response = st_supabase_client.table("Usuario").select("id, nombres, apellidos").execute()
        usuarios = response.data
    except Exception as e:
        st.error(f"❌ Error al obtener usuarios: {e}")
        return
        
    if not usuarios:
        st.info("⚠️ No hay usuarios creados.")
        return
    
    # Selección dinámica (fuera del form para que actualice en tiempo real)
    tipo_movimiento = st.selectbox("Tipo de movimiento", options=["Entrada","Salida","De baja","Entrega a sede"])
    
    if tipo_movimiento == "Entrega a sede":
        try:
            response = st_supabase_client.table("Sede").select("id, nombre").execute()
            sedes = response.data
        except Exception as e:
            st.error(f"❌ Error al obtener sedes: {e}")
            return
        
        if not sedes:
            st.info("⚠️ No hay sedes creadas.")
            return
        
    # Formulario
    with st.form(key="Movimiento_Inventario_form"):
        # Mapeo de opciones
        st.text("Campos a llenar:")
        
        # Campos dinámicos según tipo
        if tipo_movimiento == "Entrega a sede":
            opciones_sedes = {sede["nombre"]: sede["id"] for sede in sedes}
            seleccion_sede = st.selectbox("Selecciona una sede", list(opciones_sedes.keys()))
            id_sede = opciones_sedes[seleccion_sede]
        
        # Campos comunes
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        persona_aprueba = st.text_input("Persona que realiza el movimiento")
        observaciones = st.text_area("Observaciones:")
        opciones = {elemento["nombre"]: elemento["id"] for elemento in elementos}
        seleccion_elemento = st.selectbox("Selecciona el elemento", list(opciones.keys()))
        
        id_elemento = opciones[seleccion_elemento]
        
        opciones_usuario = {usuario["nombres"]: usuario["id"] for usuario in usuarios}
        seleccion_usuario = st.selectbox("Selecciona el usuario", list(opciones_usuario.keys()))
        id_usuario = opciones_usuario[seleccion_usuario]
        
        # Botón submit
        send_button = st.form_submit_button("Agregar movimiento")
        
        if send_button:
            send_data = {
                "cantidad": cantidad,
                "tipo_movimiento": tipo_movimiento,
                "persona_aprueba": persona_aprueba.strip(),
                "observaciones": observaciones.strip() if observaciones else None,
                "id_elemento": id_elemento,
                "id_usuario": id_usuario,
            }
            
            try:
                df_inventario = calcular_inventario(st_supabase_client)
                
                stock_actual = int(df_inventario.loc[df_inventario["Elemento"] == seleccion_elemento, "Stock_Final"].values[0])
                
                if stock_actual <= cantidad and tipo_movimiento in ["Salida", "De baja", "Entrega a sede"]:
                    st.warning("⚠️ No hay stock disponible de este elemento.")
                    return
                else:
                    response  = st_supabase_client.table("MovimientoInventario").insert(send_data).execute()
                    id_movimiento = response.data[0]["id"]
                    # ---- Características dinámicas ----
                    if tipo_movimiento == "Entrega a sede":
                        send_data2 = {"id_sede": id_sede, "id_movimiento": id_movimiento}
                        st_supabase_client.table("ActividadEntregaSede").insert(send_data2).execute()

                    st.success("✅ Movimiento de inventario agregado correctamente")
            except Exception as e:
                st.error(f"❌ Error al crear el movimiento de inventario: {e}")


def obtener_inventario_general(st_supabase_client):
    
    df_final = calcular_inventario(st_supabase_client)
    
    _, col2, _ = st.columns([0.3,1,0.3])
    
    with col2:
        st.subheader("Inventario genenal")
        df_inventario = df_final[["Elemento","Stock_Final"]].rename(
                columns={"Elemento": "Nombre elemento", "Stock_Final": "Unidades"}
            )
        
        df_inventario = df_inventario.sort_values(by="Nombre elemento")
        
        st.dataframe(df_inventario,hide_index=True)
    
    
def obtener_movimientos_inventario(st_supabase_client):
    try:
        response = st_supabase_client.table("MovimientoInventario").select("*").execute()
    except Exception as e:
        st.error(f"❌ Error al traer los movimientos de inventario: {e}")
        return

    # DataFrames de movimientos y elementos
    df_activity_inventory = pd.DataFrame(response.data)
    df_elements = pd.DataFrame(
        st_supabase_client.table("Elemento").select("id, nombre").execute().data
    )

    if df_activity_inventory.empty:
        st.info("⚠️ No hay movimientos registrados.")
    else:
        # Merge con los nombres de los elementos
        df_merged = pd.merge(
            df_activity_inventory,
            df_elements.rename(columns={"nombre": "nombre_elemento"}),
            left_on="id_elemento",
            right_on="id",
            how="left"
        )
        

        # Reordenar columnas y reemplazar id_elemento por nombre
        columnas_mostrar = [
            "fecha", "nombre_elemento", "tipo_movimiento", "cantidad",
            "persona_aprueba", "observaciones"
        ]

        st.subheader("📑 Movimientos de inventario")
        st.dataframe(df_merged[columnas_mostrar].rename(columns={
            "id": "ID Movimiento",
            "fecha": "Fecha movimiento",
            "nombre_elemento": "Nombre de elemento",
            "tipo_movimiento": "Tipo de movimiento",
            "cantidad": "Cantidad",
            "persona_aprueba": "Responsable",
            "observaciones": "Observaciones",
            "created_at": "Fecha"
        }), hide_index=True)


# Inicializar conexión y estado
st_supabase_client = init_connection()
if "accion" not in st.session_state:
    st.session_state.accion = None

st.header("📦 Movimiento de inventario")

# Botones
col1, col2, col3, col4, col5 = st.columns([1,0.1,1,0.1,1])

with col1:
    if st.button("Crear movimiento"):
        st.session_state.accion = "crear"

with col3:
    if st.button("Obtener inventario general"):
        st.session_state.accion = "inventario"
with col5:
    if st.button("Obtener movimientos inventario"):
        st.session_state.accion = "movimientos_inventario"

# Mostrar contenido según la acción guardada en session_state
if st.session_state.accion == "crear":
    crear_movimiento_inventario(st_supabase_client)
elif st.session_state.accion == "inventario":
    obtener_inventario_general(st_supabase_client)
elif st.session_state.accion == "movimientos_inventario":
    obtener_movimientos_inventario(st_supabase_client)