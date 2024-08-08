import streamlit as st
import json
import pandas as pd

# Cargar los datos del JSON
@st.cache_data
def load_data():
    data = json.loads('actions.json')
    return data

data = load_data()

# Título de la aplicación
st.title('Dashboard de Bots de Trading')

# Sidebar para seleccionar el bot
bot_names = list(data['bot'].keys())
selected_bot = st.sidebar.selectbox('Seleccione un bot', bot_names)

# Mostrar información del bot seleccionado
if selected_bot:
    bot_data = data['bot'][selected_bot]
    st.subheader(f'Información de {selected_bot}')
    
    # Crear un DataFrame con la información del bot
    df = pd.DataFrame([bot_data])
    st.dataframe(df.T)

    # Mostrar gráficos o métricas adicionales
    col1, col2, col3 = st.columns(3)
    col1.metric("Símbolo", bot_data['sym'])
    col2.metric("Estado", bot_data['state'])
    col3.metric("Tiempo de gráfico", bot_data['graf_temp'])

# Sección para mostrar indicadores
st.subheader('Indicadores')
st.write(data['indicators'])

# Sección para mostrar límites de RSI
st.subheader('Límites de RSI')
st.json(data['RSI_limit'])
