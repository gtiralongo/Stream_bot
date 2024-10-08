import streamlit as st
import json
import pandas as pd
import requests

def save_info(info, file):
    with open(file, 'r') as fp:
        data = json.load(fp)
    data.update(info)
    with open(file, 'w') as fp:
        json.dump(data, fp)
    fp.close()

@st.cache_data
def get_save_info(file):
    with open(file, 'r') as fp:
        data = json.load(fp)
    fp.close()
    return data

# Función para obtener los precios actuales de todos los símbolos
def get_current_prices(symbols):
    # Esta es una implementación de ejemplo. Ajústela según su fuente de datos real.
    url ="https://api.binance.us/api/v3/ticker/price"
    response = requests.get(url)
    all_prices = {item['symbol']: float(item['price']) for item in response.json()}
    return {symbol: all_prices.get(symbol, 0) for symbol in symbols}

# Cargar datos
data = get_save_info('actions.json')

# Título de la aplicación
st.title('Dashboard de Bots de Trading')

# Obtener todos los símbolos únicos
symbols = list(set(bot_info['sym'] for bot_info in data['bot'].values()))

# Obtener los precios actuales para todos los símbolos
current_prices = get_current_prices(symbols)

# Crear DataFrame con todos los bots
bots_data = []
for bot_name, bot_info in data['bot'].items():
    current_price = current_prices.get(bot_info['sym'], 0)
    if bot_info['state'] == 'SELL':
        profit_loss = (current_price - float(bot_info['valor_compra'])) / float(bot_info['valor_compra']) * 100
    else:  # state == 'BUY'
        profit_loss = (float(bot_info['valor_venta']) - current_price) / current_price * 100
    
    bots_data.append({
        'Bot': bot_name,
        'Símbolo': bot_info['sym'],
        'Estado': bot_info['state'],
        'Precio Actual': current_price,
        'Precio Compra': bot_info['valor_compra'],
        'Precio Venta': bot_info['valor_venta'],
        'Ganancia/Pérdida (%)': round(profit_loss, 2)
    })

df_bots = pd.DataFrame(bots_data)

# Mostrar tabla de todos los bots
st.subheader('Resumen de Bots')
st.dataframe(df_bots)

# Seleccionar bot para modificar
selected_bot = st.selectbox('Seleccione un bot para modificar', list(data['bot'].keys()))

if selected_bot:
    st.subheader(f'Modificar {selected_bot}')
    bot_data = data['bot'][selected_bot]
    
    # Crear formulario para modificar datos del bot
    with st.form(key='bot_form'):
        sym = st.text_input('Símbolo', value=bot_data['sym'])
        run = st.selectbox('Run', ['on', 'off'], index=['on', 'off'].index(bot_data['run']))
        state = st.selectbox('Estado', ['BUY', 'SELL'], index=['BUY', 'SELL'].index(bot_data['state']))
        graf_temp = st.selectbox('Tiempo de Gráfico', ['15m', '1h', '4h', '1d', '1w', '1M'], index=['15m', '1h', '4h', '1d', '1w', '1M'].index(bot_data['graf_temp']))
        valor_compra = st.number_input('Valor de Compra', value=float(bot_data['valor_compra']))
        valor_venta = st.number_input('Valor de Venta', value=float(bot_data['valor_venta']))
        
        submit_button = st.form_submit_button(label='Guardar Cambios')
        
        if submit_button:
            # Actualizar datos del bot
            data['bot'][selected_bot].update({
                'sym': sym,
                'run': run,
                'state': state,
                'graf_temp': graf_temp,
                'valor_compra': str(valor_compra),
                'valor_venta': str(valor_venta)
            })
            
            # Guardar cambios en el archivo
            save_info(data, 'actions.json')
            st.success('Cambios guardados exitosamente')
