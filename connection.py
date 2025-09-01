import streamlit as st
from st_supabase_connection import SupabaseConnection

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    st_supabase_client = st.connection(
        name="supabase_connection",
        type=SupabaseConnection,
        url=st.secrets["SUPABASE_URL"],
        key=st.secrets["SUPABASE_KEY"]
    )
    
    return st_supabase_client