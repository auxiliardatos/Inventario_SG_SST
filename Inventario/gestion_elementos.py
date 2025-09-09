import streamlit as st
from connection import init_connection
from st_supabase_connection import SupabaseConnection
import pandas as pd
import datetime


def to_date(value):
    """Convierte string/None a datetime.date para usar en date_input"""
    if isinstance(value, str):
        try:
            return datetime.date.fromisoformat(value)
        except:
            return datetime.date.today()
    return value or datetime.date.today()


def crear_elemento(st_supabase_client):
    st.subheader("✅ Creando elemento")
    
    # Selección dinámica (fuera del form para que actualice en tiempo real)
    tipo = st.selectbox("Tipo de elemento", options=["EPP","Botiquin","Camilla","Extintor","Señaletica","Otro"])
    
    # Empieza el formulario
    with st.form(key="Elemento_form"):
        st.text("Campos a llenar:")
        nombre = st.text_input("Nombre de elemento")
        
        # Campos dinámicos según tipo
        if tipo == "Botiquin":
            clase_botiquin = st.text_input("Clase de botiquín")
            tipo_botiquin = st.text_input("Tipo de botiquín")
        elif tipo == "Camilla":
            tipo_camilla = st.text_input("Tipo de camilla")
        elif tipo == "EPP":
            epp_tipo_proteccion = st.text_input("Tipo de protección")
        elif tipo == "Extintor":
            codigo_extintor = st.text_input("Código de extintor")
            tipo_extintor = st.text_input("Tipo de extintor")
            clase_extintor = st.selectbox("Clase de extintor", options=["ABC","CO2","H2O (AGUA)", "H2O (AGUA) A PRESIÓN"])
            fecha_ultima_recarga = st.date_input("Fecha de última recarga")
            fecha_esperada_recarga = st.date_input("Fecha esperada de recarga")
        elif tipo == "Señaletica":
            tipo_senaletica = st.text_input("Tipo de señalética")
        
        # Campos comunes
        unidad_medida = st.text_input("Unidades de medida")
        ruta_imagen = st.text_input("Imagen")
        descripcion_uso = st.text_area("Descripción de uso")
        descripcion_mantenimiento = st.text_area("Descripción de mantenimiento")
        descripcion_tecnica = st.text_area("Descripción técnica")
        estandar_normativo = st.text_input("Estandar normativo")    
        periodo_cambio = st.text_input("Periodo de cambio")
        observaciones = st.text_area("Observaciones adicionales")
        
        # Botón de submit
        send_button = st.form_submit_button("Agregar elemento nuevo")
        
        if send_button:
            if not nombre.strip():  # <- valida que no esté vacío o solo espacios
                st.warning("⚠️ El nombre del elemento es obligatorio.")
            else:
                send_data = {
                    "nombre": nombre,
                    "tipo": tipo,
                    "unidad_medida": unidad_medida,
                    "ruta_imagen": ruta_imagen,
                    "descripcion_uso": descripcion_uso,
                    "descripcion_mantenimiento": descripcion_mantenimiento,
                    "estandar_normativo": estandar_normativo,
                    "periodo_cambio": periodo_cambio,
                    "descripcion_tecnica": descripcion_tecnica,
                    "observaciones": observaciones
                }

                try:
                    response  = st_supabase_client.table("Elemento").insert(send_data).execute()
                    id_elemento = response.data[0]["id"]

                    # ---- Características dinámicas ----
                    if tipo == "Botiquin":
                        send_data2 = {"clase_botiquin": clase_botiquin, "tipo_botiquin": tipo_botiquin, "id_elemento": id_elemento}
                        st_supabase_client.table("CaracteristicaBotiquin").insert(send_data2).execute()
                    elif tipo == "Camilla":
                        send_data2 = {"tipo_camilla": tipo_camilla, "id_elemento": id_elemento}
                        st_supabase_client.table("CaracteristicaCamilla").insert(send_data2).execute()
                    elif tipo == "EPP":
                        send_data2 = {"tipo_proteccion": epp_tipo_proteccion, "id_elemento": id_elemento}
                        st_supabase_client.table("CaracteristicaEpp").insert(send_data2).execute()
                    elif tipo == "Extintor":
                        send_data2 = {
                            "tipo_extintor": tipo_extintor,
                            "codigo": codigo_extintor,
                            "clase_extintor": clase_extintor,
                            "fecha_ultima_recarga": fecha_ultima_recarga.isoformat() if fecha_ultima_recarga else None,
                            "fecha_esperada_recarga": fecha_esperada_recarga.isoformat() if fecha_ultima_recarga else None,
                            "id_elemento": id_elemento,
                        }
                        st_supabase_client.table("CaracteristicaExtintor").insert(send_data2).execute()
                    elif tipo == "Señaletica":
                        send_data2 = {"tipo_senal": tipo_senaletica, "id_elemento": id_elemento}
                        st_supabase_client.table("CaracteristicaSenaletica").insert(send_data2).execute()

                    st.success("Elemento agregado correctamente ✅")
                except Exception as e:
                    st.error(f"❌ Error al crear el elemento: {e}")


def eliminar_elemento(st_supabase_client):
    st.subheader("🗑️ Eliminando elemento")
    
    # Traer todos los elementos disponibles
    try:
        response = st_supabase_client.table("Elemento").select("id, nombre, tipo").execute()
        elementos = response.data
    except Exception as e:
        st.error(f"❌ Error al obtener elementos: {e}")
        return
    
    if not elementos:
        st.info("No hay elementos registrados.")
        return
    
    # Mostrar opciones en un selectbox
    opciones = {f"{el['nombre']} ({el['tipo']})": el["id"] for el in elementos}
    seleccion = st.selectbox("Selecciona el elemento a eliminar", list(opciones.keys()))
    
    id_elemento = opciones[seleccion]
    
    # Confirmación
    confirmar = st.checkbox(f"⚠️ Confirmo que quiero eliminar al usuario: {seleccion}")
    
    if st.button("Eliminar definitivamente 🚨"):
        if not confirmar:
            st.warning("Debes confirmar la eliminación antes de continuar.")
            return
        
        try:
            # Eliminar registros relacionados primero (dependiendo del tipo)
            tipo = next(el["tipo"] for el in elementos if el["id"] == id_elemento)
            
            if tipo == "Botiquin":
                st_supabase_client.table("CaracteristicaBotiquin").delete().eq("id_elemento", id_elemento).execute()
            elif tipo == "Camilla":
                st_supabase_client.table("CaracteristicaCamilla").delete().eq("id_elemento", id_elemento).execute()
            elif tipo == "EPP":
                st_supabase_client.table("CaracteristicaEpp").delete().eq("id_elemento", id_elemento).execute()
            elif tipo == "Extintor":
                st_supabase_client.table("CaracteristicaExtintor").delete().eq("id_elemento", id_elemento).execute()
            elif tipo == "Señaletica":
                st_supabase_client.table("CaracteristicaSenaletica").delete().eq("id_elemento", id_elemento).execute()
            
            # Eliminar el elemento principal
            st_supabase_client.table("Elemento").delete().eq("id", id_elemento).execute()
            
            st.success(f"Elemento '{seleccion}' eliminado correctamente ✅")
        except Exception as e:
            st.error(f"❌ Error al eliminar: {e}")
    
    
def editar_elemento(st_supabase_client):
    st.subheader("✏️ Editando elemento")

    # 1. Obtener todos los elementos
    elementos = st_supabase_client.table("Elemento").select("*").execute().data

    if not elementos:
        st.info("No hay elementos para editar.")
        return

    # 2. Seleccionar cuál editar
    opciones = {e["id"]: f'{e["id"]} - {e["nombre"]} ({e["tipo"]})' for e in elementos}
    id_seleccionado = st.selectbox("Selecciona un elemento", options=list(opciones.keys()), format_func=lambda x: opciones[x])

    # Buscar datos actuales
    elemento = next(e for e in elementos if e["id"] == id_seleccionado)

    # 3. Formulario con datos precargados
    with st.form(key="EditarElementoForm"):
        nombre = st.text_input("Nombre", value=elemento["nombre"])
        unidad_medida = st.text_input("Unidades de medida", value=elemento["unidad_medida"])
        ruta_imagen = st.text_input("Imagen", value=elemento["ruta_imagen"] or "")
        descripcion_uso = st.text_area("Descripción de uso", value=elemento["descripcion_uso"] or "")
        descripcion_mantenimiento = st.text_area("Descripción de mantenimiento", value=elemento["descripcion_mantenimiento"] or "")
        descripcion_tecnica = st.text_area("Descripción técnica", value=elemento["descripcion_tecnica"] or "")
        estandar_normativo = st.text_input("Estandar normativo", value=elemento["estandar_normativo"] or "")
        periodo_cambio = st.text_input("Periodo de cambio", value=elemento["periodo_cambio"] or "")
        observaciones = st.text_area("Observaciones", value=elemento["observaciones"] or "")

        # 4. Cargar también la tabla de características según el tipo
        tipo = elemento["tipo"]

        # Diccionario de tablas
        tablas_tipo = {
            "Botiquin": "CaracteristicaBotiquin",
            "Camilla": "CaracteristicaCamilla",
            "EPP": "CaracteristicaEpp",
            "Extintor": "CaracteristicaExtintor",
            "Señaletica": "CaracteristicaSenaletica",
        }

        caracteristicas = {}
        if tipo in tablas_tipo:
            resp = st_supabase_client.table(tablas_tipo[tipo]).select("*").eq("id_elemento", id_seleccionado).execute()
            if resp.data:
                caracteristicas = resp.data[0]
        # Campos dinámicos
        if tipo == "Botiquin":
            clase_botiquin = st.text_input("Clase de botiquín", value=caracteristicas.get("clase_botiquin", ""))
            tipo_botiquin = st.text_input("Tipo de botiquín", value=caracteristicas.get("tipo_botiquin", ""))
        elif tipo == "Camilla":
            tipo_camilla = st.text_input("Tipo de camilla", value=caracteristicas.get("tipo_camilla", ""))
        elif tipo == "EPP":
            epp_tipo_proteccion = st.text_input("Tipo de protección", value=caracteristicas.get("tipo_proteccion", "")) 
        elif tipo == "Extintor":
            tipo_extintor = st.text_input("Tipo de extintor", value=caracteristicas.get("tipo_extintor", ""))
            codigo_extintor = st.text_input("Código de extintor", value=caracteristicas.get("codigo", ""))
            opciones_extintor = ["ABC","CO2","H2O (AGUA)", "H2O (AGUA) A PRESIÓN"]
            clase_guardada = caracteristicas.get("clase_extintor", opciones_extintor[0])  # por defecto el primero
            clase_extintor = st.selectbox(
                "Clase de extintor",
                options=opciones_extintor,
                index=opciones_extintor.index(clase_guardada) if clase_guardada in opciones_extintor else 0
            )
        
            fecha_ultima_recarga = st.date_input(
                "Fecha de última recarga",
                value=to_date(caracteristicas.get("fecha_ultima_recarga"))
            )
            fecha_esperada_recarga = st.date_input(
                "Fecha esperada de recarga",
                value=to_date(caracteristicas.get("fecha_esperada_recarga"))
            )
        elif tipo == "Señaletica":
            tipo_senaletica = st.text_input("Tipo de señalética", value=caracteristicas.get("tipo_senal", ""))

        # Botón submit
        update_button = st.form_submit_button("Actualizar elemento")

        if update_button:
            try:
                # 5. Actualizar tabla Elemento
                update_data = {
                    "nombre": nombre,
                    "unidad_medida": unidad_medida,
                    "ruta_imagen": ruta_imagen,
                    "descripcion_uso": descripcion_uso,
                    "descripcion_mantenimiento": descripcion_mantenimiento,
                    "estandar_normativo": estandar_normativo,
                    "periodo_cambio": periodo_cambio,
                    "descripcion_tecnica": descripcion_tecnica,
                    "observaciones": observaciones
                }

                st_supabase_client.table("Elemento").update(update_data).eq("id", id_seleccionado).execute()

                # 6. Actualizar características según tipo
                if tipo in tablas_tipo:
                    update_carac = {}
                    if tipo == "Botiquin":
                        update_carac = {"clase_botiquin": clase_botiquin, "tipo_botiquin":tipo_botiquin}
                    elif tipo == "Camilla":
                        update_carac = {"tipo_camilla": tipo_camilla}
                    elif tipo == "EPP":
                        update_carac = {"tipo_proteccion": epp_tipo_proteccion}
                    elif tipo == "Extintor":
                        update_carac = {
                            "tipo_extintor": tipo_extintor,
                            "codigo": codigo_extintor,
                            "clase_extintor": clase_extintor,
                            "fecha_ultima_recarga": fecha_ultima_recarga.isoformat() if fecha_ultima_recarga else None,
                            "fecha_esperada_recarga": fecha_esperada_recarga.isoformat() if fecha_esperada_recarga else None
                        }
                    elif tipo == "Señaletica":
                        update_carac = {"tipo_senal": tipo_senaletica}

                    st_supabase_client.table(tablas_tipo[tipo]).update(update_carac).eq("id_elemento", id_seleccionado).execute()

                st.success(f"Elemento {id_seleccionado} actualizado correctamente ✅")

            except Exception as e:
                st.error(f"❌ Error al actualizar: {e}")


# Inicializar conexión y estado
st_supabase_client = init_connection()
if "accion" not in st.session_state:
    st.session_state.accion = None

st.header("Gestión de inventario")

# Botones
col1, col2, col3, col4, col5 = st.columns([1,0.1,1,0.1,1])

with col1:
    if st.button("Crear elemento"):
        st.session_state.accion = "crear"

with col3:
    if st.button("Eliminar elemento"):
        st.session_state.accion = "eliminar"

with col5:
    if st.button("Editar elemento"):
        st.session_state.accion = "editar"

# Mostrar contenido según la acción guardada en session_state
if st.session_state.accion == "crear":
    crear_elemento(st_supabase_client)
elif st.session_state.accion == "editar":
    editar_elemento(st_supabase_client)
elif st.session_state.accion == "eliminar":
    eliminar_elemento(st_supabase_client)